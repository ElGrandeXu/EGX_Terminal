from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / "experiments" / "kernel-v1" / "tools" / "probe_ollama.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("testable_probe_ollama", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROBE = load_probe()


def make_model_store(root: Path, digest: str = PROBE.EXPECTED_DIGEST) -> str:
    config = {
        "model_format": "gguf",
        "model_family": "qwen35moe",
        "model_families": ["qwen35moe"],
        "model_type": "36.0B",
        "file_type": "Q4_K_M",
    }
    config_raw = json.dumps(config).encode()
    config_digest = "sha256:" + "a" * 64
    model_raw = b"model"
    params_raw = b"params"
    license_raw = b"Apache License\nVersion 2.0, January 2004\n"
    entries = [
        {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "digest": config_digest,
            "size": len(config_raw),
        },
        {
            "mediaType": PROBE.MODEL_MEDIA_TYPE,
            "digest": digest,
            "size": len(model_raw),
        },
        {
            "mediaType": "application/vnd.ollama.image.params",
            "digest": "sha256:" + "b" * 64,
            "size": len(params_raw),
        },
        {
            "mediaType": PROBE.LICENSE_MEDIA_TYPE,
            "digest": "sha256:" + "c" * 64,
            "size": len(license_raw),
        },
    ]
    manifest = {"schemaVersion": 2, "config": entries[0], "layers": entries[1:]}
    manifest_path = root / "manifests" / "registry.ollama.ai" / "library" / "qwen3.6" / "35b"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    blobs = root / "blobs"
    blobs.mkdir()
    (blobs / ("sha256-" + "a" * 64)).write_bytes(config_raw)
    (blobs / ("sha256-" + digest.removeprefix("sha256:"))).write_bytes(model_raw)
    (blobs / ("sha256-" + "b" * 64)).write_bytes(params_raw)
    (blobs / ("sha256-" + "c" * 64)).write_bytes(license_raw)
    return "sha256:" + hashlib.sha256(manifest_path.read_bytes()).hexdigest()


class ProbeOllamaTests(unittest.TestCase):
    def test_plan_starts_no_server_or_subprocess(self) -> None:
        with mock.patch.object(PROBE.subprocess, "Popen", side_effect=AssertionError("server")):
            summary = PROBE._plan()
        self.assertEqual(0, summary["processes_started"])
        self.assertEqual(0, summary["model_loads"])
        self.assertEqual(0, summary["inference_calls"])

    def test_acknowledgement_is_required(self) -> None:
        stderr = io.StringIO()
        with mock.patch.object(PROBE, "_run") as run:
            with contextlib.redirect_stderr(stderr):
                code = PROBE.main(["run"])
        self.assertEqual(2, code)
        run.assert_not_called()

    def test_model_and_endpoint_are_locked(self) -> None:
        parser = PROBE._parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["run", "--model", "other"])
        self.assertEqual("qwen3.6:35b", PROBE.MODEL)
        self.assertEqual("http://127.0.0.1:11434", PROBE.BASE_URL)

    def test_non_loopback_endpoint_is_refused(self) -> None:
        for url in (
            "http://localhost:11434",
            "http://0.0.0.0:11434",
            "https://127.0.0.1:11434",
            "http://127.0.0.1:1234",
            "https://ollama.com/api",
        ):
            with self.assertRaises(PROBE.ProbeError):
                PROBE.validate_endpoint(url)

    def test_preexisting_server_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            session = PROBE.ServerSession("ollama", Path(name), Path(name))
            with mock.patch.object(PROBE, "_loopback_responds", return_value=True):
                with self.assertRaises(PROBE.ProbeError):
                    session.start()

    def test_listener_must_be_owned_and_exactly_loopback(self) -> None:
        PROBE.require_owned_loopback_listener(
            [{"local_address": PROBE.HOST, "local_port": PROBE.PORT, "owning_pid": 42}],
            {42},
        )
        with self.assertRaises(PROBE.ProbeError):
            PROBE.require_owned_loopback_listener(
                [{"local_address": "0.0.0.0", "local_port": PROBE.PORT, "owning_pid": 42}],
                {42},
            )
        with self.assertRaises(PROBE.ProbeError):
            PROBE.require_owned_loopback_listener(
                [{"local_address": PROBE.HOST, "local_port": PROBE.PORT, "owning_pid": 99}],
                {42},
            )

    def test_digest_and_all_blobs_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            manifest_digest = make_model_store(root)
            with mock.patch.dict(
                PROBE.ACTIVE_PROFILE,
                {"declared_size_bytes": len(b"model"), "manifest_digest": manifest_digest},
            ):
                identity = PROBE.validate_local_model(root)
            self.assertEqual(PROBE.EXPECTED_DIGEST, identity["declared_digest"])
            self.assertTrue(identity["manifest_digest"].startswith("sha256:"))
            self.assertTrue(identity["all_required_blobs_present"])
            self.assertEqual(PROBE.model_store_snapshot(root), PROBE.model_store_snapshot(root))
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            make_model_store(root, "sha256:" + "c" * 64)
            with self.assertRaises(PROBE.ProbeError):
                PROBE.validate_local_model(root)

    def test_profile_registry_contains_exact_historical_and_new_profiles(self) -> None:
        profiles = PROBE.load_model_profiles()
        self.assertEqual(PROBE.REQUIRED_PROFILE_IDS, set(profiles))
        self.assertEqual("qwen3.6:35b", profiles[PROBE.DEFAULT_PROFILE_ID]["ollama_model"])
        self.assertEqual("qwen35moe", profiles[PROBE.DEFAULT_PROFILE_ID]["architecture"])
        self.assertEqual("3.0B", profiles[PROBE.DEFAULT_PROFILE_ID]["parameters_active"])
        self.assertEqual("qwen3.6:27b", profiles["qwen3.6-27b-q4km"]["ollama_model"])
        self.assertEqual("dense", profiles["qwen3.6-27b-q4km"]["architecture_type"])
        self.assertEqual(4_294_967_296, profiles["qwen3.6-27b-q4km"]["gpu_overhead_bytes"])

    def test_27b_allocation_policy_is_read_exactly(self) -> None:
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            self.assertEqual(
                {
                    "gpu_overhead_bytes": 4_294_967_296,
                    "gpu_overhead_gib": 4,
                    "minimum_free_vram_mib": 3_072,
                    "context_length": 16_384,
                    "num_parallel": 1,
                },
                PROBE.allocation_policy(),
            )
        finally:
            PROBE.activate_profile()

    def test_invalid_gpu_overhead_values_are_rejected(self) -> None:
        registry = json.loads(PROBE.PROFILE_PATH.read_text(encoding="utf-8"))
        invalid = (-1, "4294967296", PROBE.MAX_REASONABLE_GPU_OVERHEAD_BYTES + 1)
        for value in invalid:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as name:
                candidate = json.loads(json.dumps(registry))
                candidate["profiles"][PROBE.GPU_OVERHEAD_PROFILE_ID]["gpu_overhead_bytes"] = value
                path = Path(name) / "profiles.json"
                path.write_text(json.dumps(candidate), encoding="utf-8")
                with self.assertRaises(PROBE.ProbeError):
                    PROBE.load_model_profiles(path)

    def test_historical_35b_profile_is_byte_for_byte_semantically_unchanged(self) -> None:
        profile = PROBE.load_model_profiles()[PROBE.DEFAULT_PROFILE_ID]
        canonical = json.dumps(profile, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(
            "d237648b45051b9552e0427173ad91b213bb5a3fbeb4f4296cfb6fd61a84c657",
            hashlib.sha256(canonical).hexdigest(),
        )
        self.assertTrue(PROBE.ALLOCATION_POLICY_FIELDS.isdisjoint(profile))

    def test_gpu_overhead_is_scoped_to_child_server_environment(self) -> None:
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            with tempfile.TemporaryDirectory() as name, mock.patch.dict(
                PROBE.os.environ,
                {"PATH": "safe", "OLLAMA_GPU_OVERHEAD": "parent-value"},
                clear=True,
            ):
                parent_before = dict(PROBE.os.environ)
                session = PROBE.ServerSession("ollama", Path(name), Path(name))
                self.assertEqual("4294967296", session.environment["OLLAMA_GPU_OVERHEAD"])
                self.assertEqual(parent_before, dict(PROBE.os.environ))
        finally:
            PROBE.activate_profile()

    def test_35b_server_does_not_inherit_global_gpu_overhead(self) -> None:
        PROBE.activate_profile()
        with tempfile.TemporaryDirectory() as name, mock.patch.dict(
            PROBE.os.environ,
            {"PATH": "safe", "OLLAMA_GPU_OVERHEAD": "parent-value"},
            clear=True,
        ):
            env = PROBE._server_environment(Path(name))
        self.assertNotIn("OLLAMA_GPU_OVERHEAD", env)

    def test_profile_selection_preserves_historical_default(self) -> None:
        try:
            selected = PROBE.activate_profile("qwen3.6-27b-q4km")
            self.assertEqual("qwen3.6:27b", PROBE.MODEL)
            self.assertEqual(16_384, PROBE.CONTEXT_TOKENS)
            self.assertEqual(selected["parameters_total"], selected["parameters_active"])
        finally:
            PROBE.activate_profile()
        self.assertEqual("qwen3.6:35b", PROBE.MODEL)

    def test_plan_exposes_effective_allocation_policy(self) -> None:
        try:
            PROBE.activate_profile("qwen3.6-27b-q4km")
            policy = PROBE._plan()["allocation_policy"]
            self.assertEqual(4_294_967_296, policy["gpu_overhead_bytes"])
            self.assertEqual(3_072, policy["minimum_free_vram_mib"])
        finally:
            PROBE.activate_profile()

    def test_only_one_inference_and_no_retry(self) -> None:
        budget = PROBE.InferenceBudget()
        budget.reserve()
        self.assertEqual(1, budget.calls)
        with self.assertRaises(PROBE.ProbeError):
            budget.reserve()
        self.assertEqual(0, PROBE._plan()["fixed_budget"]["inference_retries"])

    def test_ram_guard(self) -> None:
        PROBE.guard_ram({"ram": {"available_bytes": PROBE.MIN_AVAILABLE_RAM}})
        with self.assertRaises(PROBE.ProbeError):
            PROBE.guard_ram({"ram": {"available_bytes": PROBE.MIN_AVAILABLE_RAM - 1}})

    def test_metadata_parsing(self) -> None:
        parsed = PROBE.parse_show(
            {
                "details": {
                    "format": "gguf",
                    "family": "qwen35moe",
                    "families": ["qwen35moe"],
                    "parameter_size": "36.0B",
                    "quantization_level": "Q4_K_M",
                },
                "model_info": {"qwen35moe.context_length": 262144},
                "capabilities": ["completion", "tools", "thinking"],
                "template": "private template",
                "parameters": "temperature 0.6",
            }
        )
        self.assertEqual(262144, parsed["maximum_context_tokens"])
        self.assertEqual(16, parsed["template_characters"])
        self.assertNotIn("private template", json.dumps(parsed))

    def test_metrics_parsing_and_tokens_per_second(self) -> None:
        parsed = PROBE.parse_metrics(
            {
                "done": True,
                "done_reason": "stop",
                "total_duration": 4_000_000_000,
                "load_duration": 10,
                "prompt_eval_count": 8,
                "prompt_eval_duration": 1_000_000_000,
                "eval_count": 16,
                "eval_duration": 2_000_000_000,
            },
            4.1,
        )
        self.assertEqual(8.0, parsed["tokens_per_second"])
        self.assertEqual("stop", parsed["done_reason"])

    def test_wddm_process_memory_can_be_unavailable(self) -> None:
        completed = PROBE.subprocess.CompletedProcess(
            [], 0, "42, ollama_llama_server.exe, [N/A]\n", ""
        )
        gpu = PROBE.subprocess.CompletedProcess([], 0, "GPU, 24564, 1000, 23564\n", "")
        with mock.patch.object(PROBE.shutil, "which", return_value="nvidia-smi"), mock.patch.object(
            PROBE, "_run_text", side_effect=[gpu, completed]
        ):
            snapshot = PROBE.gpu_snapshot()
        self.assertIsNone(snapshot["relevant_compute_processes"][0]["used_mib"])

    def test_context_difference_is_detected(self) -> None:
        running = [
            {
                "name": PROBE.MODEL,
                "digest": PROBE.EXPECTED_DIGEST.removeprefix("sha256:"),
                "size_bytes": 10,
                "size_vram_bytes": 8,
                "size_cpu_bytes": 2,
                "context_length": PROBE.CONTEXT_TOKENS - 1,
                "gpu_percent": 80.0,
                "cpu_percent": 20.0,
            }
        ]
        with self.assertRaises(PROBE.ProbeError):
            PROBE.require_context(running)

    def test_already_loaded_model_is_detected(self) -> None:
        PROBE.require_no_loaded_model({"models": []})
        with self.assertRaises(PROBE.ProbeError):
            PROBE.require_no_loaded_model({"models": [{"name": PROBE.MODEL}]})

    def test_cleanup_after_success_and_error_is_simulated(self) -> None:
        class FakeSession:
            def __init__(self):
                self.started = 0
                self.cleaned = 0

            def start(self):
                self.started += 1

            def cleanup(self):
                self.cleaned += 1
                return {"success": True}

        success = FakeSession()
        value, cleanup = PROBE.execute_with_cleanup(success, lambda: "ok")
        self.assertEqual("ok", value)
        self.assertTrue(cleanup["success"])
        self.assertEqual(1, success.cleaned)

        failure = FakeSession()
        with self.assertRaises(RuntimeError):
            PROBE.execute_with_cleanup(failure, lambda: (_ for _ in ()).throw(RuntimeError("x")))
        self.assertEqual(1, failure.cleaned)

    def test_refuses_to_kill_unowned_pid(self) -> None:
        with self.assertRaises(PROBE.ProbeError):
            PROBE.terminate_owned_pid(12345, {54321})

    def test_temporary_logs_are_removed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="egx-ollama-test-") as name:
            path = Path(name)
            (path / "ollama.stdout.log").write_text("temporary", encoding="utf-8")
            (path / "ollama.stderr.log").write_text("temporary", encoding="utf-8")
        self.assertFalse(path.exists())

    def test_summary_strips_secrets_and_personal_home(self) -> None:
        raw = {
            "api_key": "DO_NOT_KEEP",
            "nested": {"password": "DO_NOT_KEEP", "path": str(Path.home() / "private")},
            "prompt_eval_count": 3,
        }
        serialized = json.dumps(PROBE.sanitize_summary(raw))
        self.assertNotIn("DO_NOT_KEEP", serialized)
        self.assertNotIn(str(Path.home()), serialized)
        self.assertIn("prompt_eval_count", serialized)


if __name__ == "__main__":
    unittest.main()
