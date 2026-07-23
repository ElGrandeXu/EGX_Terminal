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
CURRENT_PHASE = "PUBLIC_REPOSITORY_VERIFIED"
CURRENT_REMOTE_STATUS = "PUBLIC_SETTINGS_OBSERVED_VERIFIED"
FINAL_PUBLICATION_CHECKPOINT = "1d79ea37a1c614728cc7651c4d611218eaca174a"
FINAL_PUBLICATION_COMMIT_COUNT = 43
DATED_REMOTE_SNAPSHOT_CHECKPOINT = "fb2a350de17df8072c63ec6a36b028bcb1b64fda"
DATED_REMOTE_SNAPSHOT_COMMIT_COUNT = 44
FINAL_RUN_ID = 30002915548
HISTORICAL_RUN_ID = 29951087998
FINAL_RUN_CREATED_AT = "2026-07-23T11:23:01Z"
FINAL_RUN_UPDATED_AT = "2026-07-23T11:26:08Z"
EXPECTED_TOPICS = (
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
)
EXPECTED_LEVEL_A_CHECKS = (
    "REPOSITORY_API",
    "HTTPS_CLONE",
    "ZIP_ARCHIVE",
    "TAR_ARCHIVE",
    "README",
    "PULL_REQUEST_AND_COMMITS",
    "WORKFLOW_RUN_AND_JOB_METADATA",
    "TAGS_AND_RELEASES",
    "PUBLICLY_OBSERVABLE_RULESET_WHEN_EXPOSED",
)
EXPECTED_LEVEL_B_CHECKS = (
    "ACTIONS_PAGE_ACCESS",
    "READ_THREE_JOBS",
    "READ_OR_DOWNLOAD_LOGS",
    "FINAL_NO_REPOSITORY_RIGHTS_VERIFICATION",
)
EXPECTED_LEVEL_C_CHECKS = (
    "COMPLETE_LOG_DOWNLOAD",
    "PRIVACY_SCAN",
    "ADMINISTRATIVE_CONTROLS",
    "RULESETS_AND_PROTECTIONS",
    "SECURITY_ALERTS",
    "NO_SECRET_PRIVATE_PATH_OR_PRIVATE_EMAIL",
    "NO_SIGNED_URL_RETAINED",
)
EXPECTED_RETRY_PREREQUISITES = (
    "MERGE_GOVERNANCE_PULL_REQUEST",
    "AUDIT_MERGED_HEAD",
    "PREPARE_LEVEL_B_ACCOUNT",
    "VERIFY_CORRECTED_HARNESS",
    "NO_NEW_BLOCKER",
)
EXPECTED_DISPATCH_RESPONSE_FIELDS = ("workflow_run_id", "run_url", "html_url")
EXPECTED_EVIDENCE_EXCLUSIONS = (
    "temp_clone_token",
    "authorization",
    "cookie",
    "tokens",
    "credentials",
    "temporary_signed_urls",
)
EXPECTED_DANGEROUS_CAPTURE_POLICY = (
    "QUARANTINE_PRIVATELY",
    "RECORD_REDACTED_EXISTENCE",
    "DECIDE_DESTRUCTION_OR_RETENTION_EXPLICITLY",
    "NEVER_PUBLISH",
)
EXPECTED_CURRENT_DOCUMENTS = (
    "README.md",
    "SECURITY.md",
    "docs/QUICKSTART.md",
    "docs/STATUS.md",
    "docs/decisions/README.md",
    "docs/publication/PUBLICATION_BOUNDARY.md",
    "docs/publication/GITHUB_PUBLICATION_PLAN.md",
    "docs/publication/RELEASE_POLICY.md",
)
EXPECTED_METADATA = {
    "description": "Evidence-led research for inspectable, LLM-agnostic terminal environments.",
    "homepage": "",
    "topics": list(EXPECTED_TOPICS),
    "status": "APPLIED",
}
EXPECTED_FEATURES = {
    "issues": True,
    "projects": False,
    "wiki": False,
    "discussions": False,
    "sponsorship": "NOT_CONFIGURED",
    "pages": False,
    "status": "OBSERVED_ON_VERIFIED_PUBLIC_REPOSITORY",
}
EXPECTED_MERGE_POLICY = {
    "squash_merge": True,
    "merge_commits": False,
    "rebase_merge": False,
    "squash_message": "PR_TITLE_AND_BODY",
    "delete_merged_branches": True,
    "auto_merge": False,
    "linear_history": True,
    "status": "APPLIED",
}
EXPECTED_RECOVERY_CLOSURE = {
    "starting_head": "dee7a7c97ad6991746d7de35f6d7ddb290bb895e",
    "starting_commit_count": 37,
    "final_commit_count": 38,
    "temporary_repositories_backed_up_locally": True,
    "temporary_repositories_deleted": True,
    "private_evidence_outside_repository": True,
    "historical_direct_push_exception": "AUTHORIZED_ONCE_WHILE_PRIVATE_BEFORE_RULESET_ACTIVATION",
    "future_direct_push_authorized": False,
    "force_push_used": False,
    "git_tag_created": False,
    "github_release_created": False,
    "pull_request_created": False,
    "experimental_evidence_modified": False,
    "status": "HISTORICAL_CLOSED",
}
EXPECTED_REMOTE_CONTROLS = {
    "main_ruleset": {
        "desired_state": "ACTIVE",
        "observed_state": "ACTIVE",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal/rulesets/19606748",
        "http_status": 200,
    },
    "main_branch": {
        "desired_state": "PROTECTED",
        "observed_state": "PROTECTED",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal/branches/main",
        "http_status": 200,
    },
    "private_vulnerability_reporting": {
        "desired_state": "ACTIVE",
        "observed_state": "ACTIVE_VERIFIED",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal/private-vulnerability-reporting",
        "http_status": 200,
    },
    "secret_scanning": {
        "desired_state": "ACTIVE",
        "observed_state": "ACTIVE",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal",
        "http_status": 200,
    },
    "push_protection": {
        "desired_state": "ACTIVE",
        "observed_state": "ACTIVE",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal",
        "http_status": 200,
    },
    "security_alerts": {
        "desired_state": "ACTIVE",
        "observed_state": "ACTIVE",
        "limitation": None,
        "application_status": "APPLIED_VERIFIED",
        "endpoint": "GET /repos/ElGrandeXu/EGX_Terminal/vulnerability-alerts",
        "http_status": 204,
    },
}
EXPECTED_MAIN_RULESET = {
    "name": "main-protection",
    "target": "main",
    "enforcement": "active",
    "bypass_actors": [],
    "rules": {
        "prevent_deletion": True,
        "prevent_force_push": True,
        "require_linear_history": True,
        "require_pull_request": True,
        "required_approvals": 0,
        "require_conversation_resolution": True,
        "require_branch_up_to_date": True,
        "require_signed_commits": False,
        "require_code_owner_review": False,
        "required_status_checks": list(EXPECTED_CHECKS),
    },
}
EXPECTED_PACKAGE_SURFACES = tuple(
    (api_scope, package_type)
    for api_scope in ("authenticated-user", "owner-public")
    for package_type in ("npm", "maven", "rubygems", "docker", "nuget", "container")
)
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
        "poetry-core": (
            "2.2.1",
            ("bdfce710edc10bfcf9ab35041605c480829be4ab23f5bc01202cfe5db8f125ab",),
        ),
    },
    REUSE_RUNTIME_LOCK: {
        "attrs": ("26.1.0", ("c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309",)),
        "boolean.py": ("5.0", ("ef28a70bd43115208441b53a045d1549e2f0ec6e3d08a9d142cbc41c1938e8d9",)),
        "charset-normalizer": ("3.4.4", ("5ae497466c7901d54b639cf42d5b8c1b6a4fead55215500d2f486d34db48d016",)),
        "click": ("8.4.2", ("e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76",)),
        "colorama": ("0.4.6", ("4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6",)),
        "Jinja2": ("3.1.6", ("85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67",)),
        "license-expression": ("30.4.4", ("421788fdcadb41f049d2dc934ce666626265aeccefddd25e162a26f23bcbf8a4",)),
        "MarkupSafe": (
            "3.0.3",
            (
                "0bf2a864d67e76e5c9a34dc26ec616a66b9888e25e7b9460e1c76d3293bd9dbf",
                "de8a88e63464af587c950061a5e6a67d3632e36df62b986892331d4620a35c01",
            ),
        ),
        "python-debian": ("1.1.1", ("f98ae013e8e5310e49041cc3860a7105df73af73d4ff1d8afb474770d328a6ad",)),
        "python-magic": ("0.4.27", ("c212960ad306f700aa0d01e5d7a325d20548ff97eb9920dcd29513174f0294d3",)),
        "reuse": ("6.2.0", ("4feae057a2334c9a513e6933cdb9be819d8b822f3b5b435a36138bd218897d23",)),
        "tomlkit": ("0.15.1", ("177a05aece5a8ca5266fd3c448abb47b8d352f09d477d3ca8332db4d89b24304",)),
    },
}
EXPECTED_REUSE_MARKERS = {
    (REUSE_RUNTIME_LOCK, "charset-normalizer"): 'sys_platform == "win32"',
    (REUSE_RUNTIME_LOCK, "colorama"): 'sys_platform == "win32"',
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
        non_comment = [
            line.strip()
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        records: dict[str, tuple[str, tuple[str, ...]]] = {}
        markers: dict[str, str] = {}
        valid = True
        index = 0
        while index < len(non_comment):
            package = re.fullmatch(
                r"(?P<name>[A-Za-z0-9_.-]+)==(?P<version>[A-Za-z0-9_.+-]+)"
                r"(?:\s*;\s*(?P<marker>[^\\]+?))?\s*\\",
                non_comment[index],
            )
            if not package:
                valid = False
                break
            index += 1
            hashes: list[str] = []
            while index < len(non_comment):
                digest = re.fullmatch(
                    r"--hash=sha256:(?P<hash>[0-9a-f]{64})(?P<continuation>\s*\\)?",
                    non_comment[index],
                )
                if not digest:
                    valid = False
                    break
                hashes.append(digest.group("hash"))
                index += 1
                if digest.group("continuation") is None:
                    break
            if not valid or not hashes:
                valid = False
                break
            records[package.group("name")] = (
                package.group("version"),
                tuple(hashes),
            )
            if package.group("marker") is not None:
                markers[package.group("name")] = package.group("marker").strip()
        expected_markers = {
            name: marker
            for (lock, name), marker in EXPECTED_REUSE_MARKERS.items()
            if lock == relative
        }
        if not valid or records != expected or markers != expected_markers:
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


def _check_final_publication_result(relative: str, retry: dict, findings: list[Finding]) -> None:
    final = retry.get("final_result", {}) if isinstance(retry, dict) else {}
    if not isinstance(final, dict):
        final = {}
    if set(final) != {
        "status",
        "verified_on",
        "checkpoint",
        "commit_count",
        "visibility",
        "workflow_run",
        "verification_levels",
        "repository_counts",
        "remote_governance_record",
    }:
        findings.append(_finding(relative, "FINAL_RESULT_MODEL", "final publication result fields are incomplete"))
    if final.get("status") != "PUBLICATION_APPLIED_AND_VERIFIED":
        findings.append(_finding(relative, "FINAL_PUBLICATION_STATUS", "final publication must be applied and verified"))
    if (
        final.get("verified_on") != "2026-07-23"
        or final.get("checkpoint") != FINAL_PUBLICATION_CHECKPOINT
        or final.get("commit_count") != FINAL_PUBLICATION_COMMIT_COUNT
    ):
        findings.append(_finding(relative, "FINAL_CHECKPOINT", "final publication checkpoint or date is incorrect"))
    if final.get("visibility") != "public":
        findings.append(_finding(relative, "CURRENT_VISIBILITY", "final declared repository visibility must be public"))

    run = final.get("workflow_run", {}) if isinstance(final, dict) else {}
    if not isinstance(run, dict):
        run = {}
    if set(run) != {
        "run_id",
        "event",
        "attempt",
        "checkpoint",
        "status",
        "created_at",
        "updated_at",
        "successful_checks",
    }:
        findings.append(_finding(relative, "FINAL_RUN_MODEL", "final workflow run fields are incomplete"))
    if run.get("run_id") != FINAL_RUN_ID:
        findings.append(_finding(relative, "FINAL_RUN_ID", f"final run must be {FINAL_RUN_ID}"))
    if run.get("event") != "workflow_dispatch":
        findings.append(_finding(relative, "FINAL_RUN_EVENT", "final run event must be workflow_dispatch"))
    if run.get("attempt") != 1:
        findings.append(_finding(relative, "FINAL_RUN_ATTEMPT", "final run must have exactly one attempt"))
    if run.get("checkpoint") != FINAL_PUBLICATION_CHECKPOINT or run.get("status") != "COMPLETED_SUCCESS":
        findings.append(_finding(relative, "FINAL_RUN_STATUS", "final run checkpoint and success status are incorrect"))
    if run.get("created_at") != FINAL_RUN_CREATED_AT or run.get("updated_at") != FINAL_RUN_UPDATED_AT:
        findings.append(_finding(relative, "FINAL_RUN_TIMELINE", "final run timestamps are incorrect"))
    if run.get("successful_checks") != list(EXPECTED_CHECKS):
        findings.append(_finding(relative, "FINAL_RUN_CHECKS", "final run must retain all three successful jobs"))
    if run.get("run_id") == HISTORICAL_RUN_ID:
        findings.append(_finding(relative, "RUN_DISTINCTION", "historical and final runs must remain distinct"))

    levels = final.get("verification_levels", {}) if isinstance(final, dict) else {}
    if not isinstance(levels, dict) or set(levels) != {"level_a", "level_b", "level_c"}:
        findings.append(_finding(relative, "FINAL_LEVELS", "final Levels A, B, and C results are required"))
        levels = {}
    level_a = levels.get("level_a", {})
    if not isinstance(level_a, dict) or level_a.get("status") != "PASSED":
        findings.append(_finding(relative, "LEVEL_A_RESULT", "final Level A result must be PASSED"))
    anonymous = level_a.get("anonymous_rest_log_downloads", {}) if isinstance(level_a, dict) else {}
    if anonymous != {
        "http_status": 403,
        "classifications": ["INFO", "PLATFORM_AMBIGUITY"],
        "blocking": False,
    }:
        findings.append(
            _finding(relative, "ANONYMOUS_LOG_RESULT", "anonymous HTTP 403 must remain non-blocking platform ambiguity")
        )
    for key, code in (("level_b", "LEVEL_B_RESULT"), ("level_c", "LEVEL_C_RESULT")):
        if levels.get(key) != {"status": "PASSED"}:
            findings.append(_finding(relative, code, f"final {key.replace('_', ' ').title()} result must be PASSED"))

    counts = final.get("repository_counts", {}) if isinstance(final, dict) else {}
    expected_counts = {
        "open_pull_requests": 0,
        "git_tags": 0,
        "github_releases": 0,
        "packages": 0,
        "forks": 0,
    }
    if counts != expected_counts:
        code = (
            "CURRENT_RELEASE_STATE"
            if isinstance(counts, dict) and (counts.get("git_tags") != 0 or counts.get("github_releases") != 0)
            else "CURRENT_ZERO_COUNTS"
        )
        findings.append(_finding(relative, code, "final repository zero-count observations are inconsistent"))
    if final.get("remote_governance_record") != "remote_governance":
        findings.append(_finding(relative, "REMOTE_GOVERNANCE_REFERENCE", "final result must link remote governance"))


def _check_current_remote_governance(relative: str, remote: dict, findings: list[Finding]) -> None:
    expected_snapshot = {
        "verified_on": "2026-07-23",
        "checkpoint": DATED_REMOTE_SNAPSHOT_CHECKPOINT,
        "commit_count": DATED_REMOTE_SNAPSHOT_COMMIT_COUNT,
        "plan": "GITHUB_FREE",
        "visibility": "public",
        "qualification": "DATED_V1_CLOSURE_RULESET_OBSERVATION",
    }
    if (
        not isinstance(remote, dict)
        or set(remote)
        != {
            "verified_remote_snapshot",
            "snapshot_source",
            "canonical_state",
            "offline_checker_contract",
            "public_window_record",
            "controls",
            "procedural_fallback",
        }
        or remote.get("verified_remote_snapshot") != expected_snapshot
        or remote.get("snapshot_source") != "DATED_GITHUB_API_SNAPSHOT_NOT_LIVE_CHECK"
        or remote.get("public_window_record") != "publication_transition.public_window_controls"
        or remote.get("procedural_fallback")
        != {
            "pull_request_required": True,
            "basis": "MANDATORY_PROJECT_CONVENTION",
            "github_enforced_at_final_verification": True,
        }
    ):
        findings.append(
            _finding(relative, "DATED_REMOTE_SNAPSHOT", "dated remote snapshot is incomplete or ambiguous")
        )

    if remote.get("canonical_state") != {
        "branch": "main",
        "publication_phase": CURRENT_PHASE,
        "v1_status": "CLOSED_STABLE",
        "final_publication_checkpoint": FINAL_PUBLICATION_CHECKPOINT,
        "final_publication_checkpoint_role": "HISTORICAL_VERIFIED_PUBLICATION_BASELINE",
        "current_state_role": "CANONICAL_STATE_AFTER_V1_CLOSURE_REMEDIATION",
    }:
        findings.append(
            _finding(
                relative,
                "CANONICAL_STATE",
                "current canonical state must remain distinct from the historical final-publication checkpoint",
            )
        )

    offline_contract = remote.get("offline_checker_contract", {})
    if (
        not isinstance(offline_contract, dict)
        or offline_contract.get("mode") != "OFFLINE_ONLY"
        or offline_contract.get("validates")
        != [
            "DATED_REMOTE_SNAPSHOT_CONSISTENCY",
            "CURRENT_DOCUMENT_CONSISTENCY",
            "HISTORICAL_INVARIANTS",
        ]
        or offline_contract.get("live_github_state_verified") is not False
        or offline_contract.get("remote_read_required_for") != ["AUDITS", "PUBLICATION_OPERATIONS"]
    ):
        findings.append(
            _finding(
                relative,
                "OFFLINE_SNAPSHOT_CONTRACT",
                "offline checker cannot claim live GitHub verification and remote reads remain separately required",
            )
        )
    if (
        not isinstance(offline_contract, dict)
        or offline_contract.get("current_documents") != list(EXPECTED_CURRENT_DOCUMENTS)
    ):
        findings.append(
            _finding(relative, "CURRENT_DOCUMENT_SET", "offline snapshot document set is incomplete or reordered")
        )

    controls = remote.get("controls", {}) if isinstance(remote, dict) else {}
    if not isinstance(controls, dict) or set(controls) != set(EXPECTED_REMOTE_CONTROLS):
        findings.append(_finding(relative, "CURRENT_PROTECTION", "all six final protection observations are required"))
        controls = {}
    for name, expected in EXPECTED_REMOTE_CONTROLS.items():
        control = controls.get(name, {})
        if not isinstance(control, dict):
            findings.append(_finding(relative, "CURRENT_PROTECTION", f"{name} final observation is absent"))
            continue
        expected_keys = {"desired_state", "observed_state", "limitation", "application_status", "evidence"}
        if name == "main_ruleset":
            expected_keys.add("desired_configuration")
        if set(control) != expected_keys:
            findings.append(_finding(relative, "CURRENT_PROTECTION", f"{name} contains ambiguous state fields"))
        if any(control.get(key) != expected[key] for key in (
            "desired_state",
            "observed_state",
            "limitation",
            "application_status",
        )):
            findings.append(_finding(relative, "CURRENT_PROTECTION", f"{name} final active state is incorrect"))
        if control.get("evidence") != {"endpoint": expected["endpoint"], "http_status": expected["http_status"]}:
            findings.append(_finding(relative, "OBSERVATION_EVIDENCE", f"{name} dated GET evidence is incorrect"))

    ruleset = controls.get("main_ruleset", {}).get("desired_configuration", {})
    if not isinstance(ruleset, dict):
        ruleset = {}
    comparable_ruleset = json.loads(json.dumps(ruleset)) if isinstance(ruleset, dict) else {}
    comparable_rules = comparable_ruleset.get("rules", {})
    if isinstance(comparable_rules, dict):
        comparable_rules["require_branch_up_to_date"] = True
    if comparable_ruleset != EXPECTED_MAIN_RULESET:
        findings.append(_finding(relative, "RULESET_CONFIGURATION", "main-protection configuration is incomplete"))
    bypass_keys = [(key, value) for key, value in ruleset.items() if "bypass" in key.lower()]
    if bypass_keys != [("bypass_actors", [])]:
        findings.append(_finding(relative, "BYPASS", "main-protection must contain no bypass actor or role"))
    rules = ruleset.get("rules", {}) if isinstance(ruleset.get("rules", {}), dict) else {}
    if rules.get("require_branch_up_to_date") is not True:
        findings.append(
            _finding(
                relative,
                "RULESET_UP_TO_DATE",
                "main-protection must require pull-request branches to be up to date",
            )
        )
    if rules.get("required_status_checks") != list(EXPECTED_CHECKS):
        findings.append(_finding(relative, "RULESET_CHECKS", "main-protection must retain all three checks"))
    if rules.get("prevent_force_push") is not True or rules.get("prevent_deletion") is not True:
        findings.append(_finding(relative, "BRANCH_MUTATION", "main-protection must prevent force-push and deletion"))


def _check_current_documents(root: Path, findings: list[Finding]) -> None:
    # Keep only material current-state markers here. Exact checkpoints, run
    # identifiers, timestamps, job lists, and historical observations belong to
    # the machine-readable publication manifest validated above; requiring the
    # same prose in every document makes harmless editorial changes fail.
    required = {
        "README.md": (
            CURRENT_PHASE,
            "Python 3.11+",
        ),
        "SECURITY.md": (
            "https://github.com/ElGrandeXu/EGX_Terminal/security/advisories/new",
            "Private Vulnerability Reporting",
            "active",
        ),
        "docs/QUICKSTART.md": (
            "Python 3.11+",
            "standard-library `tomllib`",
            "governance/requirements-reuse-build-6.2.0.txt",
            "governance/requirements-reuse-6.2.0.txt",
            "--require-hashes",
        ),
        "docs/STATUS.md": (
            CURRENT_PHASE,
        ),
        "docs/decisions/README.md": (
            "0015",
            "0016",
        ),
        "docs/publication/PUBLICATION_BOUNDARY.md": (
            CURRENT_PHASE,
        ),
        "docs/publication/GITHUB_PUBLICATION_PLAN.md": (
            CURRENT_PHASE,
        ),
        "docs/publication/RELEASE_POLICY.md": (
            "`current_releases`",
        ),
    }
    stale_tokens = ("PUBLICATION_RETRY_PREPARATION", "CURRENTLY_PRIVATE_RETRY_NOT_APPLIED")
    for relative, declarations in required.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(_finding(relative, "DOCUMENT_CURRENT_STATE", "current-state document is unreadable"))
            continue
        normalized = re.sub(r"\s+", " ", text)
        missing = [declaration for declaration in declarations if declaration not in normalized]
        if missing:
            if relative in {"README.md", "docs/QUICKSTART.md"} and missing[0] in {
                "Python 3.11+",
                "standard-library `tomllib`",
            }:
                code = "PYTHON_REQUIREMENT"
            elif relative == "docs/QUICKSTART.md" and missing[0] in {
                "governance/requirements-reuse-build-6.2.0.txt",
                "governance/requirements-reuse-6.2.0.txt",
                "--require-hashes",
            }:
                code = "REUSE_PREREQUISITE"
            else:
                code = "DOCUMENT_CURRENT_STATE"
            findings.append(
                _finding(relative, code, f"missing current declaration: {missing[0]}")
            )
        for token in stale_tokens:
            if token in text:
                findings.append(
                    _finding(relative, "DOCUMENT_STALE_STATE", f"obsolete current-state token remains: {token}")
                )
        if relative == "SECURITY.md":
            stale_security = (
                r"PUBLICATION_TRANSITION",
                r"private-repository preflight",
                r"not considered shareable",
                r"(?:PVR|Private Vulnerability Reporting).{0,100}\b(?:will|future)\b",
                r"\b(?:will|future)\b.{0,100}(?:PVR|Private Vulnerability Reporting)",
            )
            if any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in stale_security):
                findings.append(
                    _finding(relative, "SECURITY_STALE_STATE", "security policy describes a future publication state")
                )


def _check_plan_v6(relative: str, plan: dict, findings: list[Finding]) -> None:
    expected_sections = {
        "schema_version",
        "publication_phase",
        "remote_settings_status",
        "identity",
        "visibility_strategy",
        "publication_transition",
        "log_access_diagnostic",
        "credential_handling",
        "public_verification_model",
        "api_evidence_handling",
        "publication_retry",
        "prepublication_audit",
        "packages_audit",
        "metadata",
        "features",
        "merge_policy",
        "actions_policy",
        "remote_governance",
        "community_profile",
        "release_state",
        "recovery_closure",
    }
    if set(plan) != expected_sections:
        findings.append(_finding(relative, "PUBLICATION_PLAN", "schema 6 sections are incomplete or ambiguous"))

    # B. Dated current public state; this remains an offline consistency check.
    if plan.get("publication_phase") != CURRENT_PHASE:
        findings.append(_finding(relative, "CURRENT_PHASE", f"publication phase must be {CURRENT_PHASE}"))
    if plan.get("remote_settings_status") != CURRENT_REMOTE_STATUS:
        findings.append(
            _finding(relative, "CURRENT_REMOTE_STATUS", "remote status must be a dated verified public observation")
        )
    if (
        plan.get("identity")
        != {
            "owner": "ElGrandeXu",
            "repository": "EGX_Terminal",
            "repository_id": 1308085094,
            "default_branch": "main",
        }
    ):
        findings.append(_finding(relative, "REPOSITORY_IDENTITY", "canonical repository identity is inconsistent"))

    visibility = plan.get("visibility_strategy", {})
    if not isinstance(visibility, dict) or visibility.get("target_visibility") != "public":
        findings.append(_finding(relative, "FINAL_TARGET", "final repository visibility target must remain public"))
    if (
        not isinstance(visibility, dict)
        or visibility.get("initial_visibility") != "private"
        or visibility.get("pretransition_observation")
        != {
            "observed_on": "2026-07-22",
            "checkpoint": "23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515",
            "commit_count": 41,
            "visibility": "private",
        }
    ):
        findings.append(_finding(relative, "PRETRANSITION_STATE", "historical private observation is inconsistent"))
    if (
        not isinstance(visibility, dict)
        or visibility.get("first_transition_status") != "PUBLIC_TRANSITION_ROLLED_BACK"
    ):
        findings.append(
            _finding(relative, "HISTORICAL_TRANSITION", "first public rollback must remain recorded")
        )
    if (
        not isinstance(visibility, dict)
        or visibility.get("retry_status") != "COMPLETED_SUCCESS"
        or visibility.get("status") != CURRENT_PHASE
    ):
        findings.append(_finding(relative, "FINAL_RETRY_STATUS", "corrected publication must remain completed"))
    current = visibility.get("dated_remote_observation", {}) if isinstance(visibility, dict) else {}
    if (
        current
        != {
            "observed_on": "2026-07-23",
            "checkpoint": DATED_REMOTE_SNAPSHOT_CHECKPOINT,
            "commit_count": DATED_REMOTE_SNAPSHOT_COMMIT_COUNT,
            "visibility": "public",
            "source": "GITHUB_API",
            "qualification": "DATED_V1_CLOSURE_RULESET_OBSERVATION",
        }
        or visibility.get("snapshot_source") != "DATED_GITHUB_API_SNAPSHOT_NOT_LIVE_CHECK"
    ):
        findings.append(
            _finding(relative, "CURRENT_VISIBILITY", "dated closure snapshot must declare verified public visibility")
        )

    # A. Immutable historical facts from the first transition and rollback.
    transition = plan.get("publication_transition", {})
    if not isinstance(transition, dict):
        transition = {}
    if transition.get("status") != "PUBLIC_TRANSITION_ROLLED_BACK":
        findings.append(
            _finding(relative, "FIRST_TRANSITION_STATE", "first public transition must be recorded as rolled back")
        )
    if transition.get("status") in {
        "AUTHORIZED_NOT_APPLIED",
        "NOT_APPLIED",
        "APPLIED",
        "COMPLETE",
        "SUCCESS",
        "PUBLIC_TRANSITION_SUCCEEDED",
    }:
        findings.append(
            _finding(relative, "FIRST_TRANSITION_STATE", "first transition cannot be erased or presented as successful")
        )
    if (
        transition.get("authorized_by") != "docs/decisions/0015-authorize-guarded-public-transition.md"
        or transition.get("recorded_by") != "docs/decisions/0016-record-public-transition-rollback.md"
    ):
        findings.append(_finding(relative, "FIRST_TRANSITION_RECORD", "transition decisions are not linked correctly"))

    initial = transition.get("initial_state", {})
    if (
        not isinstance(initial, dict)
        or initial.get("checkpoint") != "c887949cbc3c6fe8aade34b2675b39545c365905"
        or initial.get("commit_count") != 42
        or initial.get("linear_history") is not True
        or any(
            initial.get(key) != 0
            for key in (
                "open_pull_request_count",
                "git_tag_count",
                "github_release_count",
                "package_count",
                "fork_count",
            )
        )
        or initial.get("private_audit_verdict") != "PUBLICATION_READY_FOR_ATOMIC_MISSION_ONLY"
    ):
        findings.append(_finding(relative, "FIRST_TRANSITION_RECORD", "initial transition state is incomplete"))

    exposure = transition.get("public_exposure", {})
    if (
        not isinstance(exposure, dict)
        or exposure.get("started_at") != "2026-07-23T08:02:57.4503878Z"
        or exposure.get("rollback_completed_at") != "2026-07-23T08:34:32.3856142Z"
        or exposure.get("duration_seconds_approx") != 1895
        or exposure.get("duration_human") != "approximately 31 minutes 35 seconds"
    ):
        findings.append(
            _finding(relative, "EXPOSURE_TIMELINE", "public exposure timestamps and approximate duration are required")
        )
    if (
        not isinstance(exposure, dict)
        or exposure.get("material_leak_detected") is not False
        or exposure.get("third_party_access_or_copying_excluded") is not False
    ):
        findings.append(
            _finding(relative, "EXPOSURE_UNCERTAINTY", "absence of detected leak cannot retract possible third-party access")
        )
    if not all(
        exposure.get(key) is True
        for key in (
            "repository_id_unchanged",
            "default_branch_unchanged",
            "checkpoint_unchanged",
            "content_unchanged",
        )
    ):
        findings.append(_finding(relative, "FIRST_TRANSITION_RECORD", "unchanged repository identity must be recorded"))

    public_controls = transition.get("public_window_controls", {})
    expected_public_controls = {
        "private_vulnerability_reporting": "ACTIVE_VERIFIED",
        "secret_scanning": "ACTIVE",
        "push_protection": "ACTIVE",
        "vulnerability_alerts": "ACTIVE",
        "actions_policy": "MINIMAL",
        "external_contributor_approval": "ALL_EXTERNAL_CONTRIBUTORS",
    }
    if not isinstance(public_controls, dict) or any(
        public_controls.get(key) != value for key, value in expected_public_controls.items()
    ):
        findings.append(_finding(relative, "PUBLIC_WINDOW_CONTROLS", "verified public controls are incomplete"))
    public_ruleset = public_controls.get("main_ruleset", {}) if isinstance(public_controls, dict) else {}
    if (
        not isinstance(public_ruleset, dict)
        or public_ruleset.get("name") != "main-protection"
        or public_ruleset.get("status") != "ACTIVE_VERIFIED"
        or public_ruleset.get("bypass_actors") != []
    ):
        findings.append(_finding(relative, "BYPASS", "public main-protection record must contain no bypass"))
    if public_controls.get("successful_checks") != list(EXPECTED_CHECKS):
        findings.append(_finding(relative, "RULESET_CHECKS", "public transition must retain all three checks"))
    if any(
        public_controls.get(key) != 0
        for key in (
            "secret_scanning_open_alert_count",
            "package_count",
            "git_tag_count",
            "github_release_count",
            "fork_count",
        )
    ):
        findings.append(_finding(relative, "PUBLIC_WINDOW_CONTROLS", "public zero-count observations are incomplete"))

    historical_run = transition.get("workflow_run", {})
    if (
        not isinstance(historical_run, dict)
        or historical_run.get("run_id") != 29951087998
        or historical_run.get("attempt") != 2
        or historical_run.get("status") != "COMPLETED_SUCCESS"
        or historical_run.get("historical_evidence_retained") is not True
        or historical_run.get("deletion_allowed") is not False
        or historical_run.get("reuse_for_retry_allowed") is not False
    ):
        findings.append(_finding(relative, "HISTORICAL_RUN", "run 29951087998 must remain retained and non-reusable"))
    rollback = transition.get("rollback", {})
    if (
        not isinstance(rollback, dict)
        or rollback.get("required_by_protocol_then_in_force") is not True
        or rollback.get("reason") != "ANONYMOUS_REST_ACTIONS_LOG_DOWNLOADS_RETURNED_HTTP_403"
        or rollback.get("completed") is not True
        or rollback.get("repository_returned_to_private") is not True
        or rollback.get("public_exposure_retraction_guaranteed") is not False
    ):
        findings.append(_finding(relative, "FIRST_TRANSITION_RECORD", "rollback cause or irreversible exposure is absent"))

    diagnostic = plan.get("log_access_diagnostic", {})
    if (
        not isinstance(diagnostic, dict)
        or diagnostic.get("classification") != "GENERAL_GITHUB_ANONYMOUS_LOG_RESTRICTION"
        or diagnostic.get("documentation_status") != "PLATFORM_AMBIGUITY"
        or diagnostic.get("control_repositories") != ["actions/checkout", "cli/cli", "astral-sh/ruff"]
        or diagnostic.get("private_origin_run_restriction_supported") is not False
        or diagnostic.get("egx_vulnerability_claimed") is not False
    ):
        findings.append(_finding(relative, "LOG_ACCESS_DIAGNOSTIC", "general platform diagnostic is incomplete"))
    if (
        not isinstance(diagnostic, dict)
        or diagnostic.get("anonymous_rest_failure_absolute_blocker") is not False
        or diagnostic.get("non_blocking_only_if_levels_b_and_c_pass") is not True
        or diagnostic.get("accepted_classifications") != ["INFO", "PLATFORM_AMBIGUITY"]
    ):
        findings.append(
            _finding(relative, "LOG_ACCESS_CLASSIFICATION", "generalized anonymous 403 must depend on levels B and C")
        )

    credential = plan.get("credential_handling", {})
    if (
        not isinstance(credential, dict)
        or credential.get("field_name") != "temp_clone_token"
        or credential.get("historical_display") != "LOCAL_PRIVATE_DISPLAY_ONLY"
        or credential.get("public_exposure") != "NO_PUBLIC_EXPOSURE_DETECTED"
        or credential.get("historical_value_retained") is not False
        or credential.get("future_collection") != "EXCLUDED_AT_COLLECTION_FOR_FUTURE_CAPTURES"
    ):
        findings.append(
            _finding(relative, "CREDENTIAL_COLLECTION", "temporary clone credential must be excluded before capture")
        )
    if (
        not isinstance(credential, dict)
        or credential.get("historical_value_status") != "UNKNOWN_NOT_RETAINED"
        or credential.get("historical_value_active_claim") is not False
        or credential.get("historical_value_expired_claim") is not False
        or credential.get("credential_rotation_required_claimed") is not False
    ):
        findings.append(
            _finding(relative, "CREDENTIAL_CLAIM", "retained evidence proves neither activity nor expiration")
        )
    if isinstance(credential, dict) and any("value" in key.lower() and key != "historical_value_status"
                                            and key != "historical_value_retained"
                                            and key != "historical_value_active_claim"
                                            and key != "historical_value_expired_claim"
                                            for key in credential):
        findings.append(_finding(relative, "CREDENTIAL_COLLECTION", "credential values must not be serialized"))

    # C. Durable verification and evidence-handling invariants.
    verification = plan.get("public_verification_model", {})
    if not isinstance(verification, dict) or set(verification) != {"level_a", "level_b", "level_c"}:
        findings.append(_finding(relative, "VERIFICATION_MODEL", "levels A, B, and C are mandatory"))
        verification = {}
    level_a = verification.get("level_a", {})
    if (
        not isinstance(level_a, dict)
        or set(level_a)
        != {
            "actor",
            "required",
            "anonymous_rest_log_downloads_tested",
            "comparison_repositories_required",
            "generalized_http_403_classification",
        }
        or level_a.get("actor") != "ANONYMOUS_INTERNET_WITHOUT_GITHUB_ACCOUNT"
        or level_a.get("required") != list(EXPECTED_LEVEL_A_CHECKS)
        or level_a.get("anonymous_rest_log_downloads_tested") is not True
        or level_a.get("comparison_repositories_required") != 3
        or level_a.get("generalized_http_403_classification") != ["INFO", "PLATFORM_AMBIGUITY"]
    ):
        findings.append(_finding(relative, "LEVEL_A", "anonymous verification requirements are incomplete"))
    level_b = verification.get("level_b", {})
    if (
        not isinstance(level_b, dict)
        or set(level_b)
        != {
            "actor",
            "required",
            "must_be_distinct_from",
            "collaboration_allowed",
            "invitation_allowed",
            "team_membership_allowed",
            "private_permission_allowed",
            "required_checks",
            "token_storage_allowed",
            "failure_policy",
        }
        or level_b.get("actor") != "PREEXISTING_EXTERNAL_GITHUB_ACCOUNT"
        or level_b.get("required") is not True
        or level_b.get("must_be_distinct_from") != "ElGrandeXu"
        or any(
            level_b.get(key) is not False
            for key in (
                "collaboration_allowed",
                "invitation_allowed",
                "team_membership_allowed",
                "private_permission_allowed",
                "token_storage_allowed",
            )
        )
        or level_b.get("required_checks") != list(EXPECTED_LEVEL_B_CHECKS)
        or level_b.get("failure_policy") != "CRITICAL_ROLLBACK"
    ):
        findings.append(_finding(relative, "LEVEL_B", "external non-collaborator verification is mandatory"))
    level_c = verification.get("level_c", {})
    if (
        not isinstance(level_c, dict)
        or set(level_c) != {"actor", "required"}
        or level_c.get("actor") != "AUTHENTICATED_OWNER"
        or level_c.get("required") != list(EXPECTED_LEVEL_C_CHECKS)
    ):
        findings.append(_finding(relative, "LEVEL_C", "owner verification requirements are incomplete"))

    handling = plan.get("api_evidence_handling", {})
    if (
        not isinstance(handling, dict)
        or set(handling)
        != {
            "serialization_policy",
            "exclude_before_write_or_display",
            "signed_url_replacement",
            "removed_field_recording",
            "hash_timing",
            "sanitized_evidence_immutable",
            "active_credential_raw_retention_allowed",
            "sealed_evidence_silent_sanitization_allowed",
            "dangerous_capture_policy",
        }
        or handling.get("serialization_policy") != "ALLOWLIST_REQUIRED"
        or handling.get("exclude_before_write_or_display") != list(EXPECTED_EVIDENCE_EXCLUSIONS)
        or handling.get("signed_url_replacement") != "[SIGNED_URL_REDACTED]"
        or handling.get("removed_field_recording") != "NAME_AND_PRESENCE_ONLY"
        or handling.get("hash_timing") != "AFTER_SANITIZATION"
        or handling.get("sanitized_evidence_immutable") is not True
        or handling.get("active_credential_raw_retention_allowed") is not False
        or handling.get("sealed_evidence_silent_sanitization_allowed") is not False
        or handling.get("dangerous_capture_policy") != list(EXPECTED_DANGEROUS_CAPTURE_POLICY)
    ):
        findings.append(_finding(relative, "EVIDENCE_HANDLING", "safe API response handling is incomplete"))

    retry = plan.get("publication_retry", {})
    if (
        not isinstance(retry, dict)
        or set(retry)
        != {
            "maximum_attempts",
            "status",
            "authorized_by",
            "prerequisites",
            "workflow_dispatch_required",
            "workflow",
            "ref",
            "dispatch_response_fields",
            "new_run_id_required",
            "prohibited_run_ids",
            "empty_commit_allowed",
            "temporary_branch_allowed",
            "required_checks",
            "third_attempt_requires_new_adr",
            "git_tag_creation_allowed",
            "github_release_creation_allowed",
            "protection_weakening_allowed",
            "v1.0.1_mission",
            "final_result",
        }
    ):
        findings.append(_finding(relative, "RETRY_MODEL", "retry model fields are incomplete or ambiguous"))
    if (
        not isinstance(retry, dict)
        or retry.get("authorized_by") != "docs/decisions/0016-record-public-transition-rollback.md"
    ):
        findings.append(_finding(relative, "RETRY_AUTHORIZATION", "retry authorization must reference decision 0016"))
    if not isinstance(retry, dict) or retry.get("maximum_attempts") != 1:
        findings.append(_finding(relative, "RETRY_LIMIT", "historical corrected-attempt limit must remain one"))
    if not isinstance(retry, dict) or retry.get("status") != "COMPLETED_SUCCESS":
        findings.append(_finding(relative, "FINAL_RETRY_STATUS", "corrected retry must remain completed successfully"))
    if not isinstance(retry, dict) or retry.get("prerequisites") != list(EXPECTED_RETRY_PREREQUISITES):
        findings.append(_finding(relative, "RETRY_PREREQUISITES", "retry prerequisites are incomplete"))
    if (
        not isinstance(retry, dict)
        or retry.get("workflow_dispatch_required") is not True
        or retry.get("workflow") != ".github/workflows/validate.yml"
        or retry.get("ref") != "main"
        or retry.get("new_run_id_required") is not True
    ):
        findings.append(
            _finding(relative, "WORKFLOW_DISPATCH", "corrected attempt required a new workflow_dispatch run on main")
        )
    if (
        not isinstance(retry, dict)
        or retry.get("dispatch_response_fields") != list(EXPECTED_DISPATCH_RESPONSE_FIELDS)
    ):
        findings.append(_finding(relative, "DISPATCH_RESPONSE_FIELDS", "dispatch response fields are incomplete"))
    if not isinstance(retry, dict) or retry.get("prohibited_run_ids") != [29951087998]:
        findings.append(_finding(relative, "RUN_REUSE", "historical run 29951087998 cannot be reused"))
    if (
        not isinstance(retry, dict)
        or retry.get("empty_commit_allowed") is not False
        or retry.get("temporary_branch_allowed") is not False
    ):
        findings.append(_finding(relative, "RETRY_SAFETY", "retry cannot use an empty commit or temporary branch"))
    if not isinstance(retry, dict) or retry.get("required_checks") != list(EXPECTED_CHECKS):
        findings.append(_finding(relative, "RETRY_CHECKS", "retry must retain all three checks"))
    if (
        not isinstance(retry, dict)
        or retry.get("third_attempt_requires_new_adr") is not True
    ):
        findings.append(_finding(relative, "RETRY_LIMIT", "historical third-attempt ADR gate is incomplete"))
    if (
        not isinstance(retry, dict)
        or retry.get("git_tag_creation_allowed") is not False
        or retry.get("github_release_creation_allowed") is not False
        or retry.get("v1.0.1_mission") != "SEPARATE_LATER_MISSION"
    ):
        findings.append(_finding(relative, "RELEASE_PROHIBITION", "retry cannot create tags, releases, or v1.0.1"))
    if not isinstance(retry, dict) or retry.get("protection_weakening_allowed") is not False:
        findings.append(_finding(relative, "RETRY_PROTECTIONS", "corrected attempt could not weaken protections"))
    # B. Dated final public state declared by the completed corrected attempt.
    _check_final_publication_result(relative, retry, findings)

    prepublication_audit = plan.get("prepublication_audit", {})
    expected_prepublication_audit = {
        "checkpoint": "23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515",
        "commit_count": 41,
        "git_content_audited": True,
        "pull_requests_audited": True,
        "logs_audited": True,
        "workflows_audited": True,
        "licenses_audited": True,
        "material_leak_detected": False,
        "status": "COMPLETED_PUBLICATION_BLOCKED",
        "executive_verdict": "PUBLICATION_BLOCKED",
        "finding_disposition": {
            "F-001": "INITIAL_PACKAGES_AUDIT_INACCESSIBLE_THEN_CLOSED_SEPARATELY",
            "F-002_TO_F-005": (
                "INITIAL_GOVERNANCE_AND_DOCUMENTATION_CORRECTIONS_REQUIRED_"
                "THEN_REMEDIATED_BY_SCHEMA_5_TRANSITION_CHANGE"
            ),
        },
        "merged_head_reaudit_required": True,
    }
    if prepublication_audit != expected_prepublication_audit:
        findings.append(_finding(relative, "PREAUDIT_RECORD", "historical prepublication audit is inconsistent"))
    if (
        not isinstance(prepublication_audit, dict)
        or prepublication_audit.get("status") != "COMPLETED_PUBLICATION_BLOCKED"
        or prepublication_audit.get("executive_verdict") != "PUBLICATION_BLOCKED"
    ):
        findings.append(
            _finding(relative, "PREAUDIT_VERDICT", "schema 4 and 5 preaudit verdict must remain historical")
        )
    if not isinstance(prepublication_audit, dict) or prepublication_audit.get("merged_head_reaudit_required") is not True:
        findings.append(
            _finding(relative, "PREAUDIT_FOLLOWUP", "historical merged-HEAD re-audit requirement must remain recorded")
        )

    packages = plan.get("packages_audit", {})
    if (
        not isinstance(packages, dict)
        or packages.get("finding") != "F-001"
        or packages.get("closed_on") != "2026-07-22"
        or packages.get("authorized_surface_count") != 12
        or packages.get("http_200_surface_count") != 12
        or packages.get("package_count") != 0
        or packages.get("status") != "CLOSED"
        or tuple((item.get("api_scope"), item.get("package_type")) for item in packages.get("surfaces", []))
        != EXPECTED_PACKAGE_SURFACES
        or any(item.get("http_status") != 200 or item.get("package_count") != 0
               for item in packages.get("surfaces", []))
    ):
        findings.append(_finding(relative, "PACKAGES_AUDIT", "historical packages closure is inconsistent"))

    if plan.get("metadata") != EXPECTED_METADATA:
        findings.append(_finding(relative, "METADATA", "repository metadata is incomplete or inconsistent"))

    if plan.get("features") != EXPECTED_FEATURES:
        findings.append(_finding(relative, "FEATURES", "observed GitHub feature state is incomplete or ambiguous"))

    if plan.get("merge_policy") != EXPECTED_MERGE_POLICY:
        findings.append(_finding(relative, "MERGE_POLICY", "merge policy is incomplete or inconsistent"))

    actions = plan.get("actions_policy", {})
    expected_actions = {
        "github_token_default": "read",
        "fork_workflow_write_tokens": False,
        "allowed_actions": list(EXPECTED_ACTIONS),
        "github_owned_allowed": False,
        "verified_allowed": False,
        "full_sha_pinning_required": True,
        "sha_pinning_verified_on": "2026-07-21",
        "sha_pinning_endpoint": "GET /repos/ElGrandeXu/EGX_Terminal/actions/permissions",
        "automatic_approval_for_untrusted_workflow_changes": False,
        "external_contributor_approval": "ALL_EXTERNAL_CONTRIBUTORS",
        "post_public_target": "RETAIN_MINIMAL_PERMISSIONS_AND_PRUDENT_FORK_POLICY",
        "status": "APPLIED",
    }
    if actions != expected_actions:
        findings.append(_finding(relative, "ACTIONS_POLICY", "minimal Actions policy must be preserved"))

    _check_current_remote_governance(relative, plan.get("remote_governance", {}), findings)

    release = plan.get("release_state", {})
    expected_release = {
        "current_observation": {
            "observed_on": "2026-07-23",
            "checkpoint": FINAL_PUBLICATION_CHECKPOINT,
            "canonical_git_tag_count": 0,
            "canonical_github_release_count": 0,
        },
        "historical_releases": [
            {
                "tag": "v1.0.0",
                "status": "WITHDRAWN_DURING_PRIVACY_REMEDIATION",
                "evidence": "PRIVATE_VERIFIED_BUNDLE",
                "expected_ref_present": False,
            }
        ],
        "next_candidate": "v1.0.1",
        "retry_creation_allowed": False,
        "status": "DEFERRED_TO_SEPARATE_MISSION",
    }
    if release != expected_release:
        findings.append(_finding(relative, "CURRENT_RELEASE_STATE", "current state must preserve zero tags and releases"))

    community = plan.get("community_profile", {})
    if not isinstance(community, dict) or community.get("code_of_conduct") != "DEFERRED_UNTIL_ENFORCEABLE":
        findings.append(_finding(relative, "COMMUNITY_SCOPE", "Code of Conduct remains deliberately deferred"))

    if plan.get("recovery_closure") != EXPECTED_RECOVERY_CLOSURE:
        findings.append(_finding(relative, "RECOVERY_CLOSURE", "historical recovery closure is inconsistent"))


def _check_plan(root: Path, findings: list[Finding]) -> None:
    relative = "governance/github-publication-plan.json"
    plan = _load_json(root / relative, relative, findings)
    if not isinstance(plan, dict):
        return
    if plan.get("schema_version") != 6:
        findings.append(_finding(relative, "SCHEMA_VERSION", "current publication plan must use schema 6"))
        return
    _check_plan_v6(relative, plan, findings)


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
    _check_current_documents(root, findings)
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
    print("OFFLINE_GITHUB_GOVERNANCE_SNAPSHOT_CONSISTENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
