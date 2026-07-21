from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "scripts"))
import check_release_tree as checker  # noqa: E402


class ReleaseTreeTests(unittest.TestCase):
    def repository(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory(prefix="release tree ")
        root = Path(temporary.name) / "repository with spaces"
        shutil.copytree(
            SOURCE,
            root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
        )
        self.git(root, "init", "--quiet", "--initial-branch=main")
        self.git(root, "config", "user.name", "Release Fixture")
        self.git(root, "config", "user.email", "123456+release-fixture@users.noreply.github.com")
        self.git(root, "config", "core.autocrlf", "false")
        return temporary, root

    def git(self, root: Path, *arguments: str) -> str:
        process = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        return process.stdout.strip()

    def commit_and_tag(self, root: Path) -> tuple[str, str]:
        self.git(root, "add", "-A")
        self.git(root, "commit", "--quiet", "-m", "test: release tree")
        target = self.git(root, "rev-parse", "HEAD")
        self.git(root, "tag", "-a", "v1.0.1", "-m", "fixture release")
        tag_object = self.git(root, "rev-parse", "refs/tags/v1.0.1")
        return target, tag_object

    def test_exact_tag_checkout_passes_content_validation(self) -> None:
        temporary, root = self.repository()
        with temporary:
            target, tag_object = self.commit_and_tag(root)
            self.git(root, "checkout", "--quiet", "--detach", "refs/tags/v1.0.1")
            actual, json_count, toml_count = checker.validate(
                root, "refs/tags/v1.0.1", tag_object
            )
        self.assertEqual(target, actual)
        self.assertGreater(json_count, 0)
        self.assertGreater(toml_count, 0)

    def test_declared_tag_tree_with_forbidden_content_cannot_pass(self) -> None:
        temporary, root = self.repository()
        with temporary:
            (root / "AGENTS.md").write_text("active harness instruction\n", encoding="utf-8")
            _, tag_object = self.commit_and_tag(root)
            self.git(root, "checkout", "--quiet", "--detach", "refs/tags/v1.0.1")
            with self.assertRaises(checker.ReleaseTreeError) as context:
                checker.validate(root, "refs/tags/v1.0.1", tag_object)
        self.assertIn("check_neutral_root.py failed", str(context.exception))

    def test_policy_main_checkout_cannot_substitute_for_release_tree(self) -> None:
        temporary, root = self.repository()
        with temporary:
            target, tag_object = self.commit_and_tag(root)
            (root / "post-release.txt").write_text("later policy commit\n", encoding="utf-8")
            self.git(root, "add", "post-release.txt")
            self.git(root, "commit", "--quiet", "-m", "test: later policy")
            with self.assertRaises(checker.ReleaseTreeError) as context:
                checker.verify_exact_tag_checkout(root, "refs/tags/v1.0.1", tag_object)
            self.assertIn("TAG_TREE_MISMATCH", str(context.exception))
            self.git(root, "checkout", "--quiet", "--detach", "refs/tags/v1.0.1")
            self.assertEqual(
                target,
                checker.verify_exact_tag_checkout(root, "refs/tags/v1.0.1", tag_object),
            )


if __name__ == "__main__":
    unittest.main()
