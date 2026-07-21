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
FINAL_REMOTE_STATUSES = {"APPLIED", "DEFERRED", "UNAVAILABLE_ON_CURRENT_PLAN"}
EXPECTED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
}
REUSE_BUILD_LOCK = "governance/requirements-reuse-build-6.2.0.txt"
REUSE_RUNTIME_LOCK = "governance/requirements-reuse-6.2.0.txt"
REUSE_BUILD_COMMAND = (
    "python -m pip install --disable-pip-version-check --require-hashes "
    f"-r {REUSE_BUILD_LOCK}"
)
REUSE_RUNTIME_COMMAND = (
    "python -m pip install --disable-pip-version-check --require-hashes "
    f"--no-build-isolation -r {REUSE_RUNTIME_LOCK}"
)
EXPECTED_REUSE_LOCKS = {
    REUSE_BUILD_LOCK: {
        "poetry-core": ("2.2.1", "bdfce710edc10bfcf9ab35041605c480829be4ab23f5bc01202cfe5db8f125ab"),
    },
    REUSE_RUNTIME_LOCK: {
        "attrs": ("26.1.0", "c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309"),
        "boolean.py": ("5.0", "ef28a70bd43115208441b53a045d1549e2f0ec6e3d08a9d142cbc41c1938e8d9"),
        "click": ("8.4.2", "e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76"),
        "Jinja2": ("3.1.6", "85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67"),
        "license-expression": ("30.4.4", "421788fdcadb41f049d2dc934ce666626265aeccefddd25e162a26f23bcbf8a4"),
        "MarkupSafe": ("3.0.3", "0bf2a864d67e76e5c9a34dc26ec616a66b9888e25e7b9460e1c76d3293bd9dbf"),
        "python-debian": ("1.1.1", "f98ae013e8e5310e49041cc3860a7105df73af73d4ff1d8afb474770d328a6ad"),
        "python-magic": ("0.4.27", "c212960ad306f700aa0d01e5d7a325d20548ff97eb9920dcd29513174f0294d3"),
        "reuse": ("6.2.0", "4feae057a2334c9a513e6933cdb9be819d8b822f3b5b435a36138bd218897d23"),
        "tomlkit": ("0.15.1", "177a05aece5a8ca5266fd3c448abb47b8d352f09d477d3ca8332db4d89b24304"),
    },
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
TAG_POLICY_COMMAND = "python scripts/check_git_history.py --fail-on-review"
TAG_RELEASE_COMMAND = (
    'python scripts/check_release_tree.py --expected-ref "${GITHUB_REF}" '
    '--event-sha "${GITHUB_SHA}"'
)
TAG_CONDITION = "if: ${{ startsWith(github.ref, 'refs/tags/') }}"
ORDINARY_CONDITION = "if: ${{ !startsWith(github.ref, 'refs/tags/') }}"


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
        raise RuntimeError("cannot resolve repository root; a full Git clone is required unless --content-only is used")
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


def _check_reuse_locks(root: Path, findings: list[Finding]) -> None:
    for relative, expected in EXPECTED_REUSE_LOCKS.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(_finding(relative, "REUSE_LOCK", "hashed requirements lock is absent"))
            continue
        records: dict[str, tuple[str, str]] = {}
        pattern = re.compile(
            r"(?m)^(?P<name>[A-Za-z0-9_.-]+)==(?P<version>[A-Za-z0-9_.+-]+)\s*\\\n"
            r"\s+--hash=sha256:(?P<hash>[0-9a-f]{64})\s*$"
        )
        for match in pattern.finditer(text):
            records[match.group("name")] = (match.group("version"), match.group("hash"))
        non_comment = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if records != expected or len(non_comment) != 2 * len(expected):
            findings.append(_finding(relative, "REUSE_LOCK", "lock content, versions, or SHA256 hashes differ"))


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
    if not (root / "scripts/check_release_tree.py").is_file():
        findings.append(_finding("scripts/check_release_tree.py", "RELEASE_TREE_CHECKER", "required exact-tag content checker is absent"))
    text = path.read_text(encoding="utf-8")
    if "pull_request_target" in text:
        findings.append(_finding(".github/workflows/validate.yml", "PULL_REQUEST_TARGET", "forbidden trigger"))
    trigger = _section(text, "on:", "permissions:")
    trigger_keys = tuple(re.findall(r"(?m)^  ([a-z_]+):", trigger))
    if (
        trigger_keys != ("push", "pull_request", "workflow_dispatch")
        or trigger.count("branches: [main]") != 2
        or trigger.count('tags: ["v*"]') != 1
        or re.search(r"(?m)^\s+tags-ignore:", trigger)
    ):
        findings.append(_finding(".github/workflows/validate.yml", "TRIGGERS", "workflow must use only main branch events, workflow_dispatch, and the narrow v* tag push gate"))
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
        checkout_count = 3 if key in {"repository-ubuntu", "repository-windows"} else 2
        if block.count("actions/checkout@") != checkout_count:
            findings.append(_finding(".github/workflows/validate.yml", "CHECKOUT_COUNT", key))
        for field, code in (
            ("fetch-depth: 0", "SHALLOW_CHECKOUT"),
            ("persist-credentials: false", "PERSISTED_CREDENTIALS"),
            ("submodules: false", "CHECKOUT_SCOPE"),
            ("lfs: false", "CHECKOUT_SCOPE"),
        ):
            if block.count(field) != checkout_count:
                findings.append(_finding(".github/workflows/validate.yml", code, key))
        if block.count("ref: ${{ github.ref }}") != 2:
            findings.append(_finding(".github/workflows/validate.yml", "RELEASE_CHECKOUT_REF", key))
        if block.count("path: _validation/release") != 1:
            findings.append(_finding(".github/workflows/validate.yml", "RELEASE_CHECKOUT_PATH", key))
        if key in {"repository-ubuntu", "repository-windows"}:
            if block.count("ref: refs/heads/main") != 1 or block.count("path: _validation/policy") != 1:
                findings.append(_finding(".github/workflows/validate.yml", "POLICY_CHECKOUT", key))
            if block.count("working-directory: _validation/policy") != 1:
                findings.append(_finding(".github/workflows/validate.yml", "POLICY_WORKSPACE", key))
            if block.count("working-directory: _validation/release") != 1:
                findings.append(_finding(".github/workflows/validate.yml", "RELEASE_WORKSPACE", key))
            if block.count(TAG_POLICY_COMMAND) != 2:
                findings.append(_finding(".github/workflows/validate.yml", "TAG_POLICY_COMMAND", key))
            if block.count(TAG_RELEASE_COMMAND) != 1:
                findings.append(_finding(".github/workflows/validate.yml", "TAG_RELEASE_COMMAND", key))
        elif "refs/heads/main" in block or "_validation/policy" in block:
            findings.append(_finding(".github/workflows/validate.yml", "REUSE_POLICY_CHECKOUT", key))
    for key in ("repository-ubuntu", "repository-windows"):
        block = blocks.get(key, "")
        for command in REQUIRED_REPOSITORY_COMMANDS:
            expected_count = 2 if command in {
                TAG_POLICY_COMMAND,
                "python -m unittest discover -s tests -v",
            } else 1
            if block.count(command) != expected_count:
                findings.append(_finding(".github/workflows/validate.yml", "REPOSITORY_COMMAND", f"{key}: {command}"))
        if block.count(ORDINARY_CONDITION) != 2 or block.count(TAG_CONDITION) != 4:
            findings.append(_finding(".github/workflows/validate.yml", "EVENT_ISOLATION", key))
    windows_block = blocks.get("repository-windows", "")
    if not re.search(r"(?m)^    defaults:\s*$\n^      run:\s*$\n^        shell:\s*bash\s*$", windows_block):
        findings.append(
            _finding(
                ".github/workflows/validate.yml",
                "WINDOWS_FAIL_FAST_SHELL",
                "repository / windows must use explicit Bash fail-fast run defaults",
            )
        )
    if text.count(REUSE_BUILD_COMMAND) != 2 or text.count(REUSE_RUNTIME_COMMAND) != 2:
        findings.append(_finding(".github/workflows/validate.yml", "REUSE_INSTALL", "REUSE must install exclusively from both hashed locks"))
    if text.count("--require-hashes") != 4 or "pip install" in text.replace(REUSE_BUILD_COMMAND, "").replace(REUSE_RUNTIME_COMMAND, ""):
        findings.append(_finding(".github/workflows/validate.yml", "REUSE_INSTALL", "unhashed or additional pip installation is forbidden"))
    reuse_block = blocks.get("licensing-reuse", "")
    if (
        reuse_block.count(ORDINARY_CONDITION) != 3
        or reuse_block.count(TAG_CONDITION) != 3
        or reuse_block.count("working-directory: _validation/release") != 2
        or reuse_block.count("reuse lint") != 2
    ):
        findings.append(_finding(".github/workflows/validate.yml", "REUSE_EVENT_ISOLATION", "ordinary and tagged-tree REUSE gates must remain separate"))
    forbidden = ("actions/cache", "upload-artifact", "download-artifact", "pull_request_target", "schedule:", "repository_dispatch:", "workflow_run:", "release:", "deployment:")
    for term in forbidden:
        if term in text:
            findings.append(_finding(".github/workflows/validate.yml", "FORBIDDEN_WORKFLOW_FEATURE", term))
    approved_commands = set(REQUIRED_REPOSITORY_COMMANDS) | {
        REUSE_BUILD_COMMAND,
        REUSE_RUNTIME_COMMAND,
        "reuse lint",
        TAG_RELEASE_COMMAND,
    }
    lines = text.splitlines()
    observed_commands: list[str] = []
    index = 0
    while index < len(lines):
        match = re.match(r"^(\s{8,})run:\s*(.*)$", lines[index])
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
            plan["schema_version"] == 3
            and plan["remote_settings_status"] == "APPLIED"
            and plan["identity"]
            == {
                "owner": "ElGrandeXu",
                "repository": "EGX_Terminal",
                "repository_id": 1308085094,
                "default_branch": "main",
            }
            and plan["visibility_strategy"]["initial_visibility"] == "private"
            and plan["visibility_strategy"]["target_visibility"] == "private"
            and plan["visibility_strategy"]["observed_visibility"] == "private"
            and plan["metadata"]["description"]
            == "Evidence-led research for inspectable, LLM-agnostic terminal environments."
            and plan["metadata"]["homepage"] == ""
            and plan["metadata"]["topics"]
            == [
                "llm",
                "developer-tools",
                "cli",
                "llm-agnostic",
                "ai-governance",
                "reproducible-research",
                "opencode",
                "ollama",
                "qwen",
                "open-source",
            ]
            and plan["features"]["issues"] is True
            and plan["features"]["projects"] is False
            and plan["features"]["wiki"] is False
            and plan["features"]["discussions"] is False
            and plan["features"]["pages"] is False
            and plan["merge_policy"]["squash_merge"] is True
            and plan["merge_policy"]["merge_commits"] is False
            and plan["merge_policy"]["rebase_merge"] is False
            and plan["merge_policy"]["delete_merged_branches"] is True
            and plan["merge_policy"]["auto_merge"] is False
            and plan["actions_policy"]["github_token_default"] == "read"
            and plan["actions_policy"]["allowed_actions"] == list(EXPECTED_ACTIONS)
            and plan["actions_policy"]["github_owned_allowed"] is False
            and plan["actions_policy"]["verified_allowed"] is False
            and plan["actions_policy"]["full_sha_pinning_required"] is True
            and plan["actions_policy"]["sha_pinning_verified_on"] == "2026-07-21"
            and plan["actions_policy"]["sha_pinning_endpoint"]
            == "GET /repos/ElGrandeXu/EGX_Terminal/actions/permissions"
            and plan["security"]["private_vulnerability_reporting"] == "ACTIVE"
            and plan["security"]["secret_scanning"] == "ACTIVE"
            and plan["security"]["push_protection"] == "ACTIVE"
            and plan["security"]["security_alerts"] == "ACTIVE"
            and plan["main_ruleset"]["name"] == "main-protection"
            and plan["main_ruleset"]["target"] == "main"
            and plan["main_ruleset"]["enforcement"] == "active"
            and plan["main_ruleset"]["rules"]["required_approvals"] == 0
            and plan["main_ruleset"]["rules"]["prevent_deletion"] is True
            and plan["main_ruleset"]["rules"]["prevent_force_push"] is True
            and plan["main_ruleset"]["rules"]["require_linear_history"] is True
            and plan["main_ruleset"]["rules"]["require_pull_request"] is True
            and plan["main_ruleset"]["rules"]["require_conversation_resolution"] is True
            and plan["main_ruleset"]["rules"]["required_status_checks"] == list(EXPECTED_CHECKS)
            and plan["main_ruleset"]["administrative_bypass"]["ordinary_use"] is False
            and plan["community_profile"]["code_of_conduct"] == "DEFERRED_UNTIL_ENFORCEABLE"
            and plan["release_state"]
            == {
                "current_releases": [],
                "historical_releases": [
                    {
                        "tag": "v1.0.0",
                        "status": "WITHDRAWN_DURING_PRIVACY_REMEDIATION",
                        "evidence": "PRIVATE_VERIFIED_BUNDLE",
                        "expected_ref_present": False,
                    }
                ],
                "next_candidate": "v1.0.1",
                "canonical_git_tag_count": 0,
                "canonical_github_release_count": 0,
                "status": "APPLIED",
            }
            and plan["recovery_closure"]
            == {
                "starting_head": "dee7a7c97ad6991746d7de35f6d7ddb290bb895e",
                "starting_commit_count": 37,
                "final_commit_count": 38,
                "temporary_repositories_backed_up_locally": True,
                "temporary_repositories_deleted": True,
                "private_evidence_outside_repository": True,
                "direct_push_exception": "AUTHORIZED_ONCE_WHILE_PRIVATE_BEFORE_RULESET_ACTIVATION",
                "future_direct_push_authorized": False,
                "force_push_used": False,
                "git_tag_created": False,
                "github_release_created": False,
                "pull_request_created": False,
                "experimental_evidence_modified": False,
                "status": "APPLIED",
            }
        )
    except (KeyError, TypeError):
        valid = False
    if not valid:
        findings.append(_finding(relative, "PUBLICATION_PLAN", "plan is incomplete or inconsistent"))
    for section in (
        "visibility_strategy",
        "metadata",
        "features",
        "merge_policy",
        "actions_policy",
        "security",
        "main_ruleset",
        "community_profile",
        "release_state",
        "recovery_closure",
    ):
        if not isinstance(plan.get(section), dict) or plan[section].get("status") not in FINAL_REMOTE_STATUSES:
            findings.append(_finding(relative, "REMOTE_STATUS", f"{section} does not have a final status"))


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
        REUSE_BUILD_LOCK: "Apache-2.0",
        REUSE_RUNTIME_LOCK: "Apache-2.0",
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
    _check_reuse_locks(root, findings)
    _check_workflow(root, lock, findings)
    _check_plan(root, findings)
    _check_reuse(root, findings)
    return tuple(sorted(set(findings)))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--content-only", action="store_true", help="validate repository content present in a source archive")
    arguments = parser.parse_args(argv)
    try:
        root = (
            (arguments.root or Path(__file__).resolve().parents[1]).resolve()
            if arguments.content_only
            else repository_root(arguments.root)
        )
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
