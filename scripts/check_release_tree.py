#!/usr/bin/env python3
"""Validate the exact content tree targeted by a release-tag event.

Release authorization is deliberately checked elsewhere from canonical main.
This checker proves that its working tree is the triggering tag target and runs
only validations that are meaningful against that released content.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Sequence


TAG_REF_PATTERN = re.compile(r"^refs/tags/v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$")
CONTENT_CHECKS = (
    "check_neutral_root.py",
    "check_public_surface.py",
    "check_licensing.py",
    "check_markdown_links.py",
    "check_github_governance.py",
)


class ReleaseTreeError(RuntimeError):
    """The checkout is not the exact release tree or its content is invalid."""


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _oid(root: Path, revision: str) -> str:
    process = _git(root, "rev-parse", "--verify", revision)
    if process.returncode:
        raise ReleaseTreeError(f"cannot resolve {revision}; the full tag ref is required")
    return process.stdout.strip()


def verify_exact_tag_checkout(root: Path, expected_ref: str, event_sha: str | None) -> str:
    if TAG_REF_PATTERN.fullmatch(expected_ref) is None:
        raise ReleaseTreeError("expected ref must be an exact stable release tag under refs/tags/")
    head = _oid(root, "HEAD^{commit}")
    tag_target = _oid(root, f"{expected_ref}^{{commit}}")
    if head != tag_target:
        raise ReleaseTreeError(
            f"TAG_TREE_MISMATCH: HEAD {head} is not the target {tag_target} of {expected_ref}"
        )
    if event_sha:
        event_target = _oid(root, f"{event_sha}^{{commit}}")
        if event_target != tag_target:
            raise ReleaseTreeError("TAG_EVENT_MISMATCH: GITHUB_SHA does not resolve to the triggering tag target")
    status = _git(root, "status", "--porcelain=v1")
    if status.returncode or status.stdout:
        raise ReleaseTreeError("release checkout is not clean")
    return tag_target


def _run(root: Path, command: Sequence[str], label: str) -> None:
    process = subprocess.run(command, cwd=root, check=False)
    if process.returncode:
        raise ReleaseTreeError(f"{label} failed with exit code {process.returncode}")


def _validate_structured_files(root: Path) -> tuple[int, int]:
    json_count = 0
    toml_count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.relative_to(root).parts:
            continue
        try:
            if path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
                json_count += 1
            elif path.suffix == ".toml":
                tomllib.loads(path.read_text(encoding="utf-8"))
                toml_count += 1
        except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
            raise ReleaseTreeError(f"structured file {path.relative_to(root).as_posix()} is invalid") from error
    return json_count, toml_count


def validate(root: Path, expected_ref: str, event_sha: str | None = None) -> tuple[str, int, int]:
    root = root.resolve()
    target = verify_exact_tag_checkout(root, expected_ref, event_sha)
    for script in CONTENT_CHECKS:
        _run(root, [sys.executable, str(root / "scripts" / script), "--root", str(root)], script)
    json_count, toml_count = _validate_structured_files(root)
    _run(root, ["git", "-C", str(root), "diff", "--check"], "git diff --check")
    _run(root, ["git", "-C", str(root), "fsck", "--full"], "git fsck --full")
    return target, json_count, toml_count


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-ref", default=os.environ.get("GITHUB_REF"))
    parser.add_argument("--event-sha", default=os.environ.get("GITHUB_SHA"))
    arguments = parser.parse_args(argv)
    if not arguments.expected_ref:
        parser.error("--expected-ref or GITHUB_REF is required")
    try:
        target, json_count, toml_count = validate(
            arguments.root, arguments.expected_ref, arguments.event_sha
        )
    except ReleaseTreeError as error:
        print(f"Release tree rejected: {error}", file=sys.stderr)
        return 1
    print(
        f"Exact release tree accepted for {arguments.expected_ref}: target={target}, "
        f"JSON={json_count}, TOML={toml_count}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
