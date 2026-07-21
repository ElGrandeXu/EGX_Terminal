#!/usr/bin/env python3
"""Frozen runner for the one-shot baseline versus micro-kernel campaign."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any

sys.dont_write_bytecode = True

from fixtures import (
    CAMPAIGN_SEED,
    EXPECTED_ORDER,
    FIXTURES,
    FULL_TEST_COMMAND,
    INITIAL_FIXTURES,
    KERNEL_BYTES,
    KERNEL_PATH,
    PreparedWorkspace,
    build_workspace,
    fixture_hashes,
    snapshot_files,
    task_bytes,
)
from graders import (
    compute_comparisons,
    decide,
    grader_definition_hashes,
    grade_cell,
    hidden_evaluation,
    run_visible_tests,
    sha256_bytes,
)


SCRIPT_PATH = Path(__file__).resolve()
CAMPAIGN_ROOT = SCRIPT_PATH.parent
REPOSITORY_ROOT = SCRIPT_PATH.parents[4]
ARCHIVE_ROOT = REPOSITORY_ROOT / "experiments" / "kernel-v1"
MANIFEST_PATH = CAMPAIGN_ROOT / "manifest.json"
PROTOCOL_PATH = CAMPAIGN_ROOT / "protocol.md"
ARCHIVE_RUNNER_PATH = ARCHIVE_ROOT / "tools" / "behavioral_pilot.py"
EXPECTED_PYTHON_VERSION = (3, 11, 9)
MAX_VALID_CELLS = 10
MAX_INFRASTRUCTURE_RETRIES = 2
MAX_VALID_MODEL_REQUESTS = 80
MAX_STEPS_PER_CELL = 8
MAX_OUTPUT_TOKENS = 1_024
OPENCODE_TIMEOUT_SECONDS = 900
MODEL_PROFILE = "qwen3.6-27b-q4km"
MODEL = "qwen3.6:27b"
MODEL_DIGEST = "sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926"
CONTEXT_TOKENS = 16_384
GPU_OVERHEAD_BYTES = 4_294_967_296
MINIMUM_FREE_VRAM_MIB = 3_072
TARGETED_COMMANDS = tuple(FIXTURES[name].targeted_command for name in INITIAL_FIXTURES)
ALLOWED_SHELL_COMMANDS = (
    "git status --short",
    "git diff --check",
    FULL_TEST_COMMAND,
    *TARGETED_COMMANDS,
)
EXPECTED_FROZEN_FILES = {
    "experiments/kernel-micro-v1/behavioral/final-v1/protocol.md",
    "experiments/kernel-micro-v1/behavioral/final-v1/fixtures.py",
    "experiments/kernel-micro-v1/behavioral/final-v1/graders.py",
    "experiments/kernel-micro-v1/behavioral/final-v1/runner.py",
    "experiments/kernel-micro-v1/behavioral/final-v1/test_final_v1.py",
    "experiments/kernel-v1/tools/behavioral_pilot.py",
    "experiments/kernel-v1/tools/probe_ollama.py",
    "experiments/kernel-v1/tools/probe_opencode.py",
    "experiments/kernel-v1/tools/sync_adapters.py",
    "experiments/kernel-v1/model-profiles.json",
}


class FinalEvaluationError(Exception):
    """The pre-registration, infrastructure, or safety contract failed."""


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\0")
    return digest.hexdigest()


def randomized_order(seed: int = CAMPAIGN_SEED) -> tuple[str, ...]:
    fixtures = list(INITIAL_FIXTURES)
    random.Random(seed).shuffle(fixtures)
    cells: list[str] = []
    for index, fixture in enumerate(fixtures):
        conditions = ("baseline", "micro") if index % 2 == 0 else ("micro", "baseline")
        cells.extend(f"{fixture}-{condition}" for condition in conditions)
    return tuple(cells)


def _load_manifest() -> dict[str, Any]:
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FinalEvaluationError("final-v1 manifest is unreadable") from exc
    if not isinstance(manifest, dict):
        raise FinalEvaluationError("final-v1 manifest root must be an object")
    return manifest


def _git(command: list[str]) -> str:
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    completed = subprocess.run(
        ["git", *command], cwd=REPOSITORY_ROOT, env=env, text=True,
        capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise FinalEvaluationError(f"Git preflight failed: {' '.join(command)}")
    return completed.stdout.strip()


def _verify_root_guard(manifest: dict[str, Any]) -> None:
    guard = manifest["root_guard"]
    for relative, expected in guard["unchanged_files"].items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise FinalEvaluationError(f"active root file drift: {relative}")
    for relative in guard["must_remain_absent"]:
        if (REPOSITORY_ROOT / relative).exists():
            raise FinalEvaluationError(f"micro-kernel adapter active at root: {relative}")
    root_agents = (REPOSITORY_ROOT / "AGENTS.md").read_bytes()
    if KERNEL_BYTES in root_agents:
        raise FinalEvaluationError("micro-kernel payload is active in root AGENTS.md")


def verify_preregistration(*, require_clean: bool) -> dict[str, Any]:
    manifest = _load_manifest()
    if manifest.get("campaign") != "kernel-micro-final-v1" or manifest.get("status") != "preregistered":
        raise FinalEvaluationError("manifest campaign identity or status drift")
    expected_files = manifest.get("frozen_files", {})
    if set(expected_files) != EXPECTED_FROZEN_FILES:
        raise FinalEvaluationError("frozen component set drift")
    for relative, expected in expected_files.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise FinalEvaluationError(f"frozen file hash drift: {relative}")
    if sha256_file(PROTOCOL_PATH) != manifest["protocol"]["sha256"]:
        raise FinalEvaluationError("protocol hash drift")
    if sha256_file(KERNEL_PATH) != manifest["kernel"]["sha256"]:
        raise FinalEvaluationError("micro-kernel hash drift")
    if len(KERNEL_PATH.read_bytes()) != manifest["kernel"]["bytes"]:
        raise FinalEvaluationError("micro-kernel byte length drift")
    if fixture_hashes() != {item["id"]: item["definition_sha256"] for item in manifest["fixtures"]}:
        raise FinalEvaluationError("fixture definition hash drift")
    if grader_definition_hashes() != manifest["grader_definition_sha256"]:
        raise FinalEvaluationError("grader definition hash drift")
    if list(randomized_order()) != manifest["randomization"]["cell_order"] or randomized_order() != EXPECTED_ORDER:
        raise FinalEvaluationError("cell order drift")
    runtime = manifest["runtime"]
    expected_runtime = {
        "python": "3.11.9",
        "opencode": "1.17.9",
        "ollama": "0.20.2",
        "profile": MODEL_PROFILE,
        "model": MODEL,
        "model_digest": MODEL_DIGEST,
        "context_tokens": CONTEXT_TOKENS,
        "num_parallel": 1,
        "ollama_gpu_overhead_bytes": GPU_OVERHEAD_BYTES,
        "minimum_free_vram_mib": MINIMUM_FREE_VRAM_MIB,
        "max_output_tokens_per_request": MAX_OUTPUT_TOKENS,
        "opencode_steps_per_cell": MAX_STEPS_PER_CELL,
        "opencode_timeout_seconds": OPENCODE_TIMEOUT_SECONDS,
    }
    if any(runtime.get(key) != value for key, value in expected_runtime.items()):
        raise FinalEvaluationError("frozen runtime condition drift")
    if manifest["budgets"] != {
        "valid_cells": MAX_VALID_CELLS,
        "infrastructure_retries": MAX_INFRASTRUCTURE_RETRIES,
        "behavioral_retries": 0,
        "valid_qwen_requests": MAX_VALID_MODEL_REQUESTS,
        "requests_per_valid_cell": MAX_STEPS_PER_CELL,
        "campaigns": 1,
    }:
        raise FinalEvaluationError("campaign budget drift")
    if manifest["decision"].get("verdicts") != ["PROMOTE_MICRO", "REJECT_MICRO"] or manifest["decision"].get("inconclusive_allowed") is not False:
        raise FinalEvaluationError("binary decision contract drift")
    if tree_sha256(ARCHIVE_ROOT) != manifest["archive_guard"]["tree_sha256"]:
        raise FinalEvaluationError("immutable kernel-v1 archive drift")
    _verify_root_guard(manifest)
    if require_clean:
        if _git(["branch", "--show-current"]) != "main":
            raise FinalEvaluationError("campaign must run from main")
        if _git(["status", "--porcelain=v1"]):
            raise FinalEvaluationError("campaign requires a clean Git worktree")
        source_head = manifest["source_head"]
        completed = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_head, "HEAD"],
            cwd=REPOSITORY_ROOT, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
            capture_output=True, check=False,
        )
        if completed.returncode != 0:
            raise FinalEvaluationError("pre-registration source HEAD is not an ancestor")
    return manifest


def plan(*, require_clean: bool = True) -> dict[str, Any]:
    manifest = verify_preregistration(require_clean=require_clean)
    return {
        "status": "READY",
        "campaign": manifest["campaign"],
        "protocol_sha256": manifest["protocol"]["sha256"],
        "kernel_sha256": manifest["kernel"]["sha256"],
        "archive_tree_sha256": manifest["archive_guard"]["tree_sha256"],
        "seed": CAMPAIGN_SEED,
        "order": list(EXPECTED_ORDER),
        "processes_started": 0,
        "models_loaded": 0,
        "behavioral_runs": 0,
        "model_requests": 0,
        "files_written": 0,
        "infrastructure_retries": 0,
    }


class CampaignBudget:
    """Count valid cells separately from infrastructure-only attempts."""

    def __init__(self) -> None:
        self.valid_cells: set[str] = set()
        self.attempts: dict[str, int] = {}
        self.valid_model_requests = 0
        self.infrastructure_model_requests = 0
        self.infrastructure_retries = 0

    def start_attempt(self, cell_id: str) -> None:
        if cell_id not in EXPECTED_ORDER:
            raise FinalEvaluationError(f"unknown cell: {cell_id}")
        if cell_id in self.valid_cells:
            raise FinalEvaluationError(f"behavioral retry refused for {cell_id}")
        self.attempts[cell_id] = self.attempts.get(cell_id, 0) + 1

    def complete_valid(self, cell_id: str, requests: int) -> None:
        if requests < 0 or requests > MAX_STEPS_PER_CELL:
            raise FinalEvaluationError("per-cell valid request budget exceeded")
        if len(self.valid_cells) >= MAX_VALID_CELLS:
            raise FinalEvaluationError("ten-cell valid observation budget exhausted")
        if self.valid_model_requests + requests > MAX_VALID_MODEL_REQUESTS:
            raise FinalEvaluationError("valid Qwen request budget exhausted")
        self.valid_cells.add(cell_id)
        self.valid_model_requests += requests

    def retry_infrastructure(
        self,
        *,
        cell_id: str,
        requests: int,
        behavioral_observation: bool,
        diagnosis_recorded: bool,
        correction_verified: bool,
    ) -> None:
        if behavioral_observation:
            raise FinalEvaluationError("infrastructure retry refused after behavioral observation")
        if not diagnosis_recorded or not correction_verified:
            raise FinalEvaluationError("infrastructure retry requires recorded diagnosis and verified correction")
        if self.infrastructure_retries >= MAX_INFRASTRUCTURE_RETRIES:
            raise FinalEvaluationError("infrastructure retry budget exhausted")
        if requests < 0:
            raise FinalEvaluationError("negative infrastructure request count")
        self.infrastructure_retries += 1
        self.infrastructure_model_requests += requests


def verify_arm_equality(parent: Path, fixture_id: str) -> bool:
    baseline = build_workspace(parent, f"{fixture_id}-baseline")
    micro = build_workspace(parent, f"{fixture_id}-micro")
    return task_bytes(baseline.before) == task_bytes(micro.before)


def build_permissions() -> dict[str, Any]:
    return {
        "*": "deny",
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "list": "allow",
        "edit": "allow",
        "bash": {"*": "deny", **{command: "allow" for command in ALLOWED_SHELL_COMMANDS}},
        "external_directory": "deny",
        "task": "deny",
        "webfetch": "deny",
        "websearch": "deny",
        "skill": "deny",
        "question": "deny",
        "lsp": "deny",
        "todowrite": "deny",
        "plan_enter": "deny",
        "plan_exit": "deny",
        "doom_loop": "deny",
    }


def _load_archive_runtime() -> Any:
    spec = importlib.util.spec_from_file_location("egx_frozen_behavioral_runtime", ARCHIVE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise FinalEvaluationError("cannot import frozen behavioral runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.CHALLENGE_ALLOWED_SHELL_COMMANDS = ALLOWED_SHELL_COMMANDS
    module.OPENCODE_TIMEOUT_SECONDS = OPENCODE_TIMEOUT_SECONDS
    return module


def build_config(runtime: Any) -> dict[str, Any]:
    config = runtime.build_config()
    config["permission"] = build_permissions()
    config["agent"]["build"]["steps"] = MAX_STEPS_PER_CELL
    model_options = config["provider"][runtime.OPENCODE.PROVIDER]["models"][runtime.OPENCODE.MODEL]
    model_options["limit"] = {"context": CONTEXT_TOKENS, "output": MAX_OUTPUT_TOKENS}
    model_options["options"] = {"temperature": 0, "reasoningEffort": "none"}
    return config


def isolated_environment(runtime: Any, root: Path, config: dict[str, Any]) -> dict[str, str]:
    env = runtime.isolated_environment(root, config)
    env["OPENCODE_PERMISSION"] = json.dumps(build_permissions(), separators=(",", ":"))
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config, separators=(",", ":"))
    return env


def _runtime_preflight(runtime: Any) -> dict[str, Any]:
    manifest = verify_preregistration(require_clean=True)
    if sys.version_info[:3] != EXPECTED_PYTHON_VERSION:
        raise FinalEvaluationError("Python version differs from frozen 3.11.9")
    profile = runtime.activate_profile()
    if (
        profile["ollama_model"] != MODEL
        or profile["digest"] != MODEL_DIGEST
        or profile["test_context_tokens"] != CONTEXT_TOKENS
        or profile["gpu_overhead_bytes"] != GPU_OVERHEAD_BYTES
        or profile["minimum_free_vram_mib"] != MINIMUM_FREE_VRAM_MIB
        or profile["num_parallel"] != 1
    ):
        raise FinalEvaluationError("model profile identity drift")
    static = runtime.OPENCODE._static_plan_checks()
    executable, version = runtime.OLLAMA._preflight_cli()
    if runtime.OLLAMA.ollama_processes() or runtime.OPENCODE.opencode_processes():
        raise FinalEvaluationError("pre-existing Ollama or OpenCode process detected")
    if runtime.OLLAMA._loopback_responds() or not runtime.OLLAMA._port_is_free():
        raise FinalEvaluationError("port 11434 is occupied")
    resources = runtime.OLLAMA.resource_snapshot()
    runtime.OPENCODE.guard_initial_resources(resources)
    if runtime.OLLAMA.EXPECTED_OLLAMA_VERSION not in version:
        raise FinalEvaluationError("Ollama version drift")
    if runtime.OPENCODE.EXPECTED_OPENCODE_VERSION != "1.17.9":
        raise FinalEvaluationError("OpenCode version drift")
    config = build_config(runtime)
    return {
        "manifest": manifest,
        "static": static,
        "ollama_executable": executable,
        "resources": resources,
        "config": config,
    }


def _checkpoint(path: Path, summary: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def _output_path(value: str) -> Path:
    path = Path(value).resolve()
    try:
        path.relative_to(REPOSITORY_ROOT)
    except ValueError:
        pass
    else:
        raise FinalEvaluationError("run output must remain outside the active repository")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_ollama_log(runtime: Any, session: Any) -> str:
    return runtime._read_ollama_log(session)


def _validate_loaded_model_digest(loaded: dict[str, Any], manifest: dict[str, Any]) -> None:
    expected = manifest["runtime"]["model_manifest_digest"].removeprefix("sha256:")
    if loaded["digest"] != expected:
        raise FinalEvaluationError("loaded model digest drift")


def _cell_metrics(call: dict[str, Any], request_count: int) -> dict[str, Any]:
    behavior = call["behavior"]
    tokens = behavior["tokens"]
    present = behavior.get("token_fields_present", {})
    total = int(tokens.get("input", 0)) + int(tokens.get("output", 0)) + int(tokens.get("reasoning", 0))
    return {
        "tool_calls": behavior.get("tool_calls", 0),
        "model_requests": request_count,
        "tokens": {
            "input": int(tokens.get("input", 0)),
            "cached_input": int(tokens.get("cache_read", 0)) if present.get("cache_read") else None,
            "output": int(tokens.get("output", 0)),
            "reasoning": int(tokens.get("reasoning", 0)),
            "total": total,
        },
        "latency_seconds": call["duration_seconds"],
        "interventions_or_refusals": {
            "clarification_requested": bool(behavior.get("clarification_requested")),
            "unexpected_or_denied_shell_commands": int(behavior.get("unexpected_shell_commands", 0)),
        },
    }


def run_campaign(output_value: str) -> dict[str, Any]:
    output = _output_path(output_value)
    runtime = _load_archive_runtime()
    preflight = _runtime_preflight(runtime)
    repository_before = runtime.OPENCODE._repository_snapshot()
    archive_before = tree_sha256(ARCHIVE_ROOT)
    model_root = runtime.OLLAMA.model_root()
    store_before = runtime.OLLAMA.all_profile_store_snapshot(model_root)
    binary = runtime.OPENCODE._opencode_binary()
    budget = CampaignBudget()
    summary: dict[str, Any] = {
        "schema_version": 1,
        "campaign": "kernel-micro-final-v1",
        "status": "RUNNING",
        "protocol_sha256": preflight["manifest"]["protocol"]["sha256"],
        "kernel_sha256": preflight["manifest"]["kernel"]["sha256"],
        "seed": CAMPAIGN_SEED,
        "order": list(EXPECTED_ORDER),
        "environment": preflight["manifest"]["runtime"],
        "cells": [],
        "infrastructure_incidents": [],
    }
    _checkpoint(output, summary)
    temporary_name = tempfile.mkdtemp(prefix="egx-micro-final-v1-")
    temporary = Path(temporary_name)
    session = runtime.OLLAMA.ServerSession(preflight["ollama_executable"], model_root, temporary)
    server_monitor = None
    try:
        session.start()
        server_monitor = runtime.OPENCODE.OwnedServerConnectionMonitor(session)
        server_monitor.start()
        runtime.OLLAMA.require_no_loaded_model(runtime.OLLAMA._api_request("/api/ps"))
        shown = runtime.OLLAMA.parse_show(runtime.OLLAMA._api_request("/api/show", {"model": MODEL}, timeout=30))
        runtime.OLLAMA.validate_show_for_active_profile(shown)
        runtime.OLLAMA._api_request(
            "/api/chat",
            {"model": MODEL, "messages": [], "stream": False, "keep_alive": runtime.OLLAMA.KEEP_ALIVE, "options": {"num_ctx": CONTEXT_TOKENS}},
            timeout=runtime.OLLAMA.MODEL_LOAD_TIMEOUT_SECONDS,
        )
        session.refresh_owned_children()
        loaded = runtime.OLLAMA.require_context(runtime.OLLAMA.parse_running_models(runtime.OLLAMA._api_request("/api/ps")))
        _validate_loaded_model_digest(loaded, preflight["manifest"])
        resources_loaded = runtime.OLLAMA.resource_snapshot()
        runtime.OPENCODE.guard_loaded_resources(resources_loaded)
        summary["runtime"] = {"server_starts": session.server_starts, "model_loads": 1, "loaded_model": loaded, "resources_after_load": resources_loaded}
        _checkpoint(output, summary)
        for cell_id in EXPECTED_ORDER:
            attempt = 0
            while True:
                attempt += 1
                budget.start_attempt(cell_id)
                cell_parent = temporary / "cells" / f"{cell_id}-attempt-{attempt}"
                env_root = temporary / "sessions" / f"{cell_id}-attempt-{attempt}"
                prepared: PreparedWorkspace | None = None
                call: dict[str, Any] | None = None
                request_count = 0
                try:
                    prepared = build_workspace(cell_parent, cell_id)
                    tests_before = run_visible_tests(prepared.root)
                    hidden_before = hidden_evaluation(prepared.root, prepared.task.fixture_id)
                    if tests_before["passed"] or hidden_before.get("functional"):
                        raise FinalEvaluationError(f"initial failure not reproducible: {cell_id}")
                    env_root.mkdir(parents=True)
                    config = build_config(runtime)
                    env = isolated_environment(runtime, env_root, config)
                    before_requests = runtime.OPENCODE.count_model_requests(_read_ollama_log(runtime, session))
                    call = runtime.invoke_cell(binary, prepared, env)
                    after_requests = runtime.OPENCODE.count_model_requests(_read_ollama_log(runtime, session))
                    request_count = after_requests - before_requests
                    server_monitor.checkpoint()
                    after = snapshot_files(prepared.root)
                    exploitable = bool(
                        request_count > 0
                        or call["behavior"].get("event_count")
                        or call["behavior"].get("final_output_present")
                        or task_bytes(after) != task_bytes(prepared.before)
                    )
                    infrastructure_error = bool(
                        call["timed_out"]
                        or call["connections"].get("non_loopback_detected")
                        or not call["connections"].get("owned_processes_gone", True)
                        or (call["exit_code"] != 0 and not exploitable)
                    )
                    if infrastructure_error and not exploitable:
                        raise FinalEvaluationError("non-behavioral OpenCode infrastructure failure")
                    tests_after = run_visible_tests(prepared.root)
                    hidden_after = hidden_evaluation(prepared.root, prepared.task.fixture_id)
                    scoring = grade_cell(prepared, after, tests_after, hidden_after, call["behavior"])
                    if call["connections"].get("non_loopback_detected"):
                        scoring["security_success"] = False
                        scoring["primary_success"] = False
                        if "SECURITY_FAIL" not in scoring["labels"]:
                            scoring["labels"].append("SECURITY_FAIL")
                    budget.complete_valid(cell_id, request_count)
                    cell = {
                        "cell_id": cell_id,
                        "fixture": prepared.task.fixture_id,
                        "condition": prepared.condition,
                        "attempt": attempt,
                        "valid_observation": True,
                        "tests_before": tests_before,
                        "tests_after": tests_after,
                        "opencode": call,
                        "metrics": _cell_metrics(call, request_count),
                        "scoring": scoring,
                        "infrastructure_errors": [],
                    }
                    summary["cells"].append(cell)
                    _checkpoint(output, summary)
                    break
                except (FinalEvaluationError, OSError, subprocess.SubprocessError) as exc:
                    after = snapshot_files(prepared.root) if prepared is not None and prepared.root.exists() else {}
                    exploitable = bool(
                        prepared is not None
                        and (request_count > 0 or task_bytes(after) != task_bytes(prepared.before))
                        or call is not None and (call["behavior"].get("event_count") or call["behavior"].get("final_output_present"))
                    )
                    incident = {
                        "cell_id": cell_id,
                        "attempt": attempt,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "behavioral_observation": exploitable,
                        "model_requests": request_count,
                        "payload_fixture_grader_changed": False,
                    }
                    summary["infrastructure_incidents"].append(incident)
                    _checkpoint(output, summary)
                    if exploitable:
                        consumed: dict[str, Any] = {
                            "cell_id": cell_id,
                            "fixture": prepared.task.fixture_id if prepared is not None else cell_id.rsplit("-", 1)[0],
                            "condition": prepared.condition if prepared is not None else cell_id.rsplit("-", 1)[1],
                            "attempt": attempt,
                            "valid_observation": False,
                            "behavioral_observation_consumed": True,
                            "infrastructure_errors": [incident],
                        }
                        if prepared is not None and call is not None:
                            try:
                                tests_after = run_visible_tests(prepared.root)
                                hidden_after = hidden_evaluation(prepared.root, prepared.task.fixture_id)
                                scoring = grade_cell(prepared, after, tests_after, hidden_after, call["behavior"])
                                scoring["security_success"] = False
                                scoring["primary_success"] = False
                                if "SECURITY_FAIL" not in scoring["labels"]:
                                    scoring["labels"].append("SECURITY_FAIL")
                                budget.complete_valid(cell_id, request_count)
                                consumed.update({
                                    "valid_observation": True,
                                    "tests_after": tests_after,
                                    "opencode": call,
                                    "metrics": _cell_metrics(call, request_count),
                                    "scoring": scoring,
                                })
                            except (FinalEvaluationError, OSError, subprocess.SubprocessError):
                                pass
                        summary["cells"].append(consumed)
                        _checkpoint(output, summary)
                        break
                    if budget.infrastructure_retries >= MAX_INFRASTRUCTURE_RETRIES:
                        summary["cells"].append({
                            "cell_id": cell_id,
                            "fixture": FIXTURES[cell_id.rsplit("-", 1)[0]].fixture_id,
                            "condition": cell_id.rsplit("-", 1)[1],
                            "valid_observation": False,
                            "infrastructure_errors": [incident],
                        })
                        _checkpoint(output, summary)
                        break
                    correction_verified = bool(not runtime.OPENCODE.opencode_processes())
                    budget.retry_infrastructure(
                        cell_id=cell_id,
                        requests=request_count,
                        behavioral_observation=False,
                        diagnosis_recorded=True,
                        correction_verified=correction_verified,
                    )
                finally:
                    for cleanup_path, stage in ((cell_parent, "workspace-cleanup"), (env_root, "session-cleanup")):
                        if not cleanup_path.exists():
                            continue
                        try:
                            runtime._remove_tree_strict(cleanup_path)
                        except (OSError, runtime.PilotError) as cleanup_error:
                            summary["infrastructure_incidents"].append({
                                "cell_id": cell_id,
                                "attempt": attempt,
                                "stage": stage,
                                "error_type": type(cleanup_error).__name__,
                                "error": str(cleanup_error),
                                "behavioral_observation_replayed": False,
                                "payload_fixture_grader_changed": False,
                            })
                            _checkpoint(output, summary)
        summary["comparisons"] = compute_comparisons(summary["cells"])
        summary["decision"] = decide(summary["cells"], summary["comparisons"])
        summary["status"] = "COMPLETE"
    finally:
        if server_monitor is not None:
            with contextlib.suppress(BaseException):
                summary["ollama_connections"] = server_monitor.stop()
        with contextlib.suppress(BaseException):
            summary["cleanup"] = session.cleanup()
        with contextlib.suppress(OSError):
            shutil.rmtree(temporary)
        summary.setdefault("cleanup", {})["temporary_root_removed"] = not temporary.exists()
        summary["cleanup"]["model_store_unchanged"] = store_before == runtime.OLLAMA.all_profile_store_snapshot(model_root)
        summary["cleanup"]["repository_unchanged_during_run"] = repository_before == runtime.OPENCODE._repository_snapshot()
        summary["cleanup"]["archive_unchanged"] = archive_before == tree_sha256(ARCHIVE_ROOT)
        summary["cleanup"]["ollama_processes_after"] = len(runtime.OLLAMA.ollama_processes())
        summary["cleanup"]["opencode_processes_after"] = len(runtime.OPENCODE.opencode_processes())
        summary["cleanup"]["port_11434_free_after"] = not runtime.OLLAMA._loopback_responds() and runtime.OLLAMA._port_is_free()
        summary["budget"] = {
            "valid_cells": len(budget.valid_cells),
            "valid_model_requests": budget.valid_model_requests,
            "infrastructure_model_requests": budget.infrastructure_model_requests,
            "infrastructure_retries": budget.infrastructure_retries,
            "maximum_valid_cells": MAX_VALID_CELLS,
            "maximum_valid_model_requests": MAX_VALID_MODEL_REQUESTS,
            "maximum_infrastructure_retries": MAX_INFRASTRUCTURE_RETRIES,
            "behavioral_retries": 0,
        }
        _checkpoint(output, summary)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the frozen final micro-kernel evaluation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="verify the frozen plan without runtime or inference")
    run = subparsers.add_parser("run", help="execute the single ten-cell campaign")
    run.add_argument("--acknowledge-final-binary-campaign", action="store_true")
    run.add_argument("--output", required=True, help="checkpoint/result JSON path outside the repository")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "run" and not args.acknowledge_final_binary_campaign:
        print("REFUSED: final run requires --acknowledge-final-binary-campaign", file=sys.stderr)
        return 2
    try:
        summary = plan() if args.command == "plan" else run_campaign(args.output)
    except (FinalEvaluationError, OSError, subprocess.SubprocessError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if args.command == "plan" or summary.get("status") == "COMPLETE" else 4


if __name__ == "__main__":
    raise SystemExit(main())
