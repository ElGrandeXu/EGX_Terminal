#!/usr/bin/env python3
"""Validate the deliberately narrow GitHub governance structure used by V1."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import fnmatch
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tomllib
from typing import Sequence


REQUIRED_COMMUNITY = (
    "GOVERNANCE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/research_proposal.md",
    ".github/pull_request_template.md",
)
DEFERRED_FILES = ("CODE_OF_CONDUCT.md", "SUPPORT.md", ".github/CODEOWNERS", "CODEOWNERS")
EXPECTED_CHECKS = ("repository / ubuntu", "repository / windows", "licensing / reuse")
EXPECTED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
}
REQUIRED_REPOSITORY_COMMANDS = (
    "python scripts/check_neutral_root.py",
    "python scripts/check_public_surface.py",
    "python scripts/check_licensing.py",
    "python scripts/check_git_history.py --fail-on-review",
    "python scripts/check_markdown_links.py",
    "python scripts/check_github_governance.py",
    "python -m unittest discover -s tests -v",
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    code: str
    message: str


def _finding(path: str, code: str, message: str) -> Finding:
    return Finding(path, code, message)


def repository_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    candidate = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("cannot resolve repository root")
    return Path(result.stdout.strip()).resolve()


def _frontmatter(path: Path) -> tuple[dict[str, str], bool]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return {}, False
    if not lines or lines[0].strip() != "---":
        return {}, False
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, False
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z_]+):\s*(.*)", line)
        if not match or match.group(1) in values:
            return {}, False
        values[match.group(1)] = match.group(2).strip()
    return values, True


def _load_json(path: Path, label: str, findings: list[Finding]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        findings.append(_finding(label, "INVALID_JSON", "file is absent or invalid JSON"))
        return {}
    if not isinstance(value, dict):
        findings.append(_finding(label, "INVALID_JSON_ROOT", "JSON root must be an object"))
        return {}
    return value


def _check_community(root: Path, findings: list[Finding]) -> None:
    for relative in REQUIRED_COMMUNITY:
        if not (root / relative).is_file():
            findings.append(_finding(relative, "MISSING_COMMUNITY_FILE", "required community file is absent"))
    for relative in DEFERRED_FILES:
        if (root / relative).exists():
            findings.append(_finding(relative, "DEFERRED_FILE_PRESENT", "deferred community file must not be present in V1"))
    governance = root / "GOVERNANCE.md"
    if governance.is_file() and "DEFERRED_UNTIL_ENFORCEABLE" not in governance.read_text(encoding="utf-8", errors="replace"):
        findings.append(_finding("GOVERNANCE.md", "DEFERRED_STATUS", "Code of Conduct deferral is not documented"))
    for relative in REQUIRED_COMMUNITY[3:5]:
        values, valid = _frontmatter(root / relative)
        if not valid:
            findings.append(_finding(relative, "INVALID_FRONTMATTER", "issue template frontmatter is invalid"))
            continue
        for key in ("name", "about", "title", "labels", "assignees"):
            if key not in values:
                findings.append(_finding(relative, "FRONTMATTER_FIELD", f"missing {key}"))


def _check_lock(root: Path, findings: list[Finding]) -> dict[str, str]:
    relative = "governance/github-actions-lock.json"
    data = _load_json(root / relative, relative, findings)
    actions = data.get("actions")
    if data.get("schema_version") != 1 or not isinstance(actions, list):
        findings.append(_finding(relative, "LOCK_SCHEMA", "unsupported actions lock structure"))
        return {}
    result: dict[str, str] = {}
    for record in actions:
        if not isinstance(record, dict):
            findings.append(_finding(relative, "LOCK_RECORD", "action record must be an object"))
            continue
        required = {"repository", "stable_release", "sha", "verified_on", "official_source", "owner", "intended_use"}
        if not required.issubset(record):
            findings.append(_finding(relative, "LOCK_RECORD", "action record lacks required metadata"))
            continue
        repository, sha = record["repository"], record["sha"]
        if repository not in EXPECTED_ACTIONS:
            findings.append(_finding(relative, "UNAUTHORIZED_LOCK_ACTION", str(repository)))
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            findings.append(_finding(relative, "LOCK_SHA", f"invalid SHA for {repository}"))
        result[str(repository)] = str(sha)
    if result != EXPECTED_ACTIONS:
        findings.append(_finding(relative, "LOCK_CONTENT", "lock does not exactly match the approved actions"))
    return result


def _section(text: str, start: str, end: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(start)}\s*\n(.*?)(?=^{re.escape(end)}\s*\n)", text)
    return match.group(1) if match else ""


def _job_blocks(text: str) -> dict[str, str]:
    jobs = _section(text, "jobs:", "__never__:") if "__never__:" in text else text.split("\njobs:\n", 1)[1] if "\njobs:\n" in text else ""
    matches = list(re.finditer(r"(?m)^  ([a-z0-9-]+):\s*$", jobs))
    return {match.group(1): jobs[match.start() : (matches[index + 1].start() if index + 1 < len(matches) else len(jobs))] for index, match in enumerate(matches)}


def _check_workflow(root: Path, lock: dict[str, str], findings: list[Finding]) -> None:
    workflow_dir = root / ".github/workflows"
    workflows = sorted(path.name for path in workflow_dir.glob("*.y*ml")) if workflow_dir.is_dir() else []
    if workflows != ["validate.yml"]:
        findings.append(_finding(".github/workflows", "WORKFLOW_SET", "exactly validate.yml is allowed"))
        return
    path = workflow_dir / "validate.yml"
    text = path.read_text(encoding="utf-8")
    if "pull_request_target" in text:
        findings.append(_finding(".github/workflows/validate.yml", "PULL_REQUEST_TARGET", "forbidden trigger"))
    trigger = _section(text, "on:", "permissions:")
    trigger_keys = tuple(re.findall(r"(?m)^  ([a-z_]+):", trigger))
    if trigger_keys != ("push", "pull_request", "workflow_dispatch") or trigger.count("branches: [main]") != 2:
        findings.append(_finding(".github/workflows/validate.yml", "TRIGGERS", "trigger structure is not the approved V1 structure"))
    permission = _section(text, "permissions:", "concurrency:")
    if not re.fullmatch(r"\s*contents:\s*read\s*", permission):
        findings.append(_finding(".github/workflows/validate.yml", "PERMISSIONS", "global permissions must be exactly contents: read"))
    if re.search(r"(?im)^\s*[^#\n]+:\s*write(?:-all)?\s*$", text):
        findings.append(_finding(".github/workflows/validate.yml", "WRITE_PERMISSION", "write permission is forbidden"))
    if re.search(r"\$\{\{\s*secrets\.", text, re.IGNORECASE):
        findings.append(_finding(".github/workflows/validate.yml", "SECRET_REFERENCE", "workflow references a secret"))
    if re.search(r"(?m)^\s*environment\s*:", text):
        findings.append(_finding(".github/workflows/validate.yml", "ENVIRONMENT", "deployment environments are forbidden"))
    if not all(value in text for value in ("group: validate-", "cancel-in-progress: true")):
        findings.append(_finding(".github/workflows/validate.yml", "CONCURRENCY", "deterministic concurrency cancellation is required"))
    blocks = _job_blocks(text)
    if set(blocks) != {"repository-ubuntu", "repository-windows", "licensing-reuse"}:
        findings.append(_finding(".github/workflows/validate.yml", "JOBS", "workflow must contain exactly the three V1 jobs"))
    names = tuple(re.findall(r"(?m)^    name:\s*(.+?)\s*$", text))
    if names != EXPECTED_CHECKS:
        findings.append(_finding(".github/workflows/validate.yml", "CHECK_NAMES", "public check names differ"))
    if text.count('python-version: "3.11"') != 3:
        findings.append(_finding(".github/workflows/validate.yml", "PYTHON_VERSION", "every job must use Python 3.11"))
    if text.count("timeout-minutes:") != 3:
        findings.append(_finding(".github/workflows/validate.yml", "TIMEOUT", "each job needs an explicit timeout"))
    uses = re.findall(r"(?m)^\s*-?\s*uses:\s*([^@\s]+)@([^\s#]+)", text)
    for repository, sha in uses:
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            findings.append(_finding(".github/workflows/validate.yml", "FLOATING_ACTION", f"{repository}@{sha}"))
        if repository not in EXPECTED_ACTIONS:
            findings.append(_finding(".github/workflows/validate.yml", "UNAUTHORIZED_ACTION", repository))
        elif lock.get(repository) != sha:
            findings.append(_finding(".github/workflows/validate.yml", "LOCK_MISMATCH", repository))
    if not uses:
        findings.append(_finding(".github/workflows/validate.yml", "NO_ACTIONS", "workflow contains no understood uses entries"))
    if any(repository not in {item[0] for item in uses} for repository in EXPECTED_ACTIONS):
        findings.append(_finding(".github/workflows/validate.yml", "LOCK_ACTION_UNUSED", "approved action is not used"))
    for key, block in blocks.items():
        if "actions/checkout@" in block:
            if "fetch-depth: 0" not in block:
                findings.append(_finding(".github/workflows/validate.yml", "SHALLOW_CHECKOUT", key))
            if "persist-credentials: false" not in block:
                findings.append(_finding(".github/workflows/validate.yml", "PERSISTED_CREDENTIALS", key))
            if "submodules: false" not in block or "lfs: false" not in block:
                findings.append(_finding(".github/workflows/validate.yml", "CHECKOUT_SCOPE", key))
    for key in ("repository-ubuntu", "repository-windows"):
        block = blocks.get(key, "")
        for command in REQUIRED_REPOSITORY_COMMANDS:
            if block.count(command) != 1:
                findings.append(_finding(".github/workflows/validate.yml", "REPOSITORY_COMMAND", f"{key}: {command}"))
    if text.count("reuse==6.2.0") != 1 or re.search(r"reuse==(?!(?:6\.2\.0)\b)", text):
        findings.append(_finding(".github/workflows/validate.yml", "REUSE_VERSION", "REUSE must be pinned exactly to 6.2.0"))
    forbidden = ("actions/cache", "upload-artifact", "download-artifact", "pull_request_target", "schedule:", "repository_dispatch:", "workflow_run:", "release:", "deployment:")
    for term in forbidden:
        if term in text:
            findings.append(_finding(".github/workflows/validate.yml", "FORBIDDEN_WORKFLOW_FEATURE", term))
    approved_commands = set(REQUIRED_REPOSITORY_COMMANDS) | {
        "python -m pip install --disable-pip-version-check reuse==6.2.0",
        "reuse lint",
    }
    lines = text.splitlines()
    observed_commands: list[str] = []
    index = 0
    while index < len(lines):
        match = re.match(r"^(\s*)run:\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        indentation = len(match.group(1))
        value = match.group(2).strip()
        if value and value != "|":
            observed_commands.append(value)
            index += 1
            continue
        index += 1
        while index < len(lines):
            current = lines[index]
            if current.strip() and len(current) - len(current.lstrip()) <= indentation:
                break
            if current.strip():
                observed_commands.append(current.strip())
            index += 1
    for command in observed_commands:
        if command not in approved_commands:
            findings.append(_finding(".github/workflows/validate.yml", "UNKNOWN_RUN_COMMAND", command))


def _check_plan(root: Path, findings: list[Finding]) -> None:
    relative = "governance/github-publication-plan.json"
    plan = _load_json(root / relative, relative, findings)
    try:
        valid = (
            plan["schema_version"] == 1
            and plan["remote_settings_status"] == "PLANNED_NOT_APPLIED"
            and plan["identity"] == {"owner": "ElGrandeXu", "repository": "EGX_Terminal", "default_branch": "main"}
            and plan["visibility_strategy"]["initial_visibility"] == "private"
            and plan["visibility_strategy"]["target_visibility"] == "public"
            and plan["metadata"]["homepage"] == ""
            and 1 <= len(plan["metadata"]["topics"]) <= 10
            and plan["features"]["issues"] is True
            and plan["features"]["projects"] is False
            and plan["features"]["wiki"] is False
            and plan["features"]["discussions"] is False
            and plan["merge_policy"]["squash_merge"] is True
            and plan["merge_policy"]["merge_commits"] is False
            and plan["merge_policy"]["rebase_merge"] is False
            and plan["actions_policy"]["github_token_default"] == "read"
            and plan["actions_policy"]["allowed_actions"] == list(EXPECTED_ACTIONS)
            and plan["security"]["private_vulnerability_reporting"] == "ENABLE_BEFORE_PUBLIC"
            and plan["main_ruleset"]["name"] == "main-protection"
            and plan["main_ruleset"]["target"] == "main"
            and plan["main_ruleset"]["enforcement"] == "active"
            and plan["main_ruleset"]["rules"]["required_approvals"] == 0
            and plan["main_ruleset"]["rules"]["required_status_checks"] == list(EXPECTED_CHECKS)
            and plan["community_profile"]["code_of_conduct"] == "DEFERRED_UNTIL_ENFORCEABLE"
            and plan["release"]["candidate"] == "v1.0.0"
            and plan["release"]["tag_created"] is False
            and plan["release"]["release_created"] is False
        )
    except (KeyError, TypeError):
        valid = False
    if not valid:
        findings.append(_finding(relative, "PUBLICATION_PLAN", "plan is incomplete or inconsistent"))
    for section in ("visibility_strategy", "metadata", "features", "merge_policy", "actions_policy", "security", "main_ruleset", "community_profile", "release"):
        if not isinstance(plan.get(section), dict) or plan[section].get("status") != "PLANNED_NOT_APPLIED":
            findings.append(_finding(relative, "REMOTE_STATUS", f"{section} is not PLANNED_NOT_APPLIED"))


def _matches(pattern: str, path: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern) or (pattern.endswith("/**") and path.startswith(pattern[:-3] + "/"))


def _check_reuse(root: Path, findings: list[Finding]) -> None:
    relative = "REUSE.toml"
    try:
        data = tomllib.loads((root / relative).read_text(encoding="utf-8"))
        annotations = data["annotations"]
    except (OSError, UnicodeError, tomllib.TOMLDecodeError, KeyError, TypeError):
        findings.append(_finding(relative, "REUSE_METADATA", "cannot parse annotations"))
        return
    expected: dict[str, str] = {
        **{path: "CC-BY-4.0" for path in REQUIRED_COMMUNITY},
        "docs/publication/GITHUB_PUBLICATION_PLAN.md": "CC-BY-4.0",
        "docs/publication/RELEASE_CHECKLIST.md": "CC-BY-4.0",
        "docs/decisions/0008-finalize-public-repository-governance.md": "CC-BY-4.0",
        ".github/workflows/validate.yml": "Apache-2.0",
        "governance/github-actions-lock.json": "Apache-2.0",
        "governance/github-publication-plan.json": "Apache-2.0",
        "scripts/check_markdown_links.py": "Apache-2.0",
        "scripts/check_github_governance.py": "Apache-2.0",
        "tests/test_check_markdown_links.py": "Apache-2.0",
        "tests/test_check_github_governance.py": "Apache-2.0",
    }
    for path, license_id in expected.items():
        matches = []
        for item in annotations:
            patterns = item.get("path", []) if isinstance(item, dict) else []
            patterns = [patterns] if isinstance(patterns, str) else patterns
            if any(_matches(pattern, path) for pattern in patterns):
                matches.append(item.get("SPDX-License-Identifier"))
        if matches != [license_id]:
            findings.append(_finding(relative, "REUSE_COVERAGE", f"{path} expected {license_id}, found {matches}"))


def audit(root: Path) -> tuple[Finding, ...]:
    root = root.resolve()
    findings: list[Finding] = []
    _check_community(root, findings)
    lock = _check_lock(root, findings)
    _check_workflow(root, lock, findings)
    _check_plan(root, findings)
    _check_reuse(root, findings)
    return tuple(sorted(set(findings)))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    arguments = parser.parse_args(argv)
    try:
        root = repository_root(arguments.root)
        findings = audit(root)
    except (OSError, RuntimeError) as error:
        print(f"GitHub governance check could not start: {error}")
        return 2
    if findings:
        print(f"GitHub governance check failed for {root}:")
        for item in findings:
            print(f"  - {item.path} [{item.code}] {item.message}")
        return 1
    print(f"GitHub governance accepted for {root}: community files, CI, locks, publication plan, and REUSE coverage are coherent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
