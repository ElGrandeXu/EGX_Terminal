from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / "experiments" / "kernel-v1" / "tools" / "probe_codex.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("testable_probe_codex", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROBE = load_probe()


def jsonl(final: str = "OK", item_type: str = "agent_message", usage: bool = True) -> str:
    events = [
        {"type": "thread.started", "thread_id": "temporary"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": item_type, "text": final}},
    ]
    if usage:
        events.append(
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 20,
                    "cached_input_tokens": 5,
                    "output_tokens": 3,
                },
            }
        )
    return "\n".join(json.dumps(event) for event in events) + "\n"


class ProbeCodexTests(unittest.TestCase):
    def test_version_validation_accepts_only_exact_version(self) -> None:
        PROBE.validate_codex_version("codex-cli 0.144.6\n")
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_codex_version("codex-cli 0.144.7\n")

    def test_kernel_and_manifest_validation(self) -> None:
        source = PROBE.validate_kernel_and_manifest()
        self.assertEqual(PROBE.KERNEL_EXPECTED_OUTPUT, " ".join(source.decode().split()[:8]))
        with mock.patch.object(PROBE.SYNC, "_load_source", side_effect=PROBE.SYNC.CheckError("drift")):
            with self.assertRaises(PROBE.ProbeError):
                PROBE.validate_kernel_and_manifest()

    def test_call_ceiling(self) -> None:
        budget = PROBE.CallBudget()
        for _ in range(PROBE.MAX_SUCCESSFUL_CALLS):
            budget.reserve()
            budget.record_exit(0)
        with self.assertRaises(PROBE.BudgetError):
            budget.reserve()

        retry_budget = PROBE.CallBudget()
        for _ in range(PROBE.MAX_ATTEMPTS):
            retry_budget.reserve()
        with self.assertRaises(PROBE.BudgetError):
            retry_budget.reserve()

    def test_run_requires_acknowledgement(self) -> None:
        stderr = io.StringIO()
        with mock.patch.object(PROBE, "_run_campaign") as campaign:
            with contextlib.redirect_stderr(stderr):
                result = PROBE.main(["run"])
        self.assertEqual(2, result)
        campaign.assert_not_called()

    def test_fixture_is_created_outside_repository_and_cleaned(self) -> None:
        case = PROBE.case_definitions(PROBE.make_canaries())[0]
        with tempfile.TemporaryDirectory(prefix="egx-probe-test-") as name:
            root = Path(name) / "fixture"
            PROBE.build_fixture(root, case)
            with self.assertRaises(ValueError):
                root.relative_to(REPOSITORY)
            self.assertTrue((root / ".git").is_dir())
        self.assertFalse(root.exists())

    def test_refuses_repository_root_and_descendants(self) -> None:
        with self.assertRaises(PROBE.ProbeError):
            PROBE.refuse_repository_root(REPOSITORY)
        with self.assertRaises(PROBE.ProbeError):
            PROBE.refuse_repository_root(REPOSITORY / "nested")

    def test_case_construction(self) -> None:
        cases = PROBE.case_definitions(PROBE.make_canaries())
        self.assertEqual(6, len(cases))
        self.assertEqual(
            ["baseline", "root", "kernel", "kernel", "nested", "override"],
            [case["kind"] for case in cases],
        )
        with tempfile.TemporaryDirectory(prefix="egx-probe-cases-") as name:
            base = Path(name)
            for index, case in enumerate(cases):
                root = base / str(index)
                cwd = PROBE.build_fixture(root, case)
                self.assertTrue((root / ".git").is_dir())
                if case["kind"] == "nested":
                    self.assertEqual(root / "child", cwd)
                if case["kind"] == "kernel":
                    self.assertTrue(PROBE._sync_check(root))

    def test_parses_simulated_events_and_tokens(self) -> None:
        parsed = PROBE.parse_json_events(jsonl("EXPECTED"))
        self.assertEqual("EXPECTED", parsed["final_output"])
        self.assertFalse(parsed["tool_call"])
        self.assertEqual(
            {
                "input_tokens": 20,
                "cached_input_tokens": 5,
                "output_tokens": 3,
                "total_tokens": 23,
            },
            parsed["tokens"],
        )

    def test_detects_simulated_tool_call(self) -> None:
        parsed = PROBE.parse_json_events(jsonl("", item_type="command_execution"))
        self.assertTrue(parsed["tool_call"])
        self.assertEqual(["command_execution"], parsed["tool_types"])

    def test_token_metrics_can_be_absent(self) -> None:
        parsed = PROBE.parse_json_events(jsonl(usage=False))
        self.assertIsNone(parsed["tokens"])

    def test_no_raw_transcript_persists_and_cleanup_follows_success(self) -> None:
        case = PROBE.case_definitions(PROBE.make_canaries())[0]
        before = PROBE._repository_snapshot()
        fake = subprocess.CompletedProcess([], 0, jsonl("NO_PROJECT_DOCTRINE"), "")
        result = PROBE._run_one_case(case, PROBE.CallBudget(), lambda _cwd, _prompt: fake)
        self.assertTrue(result["fixture_cleaned"])
        self.assertEqual("<NON_KERNEL_RESPONSE_REDACTED>", result["observed_output"])
        self.assertEqual(before, PROBE._repository_snapshot())
        self.assertNotIn("NO_PROJECT_DOCTRINE", json.dumps(result))

    def test_cleanup_follows_runtime_error(self) -> None:
        case = PROBE.case_definitions(PROBE.make_canaries())[0]

        def fail(_cwd, _prompt):
            raise OSError("simulated infrastructure failure")

        result = PROBE._run_one_case(case, PROBE.CallBudget(), fail)
        self.assertTrue(result["fixture_cleaned"])
        self.assertEqual("BLOCKED", result["verdict"])

    def test_plan_never_invokes_codex_subprocess(self) -> None:
        with mock.patch.object(PROBE, "_invoke_codex", side_effect=AssertionError("model call")):
            summary = PROBE._plan()
        self.assertEqual(0, summary["model_calls"])
        self.assertEqual(0, summary["attempts"])
        self.assertTrue(summary["all_fixtures_cleaned"])

    def test_preflight_refuses_missing_ephemeral_or_read_only(self) -> None:
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_exec_help("--json --cd <DIR> --sandbox <SANDBOX_MODE>")
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_exec_help("--json --cd <DIR> --ephemeral")

    def test_command_is_fixed_to_ephemeral_read_only_json(self) -> None:
        command = PROBE._codex_command(Path("fixture"), "prompt")
        self.assertIn("--ephemeral", command)
        self.assertIn("read-only", command)
        self.assertIn("--json", command)
        self.assertNotIn("workspace-write", command)
        self.assertNotIn("danger-full-access", command)

    def test_missing_codex_executable_is_blocking(self) -> None:
        with mock.patch.object(PROBE.shutil, "which", return_value=None):
            with self.assertRaises(PROBE.ProbeError):
                PROBE._codex_executable()


if __name__ == "__main__":
    unittest.main()
