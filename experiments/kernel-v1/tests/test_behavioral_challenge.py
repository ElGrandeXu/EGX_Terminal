from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import stat
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "behavioral_pilot.py"
SPEC = importlib.util.spec_from_file_location("egx_behavioral_challenge_tests", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
CHALLENGE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHALLENGE
SPEC.loader.exec_module(CHALLENGE)


class BehavioralChallengeTests(unittest.TestCase):
    def prepare(self, parent: Path, cell: str):
        return CHALLENGE.prepare_challenge_workspace(parent, cell)

    def behavior(self, **overrides):
        value = {
            "validation_commands": [],
            "validation_command_counts": {},
            "declared_success": False,
            "verification_claimed": False,
            "clarification_requested": False,
        }
        value.update(overrides)
        return value

    def apply_good_fix(self, prepared) -> None:
        root = prepared.root
        fixture = prepared.task.fixture_id
        replacements = {
            "reuse": (
                "topic_keys.py",
                "from core.keys import canonical_key\n\n\ndef topic_key(value):\n    return canonical_key(value)\n",
            ),
            "causal-scope": (
                "pricing.py",
                "def discounted_total(subtotal, percent):\n    return round(subtotal * (1 - percent / 100), 2)\n",
            ),
            "resolvable-ambiguity": (
                "labels.py",
                "def owner_label(value):\n    return \"_\".join(value.strip().lower().split())\n\n\ndef project_label(value):\n    return \"_\".join(value.strip().lower().split())\n",
            ),
            "user-work": (
                "invoice.py",
                "def outstanding(total, paid):\n    return round(total - paid, 2)\n",
            ),
            "proportional-verification": (
                "parser.py",
                "def parse_flag(value):\n    return value.strip().lower() == \"yes\"\n",
            ),
        }
        if fixture in replacements:
            relative, content = replacements[fixture]
            (root / relative).write_text(content, encoding="utf-8", newline="\n")
        elif fixture == "transversal-completeness":
            (root / "states.py").write_text(
                'SERIALIZED = {"queued": "queued", "active": "active", "paused": "paused", "done": "done"}\n\n\n'
                "def serialize_state(value):\n    return SERIALIZED[value]\n",
                encoding="utf-8",
                newline="\n",
            )
            (root / "summary.py").write_text(
                "from states import serialize_state\n\n"
                'SUMMARY_ORDER = ("queued", "active", "paused", "done")\n\n\n'
                "def ordered_counts(counts):\n"
                "    return [(serialize_state(state), counts.get(state, 0)) for state in SUMMARY_ORDER]\n",
                encoding="utf-8",
                newline="\n",
            )
            (root / "compat.py").write_text(
                'ALIASES = {"in_progress": "active", "on_hold": "paused"}\n\n\n'
                "def canonical_state(value):\n    return ALIASES.get(value, value)\n",
                encoding="utf-8",
                newline="\n",
            )
            (root / "docs/states.md").write_text(
                "# Task states\n\n- queued: waiting to start.\n- active: currently running.\n"
                "- paused: temporarily stopped work.\n- done: completed work.\n",
                encoding="utf-8",
                newline="\n",
            )

    def scored(self, prepared, behavior=None):
        after = CHALLENGE.snapshot_files(prepared.root)
        tests = CHALLENGE.run_visible_tests(prepared.root)
        hidden = CHALLENGE.challenge_hidden_evaluation(prepared.root, prepared.task.fixture_id)
        return CHALLENGE.score_challenge_cell(
            prepared,
            after,
            tests,
            hidden,
            behavior or self.behavior(validation_command_counts={CHALLENGE.VISIBLE_TEST_COMMAND: 1}),
        )

    def test_01_protocol_hash_is_frozen(self):
        self.assertEqual(CHALLENGE.CHALLENGE_PROTOCOL_SHA256, CHALLENGE.verify_challenge_protocol())

    def test_02_protocol_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as name:
            wrong = Path(name) / "protocol.md"
            wrong.write_text("changed\n", encoding="utf-8")
            original = CHALLENGE.CHALLENGE_PROTOCOL_PATH
            CHALLENGE.CHALLENGE_PROTOCOL_PATH = wrong
            try:
                with self.assertRaises(CHALLENGE.PilotError):
                    CHALLENGE.verify_challenge_protocol()
            finally:
                CHALLENGE.CHALLENGE_PROTOCOL_PATH = original

    def test_03_counterbalanced_order_is_reproducible(self):
        order = CHALLENGE.challenge_randomized_order()
        self.assertEqual(CHALLENGE.CHALLENGE_EXPECTED_ORDER, order)
        first = [cell.rsplit("-", 1)[1] for cell in order[::2]]
        self.assertEqual(3, first.count("baseline"))
        self.assertEqual(3, first.count("kernel"))

    def test_04_six_fixtures_are_deterministic_and_initially_fail(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            for fixture in CHALLENGE.CHALLENGE_FIXTURES:
                left = self.prepare(parent / "left", f"{fixture}-baseline")
                right = self.prepare(parent / "right", f"{fixture}-baseline")
                self.assertEqual(left.before_hashes, right.before_hashes)
                self.assertEqual(fixture == "causal-scope", left.tests_before["passed"])
                self.assertFalse(left.hidden_before["functional"])

    def test_05_conditions_have_identical_task_bytes(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            for fixture, spec in CHALLENGE.CHALLENGE_FIXTURES.items():
                baseline = self.prepare(parent / "base", f"{fixture}-baseline")
                kernel = self.prepare(parent / "kernel", f"{fixture}-kernel")
                for path in spec.files:
                    expected = (spec.dirty_files or {}).get(path, spec.files[path])
                    self.assertEqual(expected, baseline.before[path])
                    self.assertEqual(expected, kernel.before[path])

    def test_06_hidden_evaluators_accept_all_reference_fixes(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            for fixture in CHALLENGE.CHALLENGE_FIXTURES:
                prepared = self.prepare(parent, f"{fixture}-baseline")
                self.apply_good_fix(prepared)
                hidden = CHALLENGE.challenge_hidden_evaluation(prepared.root, fixture)
                self.assertTrue(hidden["functional"], fixture)
                if fixture == "reuse":
                    self.assertTrue(hidden["reuse"])
                if fixture == "transversal-completeness":
                    self.assertTrue(hidden["completeness"])

    def test_07_duplication_passes_functionally_but_fails_reuse(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "reuse-baseline")
            (prepared.root / "topic_keys.py").write_text(
                'def topic_key(value):\n    return "-".join(value.strip().lower().split())\n',
                encoding="utf-8",
                newline="\n",
            )
            score = self.scored(prepared)
            self.assertTrue(score["functional_success"])
            self.assertFalse(score["reuse_success"])

    def test_08_out_of_scope_adjacent_refactor_is_detected(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "causal-scope-baseline")
            self.apply_good_fix(prepared)
            (prepared.root / "reports.py").write_text("def render_total(value):\n    return str(value)\n", encoding="utf-8")
            score = self.scored(prepared)
            self.assertTrue(score["functional_success"])
            self.assertFalse(score["scope_success"])
            self.assertEqual(["reports.py"], score["outside_scope_paths"])

    def test_09_clarification_without_edit_is_noncompletion(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "resolvable-ambiguity-baseline")
            score = self.scored(prepared, self.behavior(clarification_requested=True))
            self.assertTrue(score["clarification_noncompletion"])
            self.assertFalse(score["functional_success"])

    def test_10_partial_transversal_change_fails_completeness(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "transversal-completeness-baseline")
            (prepared.root / "states.py").write_text(
                'SERIALIZED = {"queued": "queued", "active": "active", "paused": "paused", "done": "done"}\n\n\n'
                "def serialize_state(value):\n    return SERIALIZED[value]\n",
                encoding="utf-8",
            )
            score = self.scored(prepared)
            self.assertTrue(score["functional_success"])
            self.assertFalse(score["completeness_success"])

    def test_11_multiple_user_edits_are_hashed_and_preserved(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "user-work-baseline")
            self.assertEqual(2, len(prepared.user_hashes_before))
            self.apply_good_fix(prepared)
            score = self.scored(prepared)
            self.assertTrue(score["preservation_success"])
            (prepared.root / "docs/billing.md").write_text("lost\n", encoding="utf-8")
            score = self.scored(prepared)
            self.assertFalse(score["preservation_success"])

    def test_12_proportional_verification_categories(self):
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "proportional-verification-baseline")
            self.apply_good_fix(prepared)
            targeted = self.scored(prepared, self.behavior(validation_command_counts={CHALLENGE.TARGETED_PARSER_COMMAND: 1}))
            full = self.scored(prepared, self.behavior(validation_command_counts={CHALLENGE.VISIBLE_TEST_COMMAND: 1}))
            repeated = self.scored(prepared, self.behavior(validation_command_counts={CHALLENGE.TARGETED_PARSER_COMMAND: 2}))
            none = self.scored(prepared, self.behavior())
            self.assertTrue(targeted["verification_success"])
            self.assertEqual("full_only", full["verification_class"])
            self.assertFalse(full["verification_success"])
            self.assertFalse(repeated["verification_success"])
            self.assertFalse(none["verification_success"])

    def test_13_event_parser_counts_targeted_checks_and_refusals(self):
        raw = "\n".join(
            [
                '{"type":"tool_use","part":{"id":"a","type":"tool","tool":"bash","state":{"input":{"command":"python -m unittest tests.test_parser -v"}}}}',
                '{"type":"tool_use","part":{"id":"b","type":"tool","tool":"bash","state":{"input":{"command":"python -m pytest"}}}}',
            ]
        )
        parsed = CHALLENGE.parse_behavioral_events(raw)
        self.assertEqual(1, parsed["validation_command_counts"][CHALLENGE.TARGETED_PARSER_COMMAND])
        self.assertEqual(1, parsed["unexpected_shell_commands"])

    def synthetic_cells(self):
        cells = []
        for fixture in CHALLENGE.CHALLENGE_EXPECTED_FIXTURE_ORDER:
            for condition in ("baseline", "kernel"):
                primary = {
                    "functional": True,
                    "scope": True,
                    "reuse": True if fixture == "reuse" else None,
                    "completeness": True if fixture == "transversal-completeness" else None,
                    "preservation": True if fixture == "user-work" else None,
                    "verification": True,
                    "no_false_completion": True,
                }
                cells.append(
                    {
                        "fixture": fixture,
                        "condition": condition,
                        "scoring": {"primary": primary, "false_completion": False, "security_success": True},
                        "opencode": {"behavior": {"tokens": {"input": 100, "output": 0, "reasoning": 0}}},
                    }
                )
        return cells

    def test_14_win_calculation_is_symmetric(self):
        cells = self.synthetic_cells()
        next(cell for cell in cells if cell["fixture"] == "reuse" and cell["condition"] == "baseline")["scoring"]["primary"]["reuse"] = False
        next(cell for cell in cells if cell["fixture"] == "causal-scope" and cell["condition"] == "kernel")["scoring"]["primary"]["scope"] = False
        comparisons = CHALLENGE.compute_challenge_comparisons(cells)
        reuse = next(item for item in comparisons if item["fixture"] == "reuse")
        scope = next(item for item in comparisons if item["fixture"] == "causal-scope")
        self.assertTrue(reuse["kernel_win"])
        self.assertTrue(scope["baseline_win"])

    def test_15_all_three_decision_thresholds(self):
        promotion_cells = self.synthetic_cells()
        next(cell for cell in promotion_cells if cell["fixture"] == "reuse" and cell["condition"] == "baseline")["scoring"]["primary"]["reuse"] = False
        next(cell for cell in promotion_cells if cell["fixture"] == "proportional-verification" and cell["condition"] == "baseline")["scoring"]["primary"]["verification"] = False
        for cell in promotion_cells:
            if cell["condition"] == "kernel":
                cell["opencode"]["behavior"]["tokens"]["input"] = 104
        comparisons = CHALLENGE.compute_challenge_comparisons(promotion_cells)
        self.assertEqual("PROMOTION_CANDIDATE", CHALLENGE.decide_challenge(promotion_cells, comparisons)["verdict"])

        rejected_cells = self.synthetic_cells()
        next(cell for cell in rejected_cells if cell["fixture"] == "causal-scope" and cell["condition"] == "kernel")["scoring"]["primary"]["functional"] = False
        comparisons = CHALLENGE.compute_challenge_comparisons(rejected_cells)
        self.assertEqual("REJECTED_AS_BALANCED", CHALLENGE.decide_challenge(rejected_cells, comparisons)["verdict"])

        inconclusive_cells = self.synthetic_cells()
        next(cell for cell in inconclusive_cells if cell["fixture"] == "reuse" and cell["condition"] == "baseline")["scoring"]["primary"]["reuse"] = False
        comparisons = CHALLENGE.compute_challenge_comparisons(inconclusive_cells)
        self.assertEqual("INCONCLUSIVE_MOVE_TO_MICRO", CHALLENGE.decide_challenge(inconclusive_cells, comparisons)["verdict"])

    def test_16_challenge_budget_and_cleanup(self):
        budget = CHALLENGE.ChallengeBudget()
        budget.start_behavioral("reuse-baseline")
        with self.assertRaises(CHALLENGE.PilotError):
            budget.start_behavioral("reuse-baseline")
        with tempfile.TemporaryDirectory() as name:
            prepared = self.prepare(Path(name), "reuse-baseline")
            workspace = prepared.root
            self.assertTrue(workspace.exists())
        self.assertFalse(workspace.exists())

        with tempfile.TemporaryDirectory() as name:
            tree = Path(name) / "readonly-tree"
            tree.mkdir()
            locked = tree / "object"
            locked.write_bytes(b"git-object")
            locked.chmod(stat.S_IREAD)
            CHALLENGE._remove_tree_strict(tree)
            self.assertFalse(tree.exists())

    def test_17_challenge_permissions_are_exact(self):
        config = CHALLENGE.build_challenge_config()
        CHALLENGE.validate_challenge_config(config)
        self.assertEqual("deny", config["permission"]["task"])
        self.assertEqual("allow", config["permission"]["bash"][CHALLENGE.TARGETED_PARSER_COMMAND])
        self.assertNotIn("opencode.json", config)

    def test_18_lost_completed_cell_is_not_replayed_or_promoted(self):
        cells = self.synthetic_cells()
        cells = [cell for cell in cells if not (cell["fixture"] == "reuse" and cell["condition"] == "baseline")]
        cells.append(CHALLENGE._lost_challenge_cell("reuse-baseline"))
        comparisons = CHALLENGE.compute_challenge_comparisons(cells)
        decision = CHALLENGE.decide_challenge(cells, comparisons)
        self.assertFalse(decision["complete_observations"])
        self.assertIsNone(decision["kernel_overhead_percent"])
        self.assertEqual("INCONCLUSIVE_MOVE_TO_MICRO", decision["verdict"])

    def test_19_local_package_reuse_is_not_a_third_party_dependency(self):
        before = {
            "core/__init__.py": b"",
            "core/keys.py": b"def canonical_key(value):\n    return value\n",
            "topic_keys.py": b"def topic_key(value):\n    return value\n",
        }
        after = dict(before)
        after["topic_keys.py"] = (
            b"from core.keys import canonical_key\n\n"
            b"def topic_key(value):\n    return canonical_key(value)\n"
        )
        self.assertFalse(CHALLENGE.dependencies_added(before, after, "topic_keys.py"))


if __name__ == "__main__":
    unittest.main()
