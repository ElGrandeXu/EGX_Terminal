#!/usr/bin/env python3
"""Materialize and verify the experimental static doctrine adapters."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 1
GENERATOR_NAME = "egx-static-doctrine-adapters"
GENERATOR_VERSION = "0.1.0"
STATUS = "experimental"

SOURCE_RELATIVE = PurePosixPath("experiments/kernel-v1/KERNEL.md")
MANIFEST_RELATIVE = PurePosixPath("experiments/kernel-v1/manifest.json")
CANONICAL_RELATIVE = PurePosixPath("doctrine/KERNEL.md")
AGENTS_RELATIVE = PurePosixPath("AGENTS.md")
CLAUDE_RELATIVE = PurePosixPath("CLAUDE.md")
LOCK_RELATIVE = PurePosixPath(".egx/doctrine-lock.json")
CLAUDE_CONTENT = b"@doctrine/KERNEL.md"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_SAFETY = 3
EXIT_CHECK = 4
EXIT_IO = 5


class SafetyError(Exception):
    """The requested target or overwrite is unsafe."""


class CheckError(Exception):
    """Source or target validation failed."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _load_source() -> bytes:
    root = _repo_root()
    source_path = root.joinpath(*SOURCE_RELATIVE.parts)
    manifest_path = root.joinpath(*MANIFEST_RELATIVE.parts)

    try:
        content = source_path.read_bytes()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CheckError(f"experimental source metadata is unreadable: {error}") from error

    if not isinstance(manifest, dict):
        raise CheckError("experimental source metadata must be a JSON object")

    errors: list[str] = []
    digest = _sha256(content)
    if content.startswith(b"\xef\xbb\xbf"):
        errors.append("KERNEL.md contains a UTF-8 BOM")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        errors.append("KERNEL.md is not valid UTF-8")
    if b"\r" in content:
        errors.append("KERNEL.md does not use LF-only line endings")

    expected_manifest = {
        "payload_path": SOURCE_RELATIVE.as_posix(),
        "encoding": "UTF-8",
        "line_endings": "LF",
        "final_line_ending": False,
        "bytes": len(content),
        "sha256": digest,
        "status": STATUS,
    }
    for key, expected in expected_manifest.items():
        if manifest.get(key) != expected:
            errors.append(
                f"manifest {key!r} is {manifest.get(key)!r}; expected {expected!r}"
            )
    if content.endswith(b"\n"):
        errors.append("KERNEL.md has an unexpected final line ending")

    if errors:
        raise CheckError("experimental source integrity failed: " + "; ".join(errors))
    return content


def _file_metadata(path: PurePosixPath, content: bytes) -> dict[str, Any]:
    return {
        "encoding": "UTF-8",
        "final_line_ending": False,
        "line_endings": "LF",
        "path": path.as_posix(),
        "sha256": _sha256(content),
    }


def _expected_state(source: bytes) -> tuple[dict[PurePosixPath, bytes], dict[str, Any], bytes]:
    managed = {
        CANONICAL_RELATIVE: source,
        AGENTS_RELATIVE: source,
        CLAUDE_RELATIVE: CLAUDE_CONTENT,
    }
    managed_metadata = [
        _file_metadata(path, managed[path])
        for path in sorted(managed, key=lambda item: item.as_posix())
    ]
    lock = {
        "adapters": [
            {
                "harnesses": ["Codex", "OpenCode"],
                "path": AGENTS_RELATIVE.as_posix(),
                "sha256": _sha256(source),
                "strategy": "generated-byte-for-byte-copy",
            },
            {
                "harnesses": ["Claude Code"],
                "path": CLAUDE_RELATIVE.as_posix(),
                "sha256": _sha256(CLAUDE_CONTENT),
                "strategy": "direct-relative-import",
            },
        ],
        "canonical": {
            "path": CANONICAL_RELATIVE.as_posix(),
            "sha256": _sha256(source),
            "source_path": SOURCE_RELATIVE.as_posix(),
        },
        "generator": {
            "name": GENERATOR_NAME,
            "version": GENERATOR_VERSION,
        },
        "lockfile": {
            "encoding": "UTF-8",
            "final_line_ending": True,
            "integrity": "deterministic-exact-regeneration",
            "line_endings": "LF",
            "path": LOCK_RELATIVE.as_posix(),
        },
        "managed_files": managed_metadata,
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
    }
    lock_bytes = (
        json.dumps(lock, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return managed, lock, lock_bytes


def _resolve_target(raw_target: str) -> Path:
    try:
        target = Path(raw_target).expanduser().resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise SafetyError(f"cannot resolve target: {error}") from error

    if target == _repo_root():
        raise SafetyError("target must not be the EGX_Terminal repository root")
    if target.exists() and not target.is_dir():
        raise SafetyError("target exists but is not a directory")
    return target


def _safe_path(target: Path, relative: PurePosixPath) -> Path:
    candidate = target.joinpath(*relative.parts)
    current = target
    for part in relative.parts[:-1]:
        current = current / part
        if os.path.lexists(current):
            if current.is_symlink():
                raise SafetyError(f"refusing symlinked output directory: {relative.as_posix()}")
            if not current.is_dir():
                raise SafetyError(f"output parent is not a directory: {relative.as_posix()}")
    if os.path.lexists(candidate) and candidate.is_symlink():
        raise SafetyError(f"refusing symlinked output file: {relative.as_posix()}")

    try:
        candidate.resolve(strict=False).relative_to(target)
    except (OSError, RuntimeError, ValueError) as error:
        raise SafetyError(f"output escapes target: {relative.as_posix()}") from error
    return candidate


def _paths(target: Path) -> dict[PurePosixPath, Path]:
    relatives = [CANONICAL_RELATIVE, AGENTS_RELATIVE, CLAUDE_RELATIVE, LOCK_RELATIVE]
    return {relative: _safe_path(target, relative) for relative in relatives}


def _read_lock_for_ownership(lock_path: Path, expected: dict[str, Any]) -> None:
    try:
        raw = lock_path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            raise ValueError("UTF-8 BOM is not allowed")
        actual = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise SafetyError(f"existing lockfile cannot prove ownership: {error}") from error
    if actual != expected:
        raise SafetyError("existing lockfile cannot prove ownership: metadata mismatch")


def _classify(path: Path, expected: bytes) -> str:
    if not os.path.lexists(path):
        return "CREATE"
    if not path.is_file():
        raise SafetyError(f"managed output is not a regular file: {path.name}")
    return "UNCHANGED" if path.read_bytes() == expected else "UPDATE"


def _preflight_write(
    target: Path,
    paths: dict[PurePosixPath, Path],
    expected_lock: dict[str, Any],
) -> None:
    lock_path = paths[LOCK_RELATIVE]
    lock_exists = os.path.lexists(lock_path)
    allowed_paths = set(paths.values())
    unmanaged_files = []
    if target.exists():
        unmanaged_files = [
            path.relative_to(target).as_posix()
            for path in target.rglob("*")
            if (path.is_file() or path.is_symlink()) and path not in allowed_paths
        ]
    if unmanaged_files:
        raise SafetyError(
            "refusing target with unmanaged file(s): " + ", ".join(sorted(unmanaged_files))
        )

    existing_outputs = [
        relative
        for relative in (CANONICAL_RELATIVE, AGENTS_RELATIVE, CLAUDE_RELATIVE)
        if os.path.lexists(paths[relative])
    ]

    if lock_exists:
        if lock_path.is_symlink() or not lock_path.is_file():
            raise SafetyError("existing lockfile is not a regular file")
        _read_lock_for_ownership(lock_path, expected_lock)
    elif existing_outputs:
        joined = ", ".join(path.as_posix() for path in existing_outputs)
        raise SafetyError(f"refusing unmanaged existing output(s): {joined}")

    if target.exists() and not target.is_dir():
        raise SafetyError("target exists but is not a directory")


def _operations(
    paths: dict[PurePosixPath, Path],
    managed: dict[PurePosixPath, bytes],
    lock_bytes: bytes,
) -> list[tuple[str, PurePosixPath, Path, bytes]]:
    content = {**managed, LOCK_RELATIVE: lock_bytes}
    ordered = [CANONICAL_RELATIVE, AGENTS_RELATIVE, CLAUDE_RELATIVE, LOCK_RELATIVE]
    return [
        (_classify(paths[relative], content[relative]), relative, paths[relative], content[relative])
        for relative in ordered
    ]


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def _policy_errors(relative: PurePosixPath, content: bytes, final_lf: bool) -> list[str]:
    errors: list[str] = []
    if content.startswith(b"\xef\xbb\xbf"):
        errors.append(f"encoding mismatch: {relative.as_posix()} has a UTF-8 BOM")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"encoding mismatch: {relative.as_posix()} is not UTF-8")
    if b"\r" in content:
        errors.append(f"line-ending mismatch: {relative.as_posix()} is not LF-only")
    if content.endswith(b"\n") != final_lf:
        expected = "present" if final_lf else "absent"
        errors.append(f"final line ending mismatch: {relative.as_posix()} must be {expected}")
    return errors


def command_plan(target: Path, managed: dict[PurePosixPath, bytes], lock: dict[str, Any], lock_bytes: bytes) -> int:
    paths = _paths(target)
    _preflight_write(target, paths, lock)
    for action, relative, _, _ in _operations(paths, managed, lock_bytes):
        print(f"{action} {relative.as_posix()}")
    return EXIT_OK


def command_write(target: Path, managed: dict[PurePosixPath, bytes], lock: dict[str, Any], lock_bytes: bytes) -> int:
    paths = _paths(target)
    _preflight_write(target, paths, lock)
    operations = _operations(paths, managed, lock_bytes)
    changed = [operation for operation in operations if operation[0] != "UNCHANGED"]
    if not changed:
        print("OK: target already synchronized")
        return EXIT_OK

    target.mkdir(parents=True, exist_ok=True)
    for _, relative, path, content in changed:
        if relative != LOCK_RELATIVE:
            _atomic_write(path, content)
    lock_operation = next(operation for operation in changed if operation[1] == LOCK_RELATIVE) if any(
        operation[1] == LOCK_RELATIVE for operation in changed
    ) else None
    if lock_operation is not None:
        _atomic_write(lock_operation[2], lock_operation[3])
    print(f"WROTE {len(changed)} file(s)")
    return EXIT_OK


def command_check(target: Path, managed: dict[PurePosixPath, bytes], lock: dict[str, Any], lock_bytes: bytes) -> int:
    if not target.exists():
        raise CheckError("target does not exist")
    paths = _paths(target)
    errors: list[str] = []

    lock_path = paths[LOCK_RELATIVE]
    if not lock_path.is_file() or lock_path.is_symlink():
        errors.append(f"missing or unsafe: {LOCK_RELATIVE.as_posix()}")
    else:
        actual_lock = lock_path.read_bytes()
        errors.extend(_policy_errors(LOCK_RELATIVE, actual_lock, final_lf=True))
        try:
            parsed_lock = json.loads(actual_lock.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"invalid lockfile JSON: {error}")
        else:
            if parsed_lock != lock:
                errors.append("invalid lockfile: metadata is incomplete or inconsistent")
        if actual_lock != lock_bytes:
            errors.append("invalid lockfile: bytes are not deterministic")

    for relative, expected in managed.items():
        path = paths[relative]
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing or unsafe: {relative.as_posix()}")
            continue
        actual = path.read_bytes()
        errors.extend(_policy_errors(relative, actual, final_lf=False))
        if actual != expected:
            label = "canonical differs from experimental kernel" if relative == CANONICAL_RELATIVE else "managed file drift"
            errors.append(
                f"{label}: {relative.as_posix()} "
                f"(expected {_sha256(expected)}, got {_sha256(actual)})"
            )

    if errors:
        raise CheckError("; ".join(errors))
    print(f"OK: target synchronized ({len(managed)} managed content files)")
    return EXIT_OK


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize deterministic experimental doctrine adapters."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "write", "check"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--target", required=True, help="explicit disposable workspace path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        source = _load_source()
        managed, lock, lock_bytes = _expected_state(source)
        target = _resolve_target(args.target)
        if args.command == "plan":
            return command_plan(target, managed, lock, lock_bytes)
        if args.command == "write":
            return command_write(target, managed, lock, lock_bytes)
        return command_check(target, managed, lock, lock_bytes)
    except SafetyError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return EXIT_SAFETY
    except CheckError as error:
        print(f"CHECK FAILED: {error}", file=sys.stderr)
        return EXIT_CHECK
    except OSError as error:
        print(f"I/O ERROR: {error}", file=sys.stderr)
        return EXIT_IO


if __name__ == "__main__":
    raise SystemExit(main())
