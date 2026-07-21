from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_markdown_links.py"
sys.path.insert(0, str(ROOT / "scripts"))
import check_markdown_links as checker  # noqa: E402


class MarkdownLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="markdown links ")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str | bytes = "") -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")

    def audit(self, files: tuple[str, ...] = ("README.md",)) -> tuple[checker.Finding, ...]:
        return checker.audit(self.root, files)

    def make_git_repo(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=self.root, check=True, capture_output=True)

    def test_01_valid_relative_link(self) -> None:
        self.write("README.md", "[target](docs/target.md)\n")
        self.write("docs/target.md", "# Target\n")
        self.assertEqual(self.audit(("README.md", "docs/target.md")), ())

    def test_02_broken_link(self) -> None:
        self.write("README.md", "[missing](missing.md)\n")
        self.assertEqual(self.audit()[0].code, "MISSING_PATH")

    def test_03_valid_anchor(self) -> None:
        self.write("README.md", "# Exact title\n\n<a id=\"evidence\"></a>\n\n[go](#exact-title) [evidence](#evidence)\n")
        self.assertEqual(self.audit(), ())

    def test_04_missing_anchor(self) -> None:
        self.write("README.md", "# Existing\n\n[go](#absent)\n")
        self.assertEqual(self.audit()[0].code, "MISSING_ANCHOR")

    def test_05_duplicate_github_anchors(self) -> None:
        self.write("README.md", "# Same\n\n# Same\n\n[second](#same-1)\n")
        self.assertEqual(self.audit(), ())

    def test_06_unicode_heading(self) -> None:
        self.write("README.md", "# Évaluation finale\n\n[go](#évaluation-finale)\n")
        self.assertEqual(self.audit(), ())

    def test_07_path_with_spaces(self) -> None:
        self.write("README.md", "[space](<docs/target file.md>)\n")
        self.write("docs/target file.md", "# Target\n")
        self.assertEqual(self.audit(("README.md", "docs/target file.md")), ())

    def test_08_local_image(self) -> None:
        self.write("README.md", "![pixel](images/pixel.png)\n")
        self.write("images/pixel.png", b"PNG")
        self.assertEqual(self.audit(), ())

    def test_09_root_link(self) -> None:
        self.write("README.md", "[root](/docs/target.md)\n")
        self.write("docs/target.md", "# Target\n")
        self.assertEqual(self.audit(("README.md", "docs/target.md")), ())

    def test_10_external_link_ignored(self) -> None:
        self.write("README.md", "[external](https://example.invalid/never)\n")
        self.assertEqual(self.audit(), ())

    def test_11_url_in_code_fence_ignored(self) -> None:
        self.write("README.md", "```markdown\n[bad](missing.md)\n```\n")
        self.assertEqual(self.audit(), ())

    def test_12_json_output(self) -> None:
        self.write("README.md", "# Valid\n")
        self.make_git_repo()
        report = self.root / "report.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--json", str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["findings"], [])

    def test_13_different_current_working_directory(self) -> None:
        self.write("README.md", "# Valid\n")
        self.make_git_repo()
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], cwd=self.root.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_14_diagnostic_and_return_code(self) -> None:
        self.write("README.md", "[broken](nope.md)\n")
        self.make_git_repo()
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md:1 [MISSING_PATH]", result.stdout)


if __name__ == "__main__":
    unittest.main()
