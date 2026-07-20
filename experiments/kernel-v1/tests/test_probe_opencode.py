from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib import error, request


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


def sample_chat_payload(kernel_occurrences: int = 1, tools=None) -> dict:
    payload = {
        "model": PROBE.MOCK_MODEL,
        "messages": [
            {"role": "system", "content": PROBE.SYNC._load_source().decode("utf-8") * kernel_occurrences},
            {"role": "user", "content": PROBE.PROMPT},
        ],
        "stream": True,
        "temperature": 0,
    }
    if tools is not None:
        payload["tools"] = tools
    return payload


def valid_mock_observation() -> dict:
    generation = PROBE.inspect_chat_payload(
        sample_chat_payload(),
        PROBE.SYNC._load_source().decode("utf-8"),
    )
    return {
        "total_requests": 1,
        "generation_requests": 1,
        "requests": [{"method": "POST", "route": "/v1/chat/completions", "accepted": True}],
        "generations": [generation],
        "raw_payload_retained": False,
    }


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

    def test_30_stderr_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            raw = f"Error at {name} user={Path.home().name} token=private-value\x1b[31m"
            sanitized = PROBE.sanitize_stderr(raw, (name,))
        self.assertIn("<REDACTED_PATH>", sanitized)
        self.assertIn("<REDACTED_USER>", sanitized)
        self.assertIn("token=<REDACTED>", sanitized)
        self.assertNotIn("private-value", sanitized)
        self.assertNotIn("\x1b", sanitized)

    def test_31_empty_stderr_is_explicit(self) -> None:
        self.assertIsNone(PROBE.sanitize_stderr(""))
        self.assertIsNone(PROBE.classify_stderr(""))

    def test_32_native_binary_is_preferred_over_powershell_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            launcher = root / "opencode.ps1"
            binary = root / "node_modules" / "opencode-ai" / "bin" / "opencode.exe"
            binary.parent.mkdir(parents=True)
            launcher.write_text("launcher", encoding="utf-8")
            binary.write_bytes(b"binary")
            with mock.patch.object(PROBE.shutil, "which", return_value=str(launcher)):
                self.assertEqual(binary.resolve(), PROBE._opencode_binary())

    def test_33_windows_minimal_environment_keeps_only_required_parent_keys(self) -> None:
        parent = {
            "PATH": "safe-path",
            "SYSTEMROOT": "safe-root",
            "WINDIR": "safe-win",
            "COMSPEC": "safe-shell",
            "PATHEXT": ".EXE",
            "USERNAME": "must-not-survive",
            "OPENAI_API_KEY": "must-not-survive",
        }
        with tempfile.TemporaryDirectory() as name, mock.patch.dict(PROBE.os.environ, parent, clear=True):
            root = Path(name)
            env = PROBE.isolated_environment(root)
            PROBE.validate_isolated_environment(env, root)
        for key in ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"):
            self.assertEqual(parent[key], env[key])
        self.assertNotIn("USERNAME", env)
        self.assertNotIn("OPENAI_API_KEY", env)

    def test_34_cli_option_placement_and_fixed_title(self) -> None:
        command = PROBE.opencode_command(Path("opencode.exe"), Path("fixture"))
        self.assertEqual("run", command[1])
        self.assertLess(command.index("--pure"), command.index("--dir"))
        self.assertLess(command.index("--dir"), command.index("--model"))
        self.assertLess(command.index("--model"), command.index("--format"))
        self.assertLess(command.index("--format"), command.index("--title"))
        self.assertEqual(PROBE.PROMPT, command[-1])
        self.assertNotIn("--continue", command)

    def test_35_inline_configuration_matches_v1179_schema_surface(self) -> None:
        config = PROBE.build_config()
        PROBE.validate_config(config)
        self.assertNotIn("subagent_depth", config)
        encoded = json.dumps(config, separators=(",", ":"))
        self.assertEqual(config, json.loads(encoded))

    def test_36_pure_and_inline_configuration_are_both_applied(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            env = PROBE.isolated_environment(Path(name))
        command = PROBE.opencode_command(Path("opencode.exe"), Path("fixture"))
        self.assertIn("--pure", command)
        self.assertEqual(PROBE.build_config(), json.loads(env["OPENCODE_CONFIG_CONTENT"]))

    def test_37_mock_endpoint_rejects_non_loopback(self) -> None:
        for endpoint in (
            "http://0.0.0.0:12345/v1",
            "http://localhost:12345/v1",
            "https://127.0.0.1:12345/v1",
            "http://127.0.0.1:12345/other",
        ):
            with self.assertRaises(PROBE.ProbeError):
                PROBE.validate_mock_endpoint(endpoint)

    def test_38_mock_server_binds_dynamic_literal_loopback(self) -> None:
        server = PROBE.MockProviderServer(PROBE.SYNC._load_source().decode("utf-8"))
        try:
            server.start()
            self.assertRegex(server.endpoint, r"^http://127\.0\.0\.1:\d+/v1$")
        finally:
            server.stop()
        self.assertFalse(server.thread.is_alive())

    def test_39_mock_models_endpoint(self) -> None:
        server = PROBE.MockProviderServer(PROBE.SYNC._load_source().decode("utf-8"))
        try:
            server.start()
            with request.urlopen(server.endpoint + "/models", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.stop()
        self.assertEqual(PROBE.MOCK_MODEL, payload["data"][0]["id"])
        self.assertEqual(1, server.state.summary()["total_requests"])

    def test_40_mock_chat_endpoint_and_sse_response(self) -> None:
        kernel = PROBE.SYNC._load_source().decode("utf-8")
        server = PROBE.MockProviderServer(kernel)
        body = json.dumps(sample_chat_payload()).encode("utf-8")
        try:
            server.start()
            req = request.Request(
                server.endpoint + "/chat/completions",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=5) as response:
                events = PROBE.parse_sse_json(response.read())
        finally:
            server.stop()
        self.assertEqual(PROBE.MOCK_OUTPUT, events[0]["choices"][0]["delta"]["content"])
        self.assertEqual("stop", events[-1]["choices"][0]["finish_reason"])
        self.assertEqual(1, server.state.summary()["generation_requests"])

    def test_41_mock_jsonl_response_is_parsed(self) -> None:
        parsed = PROBE.parse_jsonl(sample_jsonl(PROBE.MOCK_OUTPUT, PROBE.MOCK_MODEL))
        self.assertEqual(PROBE.MOCK_OUTPUT, parsed["final_output"])

    def test_42_kernel_occurrence_is_counted_exactly(self) -> None:
        kernel = PROBE.SYNC._load_source().decode("utf-8")
        inspection = PROBE.inspect_chat_payload(sample_chat_payload(1), kernel)
        self.assertEqual(1, inspection["kernel_occurrences"])
        self.assertEqual(1, inspection["prompt_occurrences"])

    def test_43_zero_kernel_occurrence_is_detected(self) -> None:
        kernel = PROBE.SYNC._load_source().decode("utf-8")
        payload = sample_chat_payload(0)
        inspection = PROBE.inspect_chat_payload(payload, kernel)
        self.assertEqual(0, inspection["kernel_occurrences"])
        observed = valid_mock_observation()
        observed["generations"][0] = inspection
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_mock_observation(observed)

    def test_44_duplicate_kernel_occurrence_is_detected(self) -> None:
        kernel = PROBE.SYNC._load_source().decode("utf-8")
        inspection = PROBE.inspect_chat_payload(sample_chat_payload(2), kernel)
        self.assertEqual(2, inspection["kernel_occurrences"])
        observed = valid_mock_observation()
        observed["generations"][0] = inspection
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_mock_observation(observed)

    def test_45_tools_field_is_inspected(self) -> None:
        kernel = PROBE.SYNC._load_source().decode("utf-8")
        inspection = PROBE.inspect_chat_payload(sample_chat_payload(tools=[{"type": "function"}]), kernel)
        self.assertTrue(inspection["tools_field_present"])
        self.assertEqual(1, inspection["tool_count"])
        observed = valid_mock_observation()
        observed["generations"][0] = inspection
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_mock_observation(observed)

    def test_46_additional_request_is_detected(self) -> None:
        observed = valid_mock_observation()
        observed["total_requests"] = 2
        observed["requests"].append({"method": "GET", "route": "/v1/models"})
        with self.assertRaises(PROBE.ProbeError):
            PROBE.validate_mock_observation(observed)

    def test_47_mock_configuration_is_inline_and_exclusive(self) -> None:
        endpoint = "http://127.0.0.1:12345/v1"
        config = PROBE.build_mock_config(endpoint)
        PROBE.validate_mock_config(config, endpoint)
        with tempfile.TemporaryDirectory() as name:
            env = PROBE.isolated_environment(Path(name), config, mock_endpoint=endpoint)
        self.assertEqual(config, json.loads(env["OPENCODE_CONFIG_CONTENT"]))
        self.assertEqual([PROBE.MOCK_PROVIDER], config["enabled_providers"])

    def test_48_mock_cleanup_after_handler_error(self) -> None:
        server = PROBE.MockProviderServer(PROBE.SYNC._load_source().decode("utf-8"))
        try:
            server.start()
            req = request.Request(
                server.endpoint + "/chat/completions",
                data=b"not-json",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(error.HTTPError):
                request.urlopen(req, timeout=5)
        finally:
            server.stop()
        self.assertFalse(server.thread.is_alive())
        self.assertEqual(0, server.state.summary()["generation_requests"])

    def test_49_diagnostic_preflight_never_starts_ollama_or_a_model(self) -> None:
        with mock.patch.object(PROBE, "validate_opencode_install", return_value={}), mock.patch.object(
            PROBE, "opencode_processes", return_value=[]
        ), mock.patch.object(PROBE.OLLAMA, "ollama_processes", return_value=[]), mock.patch.object(
            PROBE.OLLAMA, "_loopback_responds", return_value=False
        ), mock.patch.object(PROBE.OLLAMA, "_port_is_free", return_value=True), mock.patch.object(
            PROBE.OLLAMA, "ServerSession", side_effect=AssertionError("Ollama must not start")
        ):
            result = PROBE._diagnostic_preflight()
        self.assertTrue(result["port_11434_free"])

    def test_50_27b_profile_builds_exact_local_configuration(self) -> None:
        try:
            profile = PROBE.activate_profile("qwen3.6-27b-q4km")
            config = PROBE.build_config()
            self.assertEqual("qwen3.6:27b", PROBE.MODEL)
            self.assertEqual(
                "local-ollama/qwen3.6:27b",
                config["model"],
            )
            self.assertEqual(
                16_384,
                config["provider"][PROBE.PROVIDER]["models"][PROBE.MODEL]["limit"]["context"],
            )
            self.assertEqual("dense", profile["architecture_type"])
        finally:
            PROBE.activate_profile()

    def test_51_27b_loaded_resource_gate_uses_measured_three_gib(self) -> None:
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            snapshot = {
                "ram": {"available_bytes": PROBE.MIN_OPENCODE_AVAILABLE_RAM_BYTES},
                "gpu": {"available_mib": 3_072},
            }
            gate = PROBE.guard_loaded_resources(snapshot)
            self.assertEqual(4_294_967_296, gate["requested_gpu_overhead_bytes"])
            self.assertEqual(3_072, gate["observed_available_vram_mib"])
            self.assertEqual(0, gate["vram_margin_above_minimum_mib"])
            self.assertTrue(gate["passed"])
            snapshot["gpu"]["available_mib"] -= 1
            failed_gate = PROBE.loaded_resource_gate(snapshot)
            self.assertFalse(failed_gate["passed"])
            self.assertEqual(3_071, failed_gate["observed_available_vram_mib"])
            with self.assertRaises(PROBE.ProbeError):
                PROBE.guard_loaded_resources(snapshot)
            snapshot["gpu"]["available_mib"] = 3_072
            snapshot["ram"]["available_bytes"] -= 1
            with self.assertRaises(PROBE.ProbeError):
                PROBE.guard_loaded_resources(snapshot)
        finally:
            PROBE.activate_profile()

    def test_52_opencode_child_does_not_receive_ollama_gpu_overhead(self) -> None:
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            with tempfile.TemporaryDirectory() as name, mock.patch.dict(
                PROBE.os.environ,
                {"PATH": "safe", "OLLAMA_GPU_OVERHEAD": "parent-value"},
                clear=True,
            ):
                parent_before = dict(PROBE.os.environ)
                env = PROBE.isolated_environment(Path(name))
                self.assertNotIn("OLLAMA_GPU_OVERHEAD", env)
                self.assertEqual(parent_before, dict(PROBE.os.environ))
        finally:
            PROBE.activate_profile()

    def test_53_plan_exposes_reserved_vram_policy(self) -> None:
        static = {"kernel_sha256": "a", "opencode": {}, "model": "qwen3.6:27b"}
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            with mock.patch.object(PROBE, "_static_plan_checks", return_value=static):
                plan = PROBE._plan()
            self.assertEqual(4_294_967_296, plan["allocation_policy"]["gpu_overhead_bytes"])
            self.assertEqual(3_072, plan["allocation_policy"]["minimum_free_vram_mib"])
            self.assertEqual(16_384, plan["allocation_policy"]["context_length"])
        finally:
            PROBE.activate_profile()

    def test_54_offload_layer_split_is_parsed_when_exposed(self) -> None:
        parsed = PROBE.parse_offload_layers('msg="offloaded 58/65 layers to GPU"')
        self.assertEqual(58, parsed["gpu_layers"])
        self.assertEqual(7, parsed["cpu_layers"])
        self.assertTrue(parsed["exposed"])


if __name__ == "__main__":
    unittest.main()
