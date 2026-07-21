#!/usr/bin/env python3
"""Verify that the repository root has no active harness instructions."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


FORBIDDEN_PATHS = (
    Path("AGENTS.md"),
    Path("AGENTS.override.md"),
    Path("CLAUDE.md"),
    Path("opencode.json"),
    Path("doctrine/KERNEL.md"),
)


def repository_root() -> Path:
    """Return the repository root independently of the current directory."""

    return Path(__file__).resolve().parents[1]


def find_forbidden_paths(root: Path) -> tuple[Path, ...]:
    """Return forbidden root-relative paths that exist under *root*."""

    return tuple(
        relative
        for relative in FORBIDDEN_PATHS
        if (root / relative).exists() or (root / relative).is_symlink()
    )


def format_violations(root: Path, violations: Iterable[Path]) -> str:
    lines = [f"Neutral-root check failed for {root}:"]
    lines.extend(f"  - {path.as_posix()}" for path in violations)
    lines.append("Remove these active root paths; nested fixtures are allowed.")
    return "\n".join(lines)


def main() -> int:
    root = repository_root()
    violations = find_forbidden_paths(root)
    if violations:
        print(format_violations(root, violations))
        return 1

    print(
        f"Neutral root confirmed for {root}: "
        f"none of {len(FORBIDDEN_PATHS)} forbidden paths exists."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
