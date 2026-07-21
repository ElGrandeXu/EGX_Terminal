#!/usr/bin/env python3
"""Audit reachable Git history for publication risks without network access.

By default, only objects reachable from ``refs/heads/main`` are inspected. Use
``--all-refs`` to include every local ref. Reflogs and unreachable objects are
never scanned. The default blocking blob limit is 524288 bytes (512 KiB).

This deterministic heuristic is not a proof that history contains no secret or
that publication is legally safe. It never prints a matched sensitive value.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

from check_public_surface import (
    LOCAL_ACCOUNT_PATTERN,
    UNIX_HOME_PATTERN,
    WINDOWS_HOME_PATTERN,
    _content_violations,
    _sensitive_name_reason,
    _temporary_name_reason,
)


DEFAULT_MAX_BLOB_BYTES = 512 * 1024
SEVERITIES = ("INFO", "REVIEW", "BLOCKER")
EXPECTED_PUBLIC_REF = "refs/heads/main"
PUBLIC_IDENTITY_POLICY = Path("governance/public-commit-identity.json")
EMAIL_PATTERN = re.compile(
    r"(?i)(?<![A-Z0-9._%+-])([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})"
    r"(?![A-Z0-9._%+-])"
)
VALID_EMAIL_PATTERN = re.compile(
    r"(?i)^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9.-]*[A-Z0-9])?$"
)
ID_BASED_NOREPLY_PATTERN = re.compile(
    r"^(?P<user_id>[1-9][0-9]*)\+(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)"
    r"@users\.noreply\.github\.com$"
)
USERNAME_ONLY_NOREPLY_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?@users\.noreply\.github\.com$"
)
IDENTITY_PATTERN = re.compile(r"^(.*?)\s*<([^<>]*)>\s*(.*)$")
TRAILER_PATTERN = re.compile(
    r"(?i)^(Co-authored-by|Signed-off-by|Reviewed-by|Acked-by|Tested-by|"
    r"Reported-by|Helped-by):\s*(.*)$"
)
AUTHENTICATED_URL_PATTERN = re.compile(r"(?i)https?://[^\s/@:]+:[^\s/@]+@")
TRANSCRIPT_OR_DUMP_PATTERN = re.compile(
    r"(?i)(?:^|/|[-_])(?:transcript|conversation|chat[-_]?log|dump)(?:[._/-]|$)"
    r"|\.(?:dump|sql)$"
)
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
EXAMPLE_DOMAINS = frozenset(
    {"example.com", "example.net", "example.org", "example.invalid", "localhost"}
)
KNOWN_BINARY_SUFFIXES = frozenset(
    {
        ".avif", ".gif", ".ico", ".jpeg", ".jpg", ".pdf", ".png", ".webp",
        ".woff", ".woff2",
    }
)
THIRD_PARTY_MARKER = "THIRD_PARTY_MATERIAL_WITH_PROVEN_LICENSE:"
UNCLEAR_PROVENANCE_MARKER = "PROVENANCE_UNCLEAR"


class HistoryAuditError(RuntimeError):
    """Git metadata or an object required by the audit could not be read."""


@dataclasses.dataclass(frozen=True, order=True)
class Finding:
    severity: str
    category: str
    location: str
    message: str


@dataclasses.dataclass(frozen=True)
class Identity:
    name: str
    email: str
    classification: str


@dataclasses.dataclass(frozen=True)
class PublicIdentityPolicy:
    name: str
    email: str
    github_login: str
    github_user_id: int


@dataclasses.dataclass(frozen=True)
class CommitRecord:
    oid: str
    author: Identity
    committer: Identity
    author_date: str
    committer_date: str
    subject: str
    trailers: tuple[dict[str, str], ...]
    signature: str


@dataclasses.dataclass(frozen=True)
class BlobRecord:
    oid: str
    size: int
    paths: tuple[str, ...]
    current: bool
    binary: bool
    introduction_commit: str | None


@dataclasses.dataclass(frozen=True)
class AuditReport:
    root: str
    mode: str
    selected_refs: tuple[str, ...]
    refs: tuple[dict[str, str], ...]
    metrics: dict[str, object]
    identities: tuple[dict[str, str], ...]
    commits: tuple[CommitRecord, ...]
    blobs: tuple[BlobRecord, ...]
    historical_paths: tuple[str, ...]
    files_absent_from_head: tuple[str, ...]
    findings: tuple[Finding, ...]


def _git(
    arguments: Sequence[str],
    *,
    cwd: Path,
    input_bytes: bytes | None = None,
) -> bytes:
    try:
        process = subprocess.run(
            ["git", "-C", str(cwd), *arguments],
            input=input_bytes,
            check=False,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise HistoryAuditError("Git is not available") from error
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        command = " ".join(arguments)
        raise HistoryAuditError(detail or f"git {command} failed")
    return process.stdout


def repository_root(start: Path | None = None) -> Path:
    """Resolve a Git worktree without depending on the current directory."""

    anchor = start if start is not None else Path(__file__).resolve().parent
    raw = _git(("rev-parse", "--show-toplevel"), cwd=anchor)
    return Path(os.fsdecode(raw).strip()).resolve()


def mask_email(value: str) -> str:
    """Return a stable mask, except for GitHub's explicitly public noreply domain."""

    value = value.strip()
    if value.lower().endswith("@users.noreply.github.com"):
        return value
    if "@" not in value:
        return "<invalid>"
    local, domain = value.rsplit("@", 1)
    return f"{local[:1]}***@{domain.lower()}" if local else f"***@{domain.lower()}"


def redact_text(value: str) -> str:
    """Mask email-like data and personal-home fragments in diagnostics and JSON."""

    value = EMAIL_PATTERN.sub(lambda match: mask_email(match.group(0)), value)
    value = re.sub(
        r"(?i)(?<![A-Za-z0-9_])[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"'<>|]+",
        "<redacted-windows-home>",
        value,
    )
    value = re.sub(
        r"(?i)(?<![A-Za-z0-9_])/(?:home|Users)/[^/\s\"'<>]+",
        "<redacted-unix-home>",
        value,
    )
    return value


def _load_identity_policy(root: Path) -> PublicIdentityPolicy:
    path = root / PUBLIC_IDENTITY_POLICY
    if not path.is_file():
        raise HistoryAuditError(f"required identity policy {PUBLIC_IDENTITY_POLICY} is absent")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid") from error
    required = {
        "schema_version": 1,
        "scope": "all public repository commits",
        "privacy_mode": "github-id-based-noreply",
    }
    if not isinstance(payload, dict) or any(payload.get(key) != value for key, value in required.items()):
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid")
    name = payload.get("name")
    email = payload.get("email")
    login = payload.get("github_login")
    user_id = payload.get("github_user_id")
    if (
        not isinstance(name, str)
        or not name.strip()
        or not isinstance(email, str)
        or not isinstance(login, str)
        or not login
        or not isinstance(user_id, int)
        or isinstance(user_id, bool)
    ):
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid")
    match = ID_BASED_NOREPLY_PATTERN.fullmatch(email)
    if not match or int(match.group("user_id")) != user_id or match.group("login") != login:
        raise HistoryAuditError(
            f"identity policy {PUBLIC_IDENTITY_POLICY} has inconsistent GitHub ID-based noreply fields"
        )
    return PublicIdentityPolicy(name, email, login, user_id)


def classify_identity(
    name: str,
    email: str,
    policy: PublicIdentityPolicy | None = None,
) -> str:
    if not name.strip() or not VALID_EMAIL_PATTERN.fullmatch(email.strip()):
        return "INVALID_IDENTITY"
    lowered_name = name.lower()
    lowered_email = email.lower()
    if policy is not None and name == policy.name and email == policy.email:
        return "EXPECTED_PUBLIC_IDENTITY"
    id_based = ID_BASED_NOREPLY_PATTERN.fullmatch(email)
    if id_based:
        if policy is None:
            return "PUBLIC_ID_BASED_NOREPLY"
        if int(id_based.group("user_id")) != policy.github_user_id:
            return "NOREPLY_USER_ID_MISMATCH"
        if id_based.group("login") != policy.github_login:
            return "NOREPLY_LOGIN_MISMATCH"
        return "PUBLIC_NAME_MISMATCH"
    if USERNAME_ONLY_NOREPLY_PATTERN.fullmatch(email):
        return "USERNAME_ONLY_NOREPLY"
    if lowered_email.endswith("@users.noreply.github.com"):
        return "OTHER_GITHUB_NOREPLY"
    if any(token in lowered_name or token in lowered_email for token in ("[bot]", "github-actions", "dependabot")):
        return "AUTOMATION_IDENTITY"
    if lowered_name in {"unknown", "n/a", "none"}:
        return "UNKNOWN_IDENTITY"
    # No non-noreply identity is assumed public without an explicit human decision.
    return "PRIVATE_EMAIL_REVIEW_REQUIRED"


def _identity(
    raw: str,
    policy: PublicIdentityPolicy | None = None,
) -> tuple[Identity, str]:
    match = IDENTITY_PATTERN.match(raw)
    if not match:
        identity = Identity(redact_text(raw.strip()) or "<missing>", "<invalid>", "INVALID_IDENTITY")
        return identity, ""
    name, email, date = (part.strip() for part in match.groups())
    return Identity(name, mask_email(email), classify_identity(name, email, policy)), date


def _parse_commit(
    oid: str,
    raw: bytes,
    policy: PublicIdentityPolicy,
) -> tuple[CommitRecord, str]:
    text = raw.decode("utf-8", errors="replace")
    header_text, separator, message = text.partition("\n\n")
    if not separator:
        raise HistoryAuditError(f"commit {oid} has no readable message boundary")
    headers: dict[str, list[str]] = defaultdict(list)
    current = ""
    for line in header_text.splitlines():
        if line.startswith(" ") and current:
            headers[current][-1] += "\n" + line
            continue
        key, space, value = line.partition(" ")
        if not space:
            raise HistoryAuditError(f"commit {oid} has an unreadable header")
        headers[key].append(value)
        current = key
    try:
        author, author_date = _identity(headers["author"][0], policy)
        committer, committer_date = _identity(headers["committer"][0], policy)
    except (KeyError, IndexError) as error:
        raise HistoryAuditError(f"commit {oid} lacks author or committer metadata") from error
    trailers: list[dict[str, str]] = []
    for line in message.splitlines():
        match = TRAILER_PATTERN.match(line.strip())
        if not match:
            continue
        label, value = match.groups()
        trailer_identity, _ = _identity(value)
        trailers.append(
            {
                "label": label,
                "name": trailer_identity.name,
                "email": trailer_identity.email,
                "classification": trailer_identity.classification,
            }
        )
    signature = "PRESENT" if "gpgsig" in headers else "ABSENT"
    record = CommitRecord(
        oid=oid,
        author=author,
        committer=committer,
        author_date=author_date,
        committer_date=committer_date,
        subject=redact_text(message.splitlines()[0] if message.splitlines() else ""),
        trailers=tuple(trailers),
        signature=signature,
    )
    return record, message


def _all_refs(root: Path) -> tuple[dict[str, str], ...]:
    raw = _git(
        ("for-each-ref", "--format=%(refname)%00%(objecttype)%00%(objectname)%00"),
        cwd=root,
    )
    fields = raw.decode("utf-8", errors="replace").split("\x00")
    records: list[dict[str, str]] = []
    for index in range(0, len(fields) - 2, 3):
        name, object_type, oid = fields[index : index + 3]
        name = name.lstrip("\n")
        if name:
            records.append(
                {"name": redact_text(name), "object_type": object_type, "oid": oid}
            )
    return tuple(sorted(records, key=lambda item: item["name"]))


def _selected_refs(refs: tuple[dict[str, str], ...], all_refs: bool) -> tuple[str, ...]:
    raw_names = tuple(item["name"] for item in refs)
    if all_refs:
        if not raw_names:
            raise HistoryAuditError("the repository has no refs to inspect")
        return raw_names
    if EXPECTED_PUBLIC_REF not in raw_names:
        raise HistoryAuditError(f"required publication ref {EXPECTED_PUBLIC_REF} is absent")
    return (EXPECTED_PUBLIC_REF,)


def _reachable_objects(root: Path, selected_refs: Sequence[str]) -> dict[str, tuple[str, int]]:
    raw = _git(("rev-list", "--objects", "--no-object-names", *selected_refs), cwd=root)
    oids = tuple(sorted(set(raw.decode("ascii", errors="strict").splitlines())))
    if not oids:
        raise HistoryAuditError("no reachable objects were found")
    batch = _git(
        ("cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"),
        cwd=root,
        input_bytes=("\n".join(oids) + "\n").encode("ascii"),
    )
    result: dict[str, tuple[str, int]] = {}
    for line in batch.decode("ascii", errors="strict").splitlines():
        parts = line.split()
        if len(parts) != 3 or parts[1] == "missing":
            raise HistoryAuditError("a reachable object is unreadable")
        result[parts[0]] = (parts[1], int(parts[2]))
    if set(result) != set(oids):
        raise HistoryAuditError("Git did not describe every reachable object")
    return result


def _reachable_commits(root: Path, selected_refs: Sequence[str]) -> tuple[str, ...]:
    raw = _git(("rev-list", "--reverse", "--topo-order", *selected_refs), cwd=root)
    return tuple(raw.decode("ascii", errors="strict").splitlines())


def _tree_entries(root: Path, commit: str) -> tuple[tuple[str, str, str], ...]:
    raw = _git(("ls-tree", "-r", "-z", "--full-tree", commit), cwd=root)
    entries: list[tuple[str, str, str]] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, separator, path = item.partition(b"\t")
        parts = metadata.decode("ascii", errors="strict").split()
        if not separator or len(parts) != 3:
            raise HistoryAuditError(f"tree for commit {commit} is unreadable")
        mode, object_type, oid = parts
        entries.append((mode, oid, path.decode("utf-8", errors="surrogateescape")))
    return tuple(entries)


def _is_binary(data: bytes) -> bool:
    return b"\0" in data[:8192]


def _known_binary(path: str, data: bytes) -> bool:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in KNOWN_BINARY_SUFFIXES:
        return False
    signatures = (
        b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"\xff\xd8\xff", b"%PDF-",
        b"\x00\x00\x01\x00", b"wOFF", b"wOF2",
    )
    return any(data.startswith(signature) for signature in signatures)


def _example_email(value: str) -> bool:
    return value.rsplit("@", 1)[-1].lower() in EXAMPLE_DOMAINS


def _content_findings(location: str, text: str, *, commit_message: bool) -> list[Finding]:
    findings: list[Finding] = []
    synthetic = Path(location)
    for violation in _content_violations(synthetic, text):
        suffix = f":{violation.line}" if violation.line else ""
        findings.append(
            Finding(
                "BLOCKER",
                violation.category,
                redact_text(location) + suffix,
                violation.reason,
            )
        )
    for line_number, line in enumerate(text.splitlines(), start=1):
        if AUTHENTICATED_URL_PATTERN.search(line):
            findings.append(
                Finding(
                    "BLOCKER",
                    "AUTHENTICATED_URL",
                    f"{redact_text(location)}:{line_number}",
                    "URL contains embedded authentication; value not displayed",
                )
            )
        if commit_message:
            for match in EMAIL_PATTERN.finditer(line):
                value = match.group(0)
                if _example_email(value) or value.lower().endswith("@users.noreply.github.com"):
                    continue
                findings.append(
                    Finding(
                        "REVIEW",
                        "PRIVATE_EMAIL_IN_MESSAGE",
                        f"{redact_text(location)}:{line_number}",
                        f"message contains email {mask_email(value)}",
                    )
                )
    return findings


def _ref_findings(refs: Iterable[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for ref in refs:
        name = ref["name"]
        if name == EXPECTED_PUBLIC_REF:
            continue
        if name.startswith("refs/tags/"):
            category = "UNEXPECTED_TAG"
        elif name.startswith("refs/heads/"):
            category = "UNEXPECTED_BRANCH"
        elif name.startswith("refs/notes/"):
            category = "GIT_NOTES_REF"
        elif name.startswith("refs/remotes/"):
            category = "REMOTE_TRACKING_REF"
        else:
            category = "UNEXPECTED_REF"
        findings.append(
            Finding("REVIEW", category, name, "ref is outside the planned publication ref")
        )
    return findings


def audit(root: Path, *, all_refs: bool = False, max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES) -> AuditReport:
    if max_blob_bytes < 1:
        raise HistoryAuditError("--max-blob-bytes must be a positive integer")
    root = repository_root(root)
    policy = _load_identity_policy(root)
    refs = _all_refs(root)
    selected = _selected_refs(refs, all_refs)
    objects = _reachable_objects(root, selected)
    commits = _reachable_commits(root, selected)
    findings = _ref_findings(refs)

    paths_by_blob: dict[str, set[str]] = defaultdict(set)
    introduction: dict[str, str] = {}
    submodules: set[tuple[str, str]] = set()
    for commit in commits:
        for mode, oid, path in _tree_entries(root, commit):
            if mode == "160000":
                submodules.add((path, oid))
                continue
            if objects.get(oid, (None, 0))[0] == "blob":
                paths_by_blob[oid].add(path)
                introduction.setdefault(oid, commit)

    head_entries = _tree_entries(root, "HEAD")
    head_blobs = {oid for mode, oid, _ in head_entries if mode != "160000"}
    head_paths = {path for mode, _, path in head_entries if mode != "160000"}

    commit_records: list[CommitRecord] = []
    identities: set[tuple[str, str, str]] = set()
    reviewed_roles: set[tuple[str, str, str, str]] = set()
    for oid in commits:
        raw = _git(("cat-file", "commit", oid), cwd=root)
        record, message = _parse_commit(oid, raw, policy)
        commit_records.append(record)
        for role, identity in (("author", record.author), ("committer", record.committer)):
            identities.add((identity.name, identity.email, identity.classification))
            if identity.classification != "EXPECTED_PUBLIC_IDENTITY":
                review_key = (role, identity.name, identity.email, identity.classification)
                if review_key not in reviewed_roles:
                    reviewed_roles.add(review_key)
                    findings.append(
                        Finding(
                            "REVIEW",
                            identity.classification,
                            f"history:{role}",
                            f"{role} identity {identity.name} <{identity.email}> requires review",
                        )
                    )
        for trailer in record.trailers:
            classification = trailer["classification"]
            severity = "INFO" if classification in {
                "PUBLIC_ID_BASED_NOREPLY", "AUTOMATION_IDENTITY"
            } else "REVIEW"
            findings.append(
                Finding(
                    severity,
                    "IDENTITY_TRAILER",
                    f"commit:{oid}",
                    f"{trailer['label']} {trailer['name']} <{trailer['email']}> ({classification})",
                )
            )
        findings.extend(_content_findings(f"commit:{oid}", message, commit_message=True))

    author_identities = {(record.author.name, record.author.email) for record in commit_records}
    committer_identities = {(record.committer.name, record.committer.email) for record in commit_records}
    if len(author_identities) > 1:
        findings.append(
            Finding(
                "REVIEW",
                "MULTIPLE_AUTHOR_IDENTITIES",
                "history:author",
                f"history contains {len(author_identities)} author identities",
            )
        )
    if len(committer_identities) > 1:
        findings.append(
            Finding(
                "REVIEW",
                "MULTIPLE_COMMITTER_IDENTITIES",
                "history:committer",
                f"history contains {len(committer_identities)} committer identities",
            )
        )

    blob_records: list[BlobRecord] = []
    binary_count = 0
    lfs_count = 0
    blob_total = 0
    thresholds = {512 * 1024: 0, 1024 * 1024: 0, 10 * 1024 * 1024: 0}
    for oid, (object_type, size) in sorted(objects.items()):
        if object_type != "blob":
            continue
        data = _git(("cat-file", "blob", oid), cwd=root)
        if len(data) != size:
            raise HistoryAuditError(f"blob {oid} size changed while it was read")
        blob_total += size
        for threshold in thresholds:
            if size > threshold:
                thresholds[threshold] += 1
        paths = tuple(sorted(redact_text(path) for path in paths_by_blob.get(oid, {"<unknown>"})))
        primary_path = paths[0]
        is_binary = _is_binary(data)
        if is_binary:
            binary_count += 1
        if data.startswith(LFS_HEADER):
            lfs_count += 1
            findings.append(
                Finding("BLOCKER", "GIT_LFS_POINTER", primary_path, "reachable Git LFS pointer")
            )
        if size > max_blob_bytes:
            findings.append(
                Finding(
                    "BLOCKER",
                    "LARGE_BLOB",
                    primary_path,
                    f"blob {oid} is {size} bytes, above the {max_blob_bytes}-byte limit",
                )
            )
        for raw_path in sorted(paths_by_blob.get(oid, {"<unknown>"})):
            path = redact_text(raw_path)
            if WINDOWS_HOME_PATTERN.search(raw_path) or UNIX_HOME_PATTERN.search(raw_path):
                findings.append(
                    Finding("BLOCKER", "PERSONAL_PATH", path, "historical filename contains a personal home path")
                )
            if LOCAL_ACCOUNT_PATTERN.search(raw_path):
                findings.append(
                    Finding("BLOCKER", "LOCAL_ACCOUNT", path, "historical filename contains a local account context")
                )
            sensitive = _sensitive_name_reason(PurePosixPath(raw_path))
            if sensitive:
                findings.append(Finding("BLOCKER", "SENSITIVE_FILENAME", path, sensitive))
            temporary = _temporary_name_reason(PurePosixPath(raw_path))
            if temporary:
                findings.append(Finding("BLOCKER", "TEMPORARY_FILE", path, temporary))
            if TRANSCRIPT_OR_DUMP_PATTERN.search(raw_path):
                findings.append(
                    Finding("BLOCKER", "TRANSCRIPT_OR_DUMP", path, "historical transcript or dump filename")
                )
            if raw_path == "REUSE.toml" and UNCLEAR_PROVENANCE_MARKER in data.decode("utf-8", errors="replace"):
                findings.append(
                    Finding("BLOCKER", "THIRD_PARTY_PROVENANCE", path, "provenance is explicitly unclear")
                )
            if raw_path == "REUSE.toml" and THIRD_PARTY_MARKER in data.decode("utf-8", errors="replace"):
                findings.append(
                    Finding("INFO", "THIRD_PARTY_ANNOTATION", path, "narrow third-party annotation is present")
                )
        if is_binary:
            if not any(_known_binary(raw_path, data) for raw_path in paths_by_blob.get(oid, {""})):
                findings.append(
                    Finding("REVIEW", "UNJUSTIFIED_BINARY", primary_path, f"binary blob {oid} requires justification")
                )
            else:
                findings.append(
                    Finding("INFO", "BINARY_BLOB", primary_path, f"recognized small binary blob {oid}")
                )
        else:
            text = data.decode("utf-8", errors="replace")
            for raw_path in sorted(paths_by_blob.get(oid, {"<unknown>"})):
                findings.extend(_content_findings(raw_path, text, commit_message=False))
        blob_records.append(
            BlobRecord(
                oid=oid,
                size=size,
                paths=paths,
                current=oid in head_blobs,
                binary=is_binary,
                introduction_commit=introduction.get(oid),
            )
        )

    for path, oid in sorted(submodules):
        findings.append(
            Finding("BLOCKER", "SUBMODULE", redact_text(path), f"reachable gitlink points to {oid}")
        )

    historical_paths = tuple(sorted({path for paths in paths_by_blob.values() for path in paths}))
    absent = tuple(sorted(set(historical_paths) - head_paths))
    counts: dict[str, int] = defaultdict(int)
    for object_type, _ in objects.values():
        counts[object_type] += 1
    largest = max((record.size for record in blob_records), default=0)
    largest_records = sorted(blob_records, key=lambda record: (-record.size, record.oid))[:10]
    metrics: dict[str, object] = {
        "total_objects": len(objects),
        "commits": counts["commit"],
        "trees": counts["tree"],
        "blobs": counts["blob"],
        "total_uncompressed_blob_bytes": blob_total,
        "largest_blob_bytes": largest,
        "blobs_over_512_kib": thresholds[512 * 1024],
        "blobs_over_1_mib": thresholds[1024 * 1024],
        "blobs_over_10_mib": thresholds[10 * 1024 * 1024],
        "binary_blobs": binary_count,
        "lfs_pointers": lfs_count,
        "submodules": len(submodules),
        "merge_commits": sum(
            1
            for oid in commits
            if len(_git(("show", "-s", "--format=%P", oid), cwd=root).split()) > 1
        ),
        "historical_paths": len(historical_paths),
        "files_absent_from_head": len(absent),
        "largest_blobs": [
            {"oid": record.oid, "size": record.size, "paths": list(record.paths)}
            for record in largest_records
        ],
    }
    identity_records = tuple(
        {"name": name, "email": email, "classification": classification}
        for name, email, classification in sorted(identities)
    )
    ordered_findings = tuple(
        sorted(set(findings), key=lambda item: (SEVERITIES.index(item.severity), item.category, item.location, item.message))
    )
    return AuditReport(
        root=redact_text(str(root)),
        mode="all_refs" if all_refs else "publication_refs",
        selected_refs=tuple(selected),
        refs=refs,
        metrics=metrics,
        identities=identity_records,
        commits=tuple(commit_records),
        blobs=tuple(sorted(blob_records, key=lambda item: item.oid)),
        historical_paths=tuple(redact_text(path) for path in historical_paths),
        files_absent_from_head=tuple(redact_text(path) for path in absent),
        findings=ordered_findings,
    )


def _as_json(report: AuditReport) -> dict[str, object]:
    return dataclasses.asdict(report)


def _write_json(path: Path, report: AuditReport, root: Path) -> None:
    if path.suffix.lower() != ".json":
        raise HistoryAuditError("--json supports only a path ending in .json")
    target = path.expanduser().resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        pass
    else:
        raise HistoryAuditError("--json output must be outside the repository")
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(_as_json(report), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    target.write_text(payload, encoding="utf-8", newline="\n")


def _print_report(report: AuditReport) -> None:
    counts = {severity: 0 for severity in SEVERITIES}
    for finding in report.findings:
        counts[finding.severity] += 1
    metrics = report.metrics
    print(
        f"Git history audited for {report.root}: {metrics['commits']} commits, "
        f"{metrics['trees']} trees, {metrics['blobs']} blobs, "
        f"{metrics['total_uncompressed_blob_bytes']} uncompressed blob bytes."
    )
    print(f"Selected refs: {', '.join(report.selected_refs)}")
    print(
        f"Findings: INFO={counts['INFO']} REVIEW={counts['REVIEW']} "
        f"BLOCKER={counts['BLOCKER']}"
    )
    for finding in report.findings:
        print(f"  - {finding.severity} {finding.location} [{finding.category}] {finding.message}")
    print("This is a bounded heuristic audit, not an absolute security or legal guarantee.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Git worktree to inspect")
    parser.add_argument("--all-refs", action="store_true", help="scan objects reachable from every local ref")
    parser.add_argument("--json", type=Path, metavar="PATH", help="write deterministic JSON outside the repository")
    parser.add_argument("--fail-on-review", action="store_true", help="return nonzero when REVIEW findings exist")
    parser.add_argument(
        "--max-blob-bytes",
        type=int,
        default=DEFAULT_MAX_BLOB_BYTES,
        help=f"blocking blob threshold (default: {DEFAULT_MAX_BLOB_BYTES} bytes)",
    )
    arguments = parser.parse_args(argv)
    try:
        root = repository_root(arguments.root)
        report = audit(
            root,
            all_refs=arguments.all_refs,
            max_blob_bytes=arguments.max_blob_bytes,
        )
        if arguments.json:
            _write_json(arguments.json, report, root)
    except (HistoryAuditError, OSError, UnicodeError, ValueError) as error:
        print(f"Git-history check could not start: {redact_text(str(error))}")
        return 2
    _print_report(report)
    blockers = any(item.severity == "BLOCKER" for item in report.findings)
    reviews = any(item.severity == "REVIEW" for item in report.findings)
    return 1 if blockers or (arguments.fail_on_review and reviews) else 0


if __name__ == "__main__":
    raise SystemExit(main())
