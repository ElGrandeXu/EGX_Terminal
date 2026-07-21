#!/usr/bin/env python3
"""Audit reachable Git history for publication risks without network access.

By default, objects reachable from ``refs/heads/main`` are inspected, together
with the current bounded contribution branch when HEAD is attached elsewhere.
In a detached pull-request checkout, HEAD and the available local or
``origin/main`` base are inspected instead. Use ``--all-refs`` to inspect every
ref while retaining the same ref-policy findings.
Reflogs and unreachable objects are never scanned. The default blocking blob
limit is 524288 bytes (512 KiB).

This deterministic heuristic is not a proof that history contains no secret or
that publication is legally safe. It never prints a matched sensitive value.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import dataclasses
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Sequence

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
EXPECTED_REMOTE_MAIN = "refs/remotes/origin/main"
EXPECTED_REMOTE_HEAD = "refs/remotes/origin/HEAD"
PUBLIC_IDENTITY_POLICY = Path("governance/public-commit-identity.json")
RELEASE_POLICY = Path("governance/release-policy.json")
HISTORICAL_UNSIGNED_ATTESTATION = (
    "HISTORICAL_UNSIGNED_ANNOTATED_TAG_WITH_IMMUTABLE_GITHUB_RELEASE"
)
SSH_SIGNED_ATTESTATION = (
    "SSH_SIGNED_ANNOTATED_TAG_WITH_IMMUTABLE_GITHUB_RELEASE"
)
GITHUB_WEB_COMMITTER_NAME = "GitHub"
GITHUB_WEB_COMMITTER_EMAIL = "noreply@github.com"
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
    r"^(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)"
    r"@users\.noreply\.github\.com$"
)
AUTOMATION_MARKER_PATTERN = re.compile(
    r"(?i)(?:\[bot\]|(?:^|[-_\s])bot(?:$|[-_\s])|github-actions|dependabot)"
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
GITHUB_PR_REF_PATTERN = re.compile(r"^refs/pull/(?P<number>[1-9][0-9]*)/merge$")
GITHUB_REPOSITORY_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)
GITHUB_PR_REQUIRED_EVIDENCE = (
    "github-actions-true",
    "pull-request-event",
    "canonical-merge-ref",
    "head-sha-match",
    "readable-event-payload",
    "pull-request-number-match",
    "repository-match",
    "base-and-head-shas-present",
    "two-parent-head",
    "base-parent-match",
    "head-parent-match",
    "synthetic-remote-ref-match",
)
PERSISTENT_HISTORY = "PERSISTENT_HISTORY"
EPHEMERAL_GITHUB_PR_MERGE = "EPHEMERAL_GITHUB_PR_MERGE"


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
    accepted_author_classes: frozenset[str]
    accepted_committer_classes: frozenset[str]
    accepted_trailer_classes: frozenset[str]
    github_pr_required_evidence: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ReleaseRecord:
    tag: str
    target_commit: str
    tag_object: str
    immutable: bool
    attestation_mode: str
    signing_identity: str | None
    published: bool
    github_release_id: int | None


@dataclasses.dataclass(frozen=True)
class HistoricalReleaseRecord:
    tag: str
    status: str
    former_target_commit: str
    former_tag_object: str
    former_github_release_id: int
    evidence: str
    evidence_visibility: str
    public_verification_claim: bool
    expected_ref_present: bool
    tag_name_reuse_status: str


@dataclasses.dataclass(frozen=True)
class SigningIdentity:
    identity_id: str
    principal: str
    allowed_signers_file: str
    public_key_fingerprint: str
    activated_on: str
    revoked_on: str | None
    last_trusted_release: str | None


@dataclasses.dataclass(frozen=True)
class SignaturePolicy:
    required_from: tuple[int, int, int]
    historical_unsigned_exception: str
    mechanism: str
    status: str
    active_identity: str | None
    identities: Mapping[str, SigningIdentity]
    gate: str


@dataclasses.dataclass(frozen=True)
class ReleasePolicy:
    version_pattern: re.Pattern[str]
    main_ref: str
    allowed_taggers: frozenset[tuple[str, str, str]]
    signatures: SignaturePolicy
    current_releases: Mapping[str, ReleaseRecord]
    historical_releases: Mapping[str, HistoricalReleaseRecord]
    next_candidate: str


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
    persistence: str = PERSISTENT_HISTORY


@dataclasses.dataclass(frozen=True)
class GitHubPullRequestContext:
    attempted: bool
    valid: bool
    pr_number: int | None
    repository: str | None
    head_oid: str
    base_oid: str | None
    source_oid: str | None
    merge_ref: str | None
    evidence: tuple[str, ...]
    failures: tuple[str, ...]


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
    try:
        raw = _git(("rev-parse", "--show-toplevel"), cwd=anchor)
    except HistoryAuditError as error:
        raise HistoryAuditError(
            "a full Git clone with .git metadata is required to audit history, refs, tag objects, and identities"
        ) from error
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
    expected_authors = frozenset(
        {
            "MAINTAINER_GITHUB_NOREPLY",
            "PUBLIC_ID_BASED_NOREPLY",
            "PUBLIC_USERNAME_NOREPLY",
        }
    )
    expected_committers = expected_authors | {"GITHUB_WEB_COMMITTER"}
    expected_purpose = [
        "protect public email privacy",
        "preserve inspectable GitHub attribution",
        "support public contributions",
        "detect unexpected human or system identities",
    ]
    expected_keys = {
        "schema_version",
        "purpose",
        "maintainer",
        "accepted_author_classes",
        "accepted_committer_classes",
        "accepted_trailer_classes",
        "github_web_committer",
        "personal_email_policy",
        "invalid_identity_policy",
        "multiple_compliant_identities_policy",
        "automation_policy",
        "ephemeral_github_pr_merge",
    }
    if (
        not isinstance(payload, dict)
        or set(payload) != expected_keys
        or payload.get("schema_version") != 2
    ):
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid")
    maintainer = payload.get("maintainer")
    web_committer = payload.get("github_web_committer")
    purpose = payload.get("purpose")
    if (
        not isinstance(maintainer, dict)
        or set(maintainer) != {"name", "email", "github_login", "github_user_id"}
        or not isinstance(web_committer, dict)
    ):
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid")
    name = maintainer.get("name")
    email = maintainer.get("email")
    login = maintainer.get("github_login")
    user_id = maintainer.get("github_user_id")
    author_classes = payload.get("accepted_author_classes")
    committer_classes = payload.get("accepted_committer_classes")
    trailer_classes = payload.get("accepted_trailer_classes")
    ephemeral_context = payload.get("ephemeral_github_pr_merge")
    if (
        purpose != expected_purpose
        or not isinstance(name, str)
        or not name.strip()
        or not isinstance(email, str)
        or not email.strip()
        or not isinstance(login, str)
        or not login
        or not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or not isinstance(author_classes, list)
        or not all(isinstance(item, str) for item in author_classes)
        or not isinstance(committer_classes, list)
        or not all(isinstance(item, str) for item in committer_classes)
        or not isinstance(trailer_classes, list)
        or not all(isinstance(item, str) for item in trailer_classes)
        or ephemeral_context
        != {
            "type": "github-pull-request-merge",
            "persistence": "ephemeral",
            "identity_policy": "excluded-after-context-validation",
            "content_policy": "fully-scanned",
            "required_evidence": list(GITHUB_PR_REQUIRED_EVIDENCE),
        }
        or frozenset(author_classes) != expected_authors
        or len(author_classes) != len(expected_authors)
        or frozenset(committer_classes) != expected_committers
        or len(committer_classes) != len(expected_committers)
        or frozenset(trailer_classes) != expected_authors
        or len(trailer_classes) != len(expected_authors)
        or web_committer
        != {
            "name": GITHUB_WEB_COMMITTER_NAME,
            "email": GITHUB_WEB_COMMITTER_EMAIL,
            "allowed_role": "committer",
        }
        or payload.get("personal_email_policy") != "REVIEW"
        or payload.get("invalid_identity_policy") != "REVIEW"
        or payload.get("multiple_compliant_identities_policy") != "ACCEPT"
        or payload.get("automation_policy") != "EXPLICIT_RULE_REQUIRED"
    ):
        raise HistoryAuditError(f"identity policy {PUBLIC_IDENTITY_POLICY} is invalid")
    match = ID_BASED_NOREPLY_PATTERN.fullmatch(email)
    if not match or int(match.group("user_id")) != user_id or match.group("login") != login:
        raise HistoryAuditError(
            f"identity policy {PUBLIC_IDENTITY_POLICY} has inconsistent GitHub ID-based noreply fields"
        )
    return PublicIdentityPolicy(
        name=name,
        email=email,
        github_login=login,
        github_user_id=user_id,
        accepted_author_classes=frozenset(author_classes),
        accepted_committer_classes=frozenset(committer_classes),
        accepted_trailer_classes=frozenset(trailer_classes),
        github_pr_required_evidence=GITHUB_PR_REQUIRED_EVIDENCE,
    )


def _load_release_policy(root: Path) -> ReleasePolicy:
    path = root / RELEASE_POLICY
    if not path.is_file():
        raise HistoryAuditError(f"required release policy {RELEASE_POLICY} is absent")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} is invalid") from error
    expected_keys = {
        "schema_version",
        "version_format",
        "stable_tags",
        "tagger_identity_policy",
        "signature_policy",
        "current_releases",
        "historical_releases",
        "next_candidate",
    }
    stable = payload.get("stable_tags") if isinstance(payload, dict) else None
    taggers = payload.get("tagger_identity_policy") if isinstance(payload, dict) else None
    signatures = payload.get("signature_policy") if isinstance(payload, dict) else None
    current_releases = payload.get("current_releases") if isinstance(payload, dict) else None
    historical_releases = payload.get("historical_releases") if isinstance(payload, dict) else None
    next_candidate = payload.get("next_candidate") if isinstance(payload, dict) else None
    version_format = payload.get("version_format") if isinstance(payload, dict) else None
    if (
        not isinstance(payload, dict)
        or set(payload) != expected_keys
        or payload.get("schema_version") != 4
        or not isinstance(version_format, str)
        or stable
        != {
            "declaration_required": True,
            "annotated_required": True,
            "target_must_be_ancestor_of": EXPECTED_PUBLIC_REF,
            "unexpected_or_divergent_policy": "REVIEW",
        }
        or not isinstance(taggers, dict)
        or set(taggers) != {"source", "allowed_taggers"}
        or taggers.get("source") != PUBLIC_IDENTITY_POLICY.as_posix()
        or not isinstance(taggers.get("allowed_taggers"), list)
        or not taggers["allowed_taggers"]
        or not isinstance(signatures, dict)
        or set(signatures)
        != {
            "required_from",
            "historical_unsigned_exception",
            "mechanism",
            "status",
            "active_identity",
            "identities",
            "gate",
        }
        or not isinstance(current_releases, list)
        or not isinstance(historical_releases, list)
    ):
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} is invalid")
    try:
        pattern = re.compile(version_format)
    except re.error as error:
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid version format") from error
    if pattern.pattern != r"^v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)$":
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an unsupported version format")

    def version_tuple(value: object) -> tuple[int, int, int] | None:
        if not isinstance(value, str) or pattern.fullmatch(value) is None:
            return None
        return tuple(int(part) for part in value[1:].split("."))  # type: ignore[return-value]

    required_from = version_tuple(signatures.get("required_from"))
    next_candidate_version = version_tuple(next_candidate)
    historical_exception = signatures.get("historical_unsigned_exception")
    status = signatures.get("status")
    active_identity = signatures.get("active_identity")
    gate = signatures.get("gate")
    identities_payload = signatures.get("identities")
    if (
        required_from is None
        or next_candidate_version is None
        or required_from < (1, 0, 1)
        or historical_exception != "v1.0.0"
        or signatures.get("mechanism") != "SSH"
        or status not in {"KEY_SELECTION_REQUIRED", "ACTIVE"}
        or not isinstance(gate, str)
        or not gate.strip()
        or not isinstance(identities_payload, list)
        or (active_identity is not None and not isinstance(active_identity, str))
    ):
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid signature policy")

    signing_identities: dict[str, SigningIdentity] = {}
    identity_keys = {
        "id",
        "principal",
        "allowed_signers_file",
        "public_key_fingerprint",
        "activated_on",
        "revoked_on",
        "last_trusted_release",
    }
    for item in identities_payload:
        allowed_value = item.get("allowed_signers_file") if isinstance(item, dict) else None
        allowed_path = PurePosixPath(allowed_value) if isinstance(allowed_value, str) else None
        if (
            not isinstance(item, dict)
            or set(item) != identity_keys
            or not isinstance(item.get("id"), str)
            or re.fullmatch(r"[a-z0-9][a-z0-9._-]*", item["id"]) is None
            or not isinstance(item.get("principal"), str)
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._@+-]*", item["principal"]) is None
            or not isinstance(item.get("allowed_signers_file"), str)
            or allowed_path is None
            or allowed_path.is_absolute()
            or ".." in allowed_path.parts
            or not allowed_path.parts
            or allowed_path.parts[0] != "governance"
            or not isinstance(item.get("public_key_fingerprint"), str)
            or re.fullmatch(r"SHA256:[A-Za-z0-9+/]{43}", item["public_key_fingerprint"]) is None
            or not isinstance(item.get("activated_on"), str)
            or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", item["activated_on"]) is None
            or (
                item.get("revoked_on") is not None
                and (
                    not isinstance(item.get("revoked_on"), str)
                    or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", item["revoked_on"]) is None
                )
            )
            or (
                item.get("revoked_on") is None
                and item.get("last_trusted_release") is not None
            )
            or (
                item.get("revoked_on") is not None
                and version_tuple(item.get("last_trusted_release")) is None
            )
            or item["id"] in signing_identities
        ):
            raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid signing identity")
        try:
            date.fromisoformat(item["activated_on"])
            if item["revoked_on"] is not None:
                date.fromisoformat(item["revoked_on"])
        except ValueError as error:
            raise HistoryAuditError(
                f"release policy {RELEASE_POLICY} has an invalid signing identity date"
            ) from error
        signing_identities[item["id"]] = SigningIdentity(
            identity_id=item["id"],
            principal=item["principal"],
            allowed_signers_file=item["allowed_signers_file"],
            public_key_fingerprint=item["public_key_fingerprint"],
            activated_on=item["activated_on"],
            revoked_on=item["revoked_on"],
            last_trusted_release=item["last_trusted_release"],
        )
    if status == "KEY_SELECTION_REQUIRED" and active_identity is not None:
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} cannot activate an identity while key selection is blocked")
    if status == "ACTIVE":
        selected = signing_identities.get(active_identity or "")
        if selected is None or selected.revoked_on is not None:
            raise HistoryAuditError(f"release policy {RELEASE_POLICY} has no non-revoked active signing identity")
    signature_policy = SignaturePolicy(
        required_from=required_from,
        historical_unsigned_exception=historical_exception,
        mechanism="SSH",
        status=status,
        active_identity=active_identity,
        identities=signing_identities,
        gate=gate,
    )
    allowed_taggers: set[tuple[str, str, str]] = set()
    for item in taggers["allowed_taggers"]:
        if (
            not isinstance(item, dict)
            or set(item) != {"name", "email", "classification"}
            or not all(isinstance(item.get(key), str) and item[key] for key in item)
            or item["classification"] != "MAINTAINER_GITHUB_NOREPLY"
        ):
            raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid tagger")
        allowed_taggers.add((item["name"], item["email"], item["classification"]))
    records: dict[str, ReleaseRecord] = {}
    required_release_keys = {
        "tag",
        "target_commit",
        "tag_object",
        "immutable",
        "attestation_mode",
        "signing_identity",
        "published",
        "github_release_id",
    }
    for item in current_releases:
        if (
            not isinstance(item, dict)
            or set(item) != required_release_keys
            or not isinstance(item.get("tag"), str)
            or pattern.fullmatch(item["tag"]) is None
            or not isinstance(item.get("target_commit"), str)
            or re.fullmatch(r"[0-9a-f]{40}", item["target_commit"]) is None
            or not isinstance(item.get("tag_object"), str)
            or re.fullmatch(r"[0-9a-f]{40}", item["tag_object"]) is None
            or not isinstance(item.get("immutable"), bool)
            or item.get("attestation_mode") not in {HISTORICAL_UNSIGNED_ATTESTATION, SSH_SIGNED_ATTESTATION}
            or (
                item.get("attestation_mode") == HISTORICAL_UNSIGNED_ATTESTATION
                and item.get("signing_identity") is not None
            )
            or (
                item.get("attestation_mode") == SSH_SIGNED_ATTESTATION
                and (not isinstance(item.get("signing_identity"), str) or not item["signing_identity"])
            )
            or not isinstance(item.get("published"), bool)
            or (
                item.get("published") is True
                and (
                    item.get("immutable") is not True
                    or not isinstance(item.get("github_release_id"), int)
                    or isinstance(item.get("github_release_id"), bool)
                    or item["github_release_id"] < 1
                )
            )
            or (
                item.get("published") is False
                and (item.get("immutable") is not False or item.get("github_release_id") is not None)
            )
            or item["tag"] in records
        ):
            raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid release record")
        records[item["tag"]] = ReleaseRecord(**item)
    historical_records: dict[str, HistoricalReleaseRecord] = {}
    required_historical_keys = {
        "tag",
        "status",
        "former_target_commit",
        "former_tag_object",
        "former_github_release_id",
        "evidence",
        "evidence_visibility",
        "public_verification_claim",
        "expected_ref_present",
        "tag_name_reuse_status",
    }
    for item in historical_releases:
        if (
            not isinstance(item, dict)
            or set(item) != required_historical_keys
            or not isinstance(item.get("tag"), str)
            or pattern.fullmatch(item["tag"]) is None
            or item.get("status") != "WITHDRAWN_DURING_PRIVACY_REMEDIATION"
            or not isinstance(item.get("former_target_commit"), str)
            or re.fullmatch(r"[0-9a-f]{40}", item["former_target_commit"]) is None
            or not isinstance(item.get("former_tag_object"), str)
            or re.fullmatch(r"[0-9a-f]{40}", item["former_tag_object"]) is None
            or not isinstance(item.get("former_github_release_id"), int)
            or isinstance(item.get("former_github_release_id"), bool)
            or item["former_github_release_id"] < 1
            or item.get("evidence") != "PRIVATE_VERIFIED_BUNDLE"
            or item.get("evidence_visibility") != "PRIVATE"
            or item.get("public_verification_claim") is not False
            or item.get("expected_ref_present") is not False
            or item.get("tag_name_reuse_status")
            != "BLOCKED_BY_IMMUTABLE_RELEASE_RESERVATION"
            or item["tag"] in historical_records
        ):
            raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an invalid historical release record")
        historical_records[item["tag"]] = HistoricalReleaseRecord(**item)
    overlap = set(records).intersection(historical_records)
    if overlap:
        raise HistoryAuditError(
            f"release policy {RELEASE_POLICY} declares a tag as both current and historical"
        )
    known_versions = [_release_version(tag) for tag in (*records, *historical_records)]
    if (
        next_candidate in records
        or next_candidate in historical_records
        or next_candidate_version < required_from
        or (known_versions and next_candidate_version <= max(known_versions))
    ):
        raise HistoryAuditError(f"release policy {RELEASE_POLICY} has an incoherent next candidate")
    for identity in signing_identities.values():
        if identity.revoked_on is None:
            continue
        boundary = records.get(identity.last_trusted_release or "")
        if (
            boundary is None
            or boundary.signing_identity != identity.identity_id
            or boundary.attestation_mode != SSH_SIGNED_ATTESTATION
        ):
            raise HistoryAuditError(
                f"release policy {RELEASE_POLICY} has an invalid last trusted release"
            )
    return ReleasePolicy(
        version_pattern=pattern,
        main_ref=stable["target_must_be_ancestor_of"],
        allowed_taggers=frozenset(allowed_taggers),
        signatures=signature_policy,
        current_releases=records,
        historical_releases=historical_records,
        next_candidate=next_candidate,
    )


def classify_identity(
    name: str,
    email: str,
    role: str,
    policy: PublicIdentityPolicy | None = None,
) -> str:
    name = name.strip()
    email = email.strip()
    if role not in {"author", "committer", "trailer"}:
        raise ValueError(f"unsupported identity role {role!r}")
    if not name:
        return "INVALID_IDENTITY"
    lowered_name = name.lower()
    lowered_email = email.lower()
    if AUTOMATION_MARKER_PATTERN.search(name) or AUTOMATION_MARKER_PATTERN.search(email.split("@", 1)[0]):
        return "UNDECLARED_AUTOMATION_IDENTITY"
    if not VALID_EMAIL_PATTERN.fullmatch(email):
        return "INVALID_IDENTITY"
    if lowered_email == GITHUB_WEB_COMMITTER_EMAIL:
        if name == GITHUB_WEB_COMMITTER_NAME and role == "committer":
            return "GITHUB_WEB_COMMITTER"
        if name == GITHUB_WEB_COMMITTER_NAME:
            return "GITHUB_WEB_COMMITTER_WRONG_ROLE"
        return "UNAUTHORIZED_SYSTEM_IDENTITY"
    if policy is not None and lowered_email == policy.email.lower():
        return "MAINTAINER_GITHUB_NOREPLY"
    id_based = ID_BASED_NOREPLY_PATTERN.fullmatch(email)
    if id_based:
        return "PUBLIC_ID_BASED_NOREPLY"
    if USERNAME_ONLY_NOREPLY_PATTERN.fullmatch(email):
        return "PUBLIC_USERNAME_NOREPLY"
    if lowered_email.endswith("@users.noreply.github.com"):
        return "INVALID_IDENTITY"
    if lowered_name in {"unknown", "n/a", "none"}:
        return "INVALID_IDENTITY"
    # No non-noreply identity is assumed public without an explicit human decision.
    return "PRIVATE_EMAIL_REVIEW_REQUIRED"


def _identity(
    raw: str,
    role: str,
    policy: PublicIdentityPolicy | None = None,
) -> tuple[Identity, str]:
    match = IDENTITY_PATTERN.match(raw)
    if not match:
        identity = Identity(redact_text(raw.strip()) or "<missing>", "<invalid>", "INVALID_IDENTITY")
        return identity, ""
    name, email, date = (part.strip() for part in match.groups())
    return Identity(name, mask_email(email), classify_identity(name, email, role, policy)), date


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
        author, author_date = _identity(headers["author"][0], "author", policy)
        committer, committer_date = _identity(headers["committer"][0], "committer", policy)
    except (KeyError, IndexError) as error:
        raise HistoryAuditError(f"commit {oid} lacks author or committer metadata") from error
    trailers: list[dict[str, str]] = []
    for line in message.splitlines():
        match = TRAILER_PATTERN.match(line.strip())
        if not match:
            continue
        label, value = match.groups()
        trailer_identity, _ = _identity(value, "trailer", policy)
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
        (
            "for-each-ref",
            "--format=%(refname)%00%(objecttype)%00%(objectname)%00%(symref)%00",
        ),
        cwd=root,
    )
    fields = raw.decode("utf-8", errors="replace").split("\x00")
    records: list[dict[str, str]] = []
    for index in range(0, len(fields) - 3, 4):
        name, object_type, oid, symref = fields[index : index + 4]
        name = name.lstrip("\n")
        if name:
            records.append(
                {
                    "name": redact_text(name),
                    "object_type": object_type,
                    "oid": oid,
                    "symref": redact_text(symref),
                }
            )
    return tuple(sorted(records, key=lambda item: item["name"]))


def _github_pr_context(
    root: Path,
    refs: tuple[dict[str, str], ...],
    environment: Mapping[str, str],
) -> GitHubPullRequestContext:
    """Validate an Actions pull-request merge using only local, correlated proof."""

    head_oid = _git(("rev-parse", "HEAD"), cwd=root).decode("ascii", errors="strict").strip()
    attempted = (
        environment.get("GITHUB_EVENT_NAME") == "pull_request"
        or environment.get("GITHUB_REF", "").startswith("refs/pull/")
        or any(ref["name"].startswith("refs/remotes/pull/") for ref in refs)
    )
    if not attempted:
        return GitHubPullRequestContext(
            attempted=False,
            valid=False,
            pr_number=None,
            repository=None,
            head_oid=head_oid,
            base_oid=None,
            source_oid=None,
            merge_ref=None,
            evidence=(),
            failures=(),
        )

    failures: list[str] = []
    if environment.get("GITHUB_ACTIONS") != "true":
        failures.append("GITHUB_ACTIONS_NOT_TRUE")
    if environment.get("GITHUB_EVENT_NAME") != "pull_request":
        failures.append("GITHUB_EVENT_NAME_MISMATCH")

    github_ref = environment.get("GITHUB_REF", "")
    ref_match = GITHUB_PR_REF_PATTERN.fullmatch(github_ref)
    pr_number = int(ref_match.group("number")) if ref_match else None
    if ref_match is None:
        failures.append("GITHUB_REF_INVALID")

    github_sha = environment.get("GITHUB_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", github_sha) or github_sha != head_oid:
        failures.append("GITHUB_SHA_MISMATCH")

    event_path_value = environment.get("GITHUB_EVENT_PATH", "")
    if not event_path_value:
        failures.append("GITHUB_EVENT_PATH_MISSING")
        payload: object = {}
    else:
        event_path = Path(event_path_value)
        if not event_path.is_file():
            raise HistoryAuditError("GitHub pull-request event payload is absent or unreadable")
        try:
            payload = json.loads(event_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise HistoryAuditError("GitHub pull-request event payload is invalid") from error

    pull_request: object = payload.get("pull_request") if isinstance(payload, dict) else None
    if not isinstance(pull_request, dict):
        failures.append("PULL_REQUEST_PAYLOAD_MISSING")
        pull_request = {}

    payload_number = payload.get("number") if isinstance(payload, dict) else None
    embedded_number = pull_request.get("number")
    if (
        not isinstance(payload_number, int)
        or isinstance(payload_number, bool)
        or payload_number < 1
        or payload_number != pr_number
        or (embedded_number is not None and embedded_number != payload_number)
    ):
        failures.append("PULL_REQUEST_NUMBER_MISMATCH")

    repository_payload = payload.get("repository") if isinstance(payload, dict) else None
    payload_repository = (
        repository_payload.get("full_name") if isinstance(repository_payload, dict) else None
    )
    github_repository = environment.get("GITHUB_REPOSITORY", "")
    if (
        not GITHUB_REPOSITORY_PATTERN.fullmatch(github_repository)
        or payload_repository != github_repository
    ):
        failures.append("GITHUB_REPOSITORY_MISMATCH")

    base = pull_request.get("base") if isinstance(pull_request, dict) else None
    source = pull_request.get("head") if isinstance(pull_request, dict) else None
    base_oid = base.get("sha") if isinstance(base, dict) else None
    source_oid = source.get("sha") if isinstance(source, dict) else None
    if not isinstance(base_oid, str) or not re.fullmatch(r"[0-9a-f]{40}", base_oid):
        failures.append("PULL_REQUEST_BASE_SHA_MISSING")
        base_oid = None
    if not isinstance(source_oid, str) or not re.fullmatch(r"[0-9a-f]{40}", source_oid):
        failures.append("PULL_REQUEST_HEAD_SHA_MISSING")
        source_oid = None

    parents = _git(("show", "-s", "--format=%P", "HEAD"), cwd=root).decode("ascii").split()
    if len(parents) != 2:
        failures.append("HEAD_PARENT_COUNT_MISMATCH")
    else:
        if parents[0] != base_oid:
            failures.append("HEAD_BASE_PARENT_MISMATCH")
        if parents[1] != source_oid:
            failures.append("HEAD_SOURCE_PARENT_MISMATCH")

    merge_ref = f"refs/remotes/pull/{pr_number}/merge" if pr_number is not None else None
    observed = tuple(ref for ref in refs if ref["name"] == merge_ref)
    if (
        merge_ref is None
        or len(observed) != 1
        or observed[0]["object_type"] != "commit"
        or observed[0]["oid"] != head_oid
        or observed[0]["oid"] != github_sha
    ):
        failures.append("SYNTHETIC_MERGE_REF_MISMATCH")

    valid = not failures
    return GitHubPullRequestContext(
        attempted=True,
        valid=valid,
        pr_number=pr_number,
        repository=github_repository or None,
        head_oid=head_oid,
        base_oid=base_oid,
        source_oid=source_oid,
        merge_ref=merge_ref,
        evidence=GITHUB_PR_REQUIRED_EVIDENCE if valid else (),
        failures=tuple(dict.fromkeys(failures)),
    )


def _detached_head(root: Path) -> bool:
    return _git(("rev-parse", "--abbrev-ref", "HEAD"), cwd=root).decode("utf-8").strip() == "HEAD"


def _current_branch(root: Path) -> str | None:
    name = _git(("rev-parse", "--abbrev-ref", "HEAD"), cwd=root).decode("utf-8").strip()
    return None if name == "HEAD" else name


def _base_audit_refs(root: Path, refs: tuple[dict[str, str], ...]) -> tuple[str, ...]:
    raw_names = tuple(item["name"] for item in refs)
    current_branch = _current_branch(root)
    if current_branch is not None:
        if EXPECTED_PUBLIC_REF not in raw_names:
            raise HistoryAuditError(f"required publication ref {EXPECTED_PUBLIC_REF} is absent")
        if current_branch == "main":
            return (EXPECTED_PUBLIC_REF,)
        contribution_ref = f"refs/heads/{current_branch}"
        if contribution_ref not in raw_names:
            raise HistoryAuditError(f"current contribution ref {contribution_ref} is absent")
        return (EXPECTED_PUBLIC_REF, contribution_ref)
    bases = ["HEAD"]
    if EXPECTED_PUBLIC_REF in raw_names:
        bases.append(EXPECTED_PUBLIC_REF)
    if EXPECTED_REMOTE_MAIN in raw_names:
        bases.append(EXPECTED_REMOTE_MAIN)
    if len(bases) == 1:
        raise HistoryAuditError("detached checkout lacks a main base ref")
    return tuple(bases)


def _selected_refs(root: Path, refs: tuple[dict[str, str], ...], all_refs: bool) -> tuple[str, ...]:
    raw_names = tuple(item["name"] for item in refs)
    if all_refs:
        if not raw_names:
            raise HistoryAuditError("the repository has no refs to inspect")
        selected = list(raw_names)
        if _detached_head(root):
            selected.append("HEAD")
        return tuple(dict.fromkeys(selected))
    return _base_audit_refs(root, refs)


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


def _reachable_commit_oids(root: Path, refs: Sequence[str]) -> frozenset[str]:
    raw = _git(("rev-list", *refs), cwd=root)
    return frozenset(raw.decode("ascii", errors="strict").splitlines())


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    process = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        capture_output=True,
    )
    if process.returncode == 0:
        return True
    if process.returncode == 1:
        return False
    detail = process.stderr.decode("utf-8", errors="replace").strip()
    raise HistoryAuditError(detail or "git merge-base --is-ancestor failed")


def _release_version(tag: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in tag[1:].split("."))  # type: ignore[return-value]


def _release_policy_findings(release_policy: ReleasePolicy) -> list[Finding]:
    findings: list[Finding] = []
    signatures = release_policy.signatures
    for record in release_policy.current_releases.values():
        version = _release_version(record.tag)
        is_future = version >= signatures.required_from
        if is_future and signatures.status != "ACTIVE":
            findings.append(
                Finding(
                    "REVIEW",
                    "CURRENT_RELEASE_BLOCKED_BY_SIGNATURE_POLICY",
                    record.tag,
                    "a current release at or after v1.0.1 requires an active SSH signing policy",
                )
            )
        if record.attestation_mode == HISTORICAL_UNSIGNED_ATTESTATION:
            if record.tag != signatures.historical_unsigned_exception:
                findings.append(
                    Finding(
                        "REVIEW",
                        "UNSIGNED_RELEASE_EXCEPTION",
                        record.tag,
                        "only the exact historical v1.0.0 exception may use an unsigned attestation",
                    )
                )
            if is_future:
                findings.append(
                    Finding(
                        "REVIEW",
                        "UNSIGNED_FUTURE_RELEASE",
                        record.tag,
                        "stable releases from v1.0.1 onward require an SSH-signed annotated tag",
                    )
                )
        elif record.attestation_mode == SSH_SIGNED_ATTESTATION:
            identity = signatures.identities.get(record.signing_identity or "")
            if signatures.status != "ACTIVE":
                findings.append(
                    Finding(
                        "REVIEW",
                        "RELEASE_SIGNATURE_GATE",
                        record.tag,
                        signatures.gate,
                    )
                )
            if identity is None:
                findings.append(
                    Finding("REVIEW", "UNKNOWN_SIGNING_IDENTITY", record.tag, "release names no declared signing identity")
                )
            elif (
                identity.revoked_on is not None
                and _release_version(record.tag) > _release_version(identity.last_trusted_release or "")
            ):
                findings.append(
                    Finding(
                        "REVIEW",
                        "RELEASE_AFTER_SIGNER_REVOCATION_BOUNDARY",
                        record.tag,
                        f"release exceeds {identity.last_trusted_release}, the signer's canonical trust boundary",
                    )
                )
        if is_future and record.published and signatures.status != "ACTIVE":
            findings.append(
                Finding(
                    "REVIEW",
                    "PUBLISHED_RELEASE_WITHOUT_ACTIVE_KEY",
                    record.tag,
                    "a release at or after v1.0.1 cannot be published before SSH key selection is active",
                )
            )
    return findings


def _allowed_signers_key(root: Path, identity: SigningIdentity) -> tuple[str | None, str | None]:
    path = root / PurePosixPath(identity.allowed_signers_file)
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--error-unmatch", "--", identity.allowed_signers_file],
        check=False,
        capture_output=True,
    )
    if tracked.returncode:
        return None, "allowed-signers file is not repository-owned and tracked"
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    except (OSError, UnicodeError):
        return None, "repository-owned allowed-signers file is absent or unreadable"
    if len(lines) != 1:
        return None, "allowed-signers file must contain exactly one active signer record"
    try:
        fields = shlex.split(lines[0])
    except ValueError:
        return None, "allowed-signers record is malformed"
    if len(fields) < 4 or fields[0] != identity.principal or fields[1] != "namespaces=git":
        return None, "allowed-signers principal or namespace differs from the release policy"
    key_type, encoded_key = fields[2], fields[3]
    if not (key_type.startswith("ssh-") or key_type.startswith("sk-ssh-")):
        return None, "allowed-signers record does not contain an SSH public key"
    try:
        key_blob = base64.b64decode(encoded_key, validate=True)
    except (ValueError, binascii.Error):
        return None, "allowed-signers SSH public key is not valid base64"
    fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(key_blob).digest()).decode("ascii").rstrip("=")
    if fingerprint != identity.public_key_fingerprint:
        return None, "allowed-signers public key fingerprint differs from the release policy"
    return fingerprint, None


def _verify_ssh_tag(root: Path, tag_object: str, identity: SigningIdentity) -> tuple[bool, str]:
    fingerprint, error = _allowed_signers_key(root, identity)
    if error is not None:
        return False, error
    allowed_signers = (root / PurePosixPath(identity.allowed_signers_file)).resolve()
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "LANG": "C"})
    process = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "gpg.format=ssh",
            "-c",
            f"gpg.ssh.allowedSignersFile={allowed_signers}",
            "verify-tag",
            tag_object,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    output = process.stdout + process.stderr
    if process.returncode != 0:
        return False, "Git SSH signature verification failed"
    if f"for {identity.principal} with" not in output or fingerprint not in output:
        return False, "Git verified a signature but not the declared principal and fingerprint"
    return True, ""


def _release_tag_findings(
    root: Path,
    ref: dict[str, str],
    release_policy: ReleasePolicy,
    identity_policy: PublicIdentityPolicy,
    main_ref: str | None,
) -> list[Finding]:
    findings: list[Finding] = []
    name = ref["name"]
    tag_name = name.removeprefix("refs/tags/")
    historical = release_policy.historical_releases.get(tag_name)
    if historical is not None:
        return [
            Finding(
                "REVIEW",
                "WITHDRAWN_HISTORICAL_TAG_PRESENT",
                name,
                "a release withdrawn during privacy remediation must not have a ref in the canonical repository",
            )
        ]
    declared = release_policy.current_releases.get(tag_name)
    if release_policy.version_pattern.fullmatch(tag_name) is None:
        findings.append(Finding("REVIEW", "INVALID_RELEASE_VERSION", name, "tag name is outside the allowed stable version format"))
    if declared is None:
        findings.append(Finding("REVIEW", "UNEXPECTED_TAG", name, "tag is not declared by governance/release-policy.json"))
    if ref["object_type"] != "tag":
        findings.append(Finding("REVIEW", "LIGHTWEIGHT_RELEASE_TAG", name, "release tags must be annotated tag objects"))
        return findings
    try:
        raw = _git(("cat-file", "tag", ref["oid"]), cwd=root).decode("utf-8", errors="replace")
    except HistoryAuditError:
        findings.append(Finding("REVIEW", "UNREADABLE_TAG_OBJECT", name, "annotated tag object cannot be inspected"))
        return findings
    header, separator, message = raw.partition("\n\n")
    fields: dict[str, str] = {}
    for line in header.splitlines():
        key, space, value = line.partition(" ")
        if space and key not in fields:
            fields[key] = value
    target = fields.get("object", "")
    if fields.get("type") != "commit" or re.fullmatch(r"[0-9a-f]{40}", target) is None:
        findings.append(Finding("REVIEW", "INVALID_TAG_TARGET", name, "annotated release tag must directly target a commit"))
        target = ""
    if fields.get("tag") != tag_name:
        findings.append(Finding("REVIEW", "TAG_NAME_MISMATCH", name, "tag object name does not match its ref"))
    raw_tagger = fields.get("tagger", "")
    tagger_match = IDENTITY_PATTERN.match(raw_tagger)
    if tagger_match is None:
        findings.append(Finding("REVIEW", "TAGGER_IDENTITY", name, "tag object has no valid tagger identity"))
    else:
        tagger_name, tagger_email, tagger_date = (part.strip() for part in tagger_match.groups())
        classification = classify_identity(tagger_name, tagger_email, "committer", identity_policy)
        if re.fullmatch(r"[0-9]+ [+-][0-9]{4}", tagger_date) is None:
            findings.append(Finding("REVIEW", "INVALID_TAGGER_METADATA", name, "tagger timestamp or timezone is invalid"))
        if (tagger_name, tagger_email, classification) not in release_policy.allowed_taggers:
            findings.append(
                Finding(
                    "REVIEW",
                    "TAGGER_IDENTITY",
                    name,
                    f"tagger {tagger_name} <{mask_email(tagger_email)}> is not an authorized release tagger",
                )
            )
    if declared is not None:
        if ref["oid"] != declared.tag_object:
            findings.append(Finding("REVIEW", "TAG_OBJECT_MISMATCH", name, "tag object differs from the locked release record"))
        if target and target != declared.target_commit:
            findings.append(Finding("REVIEW", "TAG_TARGET_MISMATCH", name, "tag target differs from the declared release commit"))
        signed = "-----BEGIN PGP SIGNATURE-----" in message or "-----BEGIN SSH SIGNATURE-----" in message
        if declared.attestation_mode == HISTORICAL_UNSIGNED_ATTESTATION and signed:
            findings.append(Finding("REVIEW", "TAG_ATTESTATION_MISMATCH", name, "historical release record declares an unsigned annotated tag"))
        elif declared.attestation_mode == SSH_SIGNED_ATTESTATION:
            identity = release_policy.signatures.identities.get(declared.signing_identity or "")
            if release_policy.signatures.status != "ACTIVE":
                findings.append(Finding("REVIEW", "RELEASE_SIGNATURE_GATE", name, release_policy.signatures.gate))
            if identity is None:
                findings.append(Finding("REVIEW", "UNKNOWN_SIGNING_IDENTITY", name, "release names no declared signing identity"))
            else:
                verified, detail = _verify_ssh_tag(root, ref["oid"], identity)
                if not verified:
                    findings.append(Finding("REVIEW", "SSH_TAG_SIGNATURE", name, detail))
                if (
                    identity.revoked_on is not None
                    and _release_version(declared.tag) > _release_version(identity.last_trusted_release or "")
                ):
                    findings.append(
                        Finding(
                            "REVIEW",
                            "RELEASE_AFTER_SIGNER_REVOCATION_BOUNDARY",
                            name,
                            f"release exceeds {identity.last_trusted_release}, the signer's canonical trust boundary",
                        )
                    )
    if target:
        if main_ref is None:
            findings.append(Finding("REVIEW", "MAIN_REF_MISSING", name, "canonical main ref is unavailable for tag ancestry validation"))
        elif not _is_ancestor(root, target, main_ref):
            findings.append(Finding("REVIEW", "TAG_TARGET_OUTSIDE_MAIN", name, "tag target is not in the canonical main history"))
    if not findings:
        findings.append(Finding("INFO", "DECLARED_RELEASE_TAG", name, "annotated release tag matches the locked policy and canonical main history"))
    return findings


def _ref_findings(
    root: Path,
    refs: tuple[dict[str, str], ...],
    github_context: GitHubPullRequestContext,
    release_policy: ReleasePolicy,
    identity_policy: PublicIdentityPolicy,
) -> list[Finding]:
    """Classify publishable refs separately from transport refs and HEAD.

    ``refs/heads/*``, tags, notes, and custom refs are locally publishable and
    remain strict except for the bounded current contribution branch.
    ``refs/remotes/*`` are transport metadata: only ``origin`` is recognized,
    and its refs must describe the graph already audited from main, the current
    contribution branch, or a detached pull-request checkout. HEAD names the
    currently audited commit but is not itself a publishable ref.
    """
    findings: list[Finding] = []
    by_name = {ref["name"]: ref for ref in refs}
    canonical_main_ref = (
        EXPECTED_PUBLIC_REF
        if EXPECTED_PUBLIC_REF in by_name
        else EXPECTED_REMOTE_MAIN
        if EXPECTED_REMOTE_MAIN in by_name
        else None
    )
    current_branch = _current_branch(root)
    detached = current_branch is None
    contribution_ref = (
        f"refs/heads/{current_branch}"
        if current_branch is not None and current_branch != "main"
        else None
    )
    contribution_remote_ref = (
        f"refs/remotes/origin/{current_branch}" if contribution_ref is not None else None
    )
    base_refs = _base_audit_refs(root, refs)
    graph_roots = (
        tuple(ref for ref in base_refs if ref != EXPECTED_REMOTE_MAIN)
        if detached
        else base_refs
    )
    audited_graph = _reachable_commit_oids(root, graph_roots)
    contribution_history = (
        _reachable_commit_oids(root, (contribution_ref,))
        if contribution_ref is not None
        else frozenset()
    )
    if contribution_ref is not None:
        main_history = _reachable_commit_oids(root, (EXPECTED_PUBLIC_REF,))
        if not main_history.intersection(contribution_history):
            findings.append(
                Finding(
                    "REVIEW",
                    "UNRELATED_CONTRIBUTION_HISTORY",
                    contribution_ref,
                    "current contribution branch has no common base with main",
                )
            )
    configured_remotes = tuple(
        name for name in _git(("remote",), cwd=root).decode("utf-8", errors="replace").splitlines() if name
    )
    for remote in sorted(configured_remotes):
        if remote != "origin":
            findings.append(
                Finding("REVIEW", "UNEXPECTED_REMOTE", redact_text(remote), "only remote origin is allowed")
            )
    for ref in refs:
        name = ref["name"]
        if name == EXPECTED_PUBLIC_REF:
            continue
        if (
            github_context.valid
            and name == github_context.merge_ref
            and ref["object_type"] == "commit"
            and ref["oid"] == github_context.head_oid
        ):
            findings.append(
                Finding(
                    "INFO",
                    "GITHUB_PR_MERGE_REF",
                    name,
                    "validated ephemeral pull-request merge ref points exactly to HEAD",
                )
            )
            continue
        if contribution_ref is not None and name == contribution_ref:
            findings.append(
                Finding(
                    "INFO",
                    "CONTRIBUTION_REF",
                    name,
                    "current local contribution ref is transient and included in the audited graph",
                )
            )
            continue
        if name.startswith("refs/remotes/"):
            parts = name.split("/", 3)
            remote = parts[2] if len(parts) > 2 else ""
            if remote != "origin":
                findings.append(
                    Finding("REVIEW", "UNEXPECTED_REMOTE", name, "remote-tracking ref is not owned by origin")
                )
                continue
            if ref["object_type"] != "commit" or ref["oid"] not in audited_graph:
                findings.append(
                    Finding(
                        "REVIEW",
                        "REMOTE_REF_OUTSIDE_AUDITED_GRAPH",
                        name,
                        "remote-tracking ref does not resolve inside the audited commit graph",
                    )
                )
                continue
            if name == EXPECTED_REMOTE_HEAD:
                if ref.get("symref") != EXPECTED_REMOTE_MAIN:
                    findings.append(
                        Finding(
                            "REVIEW",
                            "INVALID_REMOTE_HEAD",
                            name,
                            "origin/HEAD must resolve symbolically to origin/main",
                        )
                    )
                else:
                    findings.append(
                        Finding("INFO", "EXPECTED_REMOTE_HEAD", name, "transport ref resolves to origin/main")
                    )
                continue
            if name == EXPECTED_REMOTE_MAIN:
                local_main = by_name.get(EXPECTED_PUBLIC_REF)
                if not detached and (local_main is None or local_main["oid"] != ref["oid"]):
                    findings.append(
                        Finding(
                            "REVIEW",
                            "DIVERGENT_REMOTE_MAIN",
                            name,
                            "origin/main differs from the publishable main branch",
                        )
                    )
                elif detached and local_main is not None and local_main["oid"] != ref["oid"]:
                    findings.append(
                        Finding(
                            "REVIEW",
                            "DIVERGENT_REMOTE_MAIN",
                            name,
                            "origin/main differs from the available local main branch",
                        )
                    )
                else:
                    findings.append(
                        Finding("INFO", "EXPECTED_REMOTE_MAIN", name, "transport ref is inside the audited graph")
                    )
                continue
            if contribution_remote_ref is not None and name == contribution_remote_ref:
                if ref["oid"] not in contribution_history:
                    findings.append(
                        Finding(
                            "REVIEW",
                            "DIVERGENT_CONTRIBUTION_REF",
                            name,
                            "remote contribution ref is not the local contribution head or one of its ancestors",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            "INFO",
                            "CONTRIBUTION_REF",
                            name,
                            "origin contribution ref is transient and synchronized or behind the local branch",
                        )
                    )
                continue
            if detached:
                findings.append(
                    Finding(
                        "INFO",
                        "CHECKOUT_REMOTE_REF",
                        name,
                        "detached-checkout transport ref is inside the audited graph",
                    )
                )
            else:
                findings.append(
                    Finding("REVIEW", "UNEXPECTED_REMOTE_REF", name, "unexpected origin transport ref")
                )
            continue
        if name.startswith("refs/tags/"):
            findings.extend(
                _release_tag_findings(
                    root,
                    ref,
                    release_policy,
                    identity_policy,
                    canonical_main_ref,
                )
            )
            continue
        elif name.startswith("refs/heads/"):
            category = "UNEXPECTED_BRANCH"
        elif name.startswith("refs/notes/"):
            category = "GIT_NOTES_REF"
        else:
            category = "UNEXPECTED_REF"
        findings.append(
            Finding("REVIEW", category, name, "publishable ref is outside refs/heads/main")
        )
    return findings


def audit(
    root: Path,
    *,
    all_refs: bool = False,
    max_blob_bytes: int = DEFAULT_MAX_BLOB_BYTES,
    environment: Mapping[str, str] | None = None,
) -> AuditReport:
    if max_blob_bytes < 1:
        raise HistoryAuditError("--max-blob-bytes must be a positive integer")
    root = repository_root(root)
    policy = _load_identity_policy(root)
    release_policy = _load_release_policy(root)
    refs = _all_refs(root)
    github_context = _github_pr_context(root, refs, os.environ if environment is None else environment)
    selected = _selected_refs(root, refs, all_refs)
    objects = _reachable_objects(root, selected)
    commits = _reachable_commits(root, selected)
    findings: list[Finding] = []
    if github_context.attempted and not github_context.valid:
        findings.append(
            Finding(
                "REVIEW",
                "GITHUB_PR_CONTEXT_INVALID",
                "github-actions-context",
                "ephemeral merge exception rejected: " + ", ".join(github_context.failures),
            )
        )
    findings.extend(_release_policy_findings(release_policy))
    findings.extend(_ref_findings(root, refs, github_context, release_policy, policy))

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
        if github_context.valid and oid == github_context.head_oid:
            record = dataclasses.replace(
                record,
                author=Identity("<ephemeral>", "<excluded>", "EPHEMERAL_METADATA_EXCLUDED"),
                committer=Identity("<ephemeral>", "<excluded>", "EPHEMERAL_METADATA_EXCLUDED"),
                author_date="<excluded>",
                committer_date="<excluded>",
                subject="<ephemeral GitHub pull-request merge metadata excluded>",
                trailers=(),
                persistence=EPHEMERAL_GITHUB_PR_MERGE,
            )
            commit_records.append(record)
            continue
        commit_records.append(record)
        for role, identity in (("author", record.author), ("committer", record.committer)):
            identities.add((identity.name, identity.email, identity.classification))
            accepted = (
                policy.accepted_author_classes
                if role == "author"
                else policy.accepted_committer_classes
            )
            if identity.classification not in accepted:
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
            severity = "INFO" if classification in policy.accepted_trailer_classes else "REVIEW"
            findings.append(
                Finding(
                    severity,
                    "IDENTITY_TRAILER",
                    f"commit:{oid}",
                    f"{trailer['label']} {trailer['name']} <{trailer['email']}> ({classification})",
                )
            )
        findings.extend(_content_findings(f"commit:{oid}", message, commit_message=True))

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
        "persistent_commits": sum(
            record.persistence == PERSISTENT_HISTORY for record in commit_records
        ),
        "ephemeral_pr_merge_commits": sum(
            record.persistence == EPHEMERAL_GITHUB_PR_MERGE for record in commit_records
        ),
        "total_scanned_commits": len(commit_records),
        "github_pr_context_validated": github_context.valid,
        "github_pr_number": github_context.pr_number if github_context.valid else None,
        "github_pr_context_evidence": list(github_context.evidence),
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
    print(f"PERSISTENT_HISTORY={metrics['persistent_commits']}")
    print(f"EPHEMERAL_GITHUB_PR_MERGE={metrics['ephemeral_pr_merge_commits']}")
    print(f"TOTAL_SCANNED_COMMITS={metrics['total_scanned_commits']}")
    if metrics["ephemeral_pr_merge_commits"]:
        print(
            "GITHUB_PR_CONTEXT_EVIDENCE="
            + ",".join(str(item) for item in metrics["github_pr_context_evidence"])
        )
        print(
            "Validated GitHub pull-request merge metadata is ephemeral and excluded from "
            "publication identity/message policy; its parents, tree, and reachable blobs remain scanned."
        )
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
    parser.add_argument(
        "--all-refs",
        action="store_true",
        help="scan objects reachable from every ref while enforcing the bounded ref policy",
    )
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
