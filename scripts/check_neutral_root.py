#!/usr/bin/env python3
"""Verify that the repository root has no active harness instructions."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from neutral_root_policy import RegisteredSurface, load_registered_surfaces


def repository_root() -> Path:
    """Return the repository root independently of the current directory."""

    return Path(__file__).resolve().parents[1]


def registered_surfaces() -> tuple[RegisteredSurface, ...]:
    return load_registered_surfaces(Path(__file__).resolve().parents[1])


def find_forbidden_paths(
    root: Path,
    surfaces: Iterable[RegisteredSurface] | None = None,
) -> tuple[Path, ...]:
    """Return forbidden root-relative paths that exist under *root*."""

    return tuple(
        surface.path
        for surface in (registered_surfaces() if surfaces is None else surfaces)
        if (root / surface.path).exists() or (root / surface.path).is_symlink()
    )


def format_violations(root: Path, violations: Iterable[Path]) -> str:
    lines = [f"Neutral-root check failed for {root}:"]
    lines.extend(f"  - {path.as_posix()}" for path in violations)
    lines.append("Remove these known registered active project surfaces; nested fixtures elsewhere are allowed.")
    lines.append("The registry does not claim coverage of unknown future harness conventions.")
    return "\n".join(lines)


def main() -> int:
    root = repository_root()
    surfaces = registered_surfaces()
    violations = find_forbidden_paths(root, surfaces)
    if violations:
        print(format_violations(root, violations))
        return 1

    print(
        f"Neutral root confirmed for {root}: "
        f"none of {len(surfaces)} known registered active project surfaces exists."
    )
    print("This guarantee is bounded to the current machine-readable registry, not unknown future conventions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
