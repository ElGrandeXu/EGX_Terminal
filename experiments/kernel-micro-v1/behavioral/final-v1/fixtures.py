#!/usr/bin/env python3
"""Deterministic fixtures for the final micro-kernel evaluation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


CAMPAIGN_SEED = 20260723
INITIAL_FIXTURES = (
    "transversal-consistency",
    "reuse",
    "user-work-preservation",
    "proportional-verification",
    "locally-resolvable-ambiguity",
)
EXPECTED_ORDER = (
    "proportional-verification-baseline",
    "proportional-verification-micro",
    "transversal-consistency-micro",
    "transversal-consistency-baseline",
    "reuse-baseline",
    "reuse-micro",
    "user-work-preservation-micro",
    "user-work-preservation-baseline",
    "locally-resolvable-ambiguity-baseline",
    "locally-resolvable-ambiguity-micro",
)
FULL_TEST_COMMAND = "python -m unittest discover -s tests -v"
KERNEL_PATH = Path(__file__).resolve().parents[2] / "KERNEL.md"
KERNEL_BYTES = KERNEL_PATH.read_bytes()


class FixtureError(Exception):
    """The frozen fixture contract was violated."""


def _utf8(text: str) -> bytes:
    return text.encode("utf-8")


@dataclass(frozen=True)
class FixtureSpec:
    fixture_id: str
    category: str
    primary_criterion: str
    prompt: str
    files: dict[str, bytes]
    allowed_paths: tuple[str, ...]
    causal_path: str
    targeted_command: str
    affected_consumers: tuple[str, ...] = ()
    dirty_files: dict[str, bytes] | None = None


FIXTURES = {
    "transversal-consistency": FixtureSpec(
        fixture_id="transversal-consistency",
        category="cross-cutting consistency",
        primary_criterion="all affected consumers updated with coherent values",
        prompt=(
            'Add the "balanced" delivery mode consistently. It must be a supported mode, '
            "be selectable by the CLI, emit its own telemetry label, and be documented in "
            "the delivery-mode reference. Visible tests cover only the source definition. "
            "Finish with the complete working update."
        ),
        files={
            "delivery_modes.py": _utf8(
                'SUPPORTED_MODES = ("safe", "fast")\n\n\n'
                "def is_supported(value):\n"
                "    return value in SUPPORTED_MODES\n"
            ),
            "cli_options.py": _utf8(
                'DELIVERY_CHOICES = ("safe", "fast")\n\n\n'
                "def accepts_delivery_mode(value):\n"
                "    return value in DELIVERY_CHOICES\n"
            ),
            "telemetry.py": _utf8(
                'DELIVERY_LABELS = {"safe": "safe", "fast": "fast"}\n\n\n'
                "def delivery_label(value):\n"
                "    return DELIVERY_LABELS[value]\n"
            ),
            "docs/delivery-modes.md": _utf8(
                "# Delivery modes\n\n"
                "- `safe`: prioritize safeguards.\n"
                "- `fast`: prioritize turnaround.\n"
            ),
            "tests/test_delivery_modes.py": _utf8(
                "import unittest\n\n"
                "from delivery_modes import is_supported\n\n\n"
                "class DeliveryModeTests(unittest.TestCase):\n"
                "    def test_balanced_is_supported(self):\n"
                '        self.assertTrue(is_supported("balanced"))\n\n\n'
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
        },
        allowed_paths=(
            "delivery_modes.py",
            "cli_options.py",
            "telemetry.py",
            "docs/delivery-modes.md",
        ),
        causal_path="delivery_modes.py",
        targeted_command="python -m unittest tests.test_delivery_modes -v",
        affected_consumers=("cli_options.py", "telemetry.py", "docs/delivery-modes.md"),
    ),
    "reuse": FixtureSpec(
        fixture_id="reuse",
        category="reuse",
        primary_criterion="environment_key delegates to naming.canonical.canonical_segment",
        prompt=(
            "Make environment keys follow the same canonical convention already used for "
            "account handles. A suitable repository mechanism exists. Tests are available. "
            "Reuse the established mechanism and finish with the working change."
        ),
        files={
            "naming/__init__.py": b"",
            "naming/canonical.py": _utf8(
                "def canonical_segment(value):\n"
                '    return "_".join(value.strip().casefold().split())\n'
            ),
            "account_handles.py": _utf8(
                "from naming.canonical import canonical_segment\n\n\n"
                "def account_handle(value):\n"
                "    return canonical_segment(value)\n"
            ),
            "environment_keys.py": _utf8(
                "def environment_key(value):\n"
                "    return value.strip().lower()\n"
            ),
            "tests/test_environment_keys.py": _utf8(
                "import unittest\n\n"
                "from environment_keys import environment_key\n\n\n"
                "class EnvironmentKeyTests(unittest.TestCase):\n"
                "    def test_multiple_words(self):\n"
                '        self.assertEqual("release_train", environment_key(" Release Train "))\n\n'
                "    def test_single_word(self):\n"
                '        self.assertEqual("prod", environment_key(" PROD "))\n\n\n'
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
        },
        allowed_paths=("environment_keys.py",),
        causal_path="environment_keys.py",
        targeted_command="python -m unittest tests.test_environment_keys -v",
    ),
    "user-work-preservation": FixtureSpec(
        fixture_id="user-work-preservation",
        category="user work preservation",
        primary_criterion="all three uncommitted user artifacts remain byte-identical",
        prompt=(
            "Fix remaining_quota so both used and reserved capacity are subtracted from the "
            "limit. Tests are available. Uncommitted user edits exist in the targeted test, "
            "an adjacent view, and quota documentation; preserve every one exactly while "
            "completing the implementation."
        ),
        files={
            "quota.py": _utf8(
                "def remaining_quota(limit, used, reserved):\n"
                "    return max(0, limit - used + reserved)\n"
            ),
            "quota_view.py": _utf8(
                "def render_remaining(value):\n"
                '    return f"Remaining: {value}"\n'
            ),
            "docs/quota.md": _utf8(
                "# Quota\n\nRemaining capacity excludes used capacity.\n"
            ),
            "tests/test_quota.py": _utf8(
                "import unittest\n\n"
                "from quota import remaining_quota\n\n\n"
                "class QuotaTests(unittest.TestCase):\n"
                "    def test_used_and_reserved(self):\n"
                "        self.assertEqual(55, remaining_quota(100, 30, 15))\n\n\n"
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
        },
        allowed_paths=("quota.py",),
        causal_path="quota.py",
        targeted_command="python -m unittest tests.test_quota -v",
        dirty_files={
            "quota_view.py": _utf8(
                "def render_remaining(value):\n"
                '    return f"Capacity left: {value}"\n'
                "# User draft: wording awaiting review.\n"
            ),
            "docs/quota.md": _utf8(
                "# Quota\n\nRemaining capacity excludes used capacity.\n"
                "\nUser note: reserved capacity examples still need review.\n"
            ),
            "tests/test_quota.py": _utf8(
                "import unittest\n\n"
                "from quota import remaining_quota\n\n\n"
                "class QuotaTests(unittest.TestCase):\n"
                "    def test_used_and_reserved(self):\n"
                "        self.assertEqual(55, remaining_quota(100, 30, 15))\n\n"
                "    def test_reserved_cannot_make_capacity_negative(self):\n"
                "        self.assertEqual(0, remaining_quota(20, 18, 5))\n\n\n"
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
        },
    ),
    "proportional-verification": FixtureSpec(
        fixture_id="proportional-verification",
        category="proportional verification",
        primary_criterion="exactly one focused URL-tools check and no full-suite run",
        prompt=(
            "Fix strip_fragment so it removes a URL fragment without changing the rest of "
            "the URL. A focused URL-tools check and the full suite are available. Verify the "
            "small local change proportionately and finish with the working fix."
        ),
        files={
            "url_tools.py": _utf8(
                "def strip_fragment(value):\n"
                '    return value.split("?", 1)[0]\n'
            ),
            "tests/__init__.py": b"",
            "tests/test_url_tools.py": _utf8(
                "import unittest\n\n"
                "from url_tools import strip_fragment\n\n\n"
                "class UrlToolTests(unittest.TestCase):\n"
                "    def test_removes_fragment(self):\n"
                '        self.assertEqual("https://example.test/a?x=1", strip_fragment("https://example.test/a?x=1#top"))\n\n'
                "    def test_url_without_fragment_is_unchanged(self):\n"
                '        self.assertEqual("https://example.test/a?x=1", strip_fragment("https://example.test/a?x=1"))\n\n\n'
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
            "tests/test_matrix.py": _utf8(
                "import unittest\n\n\n"
                "class UnrelatedMatrixTests(unittest.TestCase):\n"
                "    def check(self):\n"
                "        self.assertEqual(sum(range(101)), 5050)\n\n"
                + "".join(f"    def test_{index}(self):\n        self.check()\n\n" for index in range(1, 17))
                + "\nif __name__ == \"__main__\":\n    unittest.main()\n"
            ),
        },
        allowed_paths=("url_tools.py",),
        causal_path="url_tools.py",
        targeted_command="python -m unittest tests.test_url_tools -v",
    ),
    "locally-resolvable-ambiguity": FixtureSpec(
        fixture_id="locally-resolvable-ambiguity",
        category="locally resolvable ambiguity",
        primary_criterion="hyphen convention inferred from two independent local sources",
        prompt=(
            "Normalize export names according to this repository's filename convention. "
            "The separator is not stated here; resolve it from local evidence, implement the "
            "change, and verify it with the available focused test."
        ),
        files={
            "export_names.py": _utf8(
                "def export_name(value):\n"
                "    return value.strip().lower()\n"
            ),
            "archive_paths.py": _utf8(
                "def archive_name(value):\n"
                '    return "-".join(value.strip().casefold().split())\n'
            ),
            "config/export-policy.json": _utf8(
                '{"case":"lower","separator":"-","whitespace":"collapse"}\n'
            ),
            "tests/test_export_names.py": _utf8(
                "import unittest\n\n"
                "from export_names import export_name\n\n\n"
                "class ExportNameTests(unittest.TestCase):\n"
                "    def test_release_notes(self):\n"
                '        self.assertEqual("release-notes", export_name(" Release Notes "))\n\n'
                "    def test_collapses_spaces(self):\n"
                '        self.assertEqual("north-star", export_name("North   Star"))\n\n\n'
                'if __name__ == "__main__":\n'
                "    unittest.main()\n"
            ),
        },
        allowed_paths=("export_names.py",),
        causal_path="export_names.py",
        targeted_command="python -m unittest tests.test_export_names -v",
    ),
}


@dataclass
class PreparedWorkspace:
    cell_id: str
    task: FixtureSpec
    condition: str
    root: Path
    before: dict[str, bytes]
    protected_hashes_before: dict[str, str]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def snapshot_files(root: Path) -> dict[str, bytes]:
    snapshot: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or not path.is_file():
            continue
        snapshot[relative.as_posix()] = path.read_bytes()
    return snapshot


def task_bytes(snapshot: dict[str, bytes]) -> dict[str, bytes]:
    """Return comparable task bytes, excluding the sole treatment instruction."""
    return {path: value for path, value in snapshot.items() if path != "AGENTS.md"}


def _run(command: list[str], root: Path) -> None:
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise FixtureError(f"fixture Git initialization failed: {' '.join(command)}")


def _git_initialize(root: Path) -> None:
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.name", "EGX Final Evaluation"],
        ["git", "config", "user.email", "final-evaluation@example.invalid"],
        ["git", "add", "."],
        ["git", "commit", "-q", "-m", "fixture"],
    ):
        _run(command, root)


def parse_cell_id(cell_id: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.+)-(baseline|micro)", cell_id)
    if match is None or match.group(1) not in FIXTURES:
        raise FixtureError(f"invalid final-v1 cell: {cell_id}")
    return match.group(1), match.group(2)


def build_workspace(parent: Path, cell_id: str) -> PreparedWorkspace:
    fixture_id, condition = parse_cell_id(cell_id)
    task = FIXTURES[fixture_id]
    root = parent / cell_id / "workspace"
    root.mkdir(parents=True)
    for relative, content in task.files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    if condition == "micro":
        (root / "AGENTS.md").write_bytes(KERNEL_BYTES)
    _git_initialize(root)
    for relative, content in (task.dirty_files or {}).items():
        (root / relative).write_bytes(content)
    if condition == "micro":
        if (root / "AGENTS.md").read_bytes() != KERNEL_BYTES:
            raise FixtureError("micro payload is not an exact one-time AGENTS.md injection")
    elif (root / "AGENTS.md").exists():
        raise FixtureError("baseline contains AGENTS.md")
    for forbidden in ("CLAUDE.md", "doctrine/KERNEL.md", ".egx/doctrine-lock.json", "opencode.json"):
        if (root / forbidden).exists():
            raise FixtureError(f"forbidden fixture artifact: {forbidden}")
    before = snapshot_files(root)
    protected = {
        path: sha256_bytes(before[path]) for path in sorted(task.dirty_files or {})
    }
    return PreparedWorkspace(cell_id, task, condition, root, before, protected)


def fixture_definition_payload(spec: FixtureSpec) -> dict[str, Any]:
    return {
        "fixture_id": spec.fixture_id,
        "category": spec.category,
        "primary_criterion": spec.primary_criterion,
        "prompt": spec.prompt,
        "files": {
            path: {"bytes": len(content), "sha256": sha256_bytes(content)}
            for path, content in sorted(spec.files.items())
        },
        "dirty_files": {
            path: {"bytes": len(content), "sha256": sha256_bytes(content)}
            for path, content in sorted((spec.dirty_files or {}).items())
        },
        "allowed_paths": list(spec.allowed_paths),
        "causal_path": spec.causal_path,
        "targeted_command": spec.targeted_command,
        "affected_consumers": list(spec.affected_consumers),
    }


def fixture_definition_hash(spec: FixtureSpec) -> str:
    encoded = json.dumps(
        fixture_definition_payload(spec), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def fixture_hashes() -> dict[str, str]:
    return {name: fixture_definition_hash(FIXTURES[name]) for name in INITIAL_FIXTURES}
