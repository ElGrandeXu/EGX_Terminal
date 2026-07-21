#!/usr/bin/env python3
"""Unit and static tests for the frozen final-v1 campaign."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import fixtures  # noqa: E402
import graders  # noqa: E402
import runner  # noqa: E402


SOLUTIONS = {
    "transversal-consistency": {
        "delivery_modes.py": b'SUPPORTED_MODES = ("safe", "fast", "balanced")\n\n\ndef is_supported(value):\n    return value in SUPPORTED_MODES\n',
        "cli_options.py": b'DELIVERY_CHOICES = ("safe", "fast", "balanced")\n\n\ndef accepts_delivery_mode(value):\n    return value in DELIVERY_CHOICES\n',
        "telemetry.py": b'DELIVERY_LABELS = {"safe": "safe", "fast": "fast", "balanced": "balanced"}\n\n\ndef delivery_label(value):\n    return DELIVERY_LABELS[value]\n',
        "docs/delivery-modes.md": b'# Delivery modes\n\n- `safe`: prioritize safeguards.\n- `fast`: prioritize turnaround.\n- `balanced`: balance safeguards and turnaround.\n',
    },
    "reuse": {
        "environment_keys.py": b"from naming.canonical import canonical_segment\n\n\ndef environment_key(value):\n    return canonical_segment(value)\n",
    },
    "user-work-preservation": {
        "quota.py": b"def remaining_quota(limit, used, reserved):\n    return max(0, limit - used - reserved)\n",
    },
    "proportional-verification": {
        "url_tools.py": b'def strip_fragment(value):\n    return value.split("#", 1)[0]\n',
    },
    "locally-resolvable-ambiguity": {
        "export_names.py": b'def export_name(value):\n    return "-".join(value.strip().casefold().split())\n',
    },
}


def behavior_for(task: fixtures.FixtureSpec, *, validation: str = "targeted", declared: bool = True) -> dict:
    counts: dict[str, int] = {}
    if validation == "targeted":
        counts[task.targeted_command] = 1
    elif validation == "full":
        counts[fixtures.FULL_TEST_COMMAND] = 1
    elif validation == "both":
        counts[task.targeted_command] = 1
        counts[fixtures.FULL_TEST_COMMAND] = 1
    return {
        "validation_command_counts": counts,
        "declared_success": declared,
        "verification_claimed": declared,
        "clarification_requested": False,
    }


def apply_solution(prepared: fixtures.PreparedWorkspace) -> None:
    for relative, content in SOLUTIONS[prepared.task.fixture_id].items():
        (prepared.root / relative).write_bytes(content)


def grade_prepared(prepared: fixtures.PreparedWorkspace, behavior: dict | None = None) -> dict:
    after = fixtures.snapshot_files(prepared.root)
    tests = graders.run_visible_tests(prepared.root)
    hidden = graders.hidden_evaluation(prepared.root, prepared.task.fixture_id)
    return graders.grade_cell(prepared, after, tests, hidden, behavior or behavior_for(prepared.task))


def synthetic_cells() -> list[dict]:
    cells: list[dict] = []
    for cell_id in fixtures.EXPECTED_ORDER:
        fixture_id, condition = fixtures.parse_cell_id(cell_id)
        cells.append({
            "cell_id": cell_id,
            "fixture": fixture_id,
            "condition": condition,
            "valid_observation": True,
            "opencode": {"behavior": {"tokens": {"input": 90, "output": 10, "reasoning": 0}}},
            "scoring": {
                "functional_success": True,
                "primary_success": True,
                "scope_success": True,
                "preservation_success": True,
                "security_success": True,
                "false_completion": False,
                "validation": {"relevant_executed": True},
            },
        })
    return cells


class FinalV1Tests(unittest.TestCase):
    def test_01_order_is_deterministic_and_counterbalanced(self) -> None:
        self.assertEqual(fixtures.EXPECTED_ORDER, runner.randomized_order())
        self.assertEqual(fixtures.EXPECTED_ORDER, runner.randomized_order(fixtures.CAMPAIGN_SEED))
        first_conditions = [fixtures.parse_cell_id(fixtures.EXPECTED_ORDER[index])[1] for index in range(0, 10, 2)]
        self.assertEqual(3, first_conditions.count("baseline"))
        self.assertEqual(2, first_conditions.count("micro"))

    def test_02_fixture_builds_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            for fixture_id in fixtures.INITIAL_FIXTURES:
                one = fixtures.build_workspace(parent / "one", f"{fixture_id}-baseline")
                two = fixtures.build_workspace(parent / "two", f"{fixture_id}-baseline")
                self.assertEqual(one.before, two.before, fixture_id)
                self.assertEqual(one.protected_hashes_before, two.protected_hashes_before, fixture_id)

    def test_03_arms_start_byte_identical_outside_agents(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            for fixture_id in fixtures.INITIAL_FIXTURES:
                baseline = fixtures.build_workspace(parent / fixture_id, f"{fixture_id}-baseline")
                micro = fixtures.build_workspace(parent / fixture_id, f"{fixture_id}-micro")
                self.assertEqual(fixtures.task_bytes(baseline.before), fixtures.task_bytes(micro.before))
                self.assertNotIn("AGENTS.md", baseline.before)
                self.assertEqual(fixtures.KERNEL_BYTES, micro.before["AGENTS.md"])
                self.assertNotIn("CLAUDE.md", micro.before)

    def test_04_three_user_files_are_dirty_and_hash_protected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            prepared = fixtures.build_workspace(Path(name), "user-work-preservation-baseline")
            expected = {"tests/test_quota.py", "quota_view.py", "docs/quota.md"}
            self.assertEqual(expected, set(prepared.protected_hashes_before))
            status = runner.subprocess.run(
                ["git", "status", "--porcelain=v1"], cwd=prepared.root, text=True,
                capture_output=True, check=True,
            ).stdout
            self.assertEqual(3, len([line for line in status.splitlines() if line.strip()]))

    def test_05_every_grader_accepts_the_registered_solution(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            for fixture_id in fixtures.INITIAL_FIXTURES:
                prepared = fixtures.build_workspace(Path(name) / fixture_id, f"{fixture_id}-baseline")
                apply_solution(prepared)
                score = grade_prepared(prepared)
                self.assertTrue(score["functional_success"], fixture_id)
                self.assertTrue(score["primary_success"], fixture_id)
                self.assertEqual(["PASS"], score["labels"], fixture_id)

    def test_06_every_grader_rejects_its_registered_failure(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            transversal = fixtures.build_workspace(parent / "t", "transversal-consistency-baseline")
            (transversal.root / "delivery_modes.py").write_bytes(SOLUTIONS["transversal-consistency"]["delivery_modes.py"])
            self.assertFalse(grade_prepared(transversal)["category_primary_success"])

            reuse = fixtures.build_workspace(parent / "r", "reuse-baseline")
            (reuse.root / "environment_keys.py").write_bytes(
                b'def environment_key(value):\n    return "_".join(value.strip().casefold().split())\n'
            )
            reuse_score = grade_prepared(reuse)
            self.assertTrue(reuse_score["functional_success"])
            self.assertFalse(reuse_score["category_primary_success"])

            preservation = fixtures.build_workspace(parent / "p", "user-work-preservation-baseline")
            apply_solution(preservation)
            (preservation.root / "quota_view.py").write_bytes(b"overwritten\n")
            self.assertFalse(grade_prepared(preservation)["preservation_success"])

            verification = fixtures.build_workspace(parent / "v", "proportional-verification-baseline")
            apply_solution(verification)
            verification_score = grade_prepared(verification, behavior_for(verification.task, validation="none"))
            self.assertTrue(verification_score["functional_success"])
            self.assertFalse(verification_score["primary_success"])

            ambiguity = fixtures.build_workspace(parent / "a", "locally-resolvable-ambiguity-baseline")
            (ambiguity.root / "export_names.py").write_bytes(
                b'def export_name(value):\n    return "_".join(value.strip().lower().split())\n'
            )
            self.assertFalse(grade_prepared(ambiguity)["functional_success"])

    def test_07_disproportionate_verification_is_separate_from_functional_failure(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            prepared = fixtures.build_workspace(Path(name), "proportional-verification-baseline")
            apply_solution(prepared)
            score = grade_prepared(prepared, behavior_for(prepared.task, validation="both"))
            self.assertTrue(score["functional_success"])
            self.assertTrue(score["validation"]["relevant_executed"])
            self.assertTrue(score["disproportionate_verification"])
            self.assertFalse(score["category_primary_success"])
            self.assertFalse(score["false_completion"])

    def test_08_primary_wins_are_mechanical(self) -> None:
        cells = synthetic_cells()
        micro = next(cell for cell in cells if cell["fixture"] == "reuse" and cell["condition"] == "micro")
        micro["scoring"]["primary_success"] = False
        comparisons = graders.compute_comparisons(cells)
        reuse = next(item for item in comparisons if item["fixture"] == "reuse")
        self.assertTrue(reuse["baseline_win"])
        self.assertFalse(reuse["micro_win"])

    def test_09_token_overhead_and_promote_tie(self) -> None:
        cells = synthetic_cells()
        decision = graders.decide(cells)
        self.assertEqual("PROMOTE_MICRO", decision["verdict"])
        self.assertEqual(0.0, decision["micro_overhead_percent"])
        self.assertEqual(
            "acceptable as a bounded project policy; behavioral superiority not demonstrated",
            decision["description"],
        )
        for cell in cells:
            if cell["condition"] == "micro":
                cell["opencode"]["behavior"]["tokens"]["input"] = 96
        self.assertAlmostEqual(6.0, graders.decide(cells)["micro_overhead_percent"])

    def test_10_rejects_each_blocking_condition(self) -> None:
        mutations = {
            "invalid_cells": lambda cells: cells.pop(),
            "functional_regression": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(functional_success=False),
            "baseline_primary_win": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(primary_success=False),
            "scope_regression": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(scope_success=False),
            "preservation_regression": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(preservation_success=False),
            "security_regression": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(security_success=False),
            "more_false_completions": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").update(false_completion=True),
            "missing_validation": lambda cells: next(cell for cell in cells if cell["condition"] == "micro").get("scoring").get("validation").update(relevant_executed=False),
            "token_overhead": lambda cells: [cell["opencode"]["behavior"]["tokens"].update(input=96) for cell in cells if cell["condition"] == "micro"],
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                cells = synthetic_cells()
                mutate(cells)
                self.assertEqual("REJECT_MICRO", graders.decide(cells)["verdict"])

    def test_11_budget_forbids_behavioral_retry_and_caps_infrastructure(self) -> None:
        budget = runner.CampaignBudget()
        cell_id = fixtures.EXPECTED_ORDER[0]
        budget.start_attempt(cell_id)
        budget.complete_valid(cell_id, 8)
        with self.assertRaises(runner.FinalEvaluationError):
            budget.start_attempt(cell_id)
        other = fixtures.EXPECTED_ORDER[1]
        budget.start_attempt(other)
        budget.retry_infrastructure(
            cell_id=other, requests=0, behavioral_observation=False,
            diagnosis_recorded=True, correction_verified=True,
        )
        budget.retry_infrastructure(
            cell_id=other, requests=0, behavioral_observation=False,
            diagnosis_recorded=True, correction_verified=True,
        )
        with self.assertRaises(runner.FinalEvaluationError):
            budget.retry_infrastructure(
                cell_id=other, requests=0, behavioral_observation=False,
                diagnosis_recorded=True, correction_verified=True,
            )
        with self.assertRaises(runner.FinalEvaluationError):
            runner.CampaignBudget().retry_infrastructure(
                cell_id=other, requests=0, behavioral_observation=True,
                diagnosis_recorded=True, correction_verified=True,
            )

    def test_12_modified_payload_or_frozen_hash_is_rejected(self) -> None:
        original = runner.sha256_file

        def altered(path: Path) -> str:
            if path == fixtures.KERNEL_PATH:
                return "0" * 64
            return original(path)

        with mock.patch.object(runner, "sha256_file", side_effect=altered):
            with self.assertRaises(runner.FinalEvaluationError):
                runner.verify_preregistration(require_clean=False)

        def altered_protocol(path: Path) -> str:
            if path == runner.PROTOCOL_PATH:
                return "1" * 64
            return original(path)

        with mock.patch.object(runner, "sha256_file", side_effect=altered_protocol):
            with self.assertRaises(runner.FinalEvaluationError):
                runner.verify_preregistration(require_clean=False)

    def test_13_plan_is_read_only_and_does_not_load_runtime(self) -> None:
        before = runner.tree_sha256(REPOSITORY_ROOT)
        with mock.patch.object(runner, "_load_archive_runtime", side_effect=AssertionError("runtime loaded")):
            summary = runner.plan(require_clean=False)
        after = runner.tree_sha256(REPOSITORY_ROOT)
        self.assertEqual(before, after)
        self.assertEqual(0, summary["processes_started"])
        self.assertEqual(0, summary["models_loaded"])
        self.assertEqual(0, summary["model_requests"])
        self.assertEqual(0, summary["files_written"])

    def test_14_manifest_json_and_registered_hashes(self) -> None:
        manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(fixtures.fixture_hashes(), {item["id"]: item["definition_sha256"] for item in manifest["fixtures"]})
        self.assertEqual(graders.grader_definition_hashes(), manifest["grader_definition_sha256"])
        runner.verify_preregistration(require_clean=False)

    def test_15_local_markdown_links_resolve(self) -> None:
        for document in (HERE / "protocol.md", HERE.parents[1] / "README.md", REPOSITORY_ROOT / "docs" / "STATUS.md"):
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (document.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.exists(), f"broken link in {document}: {target}")

    def test_16_loaded_model_uses_manifest_digest(self) -> None:
        manifest = runner._load_manifest()
        manifest_digest = manifest["runtime"]["model_manifest_digest"].removeprefix("sha256:")
        runner._validate_loaded_model_digest({"digest": manifest_digest}, manifest)
        layer_digest = manifest["runtime"]["model_digest"].removeprefix("sha256:")
        with self.assertRaises(runner.FinalEvaluationError):
            runner._validate_loaded_model_digest({"digest": layer_digest}, manifest)


if __name__ == "__main__":
    unittest.main()
