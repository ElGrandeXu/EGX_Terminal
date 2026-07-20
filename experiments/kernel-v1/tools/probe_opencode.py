#!/usr/bin/env python3
"""Diagnose OpenCode locally or smoke-test one isolated call against Ollama."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Callable
from urllib.parse import urlparse


EXPECTED_PYTHON_VERSION = (3, 11, 9)
EXPECTED_OPENCODE_VERSION = "1.17.9"
EXPECTED_OPENCODE_BINARY_SHA256 = (
    "65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6"
)
EXPECTED_OPENCODE_BINARY_BYTES = 165_154_696
EXPECTED_OLLAMA_VERSION = "0.20.2"
PROVIDER = "local-ollama"
HOST = "127.0.0.1"
PORT = 11434
BASE_URL = f"http://{HOST}:{PORT}"
OPENAI_BASE_URL = BASE_URL + "/v1"
MAX_OUTPUT_TOKENS = 64
KEEP_ALIVE = "2m"
MODEL_LOAD_TIMEOUT_SECONDS = 600
OPENCODE_TIMEOUT_SECONDS = 600
MAX_OPENCODE_INFERENCE_PROCESSES = 1
MAX_MODEL_REQUESTS = 1
MAX_RETRIES = 0
MOCK_PROVIDER = "mock-openai"
MOCK_MODEL = "egx-mock"
MOCK_OUTPUT = "MOCK_OK"
MOCK_CONTEXT_TOKENS = 4_096
MOCK_MAX_OUTPUT_TOKENS = 16
MOCK_TIMEOUT_SECONDS = 120
MAX_REQUEST_BODY_BYTES = 8 * 1024 * 1024
MISSION11_BASELINE_VRAM_MIB = 1_076
MISSION11_MODEL_DELTA_VRAM_MIB = 21_748
MAX_BASELINE_DRIFT_MIB = 256
MIN_PROJECTED_VRAM_MIB = 512
MIN_OPENCODE_AVAILABLE_RAM_BYTES = 16 * 1024**3

PROMPT = (
    "Do not use tools or read files. Based only on project instructions already "
    "supplied before this message, output only their first eight words."
)
EXPECTED_OUTPUT = "Understand the requested outcome, constraints, relevant work, and"

SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parent.parent
REPOSITORY_ROOT = SCRIPT_PATH.parents[3]
MANIFEST_PATH = EXPERIMENT_ROOT / "manifest.json"

REQUIRED_ISOLATION_KEYS = (
    "HOME",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_STATE_HOME",
    "XDG_CACHE_HOME",
    "TMP",
    "TEMP",
    "NPM_CONFIG_CACHE",
    "BUN_INSTALL_CACHE_DIR",
    "OPENCODE_CONFIG_DIR",
    "OPENCODE_DB",
)
FORBIDDEN_INHERITED_MARKERS = (
    "API_KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "CREDENTIAL",
    "OTEL_EXPORTER",
)
TOOL_MARKERS = ("tool", "bash", "edit", "write", "read", "glob", "grep", "task")
PERMISSION_MARKERS = ("permission", "approval", "ask")


class ProbeError(Exception):
    """A fixed safety, isolation, identity, or runtime condition failed."""


class OpenCodeJSONLError(ProbeError):
    """OpenCode stdout was not strict JSONL; bounded diagnostics remain available."""

    def __init__(self, message: str, diagnostic: dict[str, Any], parsed: dict[str, Any]) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic
        self.parsed = parsed


class InferenceBudget:
    """A one-process, one-request budget without a retry path."""

    def __init__(self) -> None:
        self.processes = 0
        self.requests = 0
        self.requests_recorded = False
        self.retries = 0

    def reserve_process(self) -> None:
        if self.processes >= MAX_OPENCODE_INFERENCE_PROCESSES:
            raise ProbeError("the single OpenCode inference-process budget is exhausted")
        self.processes += 1

    def record_requests(self, count: int) -> None:
        if self.requests_recorded:
            raise ProbeError("model requests were already recorded")
        self.requests_recorded = True
        self.requests = count
        if count != MAX_MODEL_REQUESTS:
            raise ProbeError(f"observed {count} OpenCode model requests; exactly one is required")


def _load_module(name: str) -> Any:
    path = SCRIPT_PATH.with_name(name)
    spec = importlib.util.spec_from_file_location(f"egx_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ProbeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC = _load_module("sync_adapters.py")
OLLAMA = _load_module("probe_ollama.py")

DEFAULT_PROFILE_ID = OLLAMA.DEFAULT_PROFILE_ID
REQUIRED_PROFILE_IDS = OLLAMA.REQUIRED_PROFILE_IDS
ACTIVE_PROFILE_ID = ""
ACTIVE_PROFILE: dict[str, Any] = {}
MODEL = ""
EXPECTED_DIGEST = ""
CONTEXT_TOKENS = 0


def activate_profile(profile_id: str = DEFAULT_PROFILE_ID) -> dict[str, Any]:
    global ACTIVE_PROFILE_ID, ACTIVE_PROFILE, MODEL, EXPECTED_DIGEST, CONTEXT_TOKENS
    profile = OLLAMA.activate_profile(profile_id)
    ACTIVE_PROFILE_ID = profile_id
    ACTIVE_PROFILE = dict(profile)
    MODEL = str(profile["ollama_model"])
    EXPECTED_DIGEST = str(profile["digest"])
    CONTEXT_TOKENS = int(profile.get("context_length", profile["test_context_tokens"]))
    return ACTIVE_PROFILE


activate_profile()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_endpoint(url: str) -> str:
    if url != OPENAI_BASE_URL:
        raise ProbeError("only the fixed loopback OpenAI-compatible Ollama endpoint is permitted")
    parsed = __import__("urllib.parse", fromlist=["urlparse"]).urlparse(url)
    try:
        address = ipaddress.ip_address(parsed.hostname or "")
    except ValueError as exc:
        raise ProbeError("provider endpoint does not resolve literally to loopback") from exc
    if parsed.scheme != "http" or not address.is_loopback or parsed.port != PORT:
        raise ProbeError("provider endpoint must be HTTP on fixed loopback port 11434")
    return url


def validate_mock_endpoint(url: str) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != HOST
        or parsed.port is None
        or parsed.port <= 0
        or parsed.port > 65_535
        or parsed.path.rstrip("/") != "/v1"
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise ProbeError("mock provider endpoint must be HTTP on literal 127.0.0.1 with a dynamic port and /v1")
    return url


def validate_provider_name(provider: str) -> str:
    if provider != PROVIDER:
        raise ProbeError("only the fixed local Ollama provider is permitted")
    return provider


def _opencode_binary() -> Path:
    launcher = shutil.which("opencode")
    if launcher is None:
        raise ProbeError("OpenCode is unavailable on PATH")
    launcher_path = Path(launcher).resolve()
    candidates = [launcher_path]
    if launcher_path.suffix.lower() in {".cmd", ".ps1"}:
        candidates.insert(
            0,
            launcher_path.parent / "node_modules" / "opencode-ai" / "bin" / "opencode.exe",
        )
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() == ".exe":
            return candidate
    raise ProbeError("the direct OpenCode executable could not be resolved")


def validate_opencode_install(binary: Path | None = None) -> dict[str, Any]:
    binary = binary or _opencode_binary()
    if binary.stat().st_size != EXPECTED_OPENCODE_BINARY_BYTES:
        raise ProbeError("OpenCode binary size differs from the locked 1.17.9 build")
    if sha256_file(binary) != EXPECTED_OPENCODE_BINARY_SHA256:
        raise ProbeError("OpenCode binary hash differs from the locked 1.17.9 build")
    package = binary.parents[1] / "package.json"
    try:
        metadata = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeError("OpenCode package metadata is unreadable") from exc
    if metadata.get("version") != EXPECTED_OPENCODE_VERSION:
        raise ProbeError("OpenCode package version differs from 1.17.9")
    return {
        "version": EXPECTED_OPENCODE_VERSION,
        "binary_sha256": EXPECTED_OPENCODE_BINARY_SHA256,
        "binary_bytes": EXPECTED_OPENCODE_BINARY_BYTES,
    }


def opencode_processes(rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    rows = rows if rows is not None else OLLAMA._process_rows()
    result = []
    for row in rows:
        name = str(row.get("Name", "")).lower()
        if "opencode" in name:
            result.append(
                {
                    "pid": int(row.get("ProcessId", 0)),
                    "parent_pid": int(row.get("ParentProcessId", 0)),
                    "name": name,
                }
            )
    return result


def guard_initial_resources(snapshot: dict[str, Any]) -> dict[str, int]:
    OLLAMA.guard_ram(snapshot)
    available_ram = int(snapshot["ram"]["available_bytes"])
    minimum_ram = (
        MIN_OPENCODE_AVAILABLE_RAM_BYTES
        if OLLAMA.allocation_policy() is not None
        else OLLAMA.MIN_AVAILABLE_RAM
    )
    if available_ram < minimum_ram:
        raise ProbeError("available RAM is below the active OpenCode profile gate")
    gpu = snapshot["gpu"]
    used = int(gpu["used_mib"])
    free = int(gpu["available_mib"])
    if ACTIVE_PROFILE_ID == "qwen3.6-27b-q4km":
        return {
            "baseline_delta_mib": used - MISSION11_BASELINE_VRAM_MIB,
            "available_before_load_mib": free,
        }
    if used > MISSION11_BASELINE_VRAM_MIB + MAX_BASELINE_DRIFT_MIB:
        raise ProbeError("initial VRAM use is materially above the Mission 11 baseline")
    projected = free - MISSION11_MODEL_DELTA_VRAM_MIB
    if projected < MIN_PROJECTED_VRAM_MIB:
        raise ProbeError("projected residual VRAM is below the fixed 512 MiB guard")
    return {"baseline_delta_mib": used - MISSION11_BASELINE_VRAM_MIB, "projected_free_mib": projected}


def loaded_resource_gate(snapshot: dict[str, Any]) -> dict[str, Any]:
    OLLAMA.guard_ram(snapshot)
    free = int(snapshot["gpu"]["available_mib"])
    policy = OLLAMA.allocation_policy()
    minimum_vram = int(policy["minimum_free_vram_mib"]) if policy is not None else 0
    minimum_ram = MIN_OPENCODE_AVAILABLE_RAM_BYTES if policy is not None else OLLAMA.MIN_AVAILABLE_RAM
    available_ram = int(snapshot["ram"]["available_bytes"])
    return {
        "requested_gpu_overhead_bytes": policy["gpu_overhead_bytes"] if policy is not None else None,
        "observed_available_vram_mib": free,
        "minimum_free_vram_mib": minimum_vram,
        "vram_margin_above_minimum_mib": free - minimum_vram,
        "observed_available_ram_bytes": available_ram,
        "minimum_available_ram_bytes": minimum_ram,
        "passed": free >= minimum_vram and available_ram >= minimum_ram,
    }


def guard_loaded_resources(snapshot: dict[str, Any]) -> dict[str, Any]:
    gate = loaded_resource_gate(snapshot)
    if gate["observed_available_vram_mib"] < gate["minimum_free_vram_mib"]:
        raise ProbeError("observed loaded VRAM is below the active profile minimum")
    if gate["observed_available_ram_bytes"] < gate["minimum_available_ram_bytes"]:
        raise ProbeError("observed loaded RAM is below the active profile minimum")
    return gate


def active_cuda_compute_processes() -> list[dict[str, Any]]:
    executable = shutil.which("nvidia-smi")
    if executable is None:
        raise ProbeError("nvidia-smi is unavailable")
    completed = OLLAMA._run_text([executable, "pmon", "-c", "1", "-s", "u"], timeout=20)
    if completed.returncode != 0:
        raise ProbeError("nvidia-smi process-utilization query failed")
    active = []
    for line in completed.stdout.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 5 or not fields[1].isdigit():
            continue
        percentages = []
        for value in fields[3:5]:
            percentages.append(int(value) if value.isdigit() else 0)
        if any(value > 0 for value in percentages):
            active.append({"pid": int(fields[1]), "type": fields[2], "active": True})
    return active


def build_config(endpoint: str = OPENAI_BASE_URL, provider: str = PROVIDER) -> dict[str, Any]:
    validate_endpoint(endpoint)
    validate_provider_name(provider)
    model_name = f"{provider}/{MODEL}"
    return {
        "autoupdate": False,
        "share": "disabled",
        "snapshot": False,
        "compaction": {"auto": False, "prune": False},
        "permission": {"*": "deny"},
        "mcp": {},
        "plugin": [],
        "instructions": [],
        "enabled_providers": [provider],
        "model": model_name,
        "small_model": model_name,
        "provider": {
            provider: {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Ollama loopback",
                "options": {"baseURL": endpoint},
                "models": {
                    MODEL: {
                        "name": f"{MODEL} Q4_K_M local",
                        "limit": {"context": CONTEXT_TOKENS, "output": MAX_OUTPUT_TOKENS},
                        "options": {"temperature": 0, "reasoningEffort": "none"},
                    }
                },
            }
        },
    }


def build_mock_config(endpoint: str) -> dict[str, Any]:
    validate_mock_endpoint(endpoint)
    model_name = f"{MOCK_PROVIDER}/{MOCK_MODEL}"
    return {
        "autoupdate": False,
        "share": "disabled",
        "snapshot": False,
        "compaction": {"auto": False, "prune": False},
        "permission": {"*": "deny"},
        "mcp": {},
        "plugin": [],
        "instructions": [],
        "enabled_providers": [MOCK_PROVIDER],
        "model": model_name,
        "small_model": model_name,
        "provider": {
            MOCK_PROVIDER: {
                "npm": "@ai-sdk/openai-compatible",
                "name": "EGX loopback mock",
                "options": {"baseURL": endpoint},
                "models": {
                    MOCK_MODEL: {
                        "name": "EGX deterministic mock",
                        "limit": {
                            "context": MOCK_CONTEXT_TOKENS,
                            "output": MOCK_MAX_OUTPUT_TOKENS,
                        },
                        "options": {"temperature": 0, "reasoningEffort": "none"},
                    }
                },
            }
        },
    }


def validate_config(config: dict[str, Any]) -> None:
    expected = build_config()
    if config != expected:
        raise ProbeError("OpenCode configuration diverges from the fixed isolated configuration")
    if config["permission"] != {"*": "deny"}:
        raise ProbeError("all tools must be denied by default")
    if config["enabled_providers"] != [PROVIDER] or set(config["provider"]) != {PROVIDER}:
        raise ProbeError("provider allowlist is not exclusive")


def validate_mock_config(config: dict[str, Any], endpoint: str) -> None:
    expected = build_mock_config(endpoint)
    if config != expected:
        raise ProbeError("OpenCode mock configuration diverges from the fixed isolated configuration")
    if config["permission"] != {"*": "deny"}:
        raise ProbeError("all mock tools must be denied by default")
    if config["enabled_providers"] != [MOCK_PROVIDER] or set(config["provider"]) != {MOCK_PROVIDER}:
        raise ProbeError("mock provider allowlist is not exclusive")


def isolated_environment(
    root: Path,
    config: dict[str, Any] | None = None,
    *,
    mock_endpoint: str | None = None,
) -> dict[str, str]:
    config = config or build_config()
    if mock_endpoint is None:
        validate_config(config)
    else:
        validate_mock_config(config, mock_endpoint)
    dirs = {
        "HOME": root / "home",
        "USERPROFILE": root / "home",
        "APPDATA": root / "appdata",
        "LOCALAPPDATA": root / "localappdata",
        "XDG_CONFIG_HOME": root / "xdg-config",
        "XDG_DATA_HOME": root / "xdg-data",
        "XDG_STATE_HOME": root / "xdg-state",
        "XDG_CACHE_HOME": root / "xdg-cache",
        "TMP": root / "temp",
        "TEMP": root / "temp",
        "NPM_CONFIG_CACHE": root / "npm-cache",
        "BUN_INSTALL_CACHE_DIR": root / "bun-cache",
        "OPENCODE_CONFIG_DIR": root / "config",
    }
    for path in set(dirs.values()):
        path.mkdir(parents=True, exist_ok=True)
    allowed_parent = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT")
    env = {name: os.environ[name] for name in allowed_parent if name in os.environ}
    env.update({name: str(path) for name, path in dirs.items()})
    env.update(
        {
            "OPENCODE_DB": ":memory:",
            "OPENCODE_CONFIG_CONTENT": json.dumps(config, separators=(",", ":")),
            "OPENCODE_DISABLE_DEFAULT_PLUGINS": "1",
            "OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
            "OPENCODE_DISABLE_LSP_DOWNLOAD": "1",
            "OPENCODE_DISABLE_MODELS_FETCH": "1",
            "OPENCODE_DISABLE_AUTOUPDATE": "1",
            "OPENCODE_DISABLE_CLAUDE_CODE": "1",
            "OPENCODE_PERMISSION": '{"*":"deny"}',
            "NPM_CONFIG_OFFLINE": "true",
            "NPM_CONFIG_UPDATE_NOTIFIER": "false",
            "DO_NOT_TRACK": "1",
            "OTEL_SDK_DISABLED": "true",
            "HTTP_PROXY": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "ALL_PROXY": "http://127.0.0.1:9",
            "http_proxy": "http://127.0.0.1:9",
            "https_proxy": "http://127.0.0.1:9",
            "all_proxy": "http://127.0.0.1:9",
            "NO_PROXY": "localhost,127.0.0.1",
            "no_proxy": "localhost,127.0.0.1",
        }
    )
    return env


def validate_isolated_environment(env: dict[str, str], root: Path) -> None:
    resolved = root.resolve()
    for key in REQUIRED_ISOLATION_KEYS:
        if key not in env:
            raise ProbeError(f"isolated environment omits {key}")
        if key != "OPENCODE_DB":
            try:
                Path(env[key]).resolve().relative_to(resolved)
            except ValueError as exc:
                raise ProbeError(f"{key} escapes the disposable root") from exc
    if env["OPENCODE_DB"] != ":memory:":
        raise ProbeError("OpenCode database must be in memory")
    if env.get("NO_PROXY") != "localhost,127.0.0.1":
        raise ProbeError("NO_PROXY must be limited to literal loopback names")
    if any(any(marker in key.upper() for marker in FORBIDDEN_INHERITED_MARKERS) for key in env if key not in {"OTEL_SDK_DISABLED"}):
        raise ProbeError("a credential or telemetry variable survived environment filtering")


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        for key in ("text", "content"):
            value = item.get(key)
            if isinstance(value, str):
                parts.append(value)
                break
    return "".join(parts)


def inspect_chat_payload(payload: Any, kernel: str, prompt: str = PROMPT) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbeError("mock chat request body must be a JSON object")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise ProbeError("mock chat request must contain a messages array")

    roles: list[str] = []
    sizes: list[int] = []
    hashes: list[str] = []
    texts: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            raise ProbeError("mock chat message must be a JSON object")
        role = message.get("role")
        roles.append(role if isinstance(role, str) else "<missing>")
        text = _content_text(message.get("content"))
        texts.append(text)
        sizes.append(len(text))
        hashes.append(hashlib.sha256(text.encode("utf-8")).hexdigest())

    tools = payload.get("tools")
    if isinstance(tools, list):
        tool_count = len(tools)
    elif isinstance(tools, dict):
        tool_count = len(tools)
    else:
        tool_count = 0
    generation_keys = (
        "stream",
        "temperature",
        "max_tokens",
        "max_completion_tokens",
        "top_p",
        "seed",
        "stop",
        "stream_options",
        "reasoning_effort",
    )
    generation = {
        key: payload[key]
        for key in generation_keys
        if key in payload and isinstance(payload[key], (str, int, float, bool, list, dict, type(None)))
    }
    return {
        "model": payload.get("model") if isinstance(payload.get("model"), str) else None,
        "message_count": len(messages),
        "message_roles": roles,
        "content_characters": sizes,
        "content_sha256": hashes,
        "kernel_detection": "exact UTF-8-decoded KERNEL.md substring across message contents",
        "kernel_occurrences": sum(text.count(kernel) for text in texts),
        "kernel_present": any(kernel in text for text in texts),
        "claude_import_occurrences": sum(text.count(SYNC.CLAUDE_CONTENT.decode("utf-8")) for text in texts),
        "prompt_occurrences": sum(text.count(prompt) for text in texts),
        "prompt_present": any(prompt in text for text in texts),
        "tools_field_present": "tools" in payload,
        "tool_count": tool_count,
        "tool_choice_present": "tool_choice" in payload,
        "generation_options": generation,
        "raw_payload_retained": False,
    }


def mock_sse_body() -> bytes:
    chunks = [
        {
            "id": "chatcmpl-egx-mock",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": MOCK_MODEL,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": MOCK_OUTPUT},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "chatcmpl-egx-mock",
            "object": "chat.completion.chunk",
            "created": 0,
            "model": MOCK_MODEL,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
    ]
    lines = [f"data: {json.dumps(chunk, separators=(',', ':'))}\n\n" for chunk in chunks]
    lines.append("data: [DONE]\n\n")
    return "".join(lines).encode("utf-8")


def parse_sse_json(raw: bytes | str) -> list[dict[str, Any]]:
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    events: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ProbeError("mock SSE contains invalid JSON") from exc
        if not isinstance(event, dict):
            raise ProbeError("mock SSE event must be a JSON object")
        events.append(event)
    return events


class MockProviderState:
    def __init__(self, kernel: str) -> None:
        self.kernel = kernel
        self.lock = threading.Lock()
        self.requests: list[dict[str, Any]] = []
        self.generations: list[dict[str, Any]] = []

    def record(self, request: dict[str, Any], generation: dict[str, Any] | None = None) -> None:
        with self.lock:
            self.requests.append(request)
            if generation is not None:
                self.generations.append(generation)

    def summary(self) -> dict[str, Any]:
        with self.lock:
            return {
                "total_requests": len(self.requests),
                "generation_requests": len(self.generations),
                "requests": [dict(item) for item in self.requests],
                "generations": [dict(item) for item in self.generations],
                "raw_payload_retained": False,
            }


def _mock_handler(state: MockProviderState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _write(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def do_GET(self) -> None:
            route = urlparse(self.path).path
            state.record({"method": "GET", "route": route})
            if route != "/v1/models":
                self._write(404, "application/json", b'{"error":{"message":"not found"}}')
                return
            body = json.dumps(
                {
                    "object": "list",
                    "data": [{"id": MOCK_MODEL, "object": "model", "created": 0, "owned_by": "egx"}],
                },
                separators=(",", ":"),
            ).encode("utf-8")
            self._write(200, "application/json", body)

        def do_POST(self) -> None:
            route = urlparse(self.path).path
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = -1
            if length < 0 or length > MAX_REQUEST_BODY_BYTES:
                state.record({"method": "POST", "route": route, "accepted": False})
                self._write(413, "application/json", b'{"error":{"message":"request too large"}}')
                return
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
                inspection = inspect_chat_payload(payload, state.kernel)
            except (UnicodeDecodeError, json.JSONDecodeError, ProbeError):
                state.record({"method": "POST", "route": route, "accepted": False})
                self._write(400, "application/json", b'{"error":{"message":"invalid request"}}')
                return
            request = {"method": "POST", "route": route, "accepted": route == "/v1/chat/completions"}
            state.record(request, inspection if route == "/v1/chat/completions" else None)
            if route != "/v1/chat/completions":
                self._write(404, "application/json", b'{"error":{"message":"not found"}}')
                return
            self._write(200, "text/event-stream", mock_sse_body())

    return Handler


class MockProviderServer:
    def __init__(self, kernel: str) -> None:
        self.state = MockProviderState(kernel)
        self.server = ThreadingHTTPServer((HOST, 0), _mock_handler(self.state), bind_and_activate=False)
        self.server.daemon_threads = True
        self.server.server_bind()
        self.server.server_activate()
        address, port = self.server.server_address[:2]
        if address != HOST:
            self.server.server_close()
            raise ProbeError("mock provider did not bind to literal loopback")
        self.endpoint = validate_mock_endpoint(f"http://{HOST}:{port}/v1")
        self.thread = threading.Thread(target=self.server.serve_forever, name="egx-opencode-mock", daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=15)
        if self.thread.is_alive():
            raise ProbeError("mock provider thread did not stop")


def _sync_write(workspace: Path) -> None:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = SYNC.main(["write", "--target", str(workspace)])
    if code != SYNC.EXIT_OK:
        raise ProbeError("sync_adapters.py write failed for the disposable workspace")


def _sync_check(workspace: Path) -> None:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = SYNC.main(["check", "--target", str(workspace)])
    if code != SYNC.EXIT_OK:
        raise ProbeError("sync_adapters.py check failed for the disposable workspace")


def validate_workspace(workspace: Path) -> dict[str, Any]:
    _sync_check(workspace)
    source = SYNC._load_source()
    expected_files = {
        ".egx/doctrine-lock.json",
        "doctrine/KERNEL.md",
        "AGENTS.md",
        "CLAUDE.md",
    }
    actual_files = {
        path.relative_to(workspace).as_posix() for path in workspace.rglob("*") if path.is_file()
    }
    if actual_files != expected_files:
        raise ProbeError("disposable workspace contains an unmanaged or missing file")
    canonical = (workspace / "doctrine" / "KERNEL.md").read_bytes()
    agents = (workspace / "AGENTS.md").read_bytes()
    if canonical != source or agents != canonical:
        raise ProbeError("canonical, source, and AGENTS.md are not byte-identical")
    if (workspace / "CLAUDE.md").read_bytes() != SYNC.CLAUDE_CONTENT:
        raise ProbeError("CLAUDE.md differs from the fixed adapter")
    if (workspace / "opencode.json").exists():
        raise ProbeError("the generated workspace must not contain opencode.json")
    lock = json.loads((workspace / ".egx" / "doctrine-lock.json").read_text(encoding="utf-8"))
    return {
        "files": sorted(actual_files),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
        "agents_identical_to_canonical": agents == canonical,
        "claude_content": SYNC.CLAUDE_CONTENT.decode("utf-8"),
        "lock_schema_version": lock.get("schema_version"),
        "opencode_json_absent": True,
        "unmanaged_files_absent": True,
    }


def snapshot_tree(root: Path, exclude_git: bool = False) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    if not root.exists():
        return snapshot
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if exclude_git and ".git" in relative.parts:
            continue
        key = relative.as_posix()
        if path.is_symlink():
            snapshot[key] = ("symlink", os.readlink(path))
        elif path.is_file():
            snapshot[key] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_dir():
            snapshot[key] = ("dir", "")
    return snapshot


def list_temporary_files(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


UTF8_BOM = b"\xef\xbb\xbf"
ANSI_BYTES_RE = re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")
MAX_SANITIZED_LINE_CHARACTERS = 512


def _line_endings(raw: bytes) -> dict[str, int]:
    crlf = raw.count(b"\r\n")
    return {
        "crlf": crlf,
        "lf": raw.count(b"\n") - crlf,
        "cr": raw.count(b"\r") - crlf,
    }


def _split_line_bytes(line: bytes) -> tuple[bytes, str]:
    if line.endswith(b"\r\n"):
        return line[:-2], "CRLF"
    if line.endswith(b"\n"):
        return line[:-1], "LF"
    if line.endswith(b"\r"):
        return line[:-1], "CR"
    return line, "none"


def _stream_encoding(raw: bytes) -> str:
    try:
        raw.removeprefix(UTF8_BOM).decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return "invalid-utf-8"
    return "utf-8-bom" if raw.startswith(UTF8_BOM) else "utf-8"


def _parse_jsonl_line(content: bytes, *, first_line: bool) -> tuple[dict[str, Any] | None, list[str]]:
    normalizations: list[str] = []
    if first_line and content.startswith(UTF8_BOM):
        content = content[len(UTF8_BOM) :]
        normalizations.append("utf-8-bom")
    text = content.decode("utf-8", errors="strict")
    if not text.strip():
        return None, [*normalizations, "blank-line"]
    if ANSI_BYTES_RE.search(content):
        stripped = content
        while True:
            match = ANSI_BYTES_RE.match(stripped)
            if match is None:
                break
            stripped = stripped[match.end() :]
        while True:
            matches = list(ANSI_BYTES_RE.finditer(stripped))
            if not matches or matches[-1].end() != len(stripped):
                break
            stripped = stripped[: matches[-1].start()]
        if stripped != content and ANSI_BYTES_RE.search(stripped) is None:
            text = stripped.decode("utf-8", errors="strict")
            normalizations.append("ansi-wrapped-json")
    event = json.loads(text)
    if not isinstance(event, dict):
        raise TypeError("JSONL event is not an object")
    return event, normalizations


def _valid_json_lines_after(lines: list[bytes], invalid_index: int) -> int:
    valid = 0
    for index, line in enumerate(lines[invalid_index + 1 :], invalid_index + 1):
        content, _ = _split_line_bytes(line)
        try:
            event, _normalizations = _parse_jsonl_line(content, first_line=index == 0)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            continue
        if event is not None:
            valid += 1
    return valid


def _summarize_jsonl_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    text_parts: list[str] = []
    tool_events: list[str] = []
    permission_events: list[str] = []
    reasoning_visible = False
    providers: set[str] = set()
    models: set[str] = set()
    tokens: dict[str, int] | None = None
    finish_reasons: set[str] = set()

    def walk(value: Any) -> None:
        nonlocal reasoning_visible, tokens
        if isinstance(value, dict):
            kind = str(value.get("type", "")).lower()
            kind_words = set(re.findall(r"[a-z]+", kind))
            if kind_words.intersection(TOOL_MARKERS):
                tool_events.append(kind)
            if kind_words.intersection(PERMISSION_MARKERS):
                permission_events.append(kind)
            if any(word.startswith("reason") for word in kind_words) and isinstance(value.get("text"), str) and value["text"]:
                reasoning_visible = True
            for key, item in value.items():
                normalized = key.lower().replace("_", "")
                if normalized == "providerid" and isinstance(item, str):
                    providers.add(item)
                if normalized == "modelid" and isinstance(item, str):
                    models.add(item)
                if normalized == "tokens" and isinstance(item, dict):
                    parsed: dict[str, int] = {}
                    for token_key, token_value in item.items():
                        if isinstance(token_value, (int, float)):
                            parsed[str(token_key)] = int(token_value)
                        elif isinstance(token_value, dict):
                            for child_key, child_value in token_value.items():
                                if isinstance(child_value, (int, float)):
                                    parsed[f"{token_key}_{child_key}"] = int(child_value)
                    if parsed:
                        tokens = parsed
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for event in events:
        event_type = str(event.get("type", "")).lower()
        part = event.get("part")
        part_type = str(part.get("type", "")).lower() if isinstance(part, dict) else ""
        if part_type == "step-finish" and isinstance(part, dict):
            reason = part.get("reason", part.get("finishReason"))
            if isinstance(reason, str) and reason:
                finish_reasons.add(reason)
        if event_type == "text" and isinstance(part, dict) and part_type == "text":
            if isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        elif event_type in {"text", "message"} and isinstance(event.get("text"), str):
            text_parts.append(event["text"])
        walk(event)

    return {
        "event_count": len(events),
        "final_output": "".join(text_parts),
        "tool_call": bool(tool_events),
        "tool_event_types": sorted(set(tool_events)),
        "permission_request": bool(permission_events),
        "permission_event_types": sorted(set(permission_events)),
        "reasoning_visible": reasoning_visible,
        "providers": sorted(providers),
        "models": sorted(models),
        "tokens": tokens,
        "finish_reasons": sorted(finish_reasons),
    }


def _invalid_jsonl_diagnostic(
    raw: bytes,
    lines: list[bytes],
    index: int,
    byte_offset: int,
    content: bytes,
    ending: str,
    valid_before: int,
    exc: BaseException,
    *,
    channel: str,
) -> dict[str, Any]:
    replacement_used = isinstance(exc, UnicodeDecodeError)
    display = content.decode("utf-8", errors="replace")
    sanitized = sanitize_stderr(display) or ""
    sanitized = sanitized[:MAX_SANITIZED_LINE_CHARACTERS]
    ansi_count = len(ANSI_BYTES_RE.findall(content))
    column = exc.colno if isinstance(exc, json.JSONDecodeError) else None
    invalid_byte = exc.start if isinstance(exc, UnicodeDecodeError) else None
    return {
        "channel": channel,
        "stream_size_bytes": len(raw),
        "stream_bom_present": raw.startswith(UTF8_BOM),
        "detected_encoding": _stream_encoding(raw),
        "line_endings": _line_endings(raw),
        "line_number": index + 1,
        "byte_offset_zero_based": byte_offset,
        "line_size_bytes": len(content),
        "line_ending": ending,
        "first_bytes_hex": content[:32].hex(),
        "line_bom_present": content.startswith(UTF8_BOM),
        "ansi_present": bool(ansi_count),
        "ansi_sequence_count": ansi_count,
        "sanitized_text": sanitized,
        "invalid_character_replaced_in_sanitized_text": replacement_used,
        "invalid_utf8_byte_offset_in_line": invalid_byte,
        "json_error_column_one_based": column,
        "valid_json_lines_before": valid_before,
        "valid_json_lines_after": _valid_json_lines_after(lines, index),
        "raw_retained": False,
    }


def parse_jsonl(raw: bytes | str, *, channel: str = "stdout") -> dict[str, Any]:
    raw_bytes = raw.encode("utf-8") if isinstance(raw, str) else raw
    lines = raw_bytes.splitlines(keepends=True)
    events: list[dict[str, Any]] = []
    normalizations: list[str] = []
    byte_offset = 0
    for index, line in enumerate(lines):
        content, ending = _split_line_bytes(line)
        try:
            event, line_normalizations = _parse_jsonl_line(content, first_line=index == 0)
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            diagnostic = _invalid_jsonl_diagnostic(
                raw_bytes,
                lines,
                index,
                byte_offset,
                content,
                ending,
                len(events),
                exc,
                channel=channel,
            )
            message = f"invalid OpenCode JSONL on {channel} at line {index + 1}"
            raise OpenCodeJSONLError(message, diagnostic, _summarize_jsonl_events(events)) from exc
        normalizations.extend(line_normalizations)
        if event is not None:
            events.append(event)
        byte_offset += len(line)
    parsed = _summarize_jsonl_events(events)
    parsed["jsonl"] = {
        "channel": channel,
        "stream_size_bytes": len(raw_bytes),
        "detected_encoding": _stream_encoding(raw_bytes),
        "bom_present": raw_bytes.startswith(UTF8_BOM),
        "line_endings": _line_endings(raw_bytes),
        "ansi_sequence_count": len(ANSI_BYTES_RE.findall(raw_bytes)),
        "blank_line_count": normalizations.count("blank-line"),
        "benign_normalizations": sorted(set(normalizations) - {"blank-line"}),
        "raw_retained": False,
    }
    return parsed


def validate_parsed_events(
    parsed: dict[str, Any],
    provider: str = PROVIDER,
    model: str | None = None,
) -> None:
    model = model or MODEL
    if parsed["tool_call"]:
        raise ProbeError("OpenCode emitted a tool event")
    if parsed["permission_request"]:
        raise ProbeError("OpenCode emitted a permission event")
    if parsed["reasoning_visible"]:
        raise ProbeError("OpenCode exposed visible model reasoning")
    if parsed["providers"] and parsed["providers"] != [provider]:
        raise ProbeError("OpenCode events exposed an unexpected provider")
    if parsed["models"] and parsed["models"] != [model]:
        raise ProbeError("OpenCode events exposed an unexpected model")


def exact_output_matches(actual: str) -> bool:
    return actual == EXPECTED_OUTPUT


def sanitize_stderr(raw: str, roots: tuple[Path | str, ...] = ()) -> str | None:
    if not raw:
        return None
    result = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", raw).replace("\r\n", "\n").replace("\r", "\n")
    replacements = [
        *(str(root) for root in roots),
        str(REPOSITORY_ROOT),
        str(Path.home()),
    ]
    for value in sorted({item for item in replacements if item}, key=len, reverse=True):
        for variant in {value, value.replace("\\", "/")}:
            result = re.sub(re.escape(variant), "<REDACTED_PATH>", result, flags=re.IGNORECASE)
    username = Path.home().name
    if username:
        result = re.sub(re.escape(username), "<REDACTED_USER>", result, flags=re.IGNORECASE)
    result = re.sub(
        r"(?i)\b(api[_-]?key|token|secret|password|credential)(\s*[:=]\s*)([^\s,;]+)",
        r"\1\2<REDACTED>",
        result,
    )
    lines = [line.rstrip() for line in result.splitlines() if line.strip()]
    return "\n".join(lines[-20:])


def classify_stderr(raw: str) -> str | None:
    if not raw:
        return None
    lowered = raw.lower()
    for marker, category in (
        ("config", "configuration"),
        ("provider", "provider-initialization"),
        ("model", "model-resolution"),
        ("network", "network"),
        ("permission", "permission"),
    ):
        if marker in lowered:
            return category
    return "unclassified"


def count_model_requests(log_text: str) -> int:
    return len(re.findall(r"POST\s+\"?/v1/chat/completions(?:\?|\"|\s)", log_text))


def parse_ollama_request_latency(log_text: str) -> float | None:
    values: list[float] = []
    pattern = re.compile(r"\|\s*(?P<duration>[0-9.]+)(?P<unit>µs|ms|s)\s*\|[^\n]*POST\s+\"?/v1/chat/completions")
    factors = {"µs": 1e-6, "ms": 1e-3, "s": 1.0}
    for match in pattern.finditer(log_text):
        values.append(float(match.group("duration")) * factors[match.group("unit")])
    return values[-1] if values else None


def evaluate_connections(records: list[dict[str, Any]]) -> dict[str, Any]:
    non_loopback = []
    loopback = []
    for record in records:
        remote = str(record.get("remote_address", ""))
        try:
            is_loopback = ipaddress.ip_address(remote).is_loopback
        except ValueError:
            is_loopback = False
        normalized = {
            "family": str(record.get("family", "")),
            "remote": f"{remote}:{int(record.get('remote_port', 0))}" if is_loopback else "<NON_LOOPBACK_REDACTED>",
            "state": str(record.get("state", "")),
        }
        (loopback if is_loopback else non_loopback).append(normalized)
    return {
        "loopback": sorted({json.dumps(item, sort_keys=True) for item in loopback}),
        "non_loopback": sorted({json.dumps(item, sort_keys=True) for item in non_loopback}),
        "non_loopback_detected": bool(non_loopback),
    }


def _owned_tcp_connections(owned_pids: set[int]) -> list[dict[str, Any]]:
    if os.name != "nt" or not owned_pids:
        return []
    script = (
        "$ids=@(" + ",".join(str(pid) for pid in sorted(owned_pids)) + ");"
        "Get-NetTCPConnection -ErrorAction SilentlyContinue | Where-Object "
        "{$ids -contains $_.OwningProcess -and $_.RemotePort -gt 0} | "
        "Select-Object OwningProcess,RemoteAddress,RemotePort,State | ConvertTo-Json -Compress"
    )
    completed = OLLAMA._run_text(["powershell", "-NoProfile", "-Command", script], timeout=10)
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError("connection monitor returned invalid data") from exc
    rows = parsed if isinstance(parsed, list) else [parsed]
    return [
        {
            "pid": int(row.get("OwningProcess", 0)),
            "family": "IPv6" if ":" in str(row.get("RemoteAddress", "")) else "IPv4",
            "remote_address": str(row.get("RemoteAddress", "")),
            "remote_port": int(row.get("RemotePort", 0)),
            "state": str(row.get("State", "")),
        }
        for row in rows
        if isinstance(row, dict)
    ]


class OwnedServerConnectionMonitor:
    """Continuously sample connections owned by the local Ollama server tree."""

    def __init__(self, session: Any) -> None:
        self.session = session
        self.records: list[dict[str, Any]] = []
        self.failure: BaseException | None = None
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, name="egx-ollama-net-monitor", daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        try:
            last_refresh = 0.0
            while not self.stop_event.is_set():
                now = time.monotonic()
                if now - last_refresh >= 0.5:
                    self.session.refresh_owned_children()
                    last_refresh = now
                self.records.extend(_owned_tcp_connections(self.session.owned_pids))
                if evaluate_connections(self.records)["non_loopback_detected"]:
                    self.failure = ProbeError("a non-loopback Ollama connection was observed")
                    return
                self.stop_event.wait(0.25)
        except BaseException as exc:
            self.failure = exc

    def checkpoint(self) -> dict[str, Any]:
        if self.failure is not None:
            if isinstance(self.failure, ProbeError):
                raise self.failure
            raise ProbeError(f"Ollama connection monitor failed: {type(self.failure).__name__}")
        return evaluate_connections(self.records)

    def stop(self) -> dict[str, Any]:
        self.stop_event.set()
        self.thread.join(timeout=15)
        if self.thread.is_alive():
            raise ProbeError("Ollama connection monitor did not stop")
        return self.checkpoint()


class ConnectionMonitor:
    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self.process = process
        self.owned_pids = {process.pid}
        self.records: list[dict[str, Any]] = []
        self.failure: BaseException | None = None
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, name="egx-opencode-net-monitor", daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        try:
            last_refresh = 0.0
            while not self.stop_event.is_set() and self.process.poll() is None:
                now = time.monotonic()
                if now - last_refresh >= 0.5:
                    self.owned_pids.update(OLLAMA.descendants(self.process.pid))
                    last_refresh = now
                self.records.extend(_owned_tcp_connections(self.owned_pids))
                evaluated = evaluate_connections(self.records)
                if evaluated["non_loopback_detected"]:
                    self.process.terminate()
                    return
                self.stop_event.wait(0.1)
        except BaseException as exc:
            self.failure = exc
            if self.process.poll() is None:
                self.process.terminate()

    def stop(self) -> dict[str, Any]:
        self.stop_event.set()
        self.thread.join(timeout=15)
        if self.failure is not None:
            raise ProbeError(f"connection monitor failed: {type(self.failure).__name__}")
        return evaluate_connections(self.records)


def normalized_command(provider: str = PROVIDER, model: str | None = None) -> str:
    model = model or MODEL
    return (
        "opencode.exe run --pure --dir <temporary-workspace> "
        f"--model {provider}/{model} --format json --title <fixed-title> <closed-prompt>"
    )


def opencode_command(
    binary: Path,
    workspace: Path,
    provider: str = PROVIDER,
    model: str | None = None,
) -> list[str]:
    model = model or MODEL
    return [
        str(binary),
        "run",
        "--pure",
        "--dir",
        str(workspace),
        "--model",
        f"{provider}/{model}",
        "--format",
        "json",
        "--title",
        "EGX isolated probe",
        PROMPT,
    ]


def invoke_opencode(
    binary: Path,
    workspace: Path,
    env: dict[str, str],
    budget: InferenceBudget,
    provider: str = PROVIDER,
    model: str | None = None,
    timeout_seconds: int = OPENCODE_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    model = model or MODEL
    budget.reserve_process()
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        opencode_command(binary, workspace, provider, model),
        cwd=workspace,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=flags,
    )
    monitor = ConnectionMonitor(process)
    started = time.monotonic()
    monitor.start()
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        if process.poll() is None:
            process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            OLLAMA.terminate_owned_pid(process.pid, {process.pid})
            stdout, stderr = process.communicate(timeout=10)
    finally:
        connections = monitor.stop()
    remaining = [pid for pid in monitor.owned_pids if OLLAMA._pid_exists(pid)]
    for pid in remaining:
        terminate_owned_opencode_pid(pid, monitor.owned_pids)
    connections["owned_process_count_observed"] = len(monitor.owned_pids)
    connections["owned_processes_gone"] = not any(
        OLLAMA._pid_exists(pid) for pid in monitor.owned_pids
    )
    elapsed = time.monotonic() - started
    if timed_out:
        raise ProbeError("the single OpenCode call timed out; no retry is permitted")
    parse_error = None
    try:
        parsed = parse_jsonl(stdout, channel="stdout")
    except OpenCodeJSONLError as exc:
        parsed = exc.parsed
        parse_error = {
            "message": str(exc),
            "first_invalid_line": exc.diagnostic,
        }
    stderr_text = stderr.decode("utf-8", errors="replace")
    return {
        "exit_code": process.returncode,
        "wall_seconds": elapsed,
        "parsed": parsed,
        "parse_error": parse_error,
        "connections": connections,
        "stderr_present": bool(stderr),
        "stderr_category": classify_stderr(stderr_text),
        "stderr_sanitized": sanitize_stderr(stderr_text, (workspace.parent, workspace)),
        "stdout_capture": {
            "channel": "stdout",
            "size_bytes": len(stdout),
            "detected_encoding": _stream_encoding(stdout),
            "bom_present": stdout.startswith(UTF8_BOM),
            "line_endings": _line_endings(stdout),
            "ansi_sequence_count": len(ANSI_BYTES_RE.findall(stdout)),
            "raw_retained": False,
        },
        "stderr_capture": {
            "channel": "stderr",
            "size_bytes": len(stderr),
            "detected_encoding": _stream_encoding(stderr),
            "bom_present": stderr.startswith(UTF8_BOM),
            "line_endings": _line_endings(stderr),
            "ansi_sequence_count": len(ANSI_BYTES_RE.findall(stderr)),
            "sanitized_text": sanitize_stderr(stderr_text, (workspace.parent, workspace)),
            "invalid_character_replaced_in_sanitized_text": _stream_encoding(stderr) == "invalid-utf-8",
            "raw_retained": False,
        },
    }


def execute_with_cleanup(session: Any, operation: Callable[[], Any]) -> tuple[Any, dict[str, Any]]:
    return OLLAMA.execute_with_cleanup(session, operation)


def terminate_owned_opencode_pid(pid: int, owned_pids: set[int]) -> None:
    OLLAMA.terminate_owned_pid(pid, owned_pids)


def _read_ollama_log(session: Any) -> str:
    for handle in (session.stdout_handle, session.stderr_handle):
        if handle is not None:
            handle.flush()
    parts = []
    for name in ("ollama.stdout.log", "ollama.stderr.log"):
        path = session.temporary / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def parse_offload_layers(log_text: str) -> dict[str, Any]:
    matches = re.findall(r"offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU", log_text, re.I)
    if not matches:
        return {"exposed": False, "gpu_layers": None, "cpu_layers": None, "total_layers": None}
    gpu_layers, total_layers = (int(value) for value in matches[-1])
    if gpu_layers > total_layers:
        raise ProbeError("Ollama log exposed an invalid layer split")
    return {
        "exposed": True,
        "gpu_layers": gpu_layers,
        "cpu_layers": total_layers - gpu_layers,
        "total_layers": total_layers,
    }


def _repository_snapshot() -> dict[str, tuple[str, str]]:
    return snapshot_tree(REPOSITORY_ROOT, exclude_git=True)


def _static_plan_checks() -> dict[str, Any]:
    if sys.version_info[:3] != EXPECTED_PYTHON_VERSION:
        raise ProbeError("Python version differs from locked 3.11.9")
    source = SYNC._load_source()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if hashlib.sha256(source).hexdigest() != manifest.get("sha256"):
        raise ProbeError("kernel hash diverges from the manifest")
    validate_config(build_config())
    identity = OLLAMA.validate_local_model()
    if identity["declared_digest"] != EXPECTED_DIGEST:
        raise ProbeError("local model digest differs from the locked digest")
    install = validate_opencode_install()
    return {
        "kernel_sha256": manifest["sha256"],
        "opencode": install,
        "profile": ACTIVE_PROFILE_ID,
        "model": MODEL,
        "model_digest": EXPECTED_DIGEST,
        "manifest_digest": identity["manifest_digest"],
    }


def _plan() -> dict[str, Any]:
    checks = _static_plan_checks()
    return {
        "mode": "plan",
        "status": "READY",
        "processes_started": 0,
        "opencode_inference_processes": 0,
        "server_starts": 0,
        "model_loads": 0,
        "model_requests": 0,
        "inference_retries": MAX_RETRIES,
        "static_checks": checks,
        "provider": PROVIDER,
        "endpoint": OPENAI_BASE_URL,
        "context_tokens": CONTEXT_TOKENS,
        "allocation_policy": OLLAMA.allocation_policy(),
        "expected_output": EXPECTED_OUTPUT,
        "protocol": [
            "refuse pre-existing Ollama or OpenCode processes and occupied port 11434",
            (
                "reserve 4 GiB per GPU in the child server and require 3072 MiB free VRAM plus 16 GiB available RAM"
                if ACTIVE_PROFILE_ID == "qwen3.6-27b-q4km"
                else "require Mission 11 GPU baseline and at least 512 MiB projected residual VRAM"
            ),
            "generate and check the exact disposable adapter workspace",
            "start one owned loopback-only Ollama 0.20.2 server",
            f"load only {MODEL} at exactly {CONTEXT_TOKENS} tokens",
            "launch one direct OpenCode 1.17.9 inference process with no retry",
            "require exactly one /v1/chat/completions request and no tools or permissions",
            "discard raw JSONL and logs, unload, stop owned processes, and remove all temporary roots",
        ],
    }


def _runtime_preflight() -> dict[str, Any]:
    static = _static_plan_checks()
    executable, version_output = OLLAMA._preflight_cli()
    if OLLAMA.ollama_processes() or opencode_processes():
        raise ProbeError("a pre-existing Ollama or OpenCode process was detected")
    if OLLAMA._loopback_responds() or not OLLAMA._port_is_free():
        raise ProbeError("port 11434 is occupied or responding before the owned server starts")
    resources = OLLAMA.resource_snapshot()
    gpu_guard = guard_initial_resources(resources)
    active_compute = active_cuda_compute_processes()
    if active_compute and ACTIVE_PROFILE_ID != "qwen3.6-27b-q4km":
        raise ProbeError("another process has active CUDA/GPU compute utilization")
    return {
        "static": static,
        "ollama_executable": executable,
        "ollama_version_verified": EXPECTED_OLLAMA_VERSION in version_output,
        "resources": resources,
        "gpu_guard": gpu_guard,
        "active_cuda_compute_processes": active_compute,
    }


def _run() -> dict[str, Any]:
    preflight = _runtime_preflight()
    binary = _opencode_binary()
    model_root = OLLAMA.model_root()
    store_before = OLLAMA.all_profile_store_snapshot(model_root)
    repository_before = _repository_snapshot()
    budget = InferenceBudget()
    summary: dict[str, Any] = {
        "mode": "run",
        "profile": ACTIVE_PROFILE_ID,
        "status": "BLOCKED",
        "versions": {
            "python": ".".join(str(item) for item in EXPECTED_PYTHON_VERSION),
            "opencode": EXPECTED_OPENCODE_VERSION,
            "ollama": EXPECTED_OLLAMA_VERSION,
        },
        "provider_requested": PROVIDER,
        "model_requested": MODEL,
        "endpoint": OPENAI_BASE_URL,
        "context_requested": CONTEXT_TOKENS,
        "opencode_inference_processes": 0,
        "server_starts": 0,
        "model_loads": 0,
        "model_requests": 0,
        "inference_retries": 0,
        "resources_before_load": preflight["resources"],
        "gpu_guard": preflight["gpu_guard"],
        "allocation_policy": OLLAMA.allocation_policy(),
    }
    failure: BaseException | None = None
    temporary_name = ""
    with tempfile.TemporaryDirectory(prefix="egx-opencode-probe-") as temporary_name:
        temporary = Path(temporary_name)
        workspace = temporary / "workspace"
        for name in ("home", "config", "data", "state", "cache", "temp", "npm-cache", "bun-cache", "session"):
            (temporary / name).mkdir(parents=True, exist_ok=True)
        _sync_write(workspace)
        workspace_evidence = validate_workspace(workspace)
        workspace_before = snapshot_tree(workspace)
        summary["workspace"] = {
            **workspace_evidence,
            "unchanged_during_call": None,
            "static_check_after": None,
        }
        env = isolated_environment(temporary)
        validate_isolated_environment(env, temporary)
        session = OLLAMA.ServerSession(preflight["ollama_executable"], model_root, temporary)
        server_monitor: OwnedServerConnectionMonitor | None = None
        try:
            session.start()
            summary["server_controls"] = {
                "ollama_gpu_overhead": session.environment.get("OLLAMA_GPU_OVERHEAD"),
                "ollama_context_length": session.environment["OLLAMA_CONTEXT_LENGTH"],
                "ollama_num_parallel": session.environment["OLLAMA_NUM_PARALLEL"],
                "scope": "owned_child_server_only",
            }
            server_monitor = OwnedServerConnectionMonitor(session)
            server_monitor.start()
            summary["server_starts"] = session.server_starts
            OLLAMA.require_no_loaded_model(OLLAMA._api_request("/api/ps"))
            shown = OLLAMA.parse_show(OLLAMA._api_request("/api/show", {"model": MODEL}, timeout=30))
            OLLAMA.validate_show_for_active_profile(shown)
            if shown["maximum_context_tokens"] is None or shown["maximum_context_tokens"] < CONTEXT_TOKENS:
                raise ProbeError("model metadata does not support the fixed 16384-token context")
            load_started = time.monotonic()
            load_response = OLLAMA._api_request(
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
                "wall_seconds": time.monotonic() - load_started,
                "load_duration": load_response.get("load_duration"),
                "eval_count": load_response.get("eval_count"),
            }
            session.refresh_owned_children()
            loaded = OLLAMA.require_context(OLLAMA.parse_running_models(OLLAMA._api_request("/api/ps")))
            if loaded["digest"] != preflight["static"]["manifest_digest"].removeprefix("sha256:"):
                raise ProbeError("loaded Ollama model digest is unexpected")
            summary["loaded_model"] = loaded
            summary["model_seen_by_ollama"] = loaded["name"]
            summary["resources_after_load"] = OLLAMA.resource_snapshot()
            summary["offload_layers"] = parse_offload_layers(_read_ollama_log(session))
            summary["comfort_gate"] = loaded_resource_gate(summary["resources_after_load"])
            if not summary["comfort_gate"]["passed"]:
                if (
                    summary["comfort_gate"]["observed_available_vram_mib"]
                    < summary["comfort_gate"]["minimum_free_vram_mib"]
                ):
                    raise ProbeError("observed loaded VRAM is below the active profile minimum")
                raise ProbeError("observed loaded RAM is below the active profile minimum")
            server_monitor.checkpoint()

            call = invoke_opencode(binary, workspace, env, budget)
            server_monitor.checkpoint()
            summary["opencode_inference_processes"] = budget.processes
            summary["opencode"] = {
                "command": normalized_command(),
                "exit_code": call["exit_code"],
                "wall_seconds": call["wall_seconds"],
                "final_output": call["parsed"]["final_output"],
                "expected_output": EXPECTED_OUTPUT,
                "exact_output": exact_output_matches(call["parsed"]["final_output"]),
                "event_count": call["parsed"]["event_count"],
                "tool_call": call["parsed"]["tool_call"],
                "tool_event_types": call["parsed"]["tool_event_types"],
                "permission_request": call["parsed"]["permission_request"],
                "reasoning_visible": call["parsed"]["reasoning_visible"],
                "providers_exposed": call["parsed"]["providers"],
                "models_exposed": call["parsed"]["models"],
                "tokens": call["parsed"]["tokens"],
                "finish_reasons": call["parsed"]["finish_reasons"],
                "jsonl": call["parsed"].get("jsonl"),
                "parse_error": call["parse_error"],
                "stdout_capture": call["stdout_capture"],
                "stderr_present": call["stderr_present"],
                "stderr_category": call["stderr_category"],
                "stderr_sanitized": call["stderr_sanitized"],
                "stderr_capture": call["stderr_capture"],
            }
            summary["connections"] = call["connections"]
            log_text = _read_ollama_log(session)
            request_count = count_model_requests(log_text)
            summary["model_requests"] = request_count
            if call["parse_error"] is not None:
                budget.requests_recorded = True
                budget.requests = request_count
                raise ProbeError(call["parse_error"]["message"])
            budget.record_requests(request_count)
            endpoint_latency = parse_ollama_request_latency(log_text)
            summary["ollama_request"] = {
                "path": "/v1/chat/completions",
                "count": request_count,
                "latency_seconds": endpoint_latency,
            }
            tokens = call["parsed"]["tokens"] or {}
            output_tokens = tokens.get("output") or tokens.get("output_tokens")
            summary["throughput"] = {
                "end_to_end_output_tokens_per_second": (
                    output_tokens / call["wall_seconds"] if output_tokens is not None and call["wall_seconds"] else None
                ),
                "ollama_endpoint_output_tokens_per_second": (
                    output_tokens / endpoint_latency if output_tokens is not None and endpoint_latency else None
                ),
            }
            loaded_after = OLLAMA.require_context(OLLAMA.parse_running_models(OLLAMA._api_request("/api/ps")))
            summary["loaded_model_after_call"] = loaded_after
            summary["resources_after_call"] = OLLAMA.resource_snapshot()
            summary["workspace"]["unchanged_during_call"] = workspace_before == snapshot_tree(workspace)
            _sync_check(workspace)
            summary["workspace"]["static_check_after"] = True
            if workspace_before != snapshot_tree(workspace):
                raise ProbeError("OpenCode changed the disposable generated workspace")
            validate_parsed_events(call["parsed"])
            if call["connections"]["non_loopback_detected"]:
                raise ProbeError("a non-loopback OpenCode connection was observed")
            if not call["connections"]["owned_processes_gone"]:
                raise ProbeError("an owned OpenCode process survived the call")
            if call["exit_code"] != 0:
                raise ProbeError("OpenCode returned a non-zero exit code")
            summary["status"] = "PASS" if summary["opencode"]["exact_output"] else "FAIL"
        except BaseException as exc:
            failure = exc
            summary["error"] = str(exc)
            summary["opencode_inference_processes"] = budget.processes
            try:
                observed_log = _read_ollama_log(session)
                summary.setdefault("offload_layers", parse_offload_layers(observed_log))
                observed_requests = count_model_requests(observed_log)
                summary["model_requests"] = observed_requests
                summary.setdefault(
                    "ollama_request",
                    {
                        "path": "/v1/chat/completions",
                        "count": observed_requests,
                        "latency_seconds": parse_ollama_request_latency(observed_log),
                    },
                )
            except (OSError, ProbeError):
                pass
        finally:
            if server_monitor is not None:
                try:
                    summary["ollama_connections"] = server_monitor.stop()
                except BaseException as exc:
                    summary["ollama_connections"] = {
                        "non_loopback_detected": True,
                        "monitor_error": type(exc).__name__,
                    }
                    if failure is None:
                        failure = exc
                        summary["error"] = str(exc)
            if summary["workspace"]["unchanged_during_call"] is None:
                summary["workspace"]["unchanged_during_call"] = workspace_before == snapshot_tree(workspace)
            if summary["workspace"]["static_check_after"] is None:
                try:
                    _sync_check(workspace)
                except ProbeError:
                    summary["workspace"]["static_check_after"] = False
                else:
                    summary["workspace"]["static_check_after"] = True
            if budget.processes and "resources_after_call" not in summary:
                summary["resources_after_call"] = OLLAMA.resource_snapshot()
            cleanup = session.cleanup()
            summary["cleanup"] = cleanup
            summary["resources_after_cleanup"] = OLLAMA.resource_snapshot()
            summary["temporary_files"] = list_temporary_files(temporary)
            summary["temporary_file_count"] = len(summary["temporary_files"])
    temporary_removed = not Path(temporary_name).exists()
    summary["cleanup"]["temporary_root_removed"] = temporary_removed
    summary["cleanup"]["model_store_unchanged"] = store_before == OLLAMA.all_profile_store_snapshot(model_root)
    summary["cleanup"]["repository_unchanged"] = repository_before == _repository_snapshot()
    summary["cleanup"]["success"] = bool(
        summary["cleanup"].get("success")
        and temporary_removed
        and summary["cleanup"]["model_store_unchanged"]
        and summary["cleanup"]["repository_unchanged"]
    )
    if not summary["cleanup"]["success"]:
        summary["status"] = "FAIL"
    elif failure is not None:
        summary["status"] = "BLOCKED" if budget.processes == 0 else "FAIL"
    return sanitize_summary(summary)


def validate_mock_observation(observed: dict[str, Any]) -> dict[str, Any]:
    if observed["total_requests"] != 1:
        raise ProbeError(f"mock observed {observed['total_requests']} total requests; exactly one is required")
    if observed["generation_requests"] != 1:
        raise ProbeError(
            f"mock observed {observed['generation_requests']} generation requests; exactly one is required"
        )
    request = observed["requests"][0]
    if request != {"method": "POST", "route": "/v1/chat/completions", "accepted": True}:
        raise ProbeError("mock observed an unexpected method or route")
    generation = observed["generations"][0]
    if generation["model"] != MOCK_MODEL:
        raise ProbeError("OpenCode requested an unexpected mock model")
    if generation["kernel_occurrences"] != 1:
        raise ProbeError(
            f"mock observed {generation['kernel_occurrences']} exact kernel occurrences; exactly one is required"
        )
    if generation["prompt_occurrences"] != 1:
        raise ProbeError("mock did not observe the closed prompt exactly once")
    if generation["tool_count"] != 0:
        raise ProbeError(f"mock observed {generation['tool_count']} active tools")
    if generation["generation_options"].get("reasoning_effort") != "none":
        raise ProbeError("mock did not observe reasoning_effort none")
    return generation


def _diagnostic_preflight() -> dict[str, Any]:
    if sys.version_info[:3] != EXPECTED_PYTHON_VERSION:
        raise ProbeError("Python version differs from locked 3.11.9")
    source = SYNC._load_source()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if hashlib.sha256(source).hexdigest() != manifest.get("sha256"):
        raise ProbeError("kernel hash diverges from the manifest")
    if OLLAMA.ollama_processes() or opencode_processes():
        raise ProbeError("a pre-existing Ollama or OpenCode process was detected")
    if OLLAMA._loopback_responds() or not OLLAMA._port_is_free():
        raise ProbeError("port 11434 is occupied or responding during mock preflight")
    return {
        "kernel_sha256": manifest["sha256"],
        "opencode": validate_opencode_install(),
        "ollama_processes": 0,
        "opencode_processes": 0,
        "port_11434_free": True,
    }


def _diagnose() -> dict[str, Any]:
    preflight = _diagnostic_preflight()
    repository_before = _repository_snapshot()
    binary = _opencode_binary()
    budget = InferenceBudget()
    summary: dict[str, Any] = {
        "mode": "diagnose",
        "status": "FAIL",
        "preflight": preflight,
        "protocol": {
            "provider": MOCK_PROVIDER,
            "model": MOCK_MODEL,
            "response": MOCK_OUTPUT,
            "transport": "OpenAI-compatible chat completions SSE",
            "server_bind": "127.0.0.1:<dynamic>",
            "model_computation": False,
            "ollama_started": False,
        },
        "opencode_invocations": 0,
        "mock_server_starts": 0,
        "mock": None,
        "cleanup": {
            "mock_stopped": False,
            "temporary_root_removed": False,
            "repository_unchanged": False,
            "success": False,
        },
    }
    temporary_name = ""
    failure: BaseException | None = None
    with tempfile.TemporaryDirectory(prefix="egx-opencode-mock-") as temporary_name:
        temporary = Path(temporary_name)
        workspace = temporary / "workspace"
        _sync_write(workspace)
        workspace_evidence = validate_workspace(workspace)
        workspace_before = snapshot_tree(workspace)
        kernel = SYNC._load_source().decode("utf-8")
        server = MockProviderServer(kernel)
        config = build_mock_config(server.endpoint)
        env = isolated_environment(temporary, config, mock_endpoint=server.endpoint)
        validate_isolated_environment(env, temporary)
        try:
            server.start()
            summary["mock_server_starts"] = 1
            call = invoke_opencode(
                binary,
                workspace,
                env,
                budget,
                provider=MOCK_PROVIDER,
                model=MOCK_MODEL,
                timeout_seconds=MOCK_TIMEOUT_SECONDS,
            )
            summary["opencode_invocations"] = budget.processes
            observed = server.state.summary()
            summary["mock"] = observed
            if call["parse_error"] is not None:
                raise ProbeError(call["parse_error"]["message"])
            generation = validate_mock_observation(observed)
            validate_parsed_events(call["parsed"], MOCK_PROVIDER, MOCK_MODEL)
            if call["connections"]["non_loopback_detected"]:
                raise ProbeError("a non-loopback OpenCode connection was observed")
            if not call["connections"]["owned_processes_gone"]:
                raise ProbeError("an owned OpenCode process survived the mock call")
            if call["exit_code"] != 0:
                raise ProbeError("OpenCode returned a non-zero exit code against the mock")
            if call["parsed"]["final_output"] != MOCK_OUTPUT:
                raise ProbeError("OpenCode JSONL did not contain the exact mock response")
            if workspace_before != snapshot_tree(workspace):
                raise ProbeError("OpenCode changed the disposable generated workspace")
            _sync_check(workspace)
            summary["workspace"] = {
                **workspace_evidence,
                "unchanged_during_call": True,
                "static_check_after": True,
            }
            summary["opencode"] = {
                "command": normalized_command(MOCK_PROVIDER, MOCK_MODEL),
                "executable": "native opencode.exe",
                "exit_code": call["exit_code"],
                "event_count": call["parsed"]["event_count"],
                "final_output": call["parsed"]["final_output"],
                "tool_call": call["parsed"]["tool_call"],
                "permission_request": call["parsed"]["permission_request"],
                "reasoning_visible": call["parsed"]["reasoning_visible"],
                "providers_exposed": call["parsed"]["providers"],
                "models_exposed": call["parsed"]["models"],
                "finish_reasons": call["parsed"]["finish_reasons"],
                "jsonl": call["parsed"].get("jsonl"),
                "parse_error": call["parse_error"],
                "stdout_capture": call["stdout_capture"],
                "stderr_present": call["stderr_present"],
                "stderr_category": call["stderr_category"],
                "stderr_sanitized": call["stderr_sanitized"],
                "stderr_capture": call["stderr_capture"],
                "jsonl_raw_retained": False,
            }
            summary["request_validation"] = {
                "model": generation["model"],
                "kernel_occurrences": generation["kernel_occurrences"],
                "prompt_occurrences": generation["prompt_occurrences"],
                "tool_count": generation["tool_count"],
                "tool_choice_present": generation["tool_choice_present"],
            }
            summary["connections"] = call["connections"]
            summary["temporary_file_count_before_removal"] = len(list_temporary_files(temporary))
            summary["status"] = "PASS"
        except BaseException as exc:
            failure = exc
            summary["error"] = sanitize_stderr(str(exc), (temporary, workspace)) or type(exc).__name__
            summary["opencode_invocations"] = budget.processes
            summary["mock"] = server.state.summary()
        finally:
            try:
                server.stop()
            except BaseException as exc:
                summary["status"] = "FAIL"
                summary["error"] = sanitize_stderr(str(exc), (temporary, workspace)) or type(exc).__name__
            else:
                summary["cleanup"]["mock_stopped"] = True
    summary["cleanup"]["temporary_root_removed"] = not Path(temporary_name).exists()
    summary["cleanup"]["repository_unchanged"] = repository_before == _repository_snapshot()
    summary["cleanup"]["ollama_processes_after"] = len(OLLAMA.ollama_processes())
    summary["cleanup"]["opencode_processes_after"] = len(opencode_processes())
    summary["cleanup"]["port_11434_free_after"] = not OLLAMA._loopback_responds() and OLLAMA._port_is_free()
    summary["cleanup"]["success"] = bool(
        summary["cleanup"]["mock_stopped"]
        and summary["cleanup"]["temporary_root_removed"]
        and summary["cleanup"]["repository_unchanged"]
        and summary["cleanup"]["ollama_processes_after"] == 0
        and summary["cleanup"]["opencode_processes_after"] == 0
        and summary["cleanup"]["port_11434_free_after"]
    )
    if not summary["cleanup"]["success"] or failure is not None:
        summary["status"] = "FAIL"
    return sanitize_summary(summary)


def sanitize_summary(value: Any) -> Any:
    forbidden_keys = ("raw", "transcript", "sessionid", "authorization", "password", "api_key", "secret")
    home = str(Path.home())
    repository = str(REPOSITORY_ROOT)
    if isinstance(value, dict):
        return {
            str(key): sanitize_summary(item)
            for key, item in value.items()
            if not any(marker in str(key).lower() for marker in forbidden_keys)
        }
    if isinstance(value, list):
        return [sanitize_summary(item) for item in value]
    if isinstance(value, str):
        result = value.replace(repository, "<REPOSITORY>") if repository else value
        return result.replace(home, "<HOME>") if home else result
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose or smoke-test isolated OpenCode 1.17.9.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="validate the fixed zero-process protocol")
    plan.add_argument("--profile", choices=sorted(REQUIRED_PROFILE_IDS), default=DEFAULT_PROFILE_ID)
    subparsers.add_parser("diagnose", help="validate OpenCode initialization against a loopback mock")
    run = subparsers.add_parser("run", help="perform the authorized single local inference")
    run.add_argument("--profile", choices=sorted(REQUIRED_PROFILE_IDS), default=DEFAULT_PROFILE_ID)
    run.add_argument("--acknowledge-local-inference", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "run" and not args.acknowledge_local_inference:
        print("REFUSED: run requires --acknowledge-local-inference", file=sys.stderr)
        return 2
    try:
        if args.command in {"plan", "run"}:
            activate_profile(args.profile)
        if args.command == "plan":
            summary = _plan()
        elif args.command == "diagnose":
            summary = _diagnose()
        else:
            summary = _run()
    except (ProbeError, OLLAMA.ProbeError, SYNC.CheckError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.command in {"run", "diagnose"} and summary["status"] != "PASS":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
