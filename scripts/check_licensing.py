#!/usr/bin/env python3
"""Validate EGX_Terminal's file-scoped licensing policy without network access.

This repository-specific control complements, but does not replace, the official
REUSE linter or a contextual legal/provenance review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


EXPECTED_COPYRIGHT = "2026 Maxime Erard"
ALLOWED_LICENSES = frozenset({"Apache-2.0", "CC-BY-4.0"})
EXPECTED_LICENSE_FILES = {
    "Apache-2.0": "LICENSES/Apache-2.0.txt",
    "CC-BY-4.0": "LICENSES/CC-BY-4.0.txt",
}
EXPECTED_LICENSE_URLS = {
    "Apache-2.0": "https://www.apache.org/licenses/LICENSE-2.0.txt",
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/legalcode.txt",
}
EXPECTED_LICENSE_HASHES = {
    "Apache-2.0": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "CC-BY-4.0": "9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94",
}
EXPECTED_ARCHIVE_HASH = "c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0"
FORBIDDEN_ROOT_PATHS = (
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    "opencode.json",
    "doctrine/KERNEL.md",
)
SPDX_TAG = re.compile(
    r"^\s*(?:#|//|/\*|\*|<!--|;)\s*"
    r"(SPDX-(?:License-Identifier|FileCopyrightText)):\s*(.*?)\s*(?:\*/|-->)?\s*$"
)
COMBINED_LICENSE = re.compile(r"\bApache-2\.0\s+(?:OR|AND)\s+CC-BY-4\.0\b", re.I)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    code: str
    message: str


@dataclass(frozen=True)
class Annotation:
    index: int
    paths: tuple[str, ...]
    precedence: str
    copyright_text: str
    license_id: str
    comment: str


@dataclass(frozen=True)
class Report:
    tracked: int
    exempt: int
    covered: int
    licensed: int
    findings: tuple[Finding, ...]


class LicensingError(RuntimeError):
    """Configuration or Git data could not be read."""


def _git(arguments: Sequence[str], *, cwd: Path) -> bytes:
    process = subprocess.run(
        ["git", "-C", str(cwd), *arguments], check=False, capture_output=True
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise LicensingError(detail or f"git {' '.join(arguments)} failed")
    return process.stdout


def repository_root(start: Path | None = None) -> Path:
    anchor = start if start is not None else Path(__file__).resolve().parent
    return Path(os.fsdecode(_git(("rev-parse", "--show-toplevel"), cwd=anchor)).strip()).resolve()


def tracked_files(root: Path) -> tuple[str, ...]:
    raw = _git(("ls-files", "-z"), cwd=root)
    return tuple(sorted(PurePosixPath(os.fsdecode(item)).as_posix() for item in raw.split(b"\0") if item))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\0")
    return digest.hexdigest()


def _glob_regex(pattern: str) -> re.Pattern[str]:
    if not pattern or "\\" in pattern or pattern.startswith("/"):
        raise ValueError("patterns must be non-empty relative POSIX paths")
    if ".." in PurePosixPath(pattern).parts or any(char in pattern for char in "?[]"):
        raise ValueError("unsupported glob syntax")
    output = ["^"]
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            output.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            output.append(".*")
            index += 2
        elif pattern[index] == "*":
            output.append("[^/]*")
            index += 1
        else:
            output.append(re.escape(pattern[index]))
            index += 1
    output.append("$")
    return re.compile("".join(output))


def glob_matches(pattern: str, path: str) -> bool:
    return bool(_glob_regex(pattern).fullmatch(PurePosixPath(path).as_posix()))


def _finding(path: str, code: str, message: str) -> Finding:
    return Finding(path, code, message)


def load_annotations(root: Path) -> tuple[tuple[Annotation, ...], list[Finding]]:
    target = root / "REUSE.toml"
    if not target.is_file():
        return (), [_finding("REUSE.toml", "MISSING_METADATA", "required metadata file is absent")]
    try:
        data = tomllib.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        return (), [_finding("REUSE.toml", "INVALID_TOML", str(error))]
    findings: list[Finding] = []
    if data.get("version") != 1:
        findings.append(_finding("REUSE.toml", "SCHEMA_VERSION", "version must equal 1"))
    raw_annotations = data.get("annotations")
    if not isinstance(raw_annotations, list):
        findings.append(_finding("REUSE.toml", "ANNOTATIONS", "annotations must be an array of tables"))
        return (), findings
    annotations: list[Annotation] = []
    for index, raw in enumerate(raw_annotations, start=1):
        location = f"REUSE.toml#annotations[{index}]"
        if not isinstance(raw, dict):
            findings.append(_finding(location, "ANNOTATION", "annotation must be a table"))
            continue
        paths = raw.get("path")
        if isinstance(paths, str):
            paths = [paths]
        if not isinstance(paths, list) or not paths or not all(isinstance(item, str) for item in paths):
            findings.append(_finding(location, "PATHS", "path must be a string or non-empty string array"))
            continue
        for pattern in paths:
            try:
                _glob_regex(pattern)
            except ValueError as error:
                findings.append(_finding(location, "UNSUPPORTED_GLOB", f"{pattern!r}: {error}"))
        precedence = raw.get("precedence", "closest")
        if precedence not in {"closest", "aggregate", "override"}:
            findings.append(_finding(location, "PRECEDENCE", f"unsupported precedence {precedence!r}"))
        copyright_text = raw.get("SPDX-FileCopyrightText")
        license_id = raw.get("SPDX-License-Identifier")
        comment = raw.get("SPDX-FileComment", "")
        if not isinstance(copyright_text, str) or not isinstance(license_id, str) or not isinstance(comment, str):
            findings.append(_finding(location, "ANNOTATION_FIELDS", "SPDX fields must be strings"))
            continue
        if COMBINED_LICENSE.search(license_id) or " OR " in license_id or " AND " in license_id:
            findings.append(_finding(location, "COMBINED_LICENSE", "original files must have exactly one license"))
        if license_id not in ALLOWED_LICENSES:
            findings.append(_finding(location, "LICENSE_ID", f"unauthorized SPDX identifier {license_id!r}"))
        third_party = comment.startswith("THIRD_PARTY_MATERIAL_WITH_PROVEN_LICENSE:")
        if "PROVENANCE_UNCLEAR" in comment:
            findings.append(_finding(location, "PROVENANCE_UNCLEAR", "unclear provenance is a publication blocker"))
        if third_party:
            if "source=" not in comment or copyright_text == EXPECTED_COPYRIGHT:
                findings.append(_finding(location, "THIRD_PARTY_PROVENANCE", "third-party annotation needs source= and its own copyright"))
        elif copyright_text != EXPECTED_COPYRIGHT:
            findings.append(_finding(location, "COPYRIGHT", f"expected {EXPECTED_COPYRIGHT!r}"))
        annotations.append(
            Annotation(index, tuple(paths), precedence, copyright_text, license_id, comment)
        )
    return tuple(annotations), findings


def is_exempt(root: Path, path: str) -> bool:
    relative = PurePosixPath(path)
    if path in {"LICENSE", "REUSE.toml"} or path.startswith("LICENSES/") or path.startswith(".reuse/"):
        return True
    if path.endswith((".spdx", ".spdx.json", ".spdx.rdf", ".spdx.yaml", ".spdx.yml")):
        return True
    target = root / Path(*relative.parts)
    return target.is_file() and target.stat().st_size == 0


def expected_license(path: str) -> str | None:
    if path == "README.md" or path.startswith("docs/"):
        return "CC-BY-4.0"
    if path in {".gitattributes", ".gitignore"} or path.startswith(("scripts/", "tests/", "experiments/", "licensing/")):
        return "Apache-2.0"
    return None


def _internal_spdx(path: Path) -> tuple[dict[str, set[str]], list[Finding]]:
    tags = {"SPDX-License-Identifier": set(), "SPDX-FileCopyrightText": set()}
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:80]
    except (OSError, UnicodeError):
        return tags, findings
    for line_number, line in enumerate(lines, start=1):
        match = SPDX_TAG.match(line)
        if match:
            tags[match.group(1)].add(match.group(2).strip())
            if match.group(1) == "SPDX-License-Identifier" and COMBINED_LICENSE.search(match.group(2)):
                findings.append(_finding(path.as_posix(), "COMBINED_LICENSE", f"combined license in internal tag at line {line_number}"))
    return tags, findings


def check_license_lock(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    lock_path = root / "licensing" / "license-lock.json"
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [_finding("licensing/license-lock.json", "MISSING_LOCK", "license lock is absent")]
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [_finding("licensing/license-lock.json", "INVALID_LOCK", str(error))]
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("licenses"), list):
        return [_finding("licensing/license-lock.json", "LOCK_SCHEMA", "expected schema_version 1 and licenses array")]
    records = data["licenses"]
    by_id = {item.get("spdx_id"): item for item in records if isinstance(item, dict)}
    if set(by_id) != ALLOWED_LICENSES or len(records) != len(ALLOWED_LICENSES):
        findings.append(_finding("licensing/license-lock.json", "LOCK_LICENSES", "lock must contain each allowed license exactly once"))
    for identifier in sorted(ALLOWED_LICENSES):
        record = by_id.get(identifier)
        if not isinstance(record, dict):
            continue
        relative = record.get("file")
        expected_file = EXPECTED_LICENSE_FILES[identifier]
        if relative != expected_file:
            findings.append(_finding("licensing/license-lock.json", "LOCK_FILE", f"{identifier} must name {expected_file}"))
            relative = expected_file
        if record.get("source_url") != EXPECTED_LICENSE_URLS[identifier]:
            findings.append(_finding(relative, "LICENSE_URL", "canonical source URL is incorrect"))
        if record.get("encoding") != "UTF-8" or record.get("retrieved") != "2026-07-21":
            findings.append(_finding(relative, "LOCK_METADATA", "encoding or retrieval date is incorrect"))
        comparison = record.get("second_source_comparison")
        if not isinstance(comparison, dict) or not comparison.get("source_url") or not comparison.get("status"):
            findings.append(_finding(relative, "SECOND_SOURCE", "official comparison status is missing"))
        target = root / Path(*PurePosixPath(relative).parts)
        if not target.is_file():
            findings.append(_finding(relative, "MISSING_LICENSE_TEXT", "expected license text is absent"))
            continue
        actual = sha256_file(target)
        if record.get("sha256") != actual:
            findings.append(_finding(relative, "LOCK_HASH", "file hash does not match the lock"))
        if actual != EXPECTED_LICENSE_HASHES[identifier]:
            findings.append(_finding(relative, "CANONICAL_HASH", "file hash does not match the reviewed canonical text"))
    directory = root / "LICENSES"
    actual_names = {item.name for item in directory.iterdir() if item.is_file()} if directory.is_dir() else set()
    expected_names = {PurePosixPath(item).name for item in EXPECTED_LICENSE_FILES.values()}
    for name in sorted(actual_names - expected_names):
        findings.append(_finding(f"LICENSES/{name}", "FOREIGN_LICENSE_FILE", "undocumented license text"))
    return findings


def check_summary(root: Path) -> list[Finding]:
    target = root / "LICENSE"
    if not target.is_file():
        return [_finding("LICENSE", "MISSING_SUMMARY", "root license summary is absent")]
    text = target.read_text(encoding="utf-8")
    required = ("file-scoped", "Apache-2.0", "CC-BY-4.0", "REUSE.toml", "LICENSES/", "Third-party", "trademark", "docs/publication/LICENSING.md")
    return [_finding("LICENSE", "SUMMARY", f"missing required concept {term!r}") for term in required if term not in text]


def check_integrity(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    archive = root / "experiments" / "kernel-v1"
    if not archive.is_dir() or tree_sha256(archive) != EXPECTED_ARCHIVE_HASH:
        findings.append(_finding("experiments/kernel-v1", "ARCHIVE_HASH", "immutable archive hash differs"))
    manifest_path = root / "experiments/kernel-micro-v1/behavioral/final-v1/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        frozen = manifest["frozen_files"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return findings + [_finding(manifest_path.as_posix(), "FROZEN_MANIFEST", "cannot read frozen-file manifest")]
    for relative, expected in sorted(frozen.items()):
        target = root / Path(*PurePosixPath(relative).parts)
        if not target.is_file() or sha256_file(target) != expected:
            findings.append(_finding(relative, "FROZEN_HASH", "Mission 24 frozen file differs"))
    return findings


def audit(root: Path, files: Iterable[str], *, enforce_integrity: bool = True) -> Report:
    root = root.resolve()
    tracked = tuple(sorted(PurePosixPath(item).as_posix() for item in files))
    annotations, findings = load_annotations(root)
    findings.extend(check_license_lock(root))
    findings.extend(check_summary(root))
    if (root / ".reuse" / "dep5").exists():
        findings.append(_finding(".reuse/dep5", "DEPRECATED_DEP5", "deprecated metadata is forbidden"))
    for forbidden in FORBIDDEN_ROOT_PATHS:
        if (root / Path(*PurePosixPath(forbidden).parts)).exists():
            findings.append(_finding(forbidden, "NEUTRAL_ROOT", "forbidden doctrinal root path exists"))
    for notice in ("NOTICE", "THIRD_PARTY_NOTICES.md"):
        target = root / notice
        if target.exists():
            content = target.read_text(encoding="utf-8", errors="replace").strip() if target.is_file() else ""
            policy = (root / "docs/publication/LICENSING.md").read_text(encoding="utf-8", errors="replace") if (root / "docs/publication/LICENSING.md").is_file() else ""
            if not content or notice not in policy:
                findings.append(_finding(notice, "UNJUSTIFIED_NOTICE", "notice is empty or not justified by policy"))
    covered = 0
    licensed = 0
    exempt = 0
    pattern_hits = {(annotation.index, pattern): 0 for annotation in annotations for pattern in annotation.paths}
    for path in tracked:
        target = root / Path(*PurePosixPath(path).parts)
        if is_exempt(root, path):
            exempt += 1
            continue
        covered += 1
        matches: list[Annotation] = []
        for annotation in annotations:
            annotation_matched = False
            for pattern in annotation.paths:
                if glob_matches(pattern, path):
                    pattern_hits[(annotation.index, pattern)] += 1
                    annotation_matched = True
            if annotation_matched:
                matches.append(annotation)
        if not matches:
            findings.append(_finding(path, "UNCLASSIFIED", "tracked covered file has no annotation"))
            continue
        if len(matches) > 1:
            findings.append(_finding(path, "MULTIPLE_CLASSIFICATION", "covered file matches more than one annotation"))
            continue
        annotation = matches[0]
        expected = expected_license(path)
        if expected is None and not annotation.comment.startswith("THIRD_PARTY_MATERIAL_WITH_PROVEN_LICENSE:"):
            findings.append(_finding(path, "UNKNOWN_CATEGORY", "original file is outside the documented boundary"))
        elif expected is not None and annotation.license_id != expected:
            findings.append(_finding(path, "BOUNDARY", f"expected {expected}, found {annotation.license_id}"))
        else:
            licensed += 1
        tags, tag_findings = _internal_spdx(target)
        findings.extend(tag_findings)
        if tags["SPDX-License-Identifier"] and tags["SPDX-License-Identifier"] != {annotation.license_id}:
            findings.append(_finding(path, "INTERNAL_LICENSE_CONFLICT", "internal SPDX license conflicts with REUSE.toml"))
        if tags["SPDX-FileCopyrightText"] and tags["SPDX-FileCopyrightText"] != {annotation.copyright_text}:
            findings.append(_finding(path, "INTERNAL_COPYRIGHT_CONFLICT", "internal SPDX copyright conflicts with REUSE.toml"))
    for (index, pattern), hits in sorted(pattern_hits.items()):
        if hits == 0:
            findings.append(_finding(f"REUSE.toml#annotations[{index}]", "UNMATCHED_PATTERN", f"pattern {pattern!r} matches no covered tracked file"))
    if enforce_integrity:
        findings.extend(check_integrity(root))
    ordered = tuple(sorted(set(findings)))
    return Report(len(tracked), exempt, covered, licensed, ordered)


def format_finding(finding: Finding) -> str:
    return f"{finding.path} [{finding.code}] {finding.message}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Git worktree to inspect")
    arguments = parser.parse_args(argv)
    try:
        root = repository_root(arguments.root)
        report = audit(root, tracked_files(root), enforce_integrity=True)
    except (LicensingError, OSError) as error:
        print(f"Licensing check could not start: {error}")
        return 2
    if report.findings:
        print(f"Licensing check failed for {root}:")
        for finding in report.findings:
            print(f"  - {format_finding(finding)}")
        print("This local policy check does not replace the official REUSE linter or legal review.")
        return 1
    print(
        f"Licensing accepted for {root}: {report.covered} covered files, "
        f"{report.licensed} licensed files, {report.exempt} REUSE-exempt files."
    )
    print("This local policy check complements, but does not replace, reuse lint or legal review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
