#!/usr/bin/env python3
"""Probe Codex CLI project-instruction discovery in disposable repositories."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable


EXPECTED_CODEX_VERSION = "codex-cli 0.144.6"
MAX_SUCCESSFUL_CALLS = 6
MAX_ATTEMPTS = 7
KERNEL_EXPECTED_OUTPUT = (
    "Understand the requested outcome, constraints, relevant work, and"
)
KERNEL_PROMPT = (
    "Do not use tools or read files. Based only on project instructions already "
    "supplied before this message, output only their first eight words."
)
IDENTIFIER_PROMPT = (
    "Do not use tools or read files. Follow the project response instruction "
    "already supplied before this message and output only its identifier."
)
REQUIRED_EXEC_HELP = (
    "--ephemeral",
    "--sandbox <SANDBOX_MODE>",
    "read-only",
    "--cd <DIR>",
    "--json",
)
SAFE_ITEM_TYPES = {"agent_message", "reasoning"}
TOOL_MARKERS = (
    "approval",
    "command_execution",
    "file_change",
    "mcp_tool_call",
    "tool_call",
    "web_search",
)

SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parent.parent
REPOSITORY_ROOT = SCRIPT_PATH.parents[3]
MANIFEST_PATH = EXPERIMENT_ROOT / "manifest.json"


class ProbeError(Exception):
    """A safety, validation, or runtime precondition failed."""


class BudgetError(ProbeError):
    """The fixed model-call budget would be exceeded."""


def _load_sync_module() -> Any:
    path = SCRIPT_PATH.with_name("sync_adapters.py")
    spec = importlib.util.spec_from_file_location("egx_kernel_sync_adapters", path)
    if spec is None or spec.loader is None:
        raise ProbeError("cannot load sync_adapters.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SYNC = _load_sync_module()


def validate_kernel_and_manifest() -> bytes:
    """Reuse the generator's integrity check, then verify its remaining metrics."""
    try:
        source = SYNC._load_source()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, SYNC.CheckError) as error:
        raise ProbeError(f"kernel or manifest validation failed: {error}") from error

    text = source.decode("utf-8")
    expected = {
        "characters": len(text),
        "words": len(re.findall(r"\S+", text)),
        "token_estimation_method": "ceil(characters / 4)",
        "estimated_tokens": math.ceil(len(text) / 4),
        "always_on_payload_token_ceiling": 300,
        "activation": False,
    }
    errors = [
        f"{key}={manifest.get(key)!r}, expected {value!r}"
        for key, value in expected.items()
        if manifest.get(key) != value
    ]
    if manifest.get("estimated_tokens", 301) > manifest.get(
        "always_on_payload_token_ceiling", 300
    ):
        errors.append("estimated token count exceeds the manifest ceiling")
    if errors:
        raise ProbeError("kernel or manifest validation failed: " + "; ".join(errors))
    return source


def validate_codex_version(output: str) -> None:
    if output.strip() != EXPECTED_CODEX_VERSION:
        raise ProbeError(
            f"Codex version is {output.strip()!r}; expected {EXPECTED_CODEX_VERSION!r}"
        )


def validate_exec_help(output: str) -> None:
    missing = [option for option in REQUIRED_EXEC_HELP if option not in output]
    if missing:
        raise ProbeError(
            "Codex exec lacks required ephemeral/read-only/JSON/cwd options: "
            + ", ".join(missing)
        )


def _codex_executable() -> str:
    executable = shutil.which("codex")
    if executable is None:
        raise ProbeError("Codex CLI executable is not available on PATH")
    return executable


def _codex_preflight() -> None:
    executable = _codex_executable()
    try:
        version = subprocess.run(
            [executable, "--version"],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        help_result = subprocess.run(
            [executable, "exec", "--help"],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProbeError(f"Codex CLI preflight failed: {type(error).__name__}") from error
    if version.returncode != 0 or help_result.returncode != 0:
        raise ProbeError("Codex CLI version/help preflight returned a non-zero exit code")
    validate_codex_version(version.stdout)
    validate_exec_help(help_result.stdout)


def refuse_repository_root(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    if resolved == REPOSITORY_ROOT:
        raise ProbeError("the EGX_Terminal repository root is never a valid fixture")
    try:
        resolved.relative_to(REPOSITORY_ROOT)
    except ValueError:
        return resolved
    raise ProbeError("fixtures must be outside EGX_Terminal")


def _write_fixture_file(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _git_init(root: Path) -> None:
    result = subprocess.run(
        ["git", "init", "--quiet"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )
    if result.returncode != 0:
        raise ProbeError("git init failed for a disposable fixture")


def _sync_write(root: Path) -> None:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        result = SYNC.main(["write", "--target", str(root)])
    if result != SYNC.EXIT_OK:
        raise ProbeError("sync_adapters.py could not produce the kernel fixture")


def _sync_check(root: Path) -> bool:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return SYNC.main(["check", "--target", str(root)]) == SYNC.EXIT_OK


def make_canaries() -> dict[str, str]:
    nonce = secrets.token_hex(12).upper()
    return {
        "root_discovery": f"EGXROOT_{nonce}",
        "nested_root": f"EGXPARENT_{nonce}",
        "nested_child": f"EGXCHILD_{nonce}",
        "standard": f"EGXSTANDARD_{nonce}",
        "override": f"EGXOVERRIDE_{nonce}",
    }


def case_definitions(canaries: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {
            "id": "case-0-baseline",
            "objective": "absence of project doctrine in the disposable baseline",
            "shape": "empty Git repository; no project instruction files",
            "kind": "baseline",
            "cwd": ".",
            "prompt": KERNEL_PROMPT,
            "expected": "any concise non-kernel-prefix response",
        },
        {
            "id": "case-1-root",
            "objective": "native discovery of a root AGENTS.md",
            "shape": "Git repository with one root AGENTS.md canary",
            "kind": "root",
            "cwd": ".",
            "prompt": IDENTIFIER_PROMPT,
            "canary": canaries["root_discovery"],
            "expected": "<ROOT_DISCOVERY_CANARY>",
        },
        {
            "id": "case-2-kernel-first",
            "objective": "loading of the byte-for-byte generated kernel adapter",
            "shape": "Git repository produced by sync_adapters.py write",
            "kind": "kernel",
            "cwd": ".",
            "prompt": KERNEL_PROMPT,
            "expected": KERNEL_EXPECTED_OUTPUT,
        },
        {
            "id": "case-3-kernel-second",
            "objective": "independent repetition of generated-kernel loading",
            "shape": "independent Git repository produced by sync_adapters.py write",
            "kind": "kernel",
            "cwd": ".",
            "prompt": KERNEL_PROMPT,
            "expected": KERNEL_EXPECTED_OUTPUT,
        },
        {
            "id": "case-4-nested",
            "objective": "precedence of the closest nested AGENTS.md scope",
            "shape": "root AGENTS.md plus child/AGENTS.md; launch from child",
            "kind": "nested",
            "cwd": "child",
            "prompt": IDENTIFIER_PROMPT,
            "canary": canaries["nested_child"],
            "root_canary": canaries["nested_root"],
            "expected": "<CHILD_CANARY>",
        },
        {
            "id": "case-5-override",
            "objective": "precedence of AGENTS.override.md over AGENTS.md at one level",
            "shape": "root AGENTS.md plus root AGENTS.override.md",
            "kind": "override",
            "cwd": ".",
            "prompt": IDENTIFIER_PROMPT,
            "canary": canaries["override"],
            "standard_canary": canaries["standard"],
            "expected": "<OVERRIDE_CANARY>",
        },
    ]


def build_fixture(root: Path, case: dict[str, Any]) -> Path:
    root = refuse_repository_root(root)
    root.mkdir(parents=True, exist_ok=False)
    kind = case["kind"]
    if kind == "root":
        _write_fixture_file(
            root,
            "AGENTS.md",
            f"For this probe, reply with exactly {case['canary']} and nothing else.",
        )
    elif kind == "kernel":
        _sync_write(root)
    elif kind == "nested":
        _write_fixture_file(
            root,
            "AGENTS.md",
            f"For this probe, reply with exactly {case['root_canary']} and nothing else.",
        )
        _write_fixture_file(
            root,
            "child/AGENTS.md",
            "This closest-scope instruction replaces the root response format. "
            f"Reply with exactly {case['canary']} and nothing else.",
        )
    elif kind == "override":
        _write_fixture_file(
            root,
            "AGENTS.md",
            f"For this probe, reply with exactly {case['standard_canary']} and nothing else.",
        )
        _write_fixture_file(
            root,
            "AGENTS.override.md",
            f"For this probe, reply with exactly {case['canary']} and nothing else.",
        )
    elif kind != "baseline":
        raise ProbeError(f"unknown fixture kind: {kind}")
    _git_init(root)
    return root / case["cwd"]


def _snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(path))
        elif path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_dir():
            snapshot[relative] = ("dir", "")
    return snapshot


def _repository_snapshot() -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(REPOSITORY_ROOT.rglob("*")):
        if ".git" in path.relative_to(REPOSITORY_ROOT).parts:
            continue
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        if path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
        elif path.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(path))
    return snapshot


def parse_json_events(raw: str) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise ProbeError(f"invalid JSONL event at line {number}") from error
        if not isinstance(event, dict):
            raise ProbeError(f"JSONL event at line {number} is not an object")
        events.append(event)

    final_messages: list[str] = []
    tool_types: list[str] = []
    usage: dict[str, int] | None = None
    for event in events:
        event_type = str(event.get("type", ""))
        item = event.get("item")
        item_type = str(item.get("type", "")) if isinstance(item, dict) else ""
        combined = f"{event_type} {item_type}".lower()
        if item_type and item_type not in SAFE_ITEM_TYPES:
            tool_types.append(item_type)
        elif any(marker in combined for marker in TOOL_MARKERS):
            tool_types.append(item_type or event_type)
        if item_type == "agent_message" and isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                final_messages.append(text)
        candidate = event.get("usage")
        if isinstance(candidate, dict) and (
            "input_tokens" in candidate or "output_tokens" in candidate
        ):
            input_tokens = int(candidate.get("input_tokens", 0))
            cached_tokens = int(candidate.get("cached_input_tokens", 0))
            output_tokens = int(candidate.get("output_tokens", 0))
            usage = {
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "total_tokens": int(candidate.get("total_tokens", input_tokens + output_tokens)),
            }
    return {
        "event_count": len(events),
        "final_output": final_messages[-1].strip() if final_messages else "",
        "tool_call": bool(tool_types),
        "tool_types": sorted(set(tool_types)),
        "tokens": usage,
    }


class CallBudget:
    def __init__(self) -> None:
        self.attempts = 0
        self.successful_calls = 0
        self.retry_used = False

    def reserve(self) -> None:
        if self.attempts >= MAX_ATTEMPTS:
            raise BudgetError("the seven-attempt campaign ceiling is exhausted")
        if self.successful_calls >= MAX_SUCCESSFUL_CALLS:
            raise BudgetError("the six-successful-call campaign ceiling is exhausted")
        self.attempts += 1

    def record_exit(self, returncode: int) -> None:
        if returncode == 0:
            self.successful_calls += 1

    def allow_infrastructure_retry(self) -> bool:
        if self.retry_used or self.attempts >= MAX_ATTEMPTS:
            return False
        self.retry_used = True
        return True


def _codex_command(cwd: Path, prompt: str) -> list[str]:
    return [
        _codex_executable(),
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--cd",
        str(cwd),
        "--json",
        "--color",
        "never",
        prompt,
    ]


def normalized_command() -> str:
    return (
        "codex exec --ephemeral --ignore-user-config --ignore-rules "
        "--sandbox read-only --cd <fixture-cwd> --json --color never <closed-prompt>"
    )


def _invoke_codex(cwd: Path, prompt: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _codex_command(cwd, prompt),
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )


def _safe_observed(case: dict[str, Any], actual: str) -> str:
    if case["kind"] == "baseline":
        if actual == KERNEL_EXPECTED_OUTPUT:
            return KERNEL_EXPECTED_OUTPUT
        return "<NON_KERNEL_RESPONSE_REDACTED>" if actual else "<EMPTY>"
    if case["kind"] == "kernel":
        return actual if actual == KERNEL_EXPECTED_OUTPUT else "<UNEXPECTED_RESPONSE_REDACTED>"
    if actual == case.get("canary"):
        return case["expected"]
    return "<UNEXPECTED_RESPONSE_REDACTED>" if actual else "<EMPTY>"


def _evaluate(case: dict[str, Any], parsed: dict[str, Any], returncode: int) -> tuple[str, str]:
    if returncode != 0:
        return "BLOCKED", "Codex returned a non-zero exit code"
    if parsed["tool_call"]:
        return "FAIL", "a tool or approval event was emitted"
    actual = parsed["final_output"]
    if not actual:
        return "FAIL", "no final agent message was present"
    if case["kind"] == "baseline":
        if actual == KERNEL_EXPECTED_OUTPUT:
            return "FAIL", "the baseline reproduced the generated kernel prefix"
        return "PASS", "command succeeded without a tool and did not reproduce the kernel prefix"
    expected = KERNEL_EXPECTED_OUTPUT if case["kind"] == "kernel" else case["canary"]
    if actual != expected:
        return "FAIL", "the final output did not exactly match the fixed expectation"
    return "PASS", "the final output exactly matched the fixed expectation without a tool"


def _run_one_case(
    case: dict[str, Any],
    budget: CallBudget,
    invoker: Callable[[Path, str], subprocess.CompletedProcess[str]] = _invoke_codex,
) -> dict[str, Any]:
    temporary_path: Path | None = None
    result: dict[str, Any]
    try:
        with tempfile.TemporaryDirectory(prefix="egx-codex-probe-") as temporary_name:
            temporary_path = Path(temporary_name) / "fixture"
            cwd = build_fixture(temporary_path, case)
            before = _snapshot(temporary_path)
            validate_kernel_and_manifest()
            completed: subprocess.CompletedProcess[str] | None = None
            infrastructure_error: BaseException | None = None
            for attempt_index in range(2):
                budget.reserve()
                try:
                    completed = invoker(cwd, case["prompt"])
                    budget.record_exit(completed.returncode)
                    infrastructure_error = None
                    break
                except (OSError, subprocess.TimeoutExpired) as error:
                    infrastructure_error = error
                    if attempt_index == 0 and budget.allow_infrastructure_retry():
                        continue
                    break
            if completed is None:
                result = {
                    "exit_code": None,
                    "observed_output": "<NONE>",
                    "tool_call": False,
                    "tool_types": [],
                    "tokens": None,
                    "verdict": "BLOCKED",
                    "reason": f"infrastructure error: {type(infrastructure_error).__name__}",
                }
            else:
                try:
                    parsed = parse_json_events(completed.stdout)
                except ProbeError as error:
                    parsed = {
                        "final_output": "",
                        "tool_call": False,
                        "tool_types": [],
                        "tokens": None,
                    }
                    verdict, reason = "BLOCKED", str(error)
                else:
                    verdict, reason = _evaluate(case, parsed, completed.returncode)
                result = {
                    "exit_code": completed.returncode,
                    "observed_output": _safe_observed(case, parsed["final_output"]),
                    "tool_call": parsed["tool_call"],
                    "tool_types": parsed["tool_types"],
                    "tokens": parsed["tokens"],
                    "verdict": verdict,
                    "reason": reason,
                }
            result["workspace_unchanged"] = before == _snapshot(temporary_path)
            result["static_check_after"] = (
                _sync_check(temporary_path) if case["kind"] == "kernel" else None
            )
            if not result["workspace_unchanged"]:
                result["verdict"] = "FAIL"
                result["reason"] = "the disposable workspace changed during the Codex call"
            if case["kind"] == "kernel" and not result["static_check_after"]:
                result["verdict"] = "FAIL"
                result["reason"] = "the generated workspace failed its post-call static check"
    finally:
        cleaned = temporary_path is None or not temporary_path.parent.exists()

    result.update(
        {
            "case": case["id"],
            "objective": case["objective"],
            "fixture_shape": case["shape"],
            "command": normalized_command(),
            "codex_version": EXPECTED_CODEX_VERSION,
            "ephemeral_confirmed": True,
            "sandbox": "read-only",
            "expected_output": case["expected"],
            "fixture_cleaned": cleaned,
        }
    )
    return result


def _plan() -> dict[str, Any]:
    validate_kernel_and_manifest()
    cases = case_definitions(make_canaries())
    cleanup: list[bool] = []
    for case in cases:
        fixture: Path | None = None
        try:
            with tempfile.TemporaryDirectory(prefix="egx-codex-probe-plan-") as name:
                fixture = Path(name) / "fixture"
                build_fixture(fixture, case)
                if case["kind"] == "kernel" and not _sync_check(fixture):
                    raise ProbeError("generated plan fixture failed static verification")
        finally:
            cleanup.append(fixture is None or not fixture.parent.exists())
    return {
        "mode": "plan",
        "model_calls": 0,
        "attempts": 0,
        "temporary_only": True,
        "all_fixtures_cleaned": all(cleanup),
        "fixed_limits": {
            "successful_calls": MAX_SUCCESSFUL_CALLS,
            "attempts": MAX_ATTEMPTS,
            "infrastructure_retries": 1,
        },
        "cases": [
            {
                "case": case["id"],
                "objective": case["objective"],
                "fixture_shape": case["shape"],
                "command": normalized_command(),
            }
            for case in cases
        ],
    }


def _run_campaign() -> dict[str, Any]:
    validate_kernel_and_manifest()
    _codex_preflight()
    repository_before = _repository_snapshot()
    budget = CallBudget()
    results: list[dict[str, Any]] = []
    stopped_reason: str | None = None
    cases = case_definitions(make_canaries())
    for case in cases:
        result = _run_one_case(case, budget)
        results.append(result)
        if case["kind"] == "baseline" and result["verdict"] != "PASS":
            stopped_reason = "baseline did not pass"
            break
        if result["tool_call"]:
            stopped_reason = "tool or approval event detected"
            break
        if not result["workspace_unchanged"]:
            stopped_reason = "workspace mutation detected"
            break
        if result["verdict"] == "BLOCKED":
            stopped_reason = "runtime infrastructure was blocked"
            break

    total_tokens: dict[str, int] | None = None
    usages = [result["tokens"] for result in results]
    if usages and all(usage is not None for usage in usages):
        total_tokens = {
            key: sum(usage[key] for usage in usages if usage is not None)
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
                "total_tokens",
            )
        }
    return {
        "mode": "run",
        "codex_version": EXPECTED_CODEX_VERSION,
        "ephemeral_confirmed": True,
        "sandbox": "read-only",
        "successful_calls": budget.successful_calls,
        "attempts": budget.attempts,
        "retry_used": budget.retry_used,
        "stopped_reason": stopped_reason,
        "token_accounting_exposed_for_all_calls": total_tokens is not None,
        "campaign_tokens": total_tokens,
        "repository_unchanged_during_campaign": repository_before == _repository_snapshot(),
        "all_fixtures_cleaned": all(result["fixture_cleaned"] for result in results),
        "results": results,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely probe Codex CLI 0.144.6 instruction discovery."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="build and clean fixtures without invoking Codex")
    run = subparsers.add_parser("run", help="execute the fixed six-case model campaign")
    run.add_argument(
        "--acknowledge-model-calls",
        action="store_true",
        help="explicitly acknowledge the fixed model-call campaign",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "run" and not args.acknowledge_model_calls:
        print(
            "REFUSED: run requires --acknowledge-model-calls",
            file=sys.stderr,
        )
        return 2
    try:
        summary = _plan() if args.command == "plan" else _run_campaign()
    except (ProbeError, OSError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 3
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.command == "run" and (
        summary["stopped_reason"] is not None
        or len(summary["results"]) != MAX_SUCCESSFUL_CALLS
    ):
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
