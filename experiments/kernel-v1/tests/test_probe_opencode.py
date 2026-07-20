from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / "experiments" / "kernel-v1" / "tools" / "probe_opencode.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("testable_probe_opencode", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROBE = load_probe()


def sample_jsonl(output: str = PROBE.EXPECTED_OUTPUT, model: str = PROBE.MODEL) -> str:
    events = [
        {
            "type": "step_start",
            "part": {
                "type": "step-start",
                "providerID": PROBE.PROVIDER,
                "modelID": model,
            },
        },
        {"type": "text", "part": {"type": "text", "text": output}},
        {
            "type": "step_finish",
            "part": {"type": "step-finish", "tokens": {"input": 100, "output": 12}},
        },
    ]
    return "\n".join(json.dumps(event) for event in events)


class ProbeOpenCodeTests(unittest.TestCase):
    def test_01_plan_starts_no_process(self) -> None:
        static = {"kernel_sha256": "a", "opencode": {}, "model": PROBE.MODEL}
        with mock.patch.object(PROBE, "_static_plan_checks", return_value=static), mock.patch.object(
            PROBE.subprocess, "Popen", side_effect=AssertionError("process")
        ), mock.patch.object(PROBE.subprocess, "run", side_effect=AssertionError("process")):
            summary = PROBE._plan()
        self.assertEqual(0, summary["processes_started"])
        self.assertEqual(0, summary["model_requests"])

    def test_02_acknowledgement_is_mandatory(self) -> None:
        stderr = io.StringIO()
        with mock.patch.object(PROBE, "_run") as run, contextlib.redirect_stderr(stderr):
            code = PROBE.main(["run"])
        self.assertEqual(2, code)
        run.assert_not_called()

    def test_03_opencode_version_is_locked(self) -> None:
        self.assertEqual("1.17.9", PROBE.EXPECTED_OPENCODE_VERSION)
        self.assertEqual(165_154_696, PROBE.EXPECTED_OPENCODE_BINARY_BYTES)
        self.assertEqual(64, len(PROBE.EXPECTED_OPENCODE_BINARY_SHA256))

    def test_04_model_and_digest_are_locked(self) -> None:
        self.assertEqual("qwen3.6:35b", PROBE.MODEL)
        self.assertEqual(
            "sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d",
            PROBE.EXPECTED_DIGEST,
        )

    def test_05_endpoint_is_locked_to_loopback(self) -> None:
        self.assertEqual("http://127.0.0.1:11434/v1", PROBE.validate_endpoint(PROBE.OPENAI_BASE_URL))

    def test_06_context_is_locked(self) -> None:
        config = PROBE.build_config()
        limit = config["provider"][PROBE.PROVIDER]["models"][PROBE.MODEL]["limit"]
        self.assertEqual(16_384, limit["context"])

    def test_07_single_inference_budget(self) -> None:
        budget = PROBE.InferenceBudget()
        budget.reserve_process()
        with self.assertRaises(PROBE.ProbeError):
            budget.reserve_process()
        budget.record_requests(1)
        self.assertEqual(1, budget.processes)
        self.assertEqual(1, budget.requests)
        with self.assertRaises(PROBE.ProbeError):
            budget.record_requests(1)

    def test_08_no_retry(self) -> None:
        self.assertEqual(0, PROBE.MAX_RETRIES)
        static = {"kernel_sha256": "a", "opencode": {}, "model": PROBE.MODEL}
        with mock.patch.object(PROBE, "_static_plan_checks", return_value=static):
            self.assertEqual(0, PROBE._plan()["inference_retries"])

    def test_09_environment_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            env = PROBE.isolated_environment(root)
            PROBE.validate_isolated_environment(env, root)
            for key in PROBE.REQUIRED_ISOLATION_KEYS:
                self.assertIn(key, env)

    def test_10_global_configuration_is_not_inherited(self) -> None:
        with tempfile.TemporaryDirectory() as name, mock.patch.dict(
            PROBE.os.environ,
            {"OPENAI_API_KEY": "forbidden", "OPENCODE_CONFIG": "global", "PATH": "safe"},
            clear=True,
        ):
            env = PROBE.isolated_environment(Path(name))
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("OPENCODE_CONFIG", env)
        self.assertEqual(":memory:", env["OPENCODE_DB"])

    def test_11_provider_allowlist_is_exclusive(self) -> None:
        config = PROBE.build_config()
        self.assertEqual([PROBE.PROVIDER], config["enabled_providers"])
        self.assertEqual({PROBE.PROVIDER}, set(config["provider"]))

    def test_12_tools_are_denied(self) -> None:
        config = PROBE.build_config()
        self.assertEqual({"*": "deny"}, config["permission"])
        with tempfile.TemporaryDirectory() as name:
            env = PROBE.isolated_environment(Path(name), config)
        self.assertEqual('{"*":"deny"}', env["OPENCODE_PERMISSION"])

    def test_13_plugins_are_disabled(self) -> None:
        config = PROBE.build_config()
        self.assertEqual([], config["plugin"])
        with tempfile.TemporaryDirectory() as name:
            env = PROBE.isolated_environment(Path(name), config)
        self.assertEqual("1", env["OPENCODE_DISABLE_DEFAULT_PLUGINS"])
        self.assertEqual("1", env["OPENCODE_DISABLE_EXTERNAL_SKILLS"])

    def test_14_update_telemetry_fetch_and_lsp_are_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            env = PROBE.isolated_environment(Path(name))
        self.assertEqual("1", env["OPENCODE_DISABLE_AUTOUPDATE"])
        self.assertEqual("1", env["OPENCODE_DISABLE_MODELS_FETCH"])
        self.assertEqual("1", env["OPENCODE_DISABLE_LSP_DOWNLOAD"])
        self.assertEqual("true", env["OTEL_SDK_DISABLED"])
        self.assertFalse(PROBE.build_config()["autoupdate"])

    def test_15_remote_provider_is_refused(self) -> None:
        with self.assertRaises(PROBE.ProbeError):
            PROBE.build_config(provider="openai")

    def test_16_non_loopback_endpoint_is_refused(self) -> None:
        for endpoint in (
            "https://api.openai.com/v1",
            "http://localhost:11434/v1",
            "http://0.0.0.0:11434/v1",
            "http://127.0.0.1:1234/v1",
        ):
            with self.assertRaises(PROBE.ProbeError):
                PROBE.validate_endpoint(endpoint)

    def test_17_jsonl_parsing(self) -> None:
        parsed = PROBE.parse_jsonl(sample_jsonl())
        self.assertEqual(PROBE.EXPECTED_OUTPUT, parsed["final_output"])
        self.assertEqual({"input": 100, "output": 12}, parsed["tokens"])
        self.assertEqual([PROBE.PROVIDER], parsed["providers"])

    def test_18_final_response_extraction_is_exact(self) -> None:
        parsed = PROBE.parse_jsonl(sample_jsonl(" exact "))
        self.assertEqual(" exact ", parsed["final_output"])

    def test_19_tool_call_is_detected(self) -> None:
        raw = json.dumps({"type": "tool_use", "part": {"type": "tool", "name": "read"}})
        parsed = PROBE.parse_jsonl(raw)
        self.assertTrue(parsed["tool_call"])
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_parsed_events(parsed)

    def test_20_permission_request_is_detected(self) -> None:
        parsed = PROBE.parse_jsonl(json.dumps({"type": "permission", "permission": "read"}))
        self.assertTrue(parsed["permission_request"])
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_parsed_events(parsed)

    def test_21_unexpected_model_is_detected(self) -> None:
        parsed = PROBE.parse_jsonl(sample_jsonl(model="other"))
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_parsed_events(parsed)

    def test_22_multiple_model_requests_are_detected(self) -> None:
        log = 'POST     "/v1/chat/completions"\nPOST "/v1/chat/completions"\n'
        self.assertEqual(2, PROBE.count_model_requests(log))
        with self.assertRaises(PROBE.ProbeError):
            PROBE.InferenceBudget().record_requests(2)

    def test_23_non_loopback_connection_is_detected(self) -> None:
        evaluated = PROBE.evaluate_connections(
            [
                {"remote_address": "127.0.0.1", "remote_port": 11434, "state": "Established"},
                {"remote_address": "203.0.113.7", "remote_port": 443, "state": "SynSent"},
            ]
        )
        self.assertTrue(evaluated["non_loopback_detected"])
        self.assertIn("<NON_LOOPBACK_REDACTED>", "".join(evaluated["non_loopback"]))
        self.assertNotIn("203.0.113.7", json.dumps(evaluated))

    def test_24_exact_output_rejects_approximations(self) -> None:
        self.assertTrue(PROBE.exact_output_matches(PROBE.EXPECTED_OUTPUT))
        for output in (PROBE.EXPECTED_OUTPUT + ".", " " + PROBE.EXPECTED_OUTPUT, PROBE.EXPECTED_OUTPUT + "\n"):
            self.assertFalse(PROBE.exact_output_matches(output))

    def test_25_workspace_snapshot_and_static_identity(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            workspace = Path(name) / "workspace"
            PROBE._sync_write(workspace)
            evidence = PROBE.validate_workspace(workspace)
            before = PROBE.snapshot_tree(workspace)
            after = PROBE.snapshot_tree(workspace)
        self.assertEqual(before, after)
        self.assertTrue(evidence["agents_identical_to_canonical"])
        self.assertTrue(evidence["opencode_json_absent"])

    def test_26_cleanup_after_success(self) -> None:
        class Session:
            def __init__(self):
                self.cleaned = 0

            def start(self):
                return None

            def cleanup(self):
                self.cleaned += 1
                return {"success": True}

        session = Session()
        value, cleanup = PROBE.execute_with_cleanup(session, lambda: "ok")
        self.assertEqual("ok", value)
        self.assertTrue(cleanup["success"])
        self.assertEqual(1, session.cleaned)

    def test_27_cleanup_after_error(self) -> None:
        class Session:
            def __init__(self):
                self.cleaned = 0

            def start(self):
                return None

            def cleanup(self):
                self.cleaned += 1
                return {"success": True}

        session = Session()
        with self.assertRaises(RuntimeError):
            PROBE.execute_with_cleanup(session, lambda: (_ for _ in ()).throw(RuntimeError("x")))
        self.assertEqual(1, session.cleaned)

    def test_28_refuses_to_kill_unowned_process(self) -> None:
        with self.assertRaises(PROBE.OLLAMA.ProbeError):
            PROBE.terminate_owned_opencode_pid(12345, {54321})

    def test_29_no_transcript_is_persisted(self) -> None:
        sanitized = PROBE.sanitize_summary(
            {"raw_jsonl": "private", "transcript": "private", "sessionID": "private", "final_output": "ok"}
        )
        serialized = json.dumps(sanitized)
        self.assertNotIn("private", serialized)
        self.assertEqual("ok", sanitized["final_output"])


if __name__ == "__main__":
    unittest.main()
