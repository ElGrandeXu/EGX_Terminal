from __future__ import annotations

import hashlib
import importlib.util
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_licensing.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("check_licensing", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class LicensingTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str) -> None:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def metadata(self, extra: str = "", *, reverse: bool = False) -> str:
        documentation = '''[[annotations]]
path = ["README.md", "docs/**"]
precedence = "override"
SPDX-FileCopyrightText = "2026 Maxime Erard"
SPDX-License-Identifier = "CC-BY-4.0"
SPDX-FileComment = "Original documentation."
'''
        functional = '''[[annotations]]
path = [".gitattributes", ".gitignore", "scripts/**", "tests/**", "experiments/**", "governance/**", "licensing/**"]
precedence = "override"
SPDX-FileCopyrightText = "2026 Maxime Erard"
SPDX-License-Identifier = "Apache-2.0"
SPDX-FileComment = "Original functional artifacts and experiment bundles."
'''
        blocks = functional + documentation if reverse else documentation + functional
        return "version = 1\n\n" + blocks + extra

    def fixture(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory(prefix="licensing fixture ")
        root = Path(temporary.name)
        self.write(root, "README.md", "documentation\n")
        self.write(root, "docs/guide.md", "guide\n")
        self.write(root, ".gitignore", "cache/\n")
        self.write(root, ".gitattributes", "LICENSES/*.txt text eol=lf\n")
        self.write(root, "scripts/tool.py", "print('ok')\n")
        self.write(root, "tests/test_tool.py", "value = True\n")
        self.write(root, "experiments/demo/README.md", "experiment bundle\n")
        self.write(root, "governance/public-commit-identity.json", "{}\n")
        self.write(root, "REUSE.toml", self.metadata())
        shutil.copyfile(REPOSITORY_ROOT / "LICENSE", root / "LICENSE")
        for name in ("Apache-2.0.txt", "CC-BY-4.0.txt"):
            target = root / "LICENSES" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPOSITORY_ROOT / "LICENSES" / name, target)
        lock = json.loads((REPOSITORY_ROOT / "licensing/license-lock.json").read_text(encoding="utf-8"))
        self.write(root, "licensing/license-lock.json", json.dumps(lock, indent=2) + "\n")
        return temporary

    def files(self, root: Path) -> tuple[str, ...]:
        return tuple(sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()))

    def report(self, root: Path):
        return CHECK.audit(root, self.files(root), enforce_integrity=False)

    def codes(self, report) -> set[str]:
        return {finding.code for finding in report.findings}

    def test_minimal_compliant_repository(self) -> None:
        with self.fixture() as temporary:
            report = self.report(Path(temporary))
        self.assertEqual((), report.findings)
        self.assertEqual(report.covered, report.licensed)

    def test_document_is_cc_by(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            report = self.report(root)
            annotations, _ = CHECK.load_annotations(root)
        match = [item for item in annotations if any(CHECK.glob_matches(p, "docs/guide.md") for p in item.paths)]
        self.assertEqual("CC-BY-4.0", match[0].license_id)
        self.assertNotIn("BOUNDARY", self.codes(report))

    def test_script_is_apache(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            annotations, _ = CHECK.load_annotations(root)
        match = [item for item in annotations if any(CHECK.glob_matches(p, "scripts/tool.py") for p in item.paths)]
        self.assertEqual("Apache-2.0", match[0].license_id)

    def test_experiment_readme_is_apache(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.assertNotIn("BOUNDARY", self.codes(self.report(root)))
            self.assertEqual("Apache-2.0", CHECK.expected_license("experiments/demo/README.md"))

    def test_governance_metadata_is_apache(self) -> None:
        self.assertEqual(
            "Apache-2.0",
            CHECK.expected_license("governance/public-commit-identity.json"),
        )

    def test_unclassified_file(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "misc/unknown.txt", "unknown\n")
            report = self.report(root)
        self.assertIn("UNCLASSIFIED", self.codes(report))

    def test_unmatched_rule(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "REUSE.toml", self.metadata('''\n[[annotations]]
path = "missing/**"
precedence = "override"
SPDX-FileCopyrightText = "2026 Maxime Erard"
SPDX-License-Identifier = "Apache-2.0"
SPDX-FileComment = "Intentional test."
'''))
            report = self.report(root)
        self.assertIn("UNMATCHED_PATTERN", self.codes(report))

    def test_unintentional_overlap(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "REUSE.toml", self.metadata('''\n[[annotations]]
path = "docs/**"
precedence = "override"
SPDX-FileCopyrightText = "2026 Maxime Erard"
SPDX-License-Identifier = "CC-BY-4.0"
SPDX-FileComment = "Overlapping test rule."
'''))
            report = self.report(root)
        self.assertIn("MULTIPLE_CLASSIFICATION", self.codes(report))

    def test_unauthorized_identifier(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            text = self.metadata().replace('SPDX-License-Identifier = "CC-BY-4.0"', 'SPDX-License-Identifier = "MIT"', 1)
            self.write(root, "REUSE.toml", text)
            report = self.report(root)
        self.assertIn("LICENSE_ID", self.codes(report))

    def test_combined_license_expression_rejected(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            combined = "Apache-2.0 " + "OR " + "CC-BY-4.0"
            text = self.metadata().replace(
                'SPDX-License-Identifier = "CC-BY-4.0"',
                f'SPDX-License-Identifier = "{combined}"',
                1,
            )
            self.write(root, "REUSE.toml", text)
            report = self.report(root)
        self.assertIn("COMBINED_LICENSE", self.codes(report))

    def test_missing_license_text(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            (root / "LICENSES/Apache-2.0.txt").unlink()
            report = self.report(root)
        self.assertIn("MISSING_LICENSE_TEXT", self.codes(report))

    def test_incorrect_license_hash(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            with (root / "LICENSES/Apache-2.0.txt").open("a", encoding="utf-8") as stream:
                stream.write("changed\n")
            report = self.report(root)
        self.assertTrue({"LOCK_HASH", "CANONICAL_HASH"} <= self.codes(report))

    def test_invalid_lock_json(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "licensing/license-lock.json", "{ invalid\n")
            report = self.report(root)
        self.assertIn("INVALID_LOCK", self.codes(report))

    def test_incorrect_copyright(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "REUSE.toml", self.metadata().replace("2026 Maxime Erard", "2025 Someone Else", 1))
            report = self.report(root)
        self.assertIn("COPYRIGHT", self.codes(report))

    def test_internal_spdx_conflict(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "scripts/tool.py", "# SPDX-License-Identifier: CC-BY-4.0\n")
            report = self.report(root)
        self.assertIn("INTERNAL_LICENSE_CONFLICT", self.codes(report))

    def test_specific_third_party_annotation_is_valid(self) -> None:
        extra = '''\n[[annotations]]
path = "third_party/vendor.txt"
precedence = "override"
SPDX-FileCopyrightText = "2024 Example Corporation"
SPDX-License-Identifier = "Apache-2.0"
SPDX-FileComment = "THIRD_PARTY_MATERIAL_WITH_PROVEN_LICENSE: source=https://example.invalid/vendor; license evidence reviewed"
'''
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "third_party/vendor.txt", "vendored content\n")
            self.write(root, "REUSE.toml", self.metadata(extra))
            report = self.report(root)
        self.assertEqual((), report.findings)

    def test_unclear_third_party_provenance_is_blocking(self) -> None:
        extra = '''\n[[annotations]]
path = "third_party/unclear.txt"
precedence = "override"
SPDX-FileCopyrightText = "Unknown"
SPDX-License-Identifier = "Apache-2.0"
SPDX-FileComment = "PROVENANCE_UNCLEAR"
'''
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "third_party/unclear.txt", "unknown origin\n")
            self.write(root, "REUSE.toml", self.metadata(extra))
            report = self.report(root)
        self.assertIn("PROVENANCE_UNCLEAR", self.codes(report))

    def test_deprecated_dep5_rejected(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, ".reuse/dep5", "Format: test\n")
            report = self.report(root)
        self.assertIn("DEPRECATED_DEP5", self.codes(report))

    def test_empty_file_is_exempt(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "unclassified/empty.txt", "")
            report = self.report(root)
        self.assertNotIn("UNCLASSIFIED", self.codes(report))

    def test_path_with_spaces(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "docs/file with spaces.md", "document\n")
            report = self.report(root)
        self.assertEqual((), report.findings)

    def test_cli_resolves_repository_outside_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run([sys.executable, str(SCRIPT_PATH)], cwd=temporary, check=False, capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn(str(REPOSITORY_ROOT), completed.stdout)

    def test_rule_order_does_not_change_disjoint_mapping(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            first = self.report(root)
            self.write(root, "REUSE.toml", self.metadata(reverse=True))
            second = self.report(root)
        self.assertEqual(first.findings, second.findings)
        self.assertEqual(first.licensed, second.licensed)

    def test_archive_annotation_does_not_modify_file(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            target = root / "experiments/demo/README.md"
            before = hashlib.sha256(target.read_bytes()).hexdigest()
            report = self.report(root)
            after = hashlib.sha256(target.read_bytes()).hexdigest()
        self.assertEqual((), report.findings)
        self.assertEqual(before, after)

    def test_tree_hash_is_independent_of_input_order_and_uses_posix_keys(self) -> None:
        entries = (
            ("Nested/File.md", b"upper\n"),
            ("nested/file.md", b"lower\n"),
            ("README.md", b"readme\n"),
            ("alpha.txt", b"alpha\n"),
        )
        expected_order = tuple(
            relative
            for relative, _ in sorted(entries, key=lambda item: (item[0].casefold(), item[0]))
        )
        self.assertEqual(
            ("alpha.txt", "Nested/File.md", "nested/file.md", "README.md"),
            expected_order,
        )
        self.assertTrue(all("\\" not in relative for relative in expected_order))
        self.assertEqual(
            CHECK._tree_sha256_entries(entries),
            CHECK._tree_sha256_entries(reversed(entries)),
        )

    def test_tree_hash_is_cwd_independent_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="archive hash ") as temporary:
            root = Path(temporary) / "archive with spaces"
            self.write(root, "Nested/File.md", "upper\n")
            self.write(root, "nested/file.md", "lower\n")
            before = CHECK.tree_sha256(root)
            previous = Path.cwd()
            try:
                os.chdir(root.parent)
                after = CHECK.tree_sha256(root)
            finally:
                os.chdir(previous)
        self.assertEqual(before, after)

    def test_real_archive_hash_and_frozen_results_remain_unchanged(self) -> None:
        experiment_root = REPOSITORY_ROOT / "experiments"
        before = {
            path.relative_to(experiment_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in experiment_root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(
            CHECK.EXPECTED_ARCHIVE_HASH,
            CHECK.tree_sha256(experiment_root / "kernel-v1"),
        )
        self.assertEqual([], CHECK.check_integrity(REPOSITORY_ROOT))
        after = {
            path.relative_to(experiment_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in experiment_root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_experimental_hash_inputs_force_lf_checkouts(self) -> None:
        paths = tuple(
            path
            for path in CHECK.tracked_files(REPOSITORY_ROOT)
            if path.startswith("experiments/")
            and (path.endswith((".md", ".py", ".json")) or path.endswith("/.gitattributes"))
        )
        completed = subprocess.run(
            ["git", "-C", str(REPOSITORY_ROOT), "check-attr", "eol", "--", *paths],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertTrue(paths)
        self.assertTrue(
            all(line.endswith(": eol: lf") for line in completed.stdout.splitlines()),
            completed.stdout,
        )

    def test_diagnostic_and_return_code(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "misc/problem.txt", "problem\n")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = CHECK.main(("--root", str(root)))
            diagnostic = output.getvalue()
        self.assertEqual(1, result)
        self.assertIn("misc/problem.txt [UNCLASSIFIED]", diagnostic)

    def test_spdx_strings_in_checker_and_tests_are_not_headers(self) -> None:
        with self.fixture() as temporary:
            root = Path(temporary)
            self.write(root, "scripts/tool.py", 'TAG = "# SPDX-License-Identifier: CC-BY-4.0"\n')
            self.write(root, "tests/test_tool.py", 'COPYRIGHT = "# SPDX-FileCopyrightText: Someone"\n')
            report = self.report(root)
        self.assertNotIn("INTERNAL_LICENSE_CONFLICT", self.codes(report))
        self.assertNotIn("INTERNAL_COPYRIGHT_CONFLICT", self.codes(report))


if __name__ == "__main__":
    unittest.main()
