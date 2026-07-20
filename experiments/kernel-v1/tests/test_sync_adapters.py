from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / "experiments" / "kernel-v1" / "tools" / "sync_adapters.py"
SOURCE = REPOSITORY / "experiments" / "kernel-v1" / "KERNEL.md"
EXPECTED_FILES = {
    Path(".egx/doctrine-lock.json"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("doctrine/KERNEL.md"),
}


class SyncAdaptersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="egx kernel v1 ")
        self.base = Path(self.temporary.name)
        try:
            self.base.relative_to(REPOSITORY)
        except ValueError:
            pass
        else:
            self.fail("temporary test directory must be outside the repository")
        self.target = self.base / "workspace with spaces"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, command: str, target: Path | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(SCRIPT), command, "--target", str(target or self.target)],
            cwd=REPOSITORY,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_successfully(self, target: Path | None = None) -> Path:
        selected = target or self.target
        result = self.run_cli("write", selected)
        self.assertEqual(0, result.returncode, result.stderr)
        return selected

    @staticmethod
    def files_under(target: Path) -> set[Path]:
        return {path.relative_to(target) for path in target.rglob("*") if path.is_file()}

    def test_plan_does_not_write(self) -> None:
        result = self.run_cli("plan")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.target.exists())
        self.assertIn("CREATE AGENTS.md", result.stdout)

    def test_plan_reports_drift_without_repairing_it(self) -> None:
        self.write_successfully()
        agents = self.target / "AGENTS.md"
        agents.write_bytes(b"drift")
        result = self.run_cli("plan")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("UPDATE AGENTS.md", result.stdout)
        self.assertEqual(b"drift", agents.read_bytes())

    def test_write_creates_only_expected_files(self) -> None:
        self.write_successfully()
        self.assertEqual(EXPECTED_FILES, self.files_under(self.target))

    def test_canonical_is_byte_identical_to_experimental_source(self) -> None:
        self.write_successfully()
        self.assertEqual(SOURCE.read_bytes(), (self.target / "doctrine/KERNEL.md").read_bytes())

    def test_agents_is_byte_identical_to_canonical(self) -> None:
        self.write_successfully()
        self.assertEqual(
            (self.target / "doctrine/KERNEL.md").read_bytes(),
            (self.target / "AGENTS.md").read_bytes(),
        )

    def test_claude_is_exact_import_without_final_newline(self) -> None:
        self.write_successfully()
        self.assertEqual(b"@doctrine/KERNEL.md", (self.target / "CLAUDE.md").read_bytes())

    def test_lockfile_is_valid_stable_and_coherent(self) -> None:
        self.write_successfully()
        raw = (self.target / ".egx/doctrine-lock.json").read_bytes()
        lock = json.loads(raw.decode("utf-8"))
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        self.assertEqual(1, lock["schema_version"])
        self.assertEqual("experimental", lock["status"])
        self.assertEqual("doctrine/KERNEL.md", lock["canonical"]["path"])
        self.assertEqual(
            ["AGENTS.md", "CLAUDE.md", "doctrine/KERNEL.md"],
            [entry["path"] for entry in lock["managed_files"]],
        )
        for entry in lock["managed_files"]:
            content = (self.target / entry["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])

    def test_no_opencode_configuration_is_created(self) -> None:
        self.write_successfully()
        self.assertFalse((self.target / "opencode.json").exists())

    def test_check_succeeds_immediately_after_write(self) -> None:
        self.write_successfully()
        result = self.run_cli("check")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("OK: target synchronized", result.stdout)

    def test_second_write_is_idempotent(self) -> None:
        self.write_successfully()
        before = {
            relative: ((self.target / relative).read_bytes(), (self.target / relative).stat().st_mtime_ns)
            for relative in EXPECTED_FILES
        }
        result = self.run_cli("write")
        self.assertEqual(0, result.returncode, result.stderr)
        after = {
            relative: ((self.target / relative).read_bytes(), (self.target / relative).stat().st_mtime_ns)
            for relative in EXPECTED_FILES
        }
        self.assertEqual(before, after)
        self.assertIn("already synchronized", result.stdout)

    def test_write_repairs_drift_when_lock_proves_ownership(self) -> None:
        self.write_successfully()
        agents = self.target / "AGENTS.md"
        agents.write_bytes(b"drift")
        result = self.run_cli("write")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(SOURCE.read_bytes(), agents.read_bytes())
        self.assertEqual(0, self.run_cli("check").returncode)

    def test_check_detects_agents_drift(self) -> None:
        self.write_successfully()
        (self.target / "AGENTS.md").write_bytes(b"drift")
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("managed file drift: AGENTS.md", result.stderr)

    def test_check_detects_claude_drift(self) -> None:
        self.write_successfully()
        (self.target / "CLAUDE.md").write_bytes(b"@wrong/path")
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("managed file drift: CLAUDE.md", result.stderr)

    def test_check_detects_canonical_drift(self) -> None:
        self.write_successfully()
        (self.target / "doctrine/KERNEL.md").write_bytes(b"drift")
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("canonical differs from experimental kernel", result.stderr)

    def test_check_detects_incomplete_lockfile(self) -> None:
        self.write_successfully()
        (self.target / ".egx/doctrine-lock.json").write_text(
            '{"schema_version": 1}\n', encoding="utf-8", newline="\n"
        )
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("invalid lockfile", result.stderr)

    def test_check_detects_extra_file_claimed_as_managed(self) -> None:
        self.write_successfully()
        lock_path = self.target / ".egx/doctrine-lock.json"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["managed_files"].append(
            {
                "encoding": "UTF-8",
                "final_line_ending": False,
                "line_endings": "LF",
                "path": "EXTRA.md",
                "sha256": hashlib.sha256(b"").hexdigest(),
            }
        )
        lock_path.write_text(
            json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("incomplete or inconsistent", result.stderr)

    def test_check_absent_target_does_not_write(self) -> None:
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertFalse(self.target.exists())

    def test_write_refuses_unmanaged_agents(self) -> None:
        self.target.mkdir()
        agents = self.target / "AGENTS.md"
        agents.write_bytes(b"user content")
        result = self.run_cli("write")
        self.assertEqual(3, result.returncode)
        self.assertEqual(b"user content", agents.read_bytes())
        self.assertEqual({Path("AGENTS.md")}, self.files_under(self.target))

    def test_write_refuses_unmanaged_claude(self) -> None:
        self.target.mkdir()
        claude = self.target / "CLAUDE.md"
        claude.write_bytes(b"user content")
        result = self.run_cli("write")
        self.assertEqual(3, result.returncode)
        self.assertEqual(b"user content", claude.read_bytes())
        self.assertEqual({Path("CLAUDE.md")}, self.files_under(self.target))

    def test_write_refuses_unrelated_unmanaged_file(self) -> None:
        self.target.mkdir()
        unrelated = self.target / "README.txt"
        unrelated.write_bytes(b"workspace content")
        result = self.run_cli("write")
        self.assertEqual(3, result.returncode)
        self.assertEqual(b"workspace content", unrelated.read_bytes())
        self.assertEqual({Path("README.txt")}, self.files_under(self.target))

    def test_write_refuses_incoherent_lock_before_any_change(self) -> None:
        self.write_successfully()
        agents = self.target / "AGENTS.md"
        agents.write_bytes(b"drift")
        lock_path = self.target / ".egx/doctrine-lock.json"
        lock_path.write_bytes(b"{}\n")
        before = {relative: (self.target / relative).read_bytes() for relative in EXPECTED_FILES}
        result = self.run_cli("write")
        self.assertEqual(3, result.returncode)
        after = {relative: (self.target / relative).read_bytes() for relative in EXPECTED_FILES}
        self.assertEqual(before, after)

    def test_write_refuses_real_repository_root(self) -> None:
        result = self.run_cli("write", REPOSITORY)
        self.assertEqual(3, result.returncode)
        self.assertIn("repository root", result.stderr)

    def test_refusal_does_not_present_workspace_as_synchronized(self) -> None:
        self.target.mkdir()
        (self.target / "AGENTS.md").write_bytes(b"user content")
        result = self.run_cli("write")
        self.assertEqual(3, result.returncode)
        self.assertFalse((self.target / ".egx/doctrine-lock.json").exists())
        self.assertFalse((self.target / "doctrine/KERNEL.md").exists())
        self.assertFalse((self.target / "CLAUDE.md").exists())

    def test_hashes_are_independently_recalculated(self) -> None:
        self.write_successfully()
        lock = json.loads((self.target / ".egx/doctrine-lock.json").read_text(encoding="utf-8"))
        independent = {
            relative.as_posix(): hashlib.sha256((self.target / relative).read_bytes()).hexdigest()
            for relative in (Path("AGENTS.md"), Path("CLAUDE.md"), Path("doctrine/KERNEL.md"))
        }
        claimed = {entry["path"]: entry["sha256"] for entry in lock["managed_files"]}
        self.assertEqual(independent, claimed)

    def test_outputs_are_deterministic_between_distinct_workspaces(self) -> None:
        first = self.base / "first workspace"
        second = self.base / "second workspace"
        self.write_successfully(first)
        self.write_successfully(second)
        self.assertEqual(EXPECTED_FILES, self.files_under(first))
        self.assertEqual(EXPECTED_FILES, self.files_under(second))
        for relative in EXPECTED_FILES:
            self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())

    def test_check_detects_encoding_and_line_ending_drift(self) -> None:
        self.write_successfully()
        (self.target / "CLAUDE.md").write_bytes(b"\xef\xbb\xbf@doctrine/KERNEL.md\r\n")
        result = self.run_cli("check")
        self.assertEqual(4, result.returncode)
        self.assertIn("UTF-8 BOM", result.stderr)
        self.assertIn("not LF-only", result.stderr)


if __name__ == "__main__":
    unittest.main()
