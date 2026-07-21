#!/usr/bin/env python3
"""Detect common publication-boundary violations in tracked repository files.

This is a deterministic heuristic check, not a proof that a repository is safe.
It uses only the Python standard library and never modifies the repository.
"""

from __future__ import annotations

import argparse
import ipaddress
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable, Mapping, NamedTuple, Sequence


LARGE_FILE_LIMIT = 512 * 1024

# Keep this tuple aligned with scripts/check_neutral_root.py. This complementary
# check is intentionally root-relative: identically named nested fixtures remain
# valid historical or test material.
FORBIDDEN_ROOT_PATHS = (
    Path("AGENTS.md"),
    Path("AGENTS.override.md"),
    Path("CLAUDE.md"),
    Path("opencode.json"),
    Path("doctrine/KERNEL.md"),
)

# A future legitimate large proof must be listed by exact path with a reviewable
# reason. There are no large-file exceptions in the V1 surface at present.
LARGE_FILE_EXCEPTIONS: Mapping[str, str] = {}

# The detector source is scanned like every other tracked file. Its regexes avoid
# embedding complete matching credentials or personal paths, so no source-wide
# exemption can hide a future violation in this script.
WINDOWS_HOME_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9_])[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"'<>|]+"
    r"(?:[\\/]+[^\s\"'<>|]+)*"
)
UNIX_HOME_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9_])/(?:home|Users)/[^/\s\"'<>]+"
    r"(?:/[^\s\"'<>]+)*"
)
LOCAL_ACCOUNT_PATTERN = re.compile(
    r"(?i)(?:[\\/]maxer(?:[\\/]|\b)|"
    r"\b(?:user(?:name)?|account|owner|home|profile|host(?:name)?|machine(?:_?id)?)"
    r"\s*[:=]\s*[\"']?maxer\b)"
)
PRIVATE_KEY_PATTERN = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
)
IPV4_PATTERN = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")

SECRET_PATTERNS = (
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GITHUB_TOKEN", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("OPENAI_API_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    (
        "SECRET_ASSIGNMENT",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
            r"client[_-]?secret|password|passwd)\s*[:=]\s*[\"']?"
            r"[A-Za-z0-9_+./=-]{16,}"
        ),
    ),
)

SAFE_ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template"}
SENSITIVE_EXACT_NAMES = {
    ".npmrc",
    ".pypirc",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "service-account.json",
    "service_account.json",
    "secrets.json",
    "secrets.toml",
    "secrets.yaml",
    "secrets.yml",
}
TEMPORARY_DIRECTORY_NAMES = {
    ".cache",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "__pycache__",
    "node_modules",
}
TEMPORARY_EXACT_NAMES = {".DS_Store", "Desktop.ini", "Thumbs.db"}
TEMPORARY_SUFFIXES = (".bak", ".log", ".swp", ".swo", ".temp", ".tmp", "~")


class Violation(NamedTuple):
    path: str
    category: str
    reason: str
    line: int | None = None


class PublicSurfaceError(RuntimeError):
    """Raised when Git metadata needed for a read-only scan is unavailable."""


def _run_git(arguments: Sequence[str], *, cwd: Path) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(cwd), *arguments],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise PublicSurfaceError(detail or f"git {' '.join(arguments)} failed")
    return completed.stdout


def repository_root(start: Path | None = None) -> Path:
    """Resolve the Git root without relying on the process current directory."""

    anchor = start if start is not None else Path(__file__).resolve().parent
    output = _run_git(("rev-parse", "--show-toplevel"), cwd=anchor)
    return Path(os.fsdecode(output).strip()).resolve()


def tracked_files(root: Path) -> tuple[Path, ...]:
    """Return tracked paths safely, including names containing spaces."""

    output = _run_git(("ls-files", "-z"), cwd=root)
    return tuple(
        Path(os.fsdecode(raw))
        for raw in output.split(b"\0")
        if raw
    )


def _sensitive_name_reason(relative: Path) -> str | None:
    name = relative.name.lower()
    if name in SAFE_ENV_EXAMPLES:
        return None
    if name == ".env" or name.startswith(".env.") or name == ".envrc":
        return "tracked environment file may contain local configuration or secrets"
    if name in SENSITIVE_EXACT_NAMES:
        return "tracked filename is commonly used for credentials or secrets"
    if name.endswith((".p12", ".pfx", ".pem", ".key")):
        return "tracked key or certificate-container filename requires removal or review"
    return None


def _temporary_name_reason(relative: Path) -> str | None:
    parts = {part.lower() for part in relative.parts}
    temporary_directories = {name.lower() for name in TEMPORARY_DIRECTORY_NAMES}
    if parts & temporary_directories:
        return "tracked path is inside a cache or dependency directory"
    if relative.name in TEMPORARY_EXACT_NAMES:
        return "tracked operating-system metadata file is temporary"
    if relative.name.lower().endswith(TEMPORARY_SUFFIXES):
        return "tracked filename has a temporary, backup, swap, or log suffix"
    return None


def _is_private_ipv4(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    if not isinstance(address, ipaddress.IPv4Address):
        return False
    if address.is_loopback or address.is_unspecified:
        return False
    first, second, _, _ = (int(part) for part in value.split("."))
    return (
        first == 10
        or (first == 172 and 16 <= second <= 31)
        or (first == 192 and second == 168)
    )


def _content_violations(relative: Path, text: str) -> list[Violation]:
    violations: list[Violation] = []
    path = relative.as_posix()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if WINDOWS_HOME_PATTERN.search(line):
            violations.append(
                Violation(path, "PERSONAL_PATH", "absolute Windows user-home path", line_number)
            )
        if UNIX_HOME_PATTERN.search(line):
            violations.append(
                Violation(path, "PERSONAL_PATH", "absolute Unix/macOS user-home path", line_number)
            )
        if LOCAL_ACCOUNT_PATTERN.search(line):
            violations.append(
                Violation(
                    path,
                    "LOCAL_ACCOUNT",
                    "local account name appears in a path or machine-configuration context",
                    line_number,
                )
            )
        if PRIVATE_KEY_PATTERN.search(line):
            violations.append(
                Violation(path, "PRIVATE_KEY", "private-key PEM header", line_number)
            )
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                violations.append(
                    Violation(
                        path,
                        "SECRET_SIGNATURE",
                        f"plausible {label.lower()} signature; value not displayed",
                        line_number,
                    )
                )
        if any(_is_private_ipv4(match.group(0)) for match in IPV4_PATTERN.finditer(line)):
            violations.append(
                Violation(
                    path,
                    "PRIVATE_ENDPOINT",
                    "non-loopback RFC 1918 address; value not displayed",
                    line_number,
                )
            )
    return violations


def scan_paths(
    root: Path,
    relative_paths: Iterable[Path],
    *,
    large_file_exceptions: Mapping[str, str] = LARGE_FILE_EXCEPTIONS,
) -> tuple[Violation, ...]:
    """Scan the supplied root-relative files and active neutral-root paths."""

    root = root.resolve()
    violations: list[Violation] = []
    for forbidden in FORBIDDEN_ROOT_PATHS:
        target = root / forbidden
        if target.exists() or target.is_symlink():
            violations.append(
                Violation(
                    forbidden.as_posix(),
                    "NEUTRAL_ROOT",
                    "active root path is forbidden by the V1 neutral-root decision",
                )
            )

    for relative in relative_paths:
        path_text = relative.as_posix()
        if relative.is_absolute() or ".." in relative.parts:
            violations.append(
                Violation(
                    path_text,
                    "TRACKED_PATH",
                    "path is not confined to the repository root and was not scanned",
                )
            )
            continue
        target = root / relative
        if target.is_symlink():
            violations.append(
                Violation(
                    path_text,
                    "TRACKED_PATH",
                    "tracked symbolic link requires manual review and was not followed",
                )
            )
            continue
        if not target.is_file():
            violations.append(
                Violation(path_text, "TRACKED_PATH", "tracked path is missing or is not a regular file")
            )
            continue

        sensitive_reason = _sensitive_name_reason(relative)
        if sensitive_reason:
            violations.append(Violation(path_text, "SENSITIVE_FILENAME", sensitive_reason))

        temporary_reason = _temporary_name_reason(relative)
        if temporary_reason:
            violations.append(Violation(path_text, "TEMPORARY_FILE", temporary_reason))

        size = target.stat().st_size
        if size > LARGE_FILE_LIMIT and path_text not in large_file_exceptions:
            violations.append(
                Violation(
                    path_text,
                    "LARGE_FILE",
                    f"tracked file is {size} bytes, above the {LARGE_FILE_LIMIT}-byte limit",
                )
            )

        content = target.read_bytes().decode("utf-8", errors="replace")
        violations.extend(_content_violations(relative, content))

    return tuple(
        sorted(
            violations,
            key=lambda item: (item.path, item.line or 0, item.category, item.reason),
        )
    )


def format_violation(violation: Violation) -> str:
    location = violation.path
    if violation.line is not None:
        location = f"{location}:{violation.line}"
    return f"{location} [{violation.category}] {violation.reason}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        help="Git worktree to scan; defaults to the repository containing this script",
    )
    arguments = parser.parse_args(argv)

    try:
        root = repository_root(arguments.root)
        files = tracked_files(root)
    except PublicSurfaceError as error:
        print(f"Public-surface check could not start: {error}")
        return 2

    violations = scan_paths(root, files)
    if violations:
        print(f"Public-surface check failed for {root}:")
        for violation in violations:
            print(f"  - {format_violation(violation)}")
        print(
            "This heuristic reports likely blockers; inspect context before classifying or removing evidence."
        )
        return 1

    print(
        f"Public surface accepted for {root}: {len(files)} tracked files, "
        "no blocking heuristic violation."
    )
    print("This result is a bounded heuristic check, not an absolute security guarantee.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
