#!/usr/bin/env python3
"""Safely validate one fixed local Ollama model with one minimal inference."""

from __future__ import annotations

import argparse
import contextlib
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


EXPECTED_OLLAMA_VERSION = "0.20.2"
HOST = "127.0.0.1"
PORT = 11434
BASE_URL = f"http://{HOST}:{PORT}"
MAX_OUTPUT_TOKENS = 16
MIN_AVAILABLE_RAM = 4 * 1024**3
SERVER_TIMEOUT_SECONDS = 45
MODEL_LOAD_TIMEOUT_SECONDS = 600
KEEP_ALIVE = "2m"
PROMPT = "Reply with exactly: QWEN_LOCAL_OK"
EXPECTED_OUTPUT = "QWEN_LOCAL_OK"
MODEL_MEDIA_TYPE = "application/vnd.ollama.image.model"
LICENSE_MEDIA_TYPE = "application/vnd.ollama.image.license"
PROFILE_PATH = Path(__file__).resolve().parent.parent / "model-profiles.json"
DEFAULT_PROFILE_ID = "qwen3.6-35b-q4km"
REQUIRED_PROFILE_IDS = {"qwen3.6-35b-q4km", "qwen3.6-27b-q4km"}
COMMON_PROFILE_FIELDS = {
    "ollama_model",
    "digest",
    "manifest_digest",
    "architecture",
    "architecture_type",
    "parameters_total",
    "parameters_active",
    "quantization",
    "declared_size_bytes",
    "native_context_tokens",
    "test_context_tokens",
    "endpoint",
    "license",
    "status",
}
ALLOCATION_POLICY_FIELDS = {
    "gpu_overhead_bytes",
    "gpu_overhead_gib",
    "minimum_free_vram_mib",
    "context_length",
    "num_parallel",
}
GPU_OVERHEAD_PROFILE_ID = "qwen3.6-27b-q4km"
MAX_REASONABLE_GPU_OVERHEAD_BYTES = 64 * 1024**3
MAX_REASONABLE_FREE_VRAM_MIB = 64 * 1024


class ProbeError(Exception):
    """A safety, identity, resource, or runtime condition failed."""


def load_model_profiles(path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = path or PROFILE_PATH
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError("model profile registry is unreadable") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise ProbeError("model profile registry has an unsupported schema")
    profiles = document.get("profiles")
    if not isinstance(profiles, dict) or set(profiles) != REQUIRED_PROFILE_IDS:
        raise ProbeError("model profile registry must contain exactly the two fixed profiles")
    for profile_id, profile in profiles.items():
        expected_fields = COMMON_PROFILE_FIELDS | (
            ALLOCATION_POLICY_FIELDS if profile_id == GPU_OVERHEAD_PROFILE_ID else set()
        )
        if not isinstance(profile, dict) or set(profile) != expected_fields:
            raise ProbeError(f"model profile {profile_id} has incomplete or unknown fields")
        if profile["endpoint"] != BASE_URL:
            raise ProbeError(f"model profile {profile_id} is not locked to loopback")
        if profile["test_context_tokens"] != 16_384:
            raise ProbeError(f"model profile {profile_id} has an unexpected test context")
        if profile["native_context_tokens"] < profile["test_context_tokens"]:
            raise ProbeError(f"model profile {profile_id} has an invalid native context")
        if profile["quantization"] != "Q4_K_M" or profile["status"] != "experimental":
            raise ProbeError(f"model profile {profile_id} has unexpected fixed metadata")
        if profile["license"] != "Apache-2.0":
            raise ProbeError(f"model profile {profile_id} has an unexpected license")
        for key in ("digest", "manifest_digest"):
            value = profile[key]
            if not isinstance(value, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
                raise ProbeError(f"model profile {profile_id} has an invalid {key}")
        if not isinstance(profile["declared_size_bytes"], int) or profile["declared_size_bytes"] <= 0:
            raise ProbeError(f"model profile {profile_id} has an invalid declared size")
        dense = profile["architecture_type"] == "dense"
        if dense and profile["parameters_active"] != profile["parameters_total"]:
            raise ProbeError(f"dense model profile {profile_id} must activate all parameters")
        if not isinstance(profile["parameters_active"], str) or not profile["parameters_active"]:
            raise ProbeError(f"model profile {profile_id} must declare active parameters")
        if dense == ("moe" in str(profile["architecture"]).lower()):
            raise ProbeError(f"model profile {profile_id} has inconsistent architecture metadata")
        if profile_id == GPU_OVERHEAD_PROFILE_ID:
            policy_values = {key: profile[key] for key in ALLOCATION_POLICY_FIELDS}
            if any(isinstance(value, bool) or not isinstance(value, int) for value in policy_values.values()):
                raise ProbeError(f"model profile {profile_id} allocation policy must use integers")
            overhead = profile["gpu_overhead_bytes"]
            if overhead < 0 or overhead > MAX_REASONABLE_GPU_OVERHEAD_BYTES:
                raise ProbeError(f"model profile {profile_id} has an unreasonable GPU overhead")
            if profile["gpu_overhead_gib"] < 0 or overhead != profile["gpu_overhead_gib"] * 1024**3:
                raise ProbeError(f"model profile {profile_id} has inconsistent GPU overhead units")
            minimum_vram = profile["minimum_free_vram_mib"]
            if minimum_vram < 0 or minimum_vram > MAX_REASONABLE_FREE_VRAM_MIB:
                raise ProbeError(f"model profile {profile_id} has an unreasonable free VRAM minimum")
            if profile["context_length"] != profile["test_context_tokens"]:
                raise ProbeError(f"model profile {profile_id} has inconsistent context policy")
            if profile["num_parallel"] != 1:
                raise ProbeError(f"model profile {profile_id} must keep parallelism at one")
    return profiles


def activate_profile(profile_id: str = DEFAULT_PROFILE_ID) -> dict[str, Any]:
    global ACTIVE_PROFILE_ID, ACTIVE_PROFILE, MODEL, EXPECTED_DIGEST, CONTEXT_TOKENS
    global GPU_OVERHEAD_BYTES, MINIMUM_FREE_VRAM_MIB, NUM_PARALLEL
    profiles = load_model_profiles()
    if profile_id not in profiles:
        raise ProbeError(f"unknown fixed model profile: {profile_id}")
    ACTIVE_PROFILE_ID = profile_id
    ACTIVE_PROFILE = dict(profiles[profile_id])
    MODEL = str(ACTIVE_PROFILE["ollama_model"])
    EXPECTED_DIGEST = str(ACTIVE_PROFILE["digest"])
    CONTEXT_TOKENS = int(ACTIVE_PROFILE.get("context_length", ACTIVE_PROFILE["test_context_tokens"]))
    GPU_OVERHEAD_BYTES = ACTIVE_PROFILE.get("gpu_overhead_bytes")
    MINIMUM_FREE_VRAM_MIB = ACTIVE_PROFILE.get("minimum_free_vram_mib")
    NUM_PARALLEL = int(ACTIVE_PROFILE.get("num_parallel", 1))
    return ACTIVE_PROFILE


ACTIVE_PROFILE_ID = ""
ACTIVE_PROFILE: dict[str, Any] = {}
MODEL = ""
EXPECTED_DIGEST = ""
CONTEXT_TOKENS = 0
GPU_OVERHEAD_BYTES: int | None = None
MINIMUM_FREE_VRAM_MIB: int | None = None
NUM_PARALLEL = 1
activate_profile()


def allocation_policy() -> dict[str, int] | None:
    if GPU_OVERHEAD_BYTES is None:
        return None
    return {
        "gpu_overhead_bytes": int(GPU_OVERHEAD_BYTES),
        "gpu_overhead_gib": int(ACTIVE_PROFILE["gpu_overhead_gib"]),
        "minimum_free_vram_mib": int(MINIMUM_FREE_VRAM_MIB),
        "context_length": CONTEXT_TOKENS,
        "num_parallel": NUM_PARALLEL,
    }


class InferenceBudget:
    """A hard one-call budget with no retry path."""

    def __init__(self) -> None:
        self.calls = 0

    def reserve(self) -> None:
        if self.calls >= 1:
            raise ProbeError("the single inference-call budget is exhausted")
        self.calls += 1


def validate_endpoint(url: str) -> str:
    parsed = urlparse.urlparse(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != HOST
        or parsed.port != PORT
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ProbeError("only the fixed loopback Ollama endpoint is permitted")
    return url


def _ollama_executable() -> str:
    executable = shutil.which("ollama")
    if executable is None:
        raise ProbeError("Ollama executable is not available on PATH")
    return executable


def _run_text(command: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, text=True, capture_output=True, check=False, timeout=timeout
    )


def validate_version(output: str) -> None:
    normalized = output.strip()
    if f"client version is {EXPECTED_OLLAMA_VERSION}" not in normalized and normalized != EXPECTED_OLLAMA_VERSION:
        raise ProbeError(
            f"Ollama client version differs from required {EXPECTED_OLLAMA_VERSION}"
        )


def _preflight_cli() -> tuple[str, str]:
    executable = _ollama_executable()
    version = _run_text([executable, "--version"])
    serve_help = _run_text([executable, "serve", "--help"])
    show_help = _run_text([executable, "show", "--help"])
    if version.returncode != 0 or serve_help.returncode != 0 or show_help.returncode != 0:
        raise ProbeError("Ollama version/help preflight returned a non-zero exit code")
    validate_version(version.stdout + version.stderr)
    required = ("OLLAMA_HOST", "OLLAMA_NO_CLOUD", "OLLAMA_CONTEXT_LENGTH")
    missing = [name for name in required if name not in serve_help.stdout]
    if missing:
        raise ProbeError("Ollama 0.20.2 help lacks required controls: " + ", ".join(missing))
    return executable, version.stdout + version.stderr


def model_root() -> Path:
    configured = os.environ.get("OLLAMA_MODELS")
    return Path(configured) if configured else Path.home() / ".ollama" / "models"


def _blob_path(root: Path, digest: str) -> Path:
    if not digest.startswith("sha256:") or len(digest) != 71:
        raise ProbeError("model manifest contains an invalid digest")
    return root / "blobs" / ("sha256-" + digest.removeprefix("sha256:"))


def _manifest_path(root: Path, model: str | None = None) -> Path:
    model = model or MODEL
    try:
        name, tag = model.split(":", 1)
    except ValueError as exc:
        raise ProbeError("model profile contains an invalid Ollama identifier") from exc
    if name != "qwen3.6" or not tag or any(part in tag for part in ("/", "\\", "..")):
        raise ProbeError("model profile contains an unexpected Ollama identifier")
    return root / "manifests" / "registry.ollama.ai" / "library" / name / tag


def validate_local_model(root: Path | None = None) -> dict[str, Any]:
    root = root or model_root()
    manifest_path = _manifest_path(root)
    try:
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError(f"the exact local model manifest is unavailable: {type(exc).__name__}") from exc
    if not isinstance(manifest, dict):
        raise ProbeError("the exact local model manifest is not a JSON object")
    entries = [manifest.get("config")] + list(manifest.get("layers", []))
    if any(not isinstance(entry, dict) for entry in entries):
        raise ProbeError("the exact local model manifest has malformed entries")
    model_entries = [entry for entry in entries if entry.get("mediaType") == MODEL_MEDIA_TYPE]
    if len(model_entries) != 1:
        raise ProbeError("the exact local model manifest has no unique model layer")
    declared_digest = str(model_entries[0].get("digest", ""))
    if declared_digest != EXPECTED_DIGEST:
        raise ProbeError(
            f"model digest divergence: declared {declared_digest or '<missing>'}"
        )
    if int(model_entries[0].get("size", -1)) != int(ACTIVE_PROFILE["declared_size_bytes"]):
        raise ProbeError("model layer size differs from the active profile")
    blobs: list[dict[str, Any]] = []
    for entry in entries:
        digest = str(entry.get("digest", ""))
        declared_size = int(entry.get("size", -1))
        path = _blob_path(root, digest)
        if not path.is_file():
            raise ProbeError(f"required local blob is missing: {digest}")
        actual_size = path.stat().st_size
        if actual_size != declared_size:
            raise ProbeError(f"required local blob has a size mismatch: {digest}")
        blobs.append(
            {
                "media_type": str(entry.get("mediaType", "")),
                "digest": digest,
                "size_bytes": actual_size,
            }
        )
    config_entry = manifest["config"]
    try:
        config = json.loads(_blob_path(root, str(config_entry["digest"])).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        raise ProbeError("local model configuration blob is unreadable") from exc
    manifest_digest = "sha256:" + hashlib.sha256(manifest_raw).hexdigest()
    if manifest_digest != ACTIVE_PROFILE["manifest_digest"]:
        raise ProbeError("model manifest digest differs from the active profile")
    expected_config = {
        "model_format": "gguf",
        "model_family": ACTIVE_PROFILE["architecture"],
        "model_type": ACTIVE_PROFILE["parameters_total"],
        "file_type": ACTIVE_PROFILE["quantization"],
    }
    if any(config.get(key) != value for key, value in expected_config.items()):
        raise ProbeError("model configuration metadata differs from the active profile")
    license_entries = [entry for entry in entries if entry.get("mediaType") == LICENSE_MEDIA_TYPE]
    if len(license_entries) != 1:
        raise ProbeError("the exact local model manifest has no unique license layer")
    try:
        license_text = _blob_path(root, str(license_entries[0]["digest"])).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, KeyError) as exc:
        raise ProbeError("local model license blob is unreadable") from exc
    if not re.search(r"Apache License\s+Version 2\.0", license_text):
        raise ProbeError("local model license is not Apache 2.0")
    return {
        "profile": ACTIVE_PROFILE_ID,
        "model": MODEL,
        "declared_digest": declared_digest,
        "manifest_digest": manifest_digest,
        "model_size_bytes": int(model_entries[0]["size"]),
        "format": config.get("model_format"),
        "family": config.get("model_family"),
        "families": config.get("model_families", []),
        "parameter_size": config.get("model_type"),
        "quantization": config.get("file_type"),
        "architecture_type": ACTIVE_PROFILE["architecture_type"],
        "parameters_active": ACTIVE_PROFILE["parameters_active"],
        "native_context_tokens": ACTIVE_PROFILE["native_context_tokens"],
        "license": ACTIVE_PROFILE["license"],
        "license_verified": True,
        "required_blobs": blobs,
        "all_required_blobs_present": True,
        "digest_recalculated": False,
    }


def model_store_snapshot(root: Path | None = None) -> dict[str, tuple[int, int, str | None]]:
    """Snapshot only the fixed model manifest and blobs, without hashing the 23.9 GB layer."""
    root = root or model_root()
    manifest_path = _manifest_path(root)
    try:
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError("cannot snapshot the fixed model store entries") from exc
    paths = [manifest_path]
    entries = [manifest.get("config")] + list(manifest.get("layers", []))
    for entry in entries:
        if not isinstance(entry, dict):
            raise ProbeError("cannot snapshot malformed model store entries")
        paths.append(_blob_path(root, str(entry.get("digest", ""))))
    snapshot: dict[str, tuple[int, int, str | None]] = {}
    for index, path in enumerate(paths):
        stat = path.stat()
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if index == 0 else None
        snapshot[str(index)] = (stat.st_size, stat.st_mtime_ns, digest)
    return snapshot


def all_profile_store_snapshot(root: Path | None = None) -> dict[str, tuple[int, int, str | None]]:
    root = root or model_root()
    active = ACTIVE_PROFILE_ID
    combined: dict[str, tuple[int, int, str | None]] = {}
    try:
        for profile_id in sorted(load_model_profiles()):
            activate_profile(profile_id)
            for key, value in model_store_snapshot(root).items():
                combined[f"{profile_id}:{key}"] = value
    finally:
        activate_profile(active)
    return combined


def _port_is_free() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        sock.bind((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _loopback_responds(timeout: float = 0.25) -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=timeout):
            return True
    except OSError:
        return False


def _process_rows() -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name | ConvertTo-Json -Compress",
    ]
    result = _run_text(command)
    if result.returncode != 0 or not result.stdout.strip():
        raise ProbeError("could not enumerate processes safely")
    parsed = json.loads(result.stdout)
    rows = parsed if isinstance(parsed, list) else [parsed]
    return [row for row in rows if isinstance(row, dict)]


def ollama_processes(rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = rows if rows is not None else _process_rows()
    relevant = []
    for row in rows:
        name = str(row.get("Name", "")).lower()
        if "ollama" in name:
            relevant.append(
                {
                    "pid": int(row.get("ProcessId", 0)),
                    "parent_pid": int(row.get("ParentProcessId", 0)),
                    "name": name,
                }
            )
    return relevant


def descendants(parent_pid: int, rows: list[dict[str, Any]] | None = None) -> set[int]:
    rows = rows if rows is not None else _process_rows()
    by_parent: dict[int, set[int]] = {}
    for row in rows:
        pid = int(row.get("ProcessId", 0))
        ppid = int(row.get("ParentProcessId", 0))
        by_parent.setdefault(ppid, set()).add(pid)
    found: set[int] = set()
    pending = [parent_pid]
    while pending:
        current = pending.pop()
        for child in by_parent.get(current, set()):
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def _pid_exists(pid: int) -> bool:
    if os.name != "nt":
        return False
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    exit_code = wintypes.DWORD()
    try:
        if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == 259  # STILL_ACTIVE
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def listener_records() -> list[dict[str, Any]]:
    if os.name != "nt":
        raise ProbeError("listener verification is implemented for the required Windows host")
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Get-NetTCPConnection -State Listen -LocalPort {PORT} -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess | ConvertTo-Json -Compress",
    ]
    result = _run_text(command)
    if result.returncode != 0:
        raise ProbeError("could not verify the owned Ollama listener")
    if not result.stdout.strip():
        return []
    parsed = json.loads(result.stdout)
    rows = parsed if isinstance(parsed, list) else [parsed]
    return [
        {
            "local_address": str(row.get("LocalAddress", "")),
            "local_port": int(row.get("LocalPort", 0)),
            "owning_pid": int(row.get("OwningProcess", 0)),
        }
        for row in rows
        if isinstance(row, dict)
    ]


def require_owned_loopback_listener(records: list[dict[str, Any]], owned_pids: set[int]) -> None:
    if not records:
        raise ProbeError("no listener was found on the fixed Ollama port")
    for record in records:
        if record["local_address"] != HOST or record["owning_pid"] not in owned_pids:
            raise ProbeError("Ollama listener is not exclusively owned on 127.0.0.1")


def terminate_owned_pid(pid: int, owned_pids: set[int]) -> None:
    if pid not in owned_pids:
        raise ProbeError("refusing to terminate a PID not owned by this probe")
    if not _pid_exists(pid):
        return
    PROCESS_TERMINATE = 0x0001
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not handle:
        raise ProbeError(f"could not open owned PID {pid} for termination")
    try:
        if not ctypes.windll.kernel32.TerminateProcess(handle, 1):
            raise ProbeError(f"could not terminate owned PID {pid}")
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def ram_snapshot() -> dict[str, int]:
    if os.name != "nt":
        raise ProbeError("RAM measurement is implemented for the required Windows host")
    status = _MemoryStatus()
    status.dwLength = ctypes.sizeof(_MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ProbeError("GlobalMemoryStatusEx failed")
    return {
        "total_bytes": int(status.ullTotalPhys),
        "used_bytes": int(status.ullTotalPhys - status.ullAvailPhys),
        "available_bytes": int(status.ullAvailPhys),
    }


def gpu_snapshot() -> dict[str, Any]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        raise ProbeError("nvidia-smi is unavailable")
    gpu = _run_text(
        [
            executable,
            "--query-gpu=name,memory.total,memory.used,memory.free",
            "--format=csv,noheader,nounits",
        ]
    )
    if gpu.returncode != 0 or not gpu.stdout.strip():
        raise ProbeError("nvidia-smi GPU query failed")
    fields = [part.strip() for part in gpu.stdout.splitlines()[0].split(",")]
    if len(fields) != 4:
        raise ProbeError("unexpected nvidia-smi GPU output")
    processes_result = _run_text(
        [
            executable,
            "--query-compute-apps=pid,process_name,used_gpu_memory",
            "--format=csv,noheader,nounits",
        ]
    )
    relevant = []
    if processes_result.returncode == 0:
        for line in processes_result.stdout.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) >= 3 and any(mark in parts[1].lower() for mark in ("ollama", "runner")):
                used_mib = int(parts[2]) if parts[2].isdigit() else None
                relevant.append(
                    {"pid": int(parts[0]), "name": Path(parts[1]).name, "used_mib": used_mib}
                )
    return {
        "name": fields[0],
        "total_mib": int(fields[1]),
        "used_mib": int(fields[2]),
        "available_mib": int(fields[3]),
        "relevant_compute_processes": relevant,
    }


def resource_snapshot() -> dict[str, Any]:
    return {"ram": ram_snapshot(), "gpu": gpu_snapshot()}


def _api_request(path: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    if not path.startswith("/") or "//" in path:
        raise ProbeError("invalid fixed API path")
    url = validate_endpoint(BASE_URL + path)
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(url, data=data, method="GET" if data is None else "POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except (OSError, urlerror.URLError, urlerror.HTTPError) as exc:
        raise ProbeError(f"loopback Ollama request failed for {path}: {type(exc).__name__}") from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError(f"loopback Ollama returned invalid JSON for {path}") from exc
    if not isinstance(parsed, dict):
        raise ProbeError(f"loopback Ollama returned a non-object for {path}")
    return parsed


def parse_show(data: dict[str, Any]) -> dict[str, Any]:
    details = data.get("details")
    info = data.get("model_info")
    if not isinstance(details, dict) or not isinstance(info, dict):
        raise ProbeError("/api/show omitted model details or model_info")
    context_values = [int(value) for key, value in info.items() if str(key).endswith(".context_length")]
    max_context = max(context_values) if context_values else None
    template = data.get("template", "")
    if not isinstance(template, str):
        raise ProbeError("/api/show returned a non-text template")
    capabilities = data.get("capabilities", [])
    if not isinstance(capabilities, list):
        raise ProbeError("/api/show returned malformed capabilities")
    return {
        "format": details.get("format"),
        "family": details.get("family"),
        "families": details.get("families", []),
        "parameter_size": details.get("parameter_size"),
        "quantization": details.get("quantization_level"),
        "maximum_context_tokens": max_context,
        "capabilities": [str(item) for item in capabilities],
        "template_characters": len(template),
        "template_sha256": hashlib.sha256(template.encode("utf-8")).hexdigest(),
        "parameters": str(data.get("parameters", "")),
    }


def validate_show_for_active_profile(shown: dict[str, Any]) -> None:
    expected = {
        "format": "gguf",
        "family": ACTIVE_PROFILE["architecture"],
        "parameter_size": ACTIVE_PROFILE["parameters_total"],
        "quantization": ACTIVE_PROFILE["quantization"],
    }
    if any(shown.get(key) != value for key, value in expected.items()):
        raise ProbeError("/api/show identity differs from the active profile")
    if shown.get("maximum_context_tokens") != ACTIVE_PROFILE["native_context_tokens"]:
        raise ProbeError("/api/show native context differs from the active profile")


def parse_running_models(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_models = data.get("models")
    if not isinstance(raw_models, list):
        raise ProbeError("/api/ps omitted its models array")
    models: list[dict[str, Any]] = []
    for item in raw_models:
        if not isinstance(item, dict):
            raise ProbeError("/api/ps returned a malformed model")
        size = int(item.get("size", 0))
        size_vram = int(item.get("size_vram", 0))
        models.append(
            {
                "name": str(item.get("name") or item.get("model") or ""),
                "digest": str(item.get("digest", "")),
                "size_bytes": size,
                "size_vram_bytes": size_vram,
                "size_cpu_bytes": max(0, size - size_vram),
                "context_length": int(item.get("context_length", 0)),
                "gpu_percent": round(100 * size_vram / size, 2) if size else None,
                "cpu_percent": round(100 * max(0, size - size_vram) / size, 2) if size else None,
            }
        )
    return models


def require_no_loaded_model(data: dict[str, Any]) -> None:
    if parse_running_models(data):
        raise ProbeError("a model is already loaded; ownership is ambiguous")


def require_context(running: list[dict[str, Any]]) -> dict[str, Any]:
    if len(running) != 1:
        raise ProbeError("the active model must be the only loaded model")
    matches = [item for item in running if item["name"] == MODEL]
    if len(matches) != 1:
        raise ProbeError("the exact model is not uniquely loaded")
    if matches[0]["context_length"] != CONTEXT_TOKENS:
        raise ProbeError(
            f"loaded context is {matches[0]['context_length']}, required {CONTEXT_TOKENS}"
        )
    return matches[0]


def parse_metrics(data: dict[str, Any], wall_seconds: float) -> dict[str, Any]:
    integer_fields = (
        "total_duration",
        "load_duration",
        "prompt_eval_count",
        "prompt_eval_duration",
        "eval_count",
        "eval_duration",
    )
    parsed: dict[str, Any] = {"wall_seconds": wall_seconds}
    for field in integer_fields:
        value = data.get(field)
        parsed[field] = int(value) if value is not None else None
    count = parsed["eval_count"]
    duration = parsed["eval_duration"]
    parsed["tokens_per_second"] = (
        count / (duration / 1_000_000_000) if count is not None and duration else None
    )
    parsed["done"] = bool(data.get("done"))
    parsed["done_reason"] = data.get("done_reason")
    return parsed


def guard_ram(snapshot: dict[str, Any]) -> None:
    available = int(snapshot["ram"]["available_bytes"])
    if available < MIN_AVAILABLE_RAM:
        raise ProbeError("available RAM fell below the fixed 4 GiB inference guard")


def _server_environment(root: Path) -> dict[str, str]:
    allowed_names = (
        "PATH",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATHEXT",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "HOMEDRIVE",
        "HOMEPATH",
        "APPDATA",
        "LOCALAPPDATA",
    )
    env = {name: os.environ[name] for name in allowed_names if name in os.environ}
    env.update(
        {
            "OLLAMA_HOST": f"{HOST}:{PORT}",
            "OLLAMA_NO_CLOUD": "1",
            "OLLAMA_CONTEXT_LENGTH": str(CONTEXT_TOKENS),
            "OLLAMA_KEEP_ALIVE": KEEP_ALIVE,
            "OLLAMA_MAX_LOADED_MODELS": "1",
            "OLLAMA_NUM_PARALLEL": str(NUM_PARALLEL),
            "OLLAMA_NOPRUNE": "1",
            "OLLAMA_MODELS": str(root),
            "NO_PROXY": "127.0.0.1,localhost",
        }
    )
    if GPU_OVERHEAD_BYTES is not None:
        env["OLLAMA_GPU_OVERHEAD"] = str(GPU_OVERHEAD_BYTES)
    return env


class ServerSession:
    def __init__(self, executable: str, root: Path, temporary: Path) -> None:
        self.executable = executable
        self.root = root
        self.temporary = temporary
        self.process: subprocess.Popen[bytes] | None = None
        self.owned_pids: set[int] = set()
        self.stdout_handle: Any = None
        self.stderr_handle: Any = None
        self.server_starts = 0
        self.environment = _server_environment(root)

    def start(self) -> None:
        if _loopback_responds() or not _port_is_free() or ollama_processes():
            raise ProbeError("pre-existing Ollama server, process, or occupied port detected")
        self.stdout_handle = (self.temporary / "ollama.stdout.log").open("wb")
        self.stderr_handle = (self.temporary / "ollama.stderr.log").open("wb")
        flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        self.process = subprocess.Popen(
            [self.executable, "serve"],
            stdin=subprocess.DEVNULL,
            stdout=self.stdout_handle,
            stderr=self.stderr_handle,
            env=self.environment,
            creationflags=flags,
        )
        self.server_starts += 1
        self.owned_pids.add(self.process.pid)
        deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise ProbeError("owned Ollama server exited during startup")
            self.refresh_owned_children()
            try:
                version = _api_request("/api/version", timeout=2)
            except ProbeError:
                time.sleep(0.2)
                continue
            if version.get("version") != EXPECTED_OLLAMA_VERSION:
                raise ProbeError("owned server version differs from Ollama 0.20.2")
            require_owned_loopback_listener(listener_records(), self.owned_pids)
            return
        raise ProbeError("owned Ollama server did not become ready before timeout")

    def refresh_owned_children(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.owned_pids.update(descendants(self.process.pid))

    def cleanup(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "unload_requested": False,
            "no_models_loaded": False,
            "server_stopped": False,
            "port_released": False,
            "owned_processes_gone": False,
            "remaining_owned_pids": [],
        }
        try:
            if self.process is not None and self.process.poll() is None and _loopback_responds():
                self.refresh_owned_children()
                try:
                    _api_request(
                        "/api/chat",
                        {"model": MODEL, "messages": [], "keep_alive": 0, "stream": False},
                        timeout=60,
                    )
                    result["unload_requested"] = True
                    deadline = time.monotonic() + 60
                    while time.monotonic() < deadline:
                        if not parse_running_models(_api_request("/api/ps", timeout=5)):
                            result["no_models_loaded"] = True
                            break
                        time.sleep(0.25)
                except ProbeError as exc:
                    result["unload_error"] = str(exc)
            elif not _loopback_responds():
                result["no_models_loaded"] = True
            if self.process is not None and self.process.poll() is None:
                self.refresh_owned_children()
                self.process.terminate()
                try:
                    self.process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    terminate_owned_pid(self.process.pid, self.owned_pids)
                    self.process.wait(timeout=10)
            result["server_stopped"] = self.process is None or self.process.poll() is not None
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                remaining = [pid for pid in self.owned_pids if _pid_exists(pid)]
                if not remaining:
                    break
                time.sleep(0.25)
            remaining = [pid for pid in self.owned_pids if _pid_exists(pid)]
            for pid in remaining:
                terminate_owned_pid(pid, self.owned_pids)
            remaining = [pid for pid in self.owned_pids if _pid_exists(pid)]
            result["remaining_owned_pids"] = remaining
            result["owned_processes_gone"] = not remaining
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and not _port_is_free():
                time.sleep(0.2)
            result["port_released"] = _port_is_free()
        finally:
            if self.stdout_handle is not None:
                self.stdout_handle.close()
            if self.stderr_handle is not None:
                self.stderr_handle.close()
        result["success"] = all(
            result[key]
            for key in (
                "no_models_loaded",
                "server_stopped",
                "port_released",
                "owned_processes_gone",
            )
        )
        return result


def execute_with_cleanup(session: Any, operation: Callable[[], Any]) -> tuple[Any, dict[str, Any]]:
    value: Any = None
    failure: BaseException | None = None
    try:
        session.start()
        value = operation()
    except BaseException as exc:
        failure = exc
    cleanup = session.cleanup()
    if failure is not None:
        raise failure
    return value, cleanup


def _plan() -> dict[str, Any]:
    return {
        "mode": "plan",
        "processes_started": 0,
        "model_loads": 0,
        "inference_calls": 0,
        "protocol": [
            "refuse any pre-existing Ollama process, listener, or loaded model",
            "validate the fixed local manifest, expected digest, and every required blob",
            "start Ollama 0.20.2 on 127.0.0.1:11434 with cloud disabled",
            "inspect /api/show and require an announced context of at least 16384",
            f"preload {MODEL} without a message at exactly num_ctx={CONTEXT_TOKENS}",
            "require /api/ps to report exactly context_length=16384 and at least 4 GiB RAM free",
            "make one non-streaming /api/chat call with think=false and num_predict=16",
            "unload explicitly, stop only owned processes, release the port, and delete temporary logs",
        ],
        "fixed_budget": {
            "server_starts": 1,
            "model_loads": 1,
            "inference_calls": 1,
            "inference_retries": 0,
            "context_tokens": CONTEXT_TOKENS,
            "maximum_output_tokens": MAX_OUTPUT_TOKENS,
            "minimum_available_ram_bytes": MIN_AVAILABLE_RAM,
        },
        "model": MODEL,
        "profile": ACTIVE_PROFILE_ID,
        "model_digest": EXPECTED_DIGEST,
        "endpoint": BASE_URL,
        "allocation_policy": allocation_policy(),
    }


def _run() -> dict[str, Any]:
    executable, _version_output = _preflight_cli()
    if _loopback_responds() or not _port_is_free() or ollama_processes():
        raise ProbeError("pre-existing Ollama server, process, or occupied port detected")
    local_identity = validate_local_model()
    root = model_root()
    store_before = all_profile_store_snapshot(root)
    before = resource_snapshot()
    guard_ram(before)
    budget = InferenceBudget()
    summary: dict[str, Any] = {
        "mode": "run",
        "profile": ACTIVE_PROFILE_ID,
        "ollama_version": EXPECTED_OLLAMA_VERSION,
        "endpoint": BASE_URL,
        "model_identity": local_identity,
        "context_requested": CONTEXT_TOKENS,
        "maximum_output_tokens": MAX_OUTPUT_TOKENS,
        "server_starts": 0,
        "model_loads": 0,
        "inference_calls": 0,
        "inference_retries": 0,
        "resources_before_load": before,
        "allocation_policy": allocation_policy(),
        "status": "BLOCKED",
    }
    cleanup: dict[str, Any] = {}
    temp_cleaned = False
    failure: BaseException | None = None
    with tempfile.TemporaryDirectory(prefix="egx-ollama-probe-") as temporary_name:
        temporary = Path(temporary_name)
        session = ServerSession(executable, root, temporary)
        try:
            session.start()
            summary["server_starts"] = session.server_starts
            require_no_loaded_model(_api_request("/api/ps"))
            shown = parse_show(_api_request("/api/show", {"model": MODEL}, timeout=30))
            summary["api_identity"] = shown
            validate_show_for_active_profile(shown)
            if shown["maximum_context_tokens"] is None or shown["maximum_context_tokens"] < CONTEXT_TOKENS:
                raise ProbeError("model metadata does not announce support for 16384 tokens")
            load_started = time.monotonic()
            load_response = _api_request(
                "/api/chat",
                {
                    "model": MODEL,
                    "messages": [],
                    "stream": False,
                    "keep_alive": KEEP_ALIVE,
                    "options": {"num_ctx": CONTEXT_TOKENS},
                },
                timeout=MODEL_LOAD_TIMEOUT_SECONDS,
            )
            summary["model_loads"] = 1
            summary["load_without_generation"] = {
                "supported": True,
                "wall_seconds": time.monotonic() - load_started,
                "load_duration": load_response.get("load_duration"),
                "eval_count": load_response.get("eval_count"),
            }
            session.refresh_owned_children()
            running = parse_running_models(_api_request("/api/ps"))
            loaded = require_context(running)
            summary["loaded_model"] = loaded
            runtime_digest = loaded["digest"]
            manifest_digest = local_identity["manifest_digest"].removeprefix("sha256:")
            if runtime_digest and runtime_digest != manifest_digest:
                raise ProbeError("/api/ps digest differs from the fixed local manifest digest")
            during_load = resource_snapshot()
            summary["resources_after_load"] = during_load
            guard_ram(during_load)
            budget.reserve()
            inference_started = time.monotonic()
            response = _api_request(
                "/api/chat",
                {
                    "model": MODEL,
                    "messages": [{"role": "user", "content": PROMPT}],
                    "stream": False,
                    "think": False,
                    "keep_alive": KEEP_ALIVE,
                    "options": {
                        "num_ctx": CONTEXT_TOKENS,
                        "temperature": 0,
                        "num_predict": MAX_OUTPUT_TOKENS,
                    },
                },
                timeout=MODEL_LOAD_TIMEOUT_SECONDS,
            )
            wall = time.monotonic() - inference_started
            summary["inference_calls"] = budget.calls
            message = response.get("message")
            if not isinstance(message, dict):
                raise ProbeError("chat response omitted its message object")
            observed = str(message.get("content", ""))
            thinking = str(message.get("thinking", ""))
            summary["smoke"] = {
                "expected_output": EXPECTED_OUTPUT,
                "observed_output": observed,
                "thinking_exposed": bool(thinking),
                "metrics": parse_metrics(response, wall),
            }
            running_after = parse_running_models(_api_request("/api/ps"))
            summary["loaded_model_after_inference"] = require_context(running_after)
            summary["resources_after_inference"] = resource_snapshot()
            summary["status"] = (
                "PASS"
                if observed == EXPECTED_OUTPUT and not thinking and response.get("done") is True
                else "FAIL"
            )
        except BaseException as exc:
            failure = exc
            summary["error"] = str(exc)
            if budget.calls:
                summary["inference_calls"] = budget.calls
        finally:
            cleanup = session.cleanup()
            summary["server_starts"] = session.server_starts
            summary["cleanup"] = cleanup
            summary["resources_after_cleanup"] = resource_snapshot()
    temp_cleaned = not Path(temporary_name).exists()
    summary["cleanup"]["temporary_logs_removed"] = temp_cleaned
    summary["cleanup"]["model_store_unchanged"] = store_before == all_profile_store_snapshot(root)
    summary["cleanup"]["success"] = bool(summary["cleanup"].get("success") and temp_cleaned)
    summary["cleanup"]["success"] = bool(
        summary["cleanup"]["success"] and summary["cleanup"]["model_store_unchanged"]
    )
    if not summary["cleanup"]["success"]:
        summary["status"] = "FAIL"
    elif failure is not None:
        summary["status"] = "BLOCKED" if budget.calls == 0 else "FAIL"
    return sanitize_summary(summary)


def sanitize_summary(value: Any) -> Any:
    secret_markers = ("password", "api_key", "authorization", "credential", "secret")
    home = str(Path.home())
    if isinstance(value, dict):
        return {
            str(key): sanitize_summary(item)
            for key, item in value.items()
            if not any(marker in str(key).lower() for marker in secret_markers)
        }
    if isinstance(value, list):
        return [sanitize_summary(item) for item in value]
    if isinstance(value, str):
        return value.replace(home, "<HOME>") if home else value
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate fixed local Ollama Qwen runtime.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="print the fixed zero-process protocol")
    plan.add_argument("--profile", choices=sorted(REQUIRED_PROFILE_IDS), default=DEFAULT_PROFILE_ID)
    run = subparsers.add_parser("run", help="perform the authorized fixed runtime probe")
    run.add_argument("--profile", choices=sorted(REQUIRED_PROFILE_IDS), default=DEFAULT_PROFILE_ID)
    run.add_argument("--acknowledge-model-load", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "run" and not args.acknowledge_model_load:
        print("REFUSED: run requires --acknowledge-model-load", file=sys.stderr)
        return 2
    try:
        activate_profile(args.profile)
        summary = _plan() if args.command == "plan" else _run()
    except (ProbeError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.command == "run" and summary["status"] != "PASS":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
