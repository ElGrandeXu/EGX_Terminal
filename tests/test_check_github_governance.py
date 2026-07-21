from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / "scripts/check_github_governance.py"
sys.path.insert(0, str(SOURCE / "scripts"))
import check_github_governance as checker  # noqa: E402


FIXTURE_FILES = (
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/research_proposal.md",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    "governance/github-actions-lock.json",
    "governance/github-publication-plan.json",
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
        self.replace(".github/workflows/validate.yml", "reuse==6.2.0", "reuse==6.1.0")
        self.assertIn("REUSE_VERSION", self.codes())

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
        self.assertIn("PUBLICATION_PLAN", self.codes())

    def test_17b_planned_remote_status_is_rejected_after_publication(self) -> None:
        path = self.root / "governance/github-publication-plan.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["metadata"]["status"] = "PLANNED_NOT_APPLIED"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertIn("REMOTE_STATUS", self.codes())

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


if __name__ == "__main__":
    unittest.main()
