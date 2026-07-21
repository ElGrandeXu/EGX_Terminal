#!/usr/bin/env python3
"""Validate links in Git-tracked Markdown without network access by default."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unicodedata
from typing import Iterable, Sequence
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
REFERENCE_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)")
REFERENCE_USE_RE = re.compile(r"(?<!!)\[([^\]]+)\]\[([^\]]*)\]")
INLINE_CODE_RE = re.compile(r"(`+)(.*?)\1")
HTML_ANCHOR_RE = re.compile(r"<(?:a|[a-z][a-z0-9-]*)\b[^>]*\b(?:id|name)\s*=\s*['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)
IGNORE_MARKER = "<!-- markdown-link-check: ignore-next-line -->"
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    target: str
    message: str


def repository_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    script_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "-C", str(script_root), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError("cannot resolve the Git repository root")
    return Path(result.stdout.strip()).resolve()


def tracked_markdown(root: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", "*.md"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError("git ls-files failed")
    return tuple(sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item))


def content_markdown(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*.md")
            if ".git" not in path.relative_to(root).parts and "__pycache__" not in path.relative_to(root).parts
        )
    )


def _visible_lines(text: str) -> list[tuple[int, str]]:
    visible: list[tuple[int, str]] = []
    fence: str | None = None
    ignore_next = False
    for number, original in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(original)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            continue
        if fence is not None:
            continue
        if IGNORE_MARKER in original:
            ignore_next = True
            continue
        if ignore_next:
            ignore_next = False
            continue
        visible.append((number, INLINE_CODE_RE.sub("", original)))
    return visible


def github_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for _, line in _visible_lines(text):
        anchors.update(unicodedata.normalize("NFC", item).lower() for item in HTML_ANCHOR_RE.findall(line))
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", match.group(2))
        title = re.sub(r"<[^>]+>", "", title)
        title = unicodedata.normalize("NFC", title).lower().strip()
        slug_chars = [
            char
            for char in title
            if char in {"-", "_", " "} or unicodedata.category(char)[0] in {"L", "N", "M"}
        ]
        base = re.sub(r"\s+", "-", "".join(slug_chars)).strip("-")
        count = counts.get(base, 0)
        anchor = base if count == 0 else f"{base}-{count}"
        counts[base] = count + 1
        anchors.add(anchor)
    return anchors


def _destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    match = re.match(r"(\S+)(?:\s+['\"(].*)?$", value)
    return match.group(1) if match else value


def _external_ok(target: str) -> bool:
    try:
        request = Request(target, method="HEAD", headers={"User-Agent": "EGX-Terminal-link-check/1"})
        with urlopen(request, timeout=10) as response:
            return 200 <= response.status < 400
    except Exception:
        return False


def audit(root: Path, files: Iterable[str], *, include_external: bool = False) -> tuple[Finding, ...]:
    root = root.resolve()
    findings: list[Finding] = []
    cache: dict[Path, set[str]] = {}
    for relative in sorted(PurePosixPath(item).as_posix() for item in files):
        source = root / Path(*PurePosixPath(relative).parts)
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(Finding(relative, 0, "READ_ERROR", "", "cannot read UTF-8 Markdown"))
            continue
        definitions: dict[str, tuple[int, str]] = {}
        uses: list[tuple[int, str]] = []
        candidates: list[tuple[int, str]] = []
        for line_number, line in _visible_lines(text):
            definition = REFERENCE_DEF_RE.match(line)
            if definition:
                key = definition.group(1).strip().casefold()
                definitions[key] = (line_number, _destination(definition.group(2)))
                candidates.append(definitions[key])
            for match in INLINE_LINK_RE.finditer(line):
                candidates.append((line_number, _destination(match.group(1))))
            for match in REFERENCE_USE_RE.finditer(line):
                key = (match.group(2) or match.group(1)).strip().casefold()
                uses.append((line_number, key))
        for line_number, key in uses:
            if key not in definitions:
                findings.append(Finding(relative, line_number, "MISSING_REFERENCE", key, "reference definition is absent"))
        for line_number, target in candidates:
            if not target:
                continue
            parsed = urlsplit(target)
            if parsed.scheme.casefold() in EXTERNAL_SCHEMES or target.startswith("//"):
                if include_external and parsed.scheme.casefold() in {"http", "https"} and not _external_ok(target):
                    findings.append(Finding(relative, line_number, "EXTERNAL_UNREACHABLE", target, "external URL did not validate"))
                continue
            if parsed.scheme or target.startswith("#") and not parsed.fragment:
                continue
            decoded_path = unquote(parsed.path)
            if decoded_path:
                if decoded_path.startswith("/"):
                    destination = root / decoded_path.lstrip("/")
                else:
                    destination = source.parent / decoded_path
            else:
                destination = source
            try:
                resolved = destination.resolve()
                resolved.relative_to(root)
            except (OSError, ValueError):
                findings.append(Finding(relative, line_number, "OUTSIDE_ROOT", target, "local target escapes the repository"))
                continue
            if not resolved.exists():
                findings.append(Finding(relative, line_number, "MISSING_PATH", target, "local target does not exist"))
                continue
            if parsed.fragment:
                if not resolved.is_file() or resolved.suffix.lower() not in {".md", ".markdown"}:
                    findings.append(Finding(relative, line_number, "INVALID_FRAGMENT_TARGET", target, "fragment target is not Markdown"))
                    continue
                if resolved not in cache:
                    try:
                        cache[resolved] = github_anchors(resolved.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError):
                        cache[resolved] = set()
                fragment = unicodedata.normalize("NFC", unquote(parsed.fragment)).lower()
                if fragment not in cache[resolved]:
                    findings.append(Finding(relative, line_number, "MISSING_ANCHOR", target, "Markdown anchor does not exist"))
    return tuple(sorted(set(findings)))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, metavar="PATH", help="write a deterministic JSON report")
    parser.add_argument("--include-external", action="store_true", help="explicitly validate HTTP(S) links over the network")
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--content-only", action="store_true", help="check Markdown present in a source archive")
    arguments = parser.parse_args(argv)
    try:
        if arguments.content_only:
            root = (arguments.root or Path(__file__).resolve().parents[1]).resolve()
            files = content_markdown(root)
        else:
            root = repository_root(arguments.root)
            files = tracked_markdown(root)
        findings = audit(root, files, include_external=arguments.include_external)
    except (OSError, RuntimeError) as error:
        print(f"Markdown link check could not start: {error}. Use a full Git clone, or --content-only for a source archive.")
        return 2
    report = {"root": str(root), "files_checked": len(files), "findings": [asdict(item) for item in findings]}
    if arguments.json:
        arguments.json.parent.mkdir(parents=True, exist_ok=True)
        arguments.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if findings:
        print(f"Markdown link check failed: {len(findings)} finding(s).")
        for item in findings:
            print(f"  - {item.path}:{item.line} [{item.code}] {item.target}: {item.message}")
        return 1
    print(f"Markdown links accepted for {root}: {len(files)} {'present' if arguments.content_only else 'tracked'} Markdown files, network={'enabled' if arguments.include_external else 'disabled'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
