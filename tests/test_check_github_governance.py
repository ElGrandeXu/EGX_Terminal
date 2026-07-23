from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / "scripts/check_github_governance.py"
sys.path.insert(0, str(SOURCE / "scripts"))
import check_github_governance as checker  # noqa: E402


FIXTURE_FILES = (
    "README.md",
    "docs/QUICKSTART.md",
    "docs/STATUS.md",
    "docs/decisions/README.md",
    "docs/publication/PUBLICATION_BOUNDARY.md",
    "docs/publication/GITHUB_PUBLICATION_PLAN.md",
    "docs/publication/RELEASE_POLICY.md",
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/research_proposal.md",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    "governance/github-actions-lock.json",
    "governance/github-publication-plan.json",
    "governance/requirements-reuse-build-6.2.0.txt",
    "governance/requirements-reuse-6.2.0.txt",
    "scripts/check_release_tree.py",
    "REUSE.toml",
)


class GitHubGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="github governance ")
        self.root = Path(self.temporary.name) / "repository with spaces"
        for relative in FIXTURE_FILES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / relative, target)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def text(self, relative: str) -> str:
        return (self.root / relative).read_text(encoding="utf-8")

    def replace(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def codes(self) -> set[str]:
        return {item.code for item in checker.audit(self.root)}

    def publication_plan(self) -> dict:
        return json.loads(self.text("governance/github-publication-plan.json"))

    def write_publication_plan(self, data: dict) -> None:
        path = self.root / "governance/github-publication-plan.json"
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_01_compliant_governance(self) -> None:
        self.assertEqual(checker.audit(self.root), ())

    def test_02_floating_action(self) -> None:
        self.replace(".github/workflows/validate.yml", "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", "actions/checkout@v7")
        self.assertIn("FLOATING_ACTION", self.codes())

    def test_03_action_absent_from_lock(self) -> None:
        path = self.root / "governance/github-actions-lock.json"
        data = json.loads(path.read_text(encoding="utf-8")); data["actions"] = data["actions"][1:]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("LOCK_CONTENT", self.codes())

    def test_04_sha_differs_from_lock(self) -> None:
        self.replace(".github/workflows/validate.yml", "3d3c42e5aac5ba805825da76410c181273ba90b1", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertIn("LOCK_MISMATCH", self.codes())

    def test_05_write_permission(self) -> None:
        self.replace(".github/workflows/validate.yml", "contents: read", "contents: write")
        self.assertIn("WRITE_PERMISSION", self.codes())

    def test_06_permissions_absent(self) -> None:
        self.replace(".github/workflows/validate.yml", "permissions:\n  contents: read\n\n", "")
        self.assertIn("PERMISSIONS", self.codes())

    def test_07_pull_request_target(self) -> None:
        self.replace(".github/workflows/validate.yml", "pull_request:", "pull_request_target:")
        self.assertIn("PULL_REQUEST_TARGET", self.codes())

    def test_08_secret_reference(self) -> None:
        self.replace(".github/workflows/validate.yml", "run: reuse lint", "run: echo ${{ secrets.TEST }}")
        self.assertIn("SECRET_REFERENCE", self.codes())

    def test_09_job_bad_name(self) -> None:
        self.replace(".github/workflows/validate.yml", "name: repository / ubuntu", "name: ubuntu")
        self.assertIn("CHECK_NAMES", self.codes())

    def test_10_shallow_checkout(self) -> None:
        self.replace(".github/workflows/validate.yml", "fetch-depth: 0", "fetch-depth: 1")
        self.assertIn("SHALLOW_CHECKOUT", self.codes())

    def test_11_persisted_credentials(self) -> None:
        self.replace(".github/workflows/validate.yml", "persist-credentials: false", "persist-credentials: true")
        self.assertIn("PERSISTED_CREDENTIALS", self.codes())

    def test_12_unauthorized_action(self) -> None:
        self.replace(".github/workflows/validate.yml", "actions/setup-python@", "owner/unknown-action@")
        self.assertIn("UNAUTHORIZED_ACTION", self.codes())

    def test_13_wrong_reuse_version(self) -> None:
        self.replace("governance/requirements-reuse-6.2.0.txt", "reuse==6.2.0", "reuse==6.1.0")
        self.assertIn("REUSE_LOCK", self.codes())

    def test_14_template_absent(self) -> None:
        (self.root / ".github/pull_request_template.md").unlink()
        self.assertIn("MISSING_COMMUNITY_FILE", self.codes())

    def test_15_invalid_frontmatter(self) -> None:
        self.replace(".github/ISSUE_TEMPLATE/bug_report.md", "name: Bug report", "name Bug report")
        self.assertIn("INVALID_FRONTMATTER", self.codes())

    def test_16_code_of_conduct_added(self) -> None:
        (self.root / "CODE_OF_CONDUCT.md").write_text("cosmetic\n", encoding="utf-8")
        self.assertIn("DEFERRED_FILE_PRESENT", self.codes())

    def test_17_invalid_publication_plan(self) -> None:
        path = self.root / "governance/github-publication-plan.json"
        data = json.loads(path.read_text(encoding="utf-8")); data["identity"]["owner"] = "Wrong"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("REPOSITORY_IDENTITY", self.codes())

    def test_17b_unapproved_remote_status_is_rejected(self) -> None:
        path = self.root / "governance/github-publication-plan.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["remote_settings_status"] = "PLANNED_NOT_APPLIED"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("CURRENT_REMOTE_STATUS", self.codes())

    def test_18_path_with_spaces(self) -> None:
        self.assertIn(" ", str(self.root))
        self.assertEqual(checker.audit(self.root), ())

    def test_19_different_current_working_directory(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_20_diagnostics_and_return_code(self) -> None:
        self.replace(".github/workflows/validate.yml", "contents: read", "contents: write")
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("[WRITE_PERMISSION]", result.stdout)

    def test_21_windows_multicommand_powershell_default_is_rejected(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            "    defaults:\n      run:\n        shell: bash\n",
            "",
        )
        self.assertIn("WINDOWS_FAIL_FAST_SHELL", self.codes())

    def test_22_windows_shell_must_be_bash(self) -> None:
        self.replace(".github/workflows/validate.yml", "shell: bash", "shell: pwsh")
        self.assertIn("WINDOWS_FAIL_FAST_SHELL", self.codes())

    def test_23_release_tag_trigger_is_required(self) -> None:
        self.replace(".github/workflows/validate.yml", '    tags: ["v*"]\n', "")
        self.assertIn("TRIGGERS", self.codes())

    def test_24_broad_tag_trigger_is_rejected(self) -> None:
        self.replace(".github/workflows/validate.yml", 'tags: ["v*"]', 'tags: ["*"]')
        self.assertIn("TRIGGERS", self.codes())

    def test_25_unhashed_reuse_install_is_rejected(self) -> None:
        self.replace(".github/workflows/validate.yml", "--require-hashes ", "")
        self.assertIn("REUSE_INSTALL", self.codes())

    def test_26_reuse_hash_change_is_rejected(self) -> None:
        self.replace(
            "governance/requirements-reuse-6.2.0.txt",
            "4feae057a2334c9a513e6933cdb9be819d8b822f3b5b435a36138bd218897d23",
            "0" * 64,
        )
        self.assertIn("REUSE_LOCK", self.codes())

    def test_26a_windows_reuse_hash_cannot_be_removed(self) -> None:
        self.replace(
            "governance/requirements-reuse-6.2.0.txt",
            " \\\n    --hash=sha256:de8a88e63464af587c950061a5e6a67d3632e36df62b986892331d4620a35c01",
            "",
        )
        self.assertIn("REUSE_LOCK", self.codes())

    def test_26b_windows_dependency_marker_cannot_be_widened(self) -> None:
        self.replace(
            "governance/requirements-reuse-6.2.0.txt",
            'colorama==0.4.6 ; sys_platform == "win32"',
            "colorama==0.4.6",
        )
        self.assertIn("REUSE_LOCK", self.codes())

    def test_27_content_only_mode_needs_no_git_metadata(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--content-only", "--root", str(self.root)],
            cwd=self.root.parent,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_28_tag_gate_must_checkout_canonical_main(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            "          ref: refs/heads/main\n",
            "",
        )
        self.assertIn("POLICY_CHECKOUT", self.codes())

    def test_29_release_tree_must_checkout_triggering_tag(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            "          ref: ${{ github.ref }}\n          path: _validation/release\n",
            "          ref: refs/heads/main\n          path: _validation/release\n",
        )
        self.assertIn("RELEASE_CHECKOUT_REF", self.codes())

    def test_30_policy_and_release_workspaces_must_be_distinct(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            "working-directory: _validation/release",
            "working-directory: _validation/policy",
        )
        self.assertIn("RELEASE_WORKSPACE", self.codes())

    def test_31_exact_release_tree_checker_is_required(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            '          python scripts/check_release_tree.py --expected-ref "${GITHUB_REF}" --event-sha "${GITHUB_SHA}"\n',
            "",
        )
        self.assertIn("TAG_RELEASE_COMMAND", self.codes())

    def test_32_ordinary_event_checkout_and_validation_are_required(self) -> None:
        self.replace(
            ".github/workflows/validate.yml",
            "        if: ${{ !startsWith(github.ref, 'refs/tags/') }}\n",
            "",
        )
        self.assertIn("EVENT_ISOLATION", self.codes())

    def test_33_schema_6_fixture_records_history_and_final_publication(self) -> None:
        data = self.publication_plan()
        controls = data["remote_governance"]["controls"]
        final = data["publication_retry"]["final_result"]
        self.assertEqual(6, data["schema_version"])
        self.assertEqual("PUBLIC_REPOSITORY_VERIFIED", data["publication_phase"])
        self.assertEqual("public", data["visibility_strategy"]["target_visibility"])
        self.assertEqual(
            "public",
            data["visibility_strategy"]["dated_remote_observation"]["visibility"],
        )
        self.assertEqual("PUBLIC_TRANSITION_ROLLED_BACK", data["publication_transition"]["status"])
        self.assertEqual("COMPLETED_SUCCESS", data["publication_retry"]["status"])
        self.assertEqual(30002915548, final["workflow_run"]["run_id"])
        self.assertEqual("workflow_dispatch", final["workflow_run"]["event"])
        self.assertEqual(1, final["workflow_run"]["attempt"])
        self.assertEqual(
            {"level_a", "level_b", "level_c"},
            set(final["verification_levels"]),
        )
        self.assertEqual(1895, data["publication_transition"]["public_exposure"]["duration_seconds_approx"])
        self.assertFalse(
            data["publication_transition"]["public_exposure"]["third_party_access_or_copying_excluded"]
        )
        self.assertEqual("ACTIVE", controls["main_ruleset"]["observed_state"])
        self.assertEqual("PROTECTED", controls["main_branch"]["observed_state"])
        self.assertEqual("ACTIVE_VERIFIED", controls["private_vulnerability_reporting"]["observed_state"])
        self.assertEqual("ACTIVE", controls["secret_scanning"]["observed_state"])
        self.assertEqual("ACTIVE", controls["push_protection"]["observed_state"])
        self.assertEqual("ACTIVE", controls["security_alerts"]["observed_state"])
        self.assertEqual(
            "OBSERVED_ON_VERIFIED_PUBLIC_REPOSITORY",
            data["features"]["status"],
        )
        self.assertNotIn("releases_allowed", data["features"])
        self.assertEqual((), checker.audit(self.root))

    def test_34_schema_other_than_6_is_rejected(self) -> None:
        data = self.publication_plan()
        for schema in (4, 5, 7):
            with self.subTest(schema=schema):
                data["schema_version"] = schema
                self.write_publication_plan(data)
                self.assertIn("SCHEMA_VERSION", self.codes())

    def test_35_retry_preparation_remote_status_is_rejected(self) -> None:
        data = self.publication_plan()
        data["remote_settings_status"] = "CURRENTLY_PRIVATE_RETRY_NOT_APPLIED"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_REMOTE_STATUS", self.codes())

    def test_36_desired_and_observed_states_are_distinct(self) -> None:
        data = self.publication_plan()
        control = data["remote_governance"]["controls"]["main_branch"]
        del control["observed_state"]
        control["state"] = "PROTECTED"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_PROTECTION", self.codes())

    def test_37_current_security_controls_cannot_be_declared_inactive(self) -> None:
        for name in ("private_vulnerability_reporting", "secret_scanning", "push_protection"):
            with self.subTest(control=name):
                data = self.publication_plan()
                data["remote_governance"]["controls"][name]["observed_state"] = "INACTIVE"
                self.write_publication_plan(data)
                self.assertIn("CURRENT_PROTECTION", self.codes())
                shutil.copy2(
                    SOURCE / "governance/github-publication-plan.json",
                    self.root / "governance/github-publication-plan.json",
                )

    def test_38_main_must_remain_declared_protected(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["controls"]["main_branch"]["observed_state"] = "UNPROTECTED"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_PROTECTION", self.codes())

    def test_39_ruleset_must_remain_active_and_applied(self) -> None:
        data = self.publication_plan()
        control = data["remote_governance"]["controls"]["main_ruleset"]
        control["observed_state"] = "INACTIVE"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_PROTECTION", self.codes())

    def test_40_secret_scanning_must_remain_applied(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["controls"]["secret_scanning"]["application_status"] = "INACTIVE"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_PROTECTION", self.codes())

    def test_41_final_target_must_be_public(self) -> None:
        data = self.publication_plan()
        data["visibility_strategy"]["target_visibility"] = "private"
        self.write_publication_plan(data)
        self.assertIn("FINAL_TARGET", self.codes())

    def test_42_first_transition_cannot_be_erased_or_presented_as_success(self) -> None:
        data = self.publication_plan()
        for status in ("NOT_APPLIED", "PUBLIC_TRANSITION_SUCCEEDED"):
            with self.subTest(status=status):
                data["publication_transition"]["status"] = status
                self.write_publication_plan(data)
                self.assertIn("FIRST_TRANSITION_STATE", self.codes())

    def test_43_nonempty_bypass_list_is_rejected(self) -> None:
        data = self.publication_plan()
        ruleset = data["remote_governance"]["controls"]["main_ruleset"]["desired_configuration"]
        ruleset["bypass_actors"] = ["Repository administrator"]
        self.write_publication_plan(data)
        self.assertIn("BYPASS", self.codes())

    def test_44_administrative_bypass_object_is_rejected(self) -> None:
        data = self.publication_plan()
        ruleset = data["remote_governance"]["controls"]["main_ruleset"]["desired_configuration"]
        ruleset["administrative_bypass"] = {"planned": True}
        self.write_publication_plan(data)
        self.assertIn("BYPASS", self.codes())

    def test_45_pvr_must_remain_a_current_invariant(self) -> None:
        data = self.publication_plan()
        pvr = data["remote_governance"]["controls"]["private_vulnerability_reporting"]
        pvr["desired_state"] = "INACTIVE"
        self.write_publication_plan(data)
        self.assertIn("CURRENT_PROTECTION", self.codes())

    def test_46_public_exposure_timeline_is_required(self) -> None:
        data = self.publication_plan()
        del data["publication_transition"]["public_exposure"]["started_at"]
        self.write_publication_plan(data)
        self.assertIn("EXPOSURE_TIMELINE", self.codes())

    def test_47_required_checks_cannot_be_lost(self) -> None:
        data = self.publication_plan()
        rules = data["remote_governance"]["controls"]["main_ruleset"]["desired_configuration"]["rules"]
        rules["required_status_checks"].pop()
        self.write_publication_plan(data)
        self.assertIn("RULESET_CHECKS", self.codes())

    def test_48_force_push_and_deletion_must_remain_blocked(self) -> None:
        for key in ("prevent_force_push", "prevent_deletion"):
            with self.subTest(rule=key):
                data = self.publication_plan()
                rules = data["remote_governance"]["controls"]["main_ruleset"]["desired_configuration"]["rules"]
                rules[key] = False
                self.write_publication_plan(data)
                self.assertIn("BRANCH_MUTATION", self.codes())

    def test_49_current_state_must_remain_api_verified(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["snapshot_source"] = "DOCUMENTATION"
        self.write_publication_plan(data)
        self.assertIn("DATED_REMOTE_SNAPSHOT", self.codes())

    def test_50_blocked_preaudit_cannot_be_rewritten_as_success(self) -> None:
        for status in ("PUBLICATION_READY", "PASSED", "COMPLETED"):
            with self.subTest(status=status):
                data = self.publication_plan()
                data["prepublication_audit"]["status"] = status
                self.write_publication_plan(data)
                self.assertIn("PREAUDIT_VERDICT", self.codes())

    def test_51_executive_verdict_cannot_be_rewritten_as_ready(self) -> None:
        data = self.publication_plan()
        data["prepublication_audit"]["executive_verdict"] = "PUBLICATION_READY"
        self.write_publication_plan(data)
        self.assertIn("PREAUDIT_VERDICT", self.codes())

    def test_52_historical_merged_head_reaudit_requirement_is_preserved(self) -> None:
        data = self.publication_plan()
        data["prepublication_audit"]["merged_head_reaudit_required"] = False
        self.write_publication_plan(data)
        self.assertIn("PREAUDIT_FOLLOWUP", self.codes())

    def test_53_incomplete_current_controls_report_specific_protection(self) -> None:
        data = self.publication_plan()
        del data["remote_governance"]["controls"]["push_protection"]
        self.write_publication_plan(data)
        messages = [item.message for item in checker.audit(self.root) if item.code == "CURRENT_PROTECTION"]
        self.assertTrue(any("six final protection" in message for message in messages))

    def test_54_exposure_duration_is_required(self) -> None:
        data = self.publication_plan()
        del data["publication_transition"]["public_exposure"]["duration_seconds_approx"]
        self.write_publication_plan(data)
        self.assertIn("EXPOSURE_TIMELINE", self.codes())

    def test_55_irreversible_exposure_uncertainty_is_required(self) -> None:
        data = self.publication_plan()
        data["publication_transition"]["public_exposure"]["third_party_access_or_copying_excluded"] = True
        self.write_publication_plan(data)
        self.assertIn("EXPOSURE_UNCERTAINTY", self.codes())

    def test_56_general_anonymous_403_cannot_be_absolute_blocker(self) -> None:
        data = self.publication_plan()
        data["log_access_diagnostic"]["anonymous_rest_failure_absolute_blocker"] = True
        self.write_publication_plan(data)
        self.assertIn("LOG_ACCESS_CLASSIFICATION", self.codes())

    def test_57_level_b_is_mandatory_and_non_collaborating(self) -> None:
        data = self.publication_plan()
        data["public_verification_model"]["level_b"]["required"] = False
        self.write_publication_plan(data)
        self.assertIn("LEVEL_B", self.codes())

    def test_58_historical_run_cannot_be_reused(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["prohibited_run_ids"] = []
        self.write_publication_plan(data)
        self.assertIn("RUN_REUSE", self.codes())

    def test_59_workflow_dispatch_is_required(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["workflow_dispatch_required"] = False
        self.write_publication_plan(data)
        self.assertIn("WORKFLOW_DISPATCH", self.codes())

    def test_60_retry_cannot_exceed_one(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["maximum_attempts"] = 2
        self.write_publication_plan(data)
        self.assertIn("RETRY_LIMIT", self.codes())

    def test_61_retry_cannot_remain_in_preparation(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["status"] = "CONDITIONALLY_AUTHORIZED_NOT_APPLIED"
        self.write_publication_plan(data)
        self.assertIn("FINAL_RETRY_STATUS", self.codes())

    def test_62_temp_clone_token_must_be_excluded_before_capture(self) -> None:
        data = self.publication_plan()
        data["credential_handling"]["future_collection"] = "RAW_RETENTION_ALLOWED"
        self.write_publication_plan(data)
        self.assertIn("CREDENTIAL_COLLECTION", self.codes())

    def test_63_old_credential_activity_or_expiry_cannot_be_claimed(self) -> None:
        for key in ("historical_value_active_claim", "historical_value_expired_claim"):
            with self.subTest(claim=key):
                data = self.publication_plan()
                data["credential_handling"][key] = True
                self.write_publication_plan(data)
                self.assertIn("CREDENTIAL_CLAIM", self.codes())
                shutil.copy2(
                    SOURCE / "governance/github-publication-plan.json",
                    self.root / "governance/github-publication-plan.json",
                )

    def test_64_public_window_ruleset_has_no_bypass(self) -> None:
        data = self.publication_plan()
        data["publication_transition"]["public_window_controls"]["main_ruleset"]["bypass_actors"] = ["admin"]
        self.write_publication_plan(data)
        self.assertIn("BYPASS", self.codes())

    def test_65_retry_cannot_authorize_tag_or_release(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["github_release_creation_allowed"] = True
        self.write_publication_plan(data)
        self.assertIn("RELEASE_PROHIBITION", self.codes())

    def test_66_workflow_dispatch_trigger_cannot_be_removed(self) -> None:
        self.replace(".github/workflows/validate.yml", "  workflow_dispatch:\n", "")
        self.assertIn("TRIGGERS", self.codes())

    def test_67_credential_value_cannot_be_serialized(self) -> None:
        data = self.publication_plan()
        data["credential_handling"]["serialized_" + "value"] = None
        self.write_publication_plan(data)
        self.assertIn("CREDENTIAL_COLLECTION", self.codes())

    def test_68_retry_checks_have_a_precise_diagnostic(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["required_checks"].pop()
        self.write_publication_plan(data)
        self.assertIn("RETRY_CHECKS", self.codes())
        self.assertNotIn("RETRY_LIMIT", self.codes())

    def test_69_new_run_id_is_required(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["new_run_id_required"] = False
        self.write_publication_plan(data)
        self.assertIn("WORKFLOW_DISPATCH", self.codes())

    def test_70_metadata_is_exact(self) -> None:
        data = self.publication_plan()
        data["metadata"]["topics"].reverse()
        self.write_publication_plan(data)
        self.assertIn("METADATA", self.codes())

    def test_71_features_are_observed_platform_state_only(self) -> None:
        data = self.publication_plan()
        data["features"]["releases_allowed"] = False
        self.write_publication_plan(data)
        self.assertIn("FEATURES", self.codes())

    def test_72_merge_policy_is_exact(self) -> None:
        data = self.publication_plan()
        data["merge_policy"]["squash_message"] = "COMMIT_MESSAGES"
        self.write_publication_plan(data)
        self.assertIn("MERGE_POLICY", self.codes())

    def test_73_recovery_closure_preserves_every_historical_fact(self) -> None:
        mutations = {
            "starting_head": "0" * 40,
            "starting_commit_count": 0,
            "final_commit_count": 0,
            "temporary_repositories_backed_up_locally": False,
            "temporary_repositories_deleted": False,
            "private_evidence_outside_repository": False,
            "historical_direct_push_exception": "NONE",
            "future_direct_push_authorized": True,
            "force_push_used": True,
            "git_tag_created": True,
            "github_release_created": True,
            "pull_request_created": True,
            "experimental_evidence_modified": True,
            "status": "OPEN",
        }
        for key, value in mutations.items():
            with self.subTest(field=key):
                data = self.publication_plan()
                data["recovery_closure"][key] = value
                self.write_publication_plan(data)
                self.assertIn("RECOVERY_CLOSURE", self.codes())
                shutil.copy2(
                    SOURCE / "governance/github-publication-plan.json",
                    self.root / "governance/github-publication-plan.json",
                )

    def test_74_level_a_required_list_is_exact(self) -> None:
        data = self.publication_plan()
        data["public_verification_model"]["level_a"]["required"].pop()
        self.write_publication_plan(data)
        self.assertIn("LEVEL_A", self.codes())

    def test_75_level_b_required_checks_are_exact(self) -> None:
        data = self.publication_plan()
        data["public_verification_model"]["level_b"]["required_checks"].pop()
        self.write_publication_plan(data)
        self.assertIn("LEVEL_B", self.codes())

    def test_76_level_c_required_list_is_exact(self) -> None:
        data = self.publication_plan()
        data["public_verification_model"]["level_c"]["required"].pop()
        self.write_publication_plan(data)
        self.assertIn("LEVEL_C", self.codes())

    def test_77_retry_authorization_is_exact(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["authorized_by"] = "docs/decisions/0015-authorize-guarded-public-transition.md"
        self.write_publication_plan(data)
        self.assertIn("RETRY_AUTHORIZATION", self.codes())

    def test_78_retry_prerequisites_are_exact(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["prerequisites"].pop()
        self.write_publication_plan(data)
        self.assertIn("RETRY_PREREQUISITES", self.codes())

    def test_79_dispatch_response_fields_are_exact(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["dispatch_response_fields"].pop()
        self.write_publication_plan(data)
        self.assertIn("DISPATCH_RESPONSE_FIELDS", self.codes())

    def test_80_empty_commit_remains_forbidden(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["empty_commit_allowed"] = True
        self.write_publication_plan(data)
        self.assertIn("RETRY_SAFETY", self.codes())

    def test_81_temporary_branch_remains_forbidden(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["temporary_branch_allowed"] = True
        self.write_publication_plan(data)
        self.assertIn("RETRY_SAFETY", self.codes())

    def test_82_protection_weakening_remains_forbidden(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["protection_weakening_allowed"] = True
        self.write_publication_plan(data)
        self.assertIn("RETRY_PROTECTIONS", self.codes())

    def test_83_dangerous_capture_policy_is_complete(self) -> None:
        data = self.publication_plan()
        data["api_evidence_handling"]["dangerous_capture_policy"].pop()
        self.write_publication_plan(data)
        self.assertIn("EVIDENCE_HANDLING", self.codes())

    def test_84_check_plan_has_no_unreachable_schema_5_validator(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        active = source[source.index("def _check_plan("):source.index("def _matches(")]
        self.assertNotIn("schema 5", active)
        self.assertNotIn("EXPECTED_TRANSITION_SEQUENCE", active)
        self.assertEqual(1, active.count("_check_plan_v6(relative, plan, findings)"))

    def test_85_retry_workflow_path_is_exact(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["workflow"] = ".github/workflows/other.yml"
        self.write_publication_plan(data)
        self.assertIn("WORKFLOW_DISPATCH", self.codes())

    def test_86_retry_ref_is_main(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["ref"] = "temporary"
        self.write_publication_plan(data)
        self.assertIn("WORKFLOW_DISPATCH", self.codes())

    def test_87_third_attempt_requires_new_adr(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["third_attempt_requires_new_adr"] = False
        self.write_publication_plan(data)
        self.assertIn("RETRY_LIMIT", self.codes())

    def test_88_retry_cannot_authorize_tag_creation(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["git_tag_creation_allowed"] = True
        self.write_publication_plan(data)
        self.assertIn("RELEASE_PROHIBITION", self.codes())

    def test_89_v1_0_1_remains_a_separate_mission(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["v1.0.1_mission"] = "IN_SCOPE"
        self.write_publication_plan(data)
        self.assertIn("RELEASE_PROHIBITION", self.codes())

    def test_90_evidence_exclusion_list_is_complete(self) -> None:
        data = self.publication_plan()
        data["api_evidence_handling"]["exclude_before_write_or_display"].pop()
        self.write_publication_plan(data)
        self.assertIn("EVIDENCE_HANDLING", self.codes())

    def test_91_current_visibility_cannot_return_to_private(self) -> None:
        data = self.publication_plan()
        data["visibility_strategy"]["dated_remote_observation"]["visibility"] = "private"
        self.write_publication_plan(data)
        codes = self.codes()
        self.assertIn("CURRENT_VISIBILITY", codes)
        self.assertNotIn("FINAL_RUN_ID", codes)

    def test_92_final_run_id_is_required(self) -> None:
        data = self.publication_plan()
        del data["publication_retry"]["final_result"]["workflow_run"]["run_id"]
        self.write_publication_plan(data)
        codes = self.codes()
        self.assertIn("FINAL_RUN_ID", codes)
        self.assertNotIn("FINAL_RUN_EVENT", codes)

    def test_93_each_final_verification_level_is_required_isolated(self) -> None:
        expected = {
            "level_a": "LEVEL_A_RESULT",
            "level_b": "LEVEL_B_RESULT",
            "level_c": "LEVEL_C_RESULT",
        }
        for level, code in expected.items():
            with self.subTest(level=level):
                data = self.publication_plan()
                del data["publication_retry"]["final_result"]["verification_levels"][level]
                self.write_publication_plan(data)
                self.assertIn(code, self.codes())
                shutil.copy2(
                    SOURCE / "governance/github-publication-plan.json",
                    self.root / "governance/github-publication-plan.json",
                )

    def test_94_active_tag_or_release_is_rejected_isolated(self) -> None:
        for field in ("git_tags", "github_releases"):
            with self.subTest(field=field):
                data = self.publication_plan()
                data["publication_retry"]["final_result"]["repository_counts"][field] = 1
                self.write_publication_plan(data)
                self.assertIn("CURRENT_RELEASE_STATE", self.codes())
                shutil.copy2(
                    SOURCE / "governance/github-publication-plan.json",
                    self.root / "governance/github-publication-plan.json",
                )

    def test_95_first_transition_checkpoint_is_immutable(self) -> None:
        data = self.publication_plan()
        data["publication_transition"]["initial_state"]["checkpoint"] = "0" * 40
        self.write_publication_plan(data)
        self.assertIn("FIRST_TRANSITION_RECORD", self.codes())

    def test_96_historical_and_final_runs_are_distinct(self) -> None:
        data = self.publication_plan()
        data["publication_retry"]["final_result"]["workflow_run"]["run_id"] = 29951087998
        self.write_publication_plan(data)
        codes = self.codes()
        self.assertIn("RUN_DISTINCTION", codes)
        self.assertIn("FINAL_RUN_ID", codes)

    def test_97_current_document_cannot_diverge_from_manifest(self) -> None:
        self.replace("README.md", "PUBLIC_REPOSITORY_VERIFIED", "PUBLICATION_RETRY_PREPARATION")
        codes = self.codes()
        self.assertIn("DOCUMENT_CURRENT_STATE", codes)
        self.assertIn("DOCUMENT_STALE_STATE", codes)

    def test_98_audit_is_offline(self) -> None:
        denied = AssertionError("network or subprocess access is forbidden")
        with (
            mock.patch.object(checker.subprocess, "run", side_effect=denied),
            mock.patch("socket.create_connection", side_effect=denied),
            mock.patch("urllib.request.urlopen", side_effect=denied),
        ):
            self.assertEqual((), checker.audit(self.root))

    def test_99_no_schema_5_validator_exists(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("def _check_plan_v5", source)
        self.assertNotIn("_check_plan_v5(", source)

    def test_100_security_cannot_return_to_publication_transition(self) -> None:
        self.replace(
            "SECURITY.md",
            "Private Vulnerability Reporting (PVR) is active.",
            "Private Vulnerability Reporting (PVR) is active during `PUBLICATION_TRANSITION`.",
        )
        self.assertIn("SECURITY_STALE_STATE", self.codes())

    def test_101_security_cannot_present_pvr_as_future(self) -> None:
        self.replace(
            "SECURITY.md",
            "Private Vulnerability Reporting (PVR) is active.",
            "Private Vulnerability Reporting (PVR) will be activated in the future.",
        )
        self.assertIn("SECURITY_STALE_STATE", self.codes())

    def test_102_decision_narrative_can_be_reworded(self) -> None:
        self.replace(
            "docs/decisions/README.md",
            "historical authorization, executed and superseded operationally\n  by the verified final public state",
            "historical authorization; the verified public result now supersedes its operational role",
        )
        self.assertEqual((), checker.audit(self.root))

    def test_103_documented_run_id_is_not_a_duplicate_machine_invariant(self) -> None:
        self.replace(
            "README.md",
            "30002915548",
            "a documented final workflow run",
        )
        self.assertEqual((), checker.audit(self.root))

    def test_104_python_prerequisite_cannot_be_generic(self) -> None:
        self.replace("docs/QUICKSTART.md", "Python 3.11+", "Python 3")
        findings = checker.audit(self.root)
        self.assertTrue(
            any(item.path == "docs/QUICKSTART.md" and item.code == "PYTHON_REQUIREMENT" for item in findings)
        )

    def test_104a_reuse_hashed_install_is_required(self) -> None:
        self.replace(
            "docs/QUICKSTART.md",
            "governance/requirements-reuse-build-6.2.0.txt",
            "install reuse from an unspecified source",
        )
        self.assertIn("REUSE_PREREQUISITE", self.codes())

    def test_105_ruleset_requires_up_to_date_branch(self) -> None:
        data = self.publication_plan()
        rules = data["remote_governance"]["controls"]["main_ruleset"]["desired_configuration"]["rules"]
        rules["require_branch_up_to_date"] = False
        self.write_publication_plan(data)
        codes = self.codes()
        self.assertIn("RULESET_UP_TO_DATE", codes)
        self.assertNotIn("RULESET_CONFIGURATION", codes)

    def test_106_security_is_in_current_document_set(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["offline_checker_contract"]["current_documents"].remove("SECURITY.md")
        self.write_publication_plan(data)
        self.assertIn("CURRENT_DOCUMENT_SET", self.codes())

    def test_107_decision_index_is_in_current_document_set(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["offline_checker_contract"]["current_documents"].remove(
            "docs/decisions/README.md"
        )
        self.write_publication_plan(data)
        self.assertIn("CURRENT_DOCUMENT_SET", self.codes())

    def test_108_snapshot_cannot_claim_live_verification(self) -> None:
        data = self.publication_plan()
        data["remote_governance"]["offline_checker_contract"]["live_github_state_verified"] = True
        self.write_publication_plan(data)
        self.assertIn("OFFLINE_SNAPSHOT_CONTRACT", self.codes())

    def test_109_success_verdict_is_explicitly_offline(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root)],
            cwd=self.root.parent,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("OFFLINE_GITHUB_GOVERNANCE_SNAPSHOT_CONSISTENT", result.stdout.strip())

    def test_110_schema_remains_exactly_6(self) -> None:
        self.assertEqual(6, self.publication_plan()["schema_version"])

    def test_111_historical_facts_remain_unchanged(self) -> None:
        data = self.publication_plan()
        self.assertEqual(
            "PUBLIC_TRANSITION_ROLLED_BACK",
            data["publication_transition"]["status"],
        )
        self.assertEqual(1895, data["publication_transition"]["public_exposure"]["duration_seconds_approx"])
        self.assertEqual(29951087998, data["publication_transition"]["workflow_run"]["run_id"])
        self.assertEqual(30002915548, data["publication_retry"]["final_result"]["workflow_run"]["run_id"])

    def test_112_checker_uses_no_github_process_or_network(self) -> None:
        denied = AssertionError("GitHub process, credential, or network access is forbidden")
        with (
            mock.patch.object(checker.subprocess, "run", side_effect=denied),
            mock.patch("socket.create_connection", side_effect=denied),
            mock.patch("urllib.request.urlopen", side_effect=denied),
        ):
            self.assertEqual((), checker.audit(self.root))


if __name__ == "__main__":
    unittest.main()
