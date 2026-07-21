from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_public_surface.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("check_public_surface", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class PublicSurfaceTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str = "safe\n") -> Path:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def categories(self, violations: tuple[object, ...]) -> set[str]:
        return {violation.category for violation in violations}

    def init_git(self, root: Path) -> None:
        completed = subprocess.run(
            ["git", "init", "--quiet", str(root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def git_add(self, root: Path, relative: str) -> None:
        completed = subprocess.run(
            ["git", "-C", str(root), "add", "--", relative],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_safe_temporary_tree_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "portable public documentation\n")
            self.assertEqual((), CHECK.scan_paths(root, (Path("README.md"),)))

    def test_path_outside_root_is_rejected_without_being_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            violations = CHECK.scan_paths(root, (Path("..") / "outside.txt",))
        self.assertEqual({"TRACKED_PATH"}, self.categories(violations))

    def test_windows_personal_path_is_detected(self) -> None:
        separator = chr(92)
        personal = "C:" + separator + "Users" + separator + "alice" + separator + "project"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "config.txt", f"workspace={personal}\n")
            violations = CHECK.scan_paths(root, (Path("config.txt"),))
        self.assertIn("PERSONAL_PATH", self.categories(violations))

    def test_unix_personal_path_is_detected(self) -> None:
        personal = "/" + "home" + "/alice/project"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "config.txt", f"workspace={personal}\n")
            violations = CHECK.scan_paths(root, (Path("config.txt"),))
        self.assertIn("PERSONAL_PATH", self.categories(violations))

    def test_local_account_requires_machine_context(self) -> None:
        account = "ma" + "xer"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "machine.ini", "username=" + account + "\n")
            self.write(root, "prose.txt", "A plain mention of " + account + " is not machine data.\n")
            violations = CHECK.scan_paths(
                root, (Path("machine.ini"), Path("prose.txt"))
            )
        account_violations = [
            item for item in violations if item.category == "LOCAL_ACCOUNT"
        ]
        self.assertEqual(1, len(account_violations))
        self.assertEqual("machine.ini", account_violations[0].path)

    def test_tracked_env_file_is_detected(self) -> None:
        name = "." + "env"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, name, "SETTING=placeholder\n")
            violations = CHECK.scan_paths(root, (Path(name),))
        self.assertIn("SENSITIVE_FILENAME", self.categories(violations))

    def test_plausible_secret_signature_is_detected(self) -> None:
        value = "AK" + "IA" + ("A" * 16)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "settings.txt", "value=" + value + "\n")
            violations = CHECK.scan_paths(root, (Path("settings.txt"),))
        self.assertIn("SECRET_SIGNATURE", self.categories(violations))

    def test_private_key_pem_is_detected(self) -> None:
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "fixture.txt", marker + "\nnot-a-real-key\n")
            violations = CHECK.scan_paths(root, (Path("fixture.txt"),))
        self.assertIn("PRIVATE_KEY", self.categories(violations))

    def test_cache_or_temporary_file_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relative = Path("build") / "__pycache__" / "module.pyc"
            self.write(root, relative.as_posix(), "not bytecode\n")
            violations = CHECK.scan_paths(root, (relative,))
        self.assertIn("TEMPORARY_FILE", self.categories(violations))

    def test_file_over_size_limit_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "large.txt"
            target.write_bytes(b"x" * (CHECK.LARGE_FILE_LIMIT + 1))
            violations = CHECK.scan_paths(root, (Path("large.txt"),))
        self.assertIn("LARGE_FILE", self.categories(violations))

    def test_loopback_hashes_versions_and_fictional_examples_are_accepted(self) -> None:
        content = (
            "endpoints=http://localhost:8000 http://127.0.0.1:11434 http://[::1]\n"
            "version=1.17.9\n"
            "commit=0123456789abcdef0123456789abcdef01234567\n"
            "sha256=" + ("a" * 64) + "\n"
            "example=203.0.113.7\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "evidence.txt", content)
            self.assertEqual(
                (), CHECK.scan_paths(root, (Path("evidence.txt"),))
            )

    def test_nested_fixture_does_not_violate_neutral_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relative = Path("fixtures") / "sample" / "AGENTS.md"
            self.write(root, relative.as_posix(), "intentional nested fixture\n")
            self.assertEqual((), CHECK.scan_paths(root, (relative,)))

    def test_each_registered_active_surface_is_rejected(self) -> None:
        surfaces = CHECK.load_registered_surfaces(REPOSITORY_ROOT)
        for surface in surfaces:
            with self.subTest(path=surface.path.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    target = root / surface.path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if surface.kind == "path_prefix":
                        target.mkdir()
                    else:
                        target.write_text("fixture\n", encoding="utf-8")
                    self.assertIn("NEUTRAL_ROOT", self.categories(CHECK.scan_paths(root, ())))

    def test_registered_surface_symlink_is_rejected_when_supported(self) -> None:
        surface = CHECK.load_registered_surfaces(REPOSITORY_ROOT)[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "fixture-target"
            target.write_text("fixture\n", encoding="utf-8")
            link = root / surface.path
            link.parent.mkdir(parents=True, exist_ok=True)
            try:
                link.symlink_to(target)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")
            self.assertIn("NEUTRAL_ROOT", self.categories(CHECK.scan_paths(root, ())))

    def test_cli_is_independent_of_current_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_PATH)],
                cwd=temporary,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn(str(REPOSITORY_ROOT), completed.stdout)

    def test_tracked_filename_with_spaces_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="public surface ") as temporary:
            root = Path(temporary)
            relative = "docs/file with spaces.md"
            self.init_git(root)
            self.write(root, relative, "safe\n")
            self.git_add(root, relative)
            self.assertEqual((Path(relative),), CHECK.tracked_files(root))
            self.assertEqual((), CHECK.scan_paths(root, CHECK.tracked_files(root)))

    def test_diagnostics_and_return_code_are_coherent(self) -> None:
        separator = chr(92)
        personal = "C:" + separator + "Users" + separator + "alice" + separator + "private"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.init_git(root)
            self.write(root, "bad.txt", "path=" + personal + "\n")
            self.git_add(root, "bad.txt")
            output = io.StringIO()
            previous = Path.cwd()
            try:
                os.chdir(Path(temporary).parent)
                with contextlib.redirect_stdout(output):
                    result = CHECK.main(("--root", str(root)))
            finally:
                os.chdir(previous)
        diagnostic = output.getvalue()
        self.assertEqual(1, result)
        self.assertIn("bad.txt:1", diagnostic)
        self.assertIn("[PERSONAL_PATH]", diagnostic)
        self.assertIn("absolute Windows user-home path", diagnostic)
        self.assertNotIn(personal, diagnostic)

    def test_content_only_mode_accepts_archive_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write(root, "README.md", "archive content\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = CHECK.main(("--content-only", "--root", str(root)))
        self.assertEqual(0, result, output.getvalue())
        self.assertIn("present source files", output.getvalue())


if __name__ == "__main__":
    unittest.main()
