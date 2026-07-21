from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_neutral_root.py"
SPEC = importlib.util.spec_from_file_location("check_neutral_root", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class NeutralRootTests(unittest.TestCase):
    def test_compliant_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual((), CHECK.find_forbidden_paths(root))

    def test_detects_each_forbidden_path(self) -> None:
        for relative in CHECK.FORBIDDEN_PATHS:
            with self.subTest(path=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("test fixture\n", encoding="utf-8")
                    self.assertEqual((relative,), CHECK.find_forbidden_paths(root))
                    original_repository_root = CHECK.repository_root
                    CHECK.repository_root = lambda: root
                    try:
                        output = io.StringIO()
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(1, CHECK.main())
                    finally:
                        CHECK.repository_root = original_repository_root
                    self.assertIn(relative.as_posix(), output.getvalue())

    def test_ignores_nested_fixture_agents_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "fixtures" / "sample" / "AGENTS.md"
            fixture.parent.mkdir(parents=True)
            fixture.write_text("nested fixture\n", encoding="utf-8")
            self.assertEqual((), CHECK.find_forbidden_paths(root))

    def test_cli_resolves_root_outside_current_directory(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
