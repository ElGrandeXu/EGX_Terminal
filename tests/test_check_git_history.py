from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_git_history.py"
POLICY_NAME = "Fixture Author"
POLICY_EMAIL = "123456+fixture-user@users.noreply.github.com"
POLICY_LOGIN = "fixture-user"
POLICY_USER_ID = 123456
GITHUB_ACTIONS_ENV_KEYS = (
    "GITHUB_ACTIONS",
    "GITHUB_EVENT_NAME",
    "GITHUB_EVENT_PATH",
    "GITHUB_REF",
    "GITHUB_SHA",
    "GITHUB_REPOSITORY",
)
sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("check_git_history", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


def without_github_actions_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in GITHUB_ACTIONS_ENV_KEYS:
        environment.pop(key, None)
    return environment


def github_actions_environment(
    *,
    event_path: Path,
    ref: str,
    sha: str,
    repository: str = "fixture/fixture",
    event_name: str = "pull_request",
    actions: str = "true",
) -> dict[str, str]:
    environment = without_github_actions_environment()
    environment.update(
        {
            "GITHUB_ACTIONS": actions,
            "GITHUB_EVENT_NAME": event_name,
            "GITHUB_EVENT_PATH": str(event_path),
            "GITHUB_REF": ref,
            "GITHUB_SHA": sha,
            "GITHUB_REPOSITORY": repository,
        }
    )
    return environment


class HistoryRepository:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "user.name", POLICY_NAME)
        self.git("config", "user.email", POLICY_EMAIL)
        self.write_policy()

    def write_policy(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "schema_version": 2,
            "purpose": [
                "protect public email privacy",
                "preserve inspectable GitHub attribution",
                "support public contributions",
                "detect unexpected human or system identities",
            ],
            "maintainer": {
                "name": POLICY_NAME,
                "email": POLICY_EMAIL,
                "github_login": POLICY_LOGIN,
                "github_user_id": POLICY_USER_ID,
            },
            "accepted_author_classes": [
                "MAINTAINER_GITHUB_NOREPLY",
                "PUBLIC_ID_BASED_NOREPLY",
                "PUBLIC_USERNAME_NOREPLY",
            ],
            "accepted_committer_classes": [
                "MAINTAINER_GITHUB_NOREPLY",
                "PUBLIC_ID_BASED_NOREPLY",
                "PUBLIC_USERNAME_NOREPLY",
                "GITHUB_WEB_COMMITTER",
            ],
            "accepted_trailer_classes": [
                "MAINTAINER_GITHUB_NOREPLY",
                "PUBLIC_ID_BASED_NOREPLY",
                "PUBLIC_USERNAME_NOREPLY",
            ],
            "github_web_committer": {
                "name": "GitHub",
                "email": "noreply@github.com",
                "allowed_role": "committer",
            },
            "personal_email_policy": "REVIEW",
            "invalid_identity_policy": "REVIEW",
            "multiple_compliant_identities_policy": "ACCEPT",
            "automation_policy": "EXPLICIT_RULE_REQUIRED",
            "ephemeral_github_pr_merge": {
                "type": "github-pull-request-merge",
                "persistence": "ephemeral",
                "identity_policy": "excluded-after-context-validation",
                "content_policy": "fully-scanned",
                "required_evidence": [
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
                ],
            },
        }
        payload.update(overrides)
        self.write(
            "governance/public-commit-identity.json",
            json.dumps(payload, indent=2) + "\n",
        )

    def git(
        self,
        *arguments: str,
        input_bytes: bytes | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        process = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            input=input_bytes,
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode:
            detail = (process.stdout + process.stderr).decode("utf-8", errors="replace")
            raise AssertionError(f"git {' '.join(arguments)} failed: {detail}")
        return process

    def write(self, relative: str, content: str | bytes = "safe\n") -> None:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")

    def commit(
        self,
        message: str = "test: fixture",
        *,
        env: dict[str, str] | None = None,
    ) -> str:
        self.git("add", "-A")
        self.git("commit", "--quiet", "-m", message, env=env)
        return self.git("rev-parse", "HEAD").stdout.decode("ascii").strip()

    def remove(self, relative: str, message: str = "test: remove fixture") -> None:
        (self.root / relative).unlink()
        self.commit(message)

    def add_remote_ref(self, name: str, oid: str, *, remote: str = "origin") -> None:
        remotes = self.git("remote").stdout.decode("utf-8").splitlines()
        if remote not in remotes:
            self.git("remote", "add", remote, f"https://example.invalid/{remote}.git")
        self.git("update-ref", f"refs/remotes/{remote}/{name}", oid)

    def add_pull_ref(self, name: str, oid: str) -> None:
        self.git("update-ref", f"refs/remotes/pull/{name}", oid)

    def commit_tree(
        self,
        tree: str,
        *parents: str,
        message: str = "test: synthetic commit",
        env: dict[str, str] | None = None,
    ) -> str:
        arguments = ["commit-tree", tree]
        for parent in parents:
            arguments.extend(("-p", parent))
        return self.git(
            *arguments,
            input_bytes=(message + "\n").encode("utf-8"),
            env=env,
        ).stdout.decode("ascii").strip()


class GitHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        environment_patch = mock.patch.dict(
            os.environ,
            without_github_actions_environment(),
            clear=True,
        )
        environment_patch.start()
        self.addCleanup(environment_patch.stop)

    def repository(self) -> tuple[tempfile.TemporaryDirectory[str], HistoryRepository]:
        temporary = tempfile.TemporaryDirectory(prefix="history audit ")
        return temporary, HistoryRepository(Path(temporary.name))

    def categories(self, report: object) -> set[str]:
        return {item.category for item in report.findings}

    def severities(self, report: object) -> set[str]:
        return {item.severity for item in report.findings}

    def capture_main(self, *arguments: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = CHECK.main(arguments)
        return result, output.getvalue()

    def github_pr_checkout(
        self,
        repo: HistoryRepository,
        *,
        base_env: dict[str, str] | None = None,
        head_env: dict[str, str] | None = None,
        personal_merge: bool = False,
        result_content: str | None = None,
        head_content: str = "feature\n",
        merge_uses_base_tree: bool = False,
        parent_count: int = 2,
    ) -> tuple[dict[str, str], Path, dict[str, str]]:
        repo.write("base.txt", "base\n")
        base = repo.commit(env=base_env)
        base_tree = repo.git("rev-parse", f"{base}^{{tree}}").stdout.decode("ascii").strip()

        repo.write("feature.txt", head_content)
        repo.git("add", "-A")
        head_tree = repo.git("write-tree").stdout.decode("ascii").strip()
        source = repo.commit_tree(head_tree, base, message="test: feature head", env=head_env)

        if result_content is not None:
            repo.write("merge-only.txt", result_content)
            repo.git("add", "-A")
            merge_tree = repo.git("write-tree").stdout.decode("ascii").strip()
        elif merge_uses_base_tree:
            merge_tree = base_tree
        else:
            merge_tree = head_tree

        if parent_count == 1:
            parents = (base,)
        elif parent_count == 2:
            parents = (base, source)
        elif parent_count == 3:
            third = repo.commit_tree(head_tree, base, message="test: third parent")
            parents = (base, source, third)
        else:
            raise AssertionError("unsupported fixture parent count")

        merge_env = os.environ.copy()
        if personal_merge:
            merge_env.update(
                {
                    "GIT_AUTHOR_NAME": "Ephemeral Author",
                    "GIT_AUTHOR_EMAIL": "merge-person" + "@" + "private.test",
                    "GIT_COMMITTER_NAME": "GitHub",
                    "GIT_COMMITTER_EMAIL": "noreply" + "@" + "github.com",
                }
            )
        merge = repo.commit_tree(
            merge_tree,
            *parents,
            message="Merge fixture into main",
            env=merge_env,
        )
        repo.add_remote_ref("main", base)
        repo.add_pull_ref("1/merge", merge)
        repo.git("checkout", "--quiet", "--detach", merge)
        repo.git("update-ref", "-d", "refs/heads/main")

        payload = {
            "number": 1,
            "repository": {"full_name": "fixture/fixture"},
            "pull_request": {
                "number": 1,
                "base": {"sha": base},
                "head": {"sha": source},
            },
        }
        event_path = repo.root / "github-event.json"
        event_path.write_text(json.dumps(payload), encoding="utf-8")
        environment = github_actions_environment(
            event_path=event_path,
            ref="refs/pull/1/merge",
            sha=merge,
        )
        return environment, event_path, {
            "base": base,
            "source": source,
            "merge": merge,
            "personal": "merge-person" + "@" + "private.test",
        }

    def test_01_minimal_compliant_history(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("README.md")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertNotIn("BLOCKER", self.severities(report))
        self.assertEqual(1, report.metrics["commits"])

    def test_02_sensitive_file_added_then_deleted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            name = "." + "env"
            repo.write(name, "SETTING=placeholder\n")
            repo.commit()
            repo.remove(name)
            report = CHECK.audit(repo.root)
        self.assertIn("SENSITIVE_FILENAME", self.categories(report))
        self.assertIn(name, report.files_absent_from_head)

    def test_03_secret_only_in_old_blob(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            value = "AK" + "IA" + ("A" * 16)
            repo.write("old.txt", "value=" + value + "\n")
            repo.commit()
            repo.write("old.txt", "safe\n")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("SECRET_SIGNATURE", self.categories(report))

    def test_04_secret_in_commit_message(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            value = "gh" + "p_" + ("a" * 30)
            repo.write("safe.txt")
            repo.commit("test: value " + value)
            report = CHECK.audit(repo.root)
        self.assertIn("SECRET_SIGNATURE", self.categories(report))

    def test_05_historical_private_key(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            marker = "-----BEGIN " + "PRIVATE KEY-----"
            repo.write("old-key.txt", marker + "\nnot-real\n")
            repo.commit()
            repo.remove("old-key.txt")
            report = CHECK.audit(repo.root)
        self.assertIn("PRIVATE_KEY", self.categories(report))

    def test_06_historical_windows_personal_path(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            slash = chr(92)
            personal = "C:" + slash + "Users" + slash + "alice" + slash + "private"
            repo.write("config.txt", "path=" + personal + "\n")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("PERSONAL_PATH", self.categories(report))

    def test_07_historical_unix_personal_path(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            personal = "/" + "home/alice/private"
            repo.write("config.txt", "path=" + personal + "\n")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("PERSONAL_PATH", self.categories(report))

    def test_08_deleted_env_file(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            name = "." + "env.local"
            repo.write(name)
            repo.commit()
            repo.remove(name)
            report = CHECK.audit(repo.root)
        self.assertIn("SENSITIVE_FILENAME", self.categories(report))

    def test_09_deleted_transcript(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            name = "private-" + "transcript.txt"
            repo.write(name)
            repo.commit()
            repo.remove(name)
            report = CHECK.audit(repo.root)
        self.assertIn("TRANSCRIPT_OR_DUMP", self.categories(report))

    def test_10_blob_over_configured_threshold(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("large.txt", "x" * 33)
            repo.commit()
            report = CHECK.audit(repo.root, max_blob_bytes=32)
        self.assertIn("LARGE_BLOB", self.categories(report))

    def test_11_id_based_noreply_identity_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual(
            {"MAINTAINER_GITHUB_NOREPLY"},
            {item["classification"] for item in report.identities},
        )

    def test_12_non_noreply_email_is_review(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "author@personal.test")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("PRIVATE_EMAIL_REVIEW_REQUIRED", self.categories(report))

    def test_13_fail_on_review(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "author@personal.test")
            repo.write("safe.txt")
            repo.commit()
            normal, _ = self.capture_main("--root", str(repo.root))
            strict, _ = self.capture_main("--root", str(repo.root), "--fail-on-review")
        self.assertEqual(0, normal)
        self.assertEqual(1, strict)

    def test_14_distinct_author_and_committer(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_AUTHOR_NAME": "Different Author",
                    "GIT_AUTHOR_EMAIL": "different@users.noreply.github.com",
                }
            )
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        commit = report.commits[0]
        self.assertNotEqual(commit.author.name, commit.committer.name)
        self.assertEqual("PUBLIC_USERNAME_NOREPLY", commit.author.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_15_coauthor_trailer_is_masked(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            email = "alice@personal.test"
            repo.write("safe.txt")
            repo.commit("test: trailer\n\nCo-authored-by: Alice <" + email + ">")
            code, output = self.capture_main("--root", str(repo.root))
        self.assertEqual(0, code)
        self.assertIn("a***@personal.test", output)
        self.assertNotIn(email, output)

    def test_16_second_branch_is_unexpected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            repo.git("branch", "other")
            report = CHECK.audit(repo.root)
        self.assertIn("UNEXPECTED_BRANCH", self.categories(report))

    def test_17_tag_is_unexpected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            repo.git("tag", "v0-test")
            report = CHECK.audit(repo.root)
        self.assertIn("UNEXPECTED_TAG", self.categories(report))

    def test_18_git_note_ref_is_detected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            repo.git("notes", "add", "-m", "safe note")
            report = CHECK.audit(repo.root)
        self.assertIn("GIT_NOTES_REF", self.categories(report))

    def test_19_unreachable_object_is_ignored(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            value = ("AK" + "IA" + ("B" * 16)).encode("ascii")
            repo.git("hash-object", "-w", "--stdin", input_bytes=value)
            report = CHECK.audit(repo.root)
        self.assertNotIn("SECRET_SIGNATURE", self.categories(report))

    def test_20_all_refs_finds_other_branch_content(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "private")
            value = "AK" + "IA" + ("C" * 16)
            repo.write("private.txt", value + "\n")
            repo.commit()
            repo.git("checkout", "--quiet", "main")
            default = CHECK.audit(repo.root)
            complete = CHECK.audit(repo.root, all_refs=True)
        self.assertNotIn("SECRET_SIGNATURE", self.categories(default))
        self.assertIn("SECRET_SIGNATURE", self.categories(complete))

    def test_41_no_remote_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertFalse({"UNEXPECTED_REMOTE", "UNEXPECTED_REMOTE_REF"} & self.categories(report))

    def test_42_matching_origin_main_is_transport_info(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            head = repo.commit()
            repo.add_remote_ref("main", head)
            code, output = self.capture_main("--root", str(repo.root), "--fail-on-review")
            report = CHECK.audit(repo.root)
        self.assertEqual(0, code, output)
        self.assertIn("EXPECTED_REMOTE_MAIN", self.categories(report))
        self.assertNotIn("REVIEW", self.severities(report))

    def test_43_divergent_origin_main_is_rejected_on_branch(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt", "base\n")
            base = repo.commit()
            repo.write("safe.txt", "head\n")
            repo.commit()
            repo.add_remote_ref("main", base)
            report = CHECK.audit(repo.root)
        self.assertIn("DIVERGENT_REMOTE_MAIN", self.categories(report))

    def test_44_symbolic_origin_head_to_main_is_transport_info(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            head = repo.commit()
            repo.add_remote_ref("main", head)
            repo.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
            report = CHECK.audit(repo.root)
        self.assertIn("EXPECTED_REMOTE_HEAD", self.categories(report))
        self.assertNotIn("INVALID_REMOTE_HEAD", self.categories(report))

    def test_45_unexpected_remote_is_rejected_without_exposing_url(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            fragments = (
                "ht",
                "tps",
                ":",
                "/",
                "/",
                "fixture-user",
                ":",
                "credential",
                "@",
                "example.invalid",
                "/private.git",
            )
            sensitive_url = "".join(fragments)
            repo.write("remote.txt", sensitive_url + "\n")
            repo.commit()
            repo.git("remote", "add", "upstream", sensitive_url)
            first = CHECK.audit(repo.root)
            second = CHECK.audit(repo.root)
            code, output = self.capture_main("--root", str(repo.root), "--fail-on-review")
            fixture_blob = repo.git("show", "HEAD:remote.txt").stdout
            tracked_paths = subprocess.run(
                ["git", "-C", str(REPOSITORY_ROOT), "ls-files", "-z"],
                check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8", errors="surrogateescape").split("\0")
            tracked_payloads = (
                (REPOSITORY_ROOT / path).read_bytes()
                for path in tracked_paths
                if path
            )
        self.assertEqual(first.findings, second.findings)
        self.assertEqual(1, code)
        self.assertIn(sensitive_url.encode("utf-8"), fixture_blob)
        self.assertIn("AUTHENTICATED_URL", self.categories(first))
        self.assertIn("UNEXPECTED_REMOTE", self.categories(first))
        self.assertNotIn(sensitive_url, output)
        self.assertNotIn("credential", output)
        self.assertTrue(
            all(sensitive_url.encode("utf-8") not in payload for payload in tracked_payloads)
        )

    def test_46_remote_ref_to_independent_graph_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            tree = repo.git("write-tree").stdout.decode("ascii").strip()
            independent = repo.commit_tree(tree, message="test: independent")
            repo.add_remote_ref("main", independent)
            report = CHECK.audit(repo.root)
        self.assertIn("REMOTE_REF_OUTSIDE_AUDITED_GRAPH", self.categories(report))

    def test_47_detached_pull_request_checkout_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            base = repo.commit()
            tree = repo.git("write-tree").stdout.decode("ascii").strip()
            feature = repo.commit_tree(tree, base, message="test: feature head")
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_AUTHOR_NAME": POLICY_NAME,
                    "GIT_AUTHOR_EMAIL": POLICY_EMAIL,
                    "GIT_COMMITTER_NAME": "GitHub",
                    "GIT_COMMITTER_EMAIL": "noreply@github.com",
                }
            )
            merge = repo.commit_tree(
                tree,
                base,
                feature,
                message="test: temporary pull request merge",
                env=environment,
            )
            repo.add_remote_ref("main", base)
            repo.add_remote_ref("pull-checkout", feature)
            repo.git("checkout", "--quiet", "--detach", merge)
            repo.git("update-ref", "-d", "refs/heads/main")
            report = CHECK.audit(repo.root)
        self.assertIn("HEAD", report.selected_refs)
        self.assertIn("CHECKOUT_REMOTE_REF", self.categories(report))
        self.assertNotIn("REVIEW", self.severities(report))

    def test_48_all_refs_scans_independent_remote_objects(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            main = repo.commit()
            repo.add_remote_ref("main", main)
            secret = ("AK" + "IA" + ("D" * 16) + "\n").encode("ascii")
            blob = repo.git("hash-object", "-w", "--stdin", input_bytes=secret).stdout.decode("ascii").strip()
            tree_input = f"100644 blob {blob}\tprivate.txt\n".encode("utf-8")
            tree = repo.git("mktree", input_bytes=tree_input).stdout.decode("ascii").strip()
            independent = repo.commit_tree(tree, message="test: independent remote content")
            repo.add_remote_ref("independent", independent)
            default = CHECK.audit(repo.root)
            complete = CHECK.audit(repo.root, all_refs=True)
        self.assertNotIn("SECRET_SIGNATURE", self.categories(default))
        self.assertIn("SECRET_SIGNATURE", self.categories(complete))

    def test_49_detached_checkout_rejects_independent_origin_main(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            head = repo.commit()
            tree = repo.git("write-tree").stdout.decode("ascii").strip()
            independent = repo.commit_tree(tree, message="test: independent remote main")
            repo.add_remote_ref("main", independent)
            repo.git("checkout", "--quiet", "--detach", head)
            repo.git("update-ref", "-d", "refs/heads/main")
            report = CHECK.audit(repo.root)
        self.assertIn("REMOTE_REF_OUTSIDE_AUDITED_GRAPH", self.categories(report))

    def test_21_safe_historical_agents_file(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("AGENTS.md", "historical bootstrap guidance\n")
            repo.commit()
            repo.remove("AGENTS.md")
            report = CHECK.audit(repo.root)
        self.assertIn("AGENTS.md", report.files_absent_from_head)
        self.assertNotIn("NEUTRAL_ROOT", self.categories(report))

    def test_22_small_known_binary_is_inventoried(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("image.png", b"\x89PNG\r\n\x1a\n\x00safe")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual(1, report.metrics["binary_blobs"])
        self.assertIn("BINARY_BLOB", self.categories(report))
        self.assertNotIn("UNJUSTIFIED_BINARY", self.categories(report))

    def test_23_git_lfs_pointer_is_detected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            pointer = "version https://git-lfs.github.com/spec/v1\n" + "oid sha256:" + ("a" * 64) + "\nsize 1\n"
            repo.write("asset.bin", pointer)
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("GIT_LFS_POINTER", self.categories(report))

    def test_24_submodule_gitlink_is_detected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            head = repo.commit()
            repo.git("update-index", "--add", "--cacheinfo", f"160000,{head},vendor/sub")
            repo.git("commit", "--quiet", "-m", "test: gitlink")
            report = CHECK.audit(repo.root)
        self.assertIn("SUBMODULE", self.categories(report))

    def test_25_path_with_spaces(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            relative = "docs/file with spaces.md"
            repo.write(relative)
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn(relative, report.historical_paths)

    def test_26_execution_from_other_working_directory(self) -> None:
        temporary, repo = self.repository()
        with temporary, tempfile.TemporaryDirectory() as other:
            repo.write("safe.txt")
            repo.commit()
            process = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--root", str(repo.root)],
                cwd=other,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)

    def test_27_json_output_is_deterministic(self) -> None:
        temporary, repo = self.repository()
        with temporary, tempfile.TemporaryDirectory() as output_dir:
            repo.write("safe.txt")
            repo.commit()
            first = Path(output_dir) / "first.json"
            second = Path(output_dir) / "second.json"
            self.assertEqual(0, CHECK.main(("--root", str(repo.root), "--json", str(first))))
            self.assertEqual(0, CHECK.main(("--root", str(repo.root), "--json", str(second))))
            first_text = first.read_text(encoding="utf-8")
            second_text = second.read_text(encoding="utf-8")
        self.assertEqual(first_text, second_text)
        json.loads(first_text)

    def test_28_sensitive_value_is_not_printed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            value = "sk-" + ("x" * 24)
            repo.write("secret.txt", value + "\n")
            repo.commit()
            code, output = self.capture_main("--root", str(repo.root))
        self.assertEqual(1, code)
        self.assertNotIn(value, output)
        self.assertIn("value not displayed", output)

    def test_29_return_codes_are_coherent(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            clean, _ = self.capture_main("--root", str(repo.root))
            repo.write("bad.txt", "gh" + "p_" + ("z" * 30))
            repo.commit()
            blocked, _ = self.capture_main("--root", str(repo.root))
        self.assertEqual(0, clean)
        self.assertEqual(1, blocked)

    def test_30_detection_fixtures_do_not_false_positive(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            text = (
                "regex=AKIA[0-9A-Z]{16}\n"
                "example=user@example.com\n"
                "commit=" + ("a" * 40) + "\n"
                "sha256=" + ("b" * 64) + "\n"
            )
            repo.write("fixtures.txt", text)
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertNotIn("BLOCKER", self.severities(report))

    def test_31_username_only_noreply_author_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "fixture-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual("PUBLIC_USERNAME_NOREPLY", report.commits[0].author.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_32_maintainer_display_name_variation_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.name", "Different Name")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual("MAINTAINER_GITHUB_NOREPLY", report.commits[0].author.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_33_other_id_based_noreply_author_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "654321+fixture-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual("PUBLIC_ID_BASED_NOREPLY", report.commits[0].author.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_34_other_id_based_login_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "123456+different-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual("PUBLIC_ID_BASED_NOREPLY", report.commits[0].author.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_35_correct_author_incorrect_committer_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_COMMITTER_NAME": "Different Committer",
                    "GIT_COMMITTER_EMAIL": "committer@personal.test",
                }
            )
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("MAINTAINER_GITHUB_NOREPLY", report.commits[0].author.classification)
        self.assertEqual("PRIVATE_EMAIL_REVIEW_REQUIRED", report.commits[0].committer.classification)
        self.assertIn("PRIVATE_EMAIL_REVIEW_REQUIRED", self.categories(report))

    def test_36_multiple_compliant_identities_are_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("one.txt")
            repo.commit()
            repo.git("config", "user.name", "Different Author")
            repo.git("config", "user.email", "654321+different@users.noreply.github.com")
            repo.write("two.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertEqual(2, len({item.author.email for item in report.commits}))
        self.assertEqual(2, len({item.committer.email for item in report.commits}))
        self.assertNotIn("REVIEW", self.severities(report))

    def test_37_missing_policy_is_an_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            (repo.root / "governance/public-commit-identity.json").unlink()
            repo.write("safe.txt")
            repo.commit()
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root)

    def test_38_invalid_policy_json_is_an_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("governance/public-commit-identity.json", "{invalid\n")
            repo.write("safe.txt")
            repo.commit()
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root)

    def test_39_invalid_version_2_policy_is_an_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write_policy(automation_policy="ALLOW_ALL")
            repo.write("safe.txt")
            repo.commit()
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root)

    def test_40_identity_diagnostic_masks_personal_email(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            email = "sensitive-person@personal.test"
            repo.git("config", "user.email", email)
            repo.write("safe.txt")
            repo.commit()
            code, output = self.capture_main(
                "--root", str(repo.root), "--fail-on-review"
            )
        self.assertEqual(1, code)
        self.assertNotIn(email, output)
        self.assertIn("s***@personal.test", output)

    def test_50_version_1_policy_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            legacy = {
                "schema_version": 1,
                "name": POLICY_NAME,
                "email": POLICY_EMAIL,
                "github_login": POLICY_LOGIN,
                "github_user_id": POLICY_USER_ID,
                "scope": "all public repository commits",
                "privacy_mode": "github-id-based-noreply",
            }
            repo.write(
                "governance/public-commit-identity.json",
                json.dumps(legacy, indent=2) + "\n",
            )
            repo.write("safe.txt")
            repo.commit()
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root)

    def test_51_github_web_identity_is_rejected_as_author(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {"GIT_AUTHOR_NAME": "GitHub", "GIT_AUTHOR_EMAIL": "noreply@github.com"}
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("GITHUB_WEB_COMMITTER_WRONG_ROLE", report.commits[0].author.classification)
        self.assertIn("REVIEW", self.severities(report))

    def test_52_id_based_noreply_committer_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_COMMITTER_NAME": "Public Committer",
                    "GIT_COMMITTER_EMAIL": "654321+public-committer@users.noreply.github.com",
                }
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("PUBLIC_ID_BASED_NOREPLY", report.commits[0].committer.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_53_username_noreply_committer_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_COMMITTER_NAME": "Public Committer",
                    "GIT_COMMITTER_EMAIL": "public-committer@users.noreply.github.com",
                }
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("PUBLIC_USERNAME_NOREPLY", report.commits[0].committer.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_54_exact_github_web_committer_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {"GIT_COMMITTER_NAME": "GitHub", "GIT_COMMITTER_EMAIL": "noreply@github.com"}
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("MAINTAINER_GITHUB_NOREPLY", report.commits[0].author.classification)
        self.assertEqual("GITHUB_WEB_COMMITTER", report.commits[0].committer.classification)
        self.assertNotIn("REVIEW", self.severities(report))

    def test_55_false_github_system_committer_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {"GIT_COMMITTER_NAME": "Not GitHub", "GIT_COMMITTER_EMAIL": "noreply@github.com"}
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("UNAUTHORIZED_SYSTEM_IDENTITY", report.commits[0].committer.classification)
        self.assertIn("REVIEW", self.severities(report))

    def test_56_undeclared_bot_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {
                    "GIT_AUTHOR_NAME": "dependabot[bot]",
                    "GIT_AUTHOR_EMAIL": "49699333+dependabot[bot]@users.noreply.github.com",
                }
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("UNDECLARED_AUTOMATION_IDENTITY", report.commits[0].author.classification)
        self.assertIn("REVIEW", self.severities(report))

    def test_57_current_contribution_branch_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature/test")
            repo.write("feature.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("CONTRIBUTION_REF", self.categories(report))
        self.assertNotIn("REVIEW", self.severities(report))
        self.assertIn("refs/heads/feature/test", report.selected_refs)

    def test_58_matching_remote_contribution_ref_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            repo.write("feature.txt")
            head = repo.commit()
            repo.add_remote_ref("feature", head)
            report = CHECK.audit(repo.root)
        contribution_findings = [
            item for item in report.findings if item.category == "CONTRIBUTION_REF"
        ]
        self.assertEqual(2, len(contribution_findings))
        self.assertNotIn("REVIEW", self.severities(report))

    def test_59_remote_contribution_ancestor_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            base = repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            repo.write("feature.txt")
            repo.commit()
            repo.add_remote_ref("feature", base)
            report = CHECK.audit(repo.root)
        self.assertNotIn("REVIEW", self.severities(report))
        self.assertIn("CONTRIBUTION_REF", self.categories(report))

    def test_60_divergent_remote_contribution_ref_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            base = repo.commit()
            repo.write("main.txt")
            main_head = repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature", base)
            repo.write("feature.txt")
            repo.commit()
            repo.add_remote_ref("feature", main_head)
            report = CHECK.audit(repo.root)
        self.assertIn("DIVERGENT_CONTRIBUTION_REF", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_61_second_local_branch_is_rejected_in_contribution_mode(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            repo.git("branch", "third")
            report = CHECK.audit(repo.root)
        self.assertIn("UNEXPECTED_BRANCH", self.categories(report))

    def test_62_second_remote_is_rejected_in_contribution_mode(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            base = repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            repo.add_remote_ref("main", base, remote="upstream")
            report = CHECK.audit(repo.root)
        self.assertIn("UNEXPECTED_REMOTE", self.categories(report))

    def test_63_all_refs_scans_current_contribution_content(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            value = "AK" + "IA" + ("E" * 16)
            repo.write("feature.txt", value + "\n")
            repo.commit()
            report = CHECK.audit(repo.root, all_refs=True)
        self.assertIn("refs/heads/feature", report.selected_refs)
        self.assertIn("SECRET_SIGNATURE", self.categories(report))

    def test_64_returning_to_main_restores_strict_ref_policy(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature")
            contribution = CHECK.audit(repo.root)
            repo.git("checkout", "--quiet", "main")
            main = CHECK.audit(repo.root)
        self.assertNotIn("UNEXPECTED_BRANCH", self.categories(contribution))
        self.assertIn("UNEXPECTED_BRANCH", self.categories(main))

    def test_65_unrelated_current_contribution_history_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            tree = repo.git("write-tree").stdout.decode("ascii").strip()
            independent = repo.commit_tree(tree, message="test: independent feature")
            repo.git("update-ref", "refs/heads/feature", independent)
            repo.git("checkout", "--quiet", "feature")
            report = CHECK.audit(repo.root)
        self.assertIn("UNRELATED_CONTRIBUTION_HISTORY", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_66_invalid_identity_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment = os.environ.copy()
            environment.update(
                {"GIT_AUTHOR_NAME": "Invalid Author", "GIT_AUTHOR_EMAIL": "not-an-email"}
            )
            repo.write("safe.txt")
            repo.commit(env=environment)
            report = CHECK.audit(repo.root)
        self.assertEqual("INVALID_IDENTITY", report.commits[0].author.classification)
        self.assertIn("REVIEW", self.severities(report))

    def test_67_complete_github_pr_context_is_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertNotIn("REVIEW", self.severities(report))
        self.assertNotIn("BLOCKER", self.severities(report))
        self.assertEqual(1, report.metrics["ephemeral_pr_merge_commits"])

    def test_68_personal_identity_is_excluded_only_for_ephemeral_merge(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo, personal_merge=True)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertNotIn("REVIEW", self.severities(report))
        ephemeral = [
            commit for commit in report.commits
            if commit.persistence == CHECK.EPHEMERAL_GITHUB_PR_MERGE
        ]
        self.assertEqual(1, len(ephemeral))
        self.assertNotIn(fixture["personal"], repr(report))

    def test_69_personal_identity_in_head_parent_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            private = os.environ.copy()
            private["GIT_AUTHOR_EMAIL"] = "head-person" + "@" + "private.test"
            environment, _, _ = self.github_pr_checkout(repo, head_env=private)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("PRIVATE_EMAIL_REVIEW_REQUIRED", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_70_personal_identity_in_base_parent_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            private = os.environ.copy()
            private["GIT_AUTHOR_EMAIL"] = "base-person" + "@" + "private.test"
            environment, _, _ = self.github_pr_checkout(repo, base_env=private)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("PRIVATE_EMAIL_REVIEW_REQUIRED", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_71_secret_in_merged_result_is_blocked(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            secret = "AK" + "IA" + ("R" * 16) + "\n"
            environment, _, _ = self.github_pr_checkout(repo, result_content=secret)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("SECRET_SIGNATURE", self.categories(report))
        self.assertIn("BLOCKER", self.severities(report))

    def test_72_secret_in_parent_is_blocked_when_absent_from_merge_tree(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            secret = "AK" + "IA" + ("P" * 16) + "\n"
            environment, _, _ = self.github_pr_checkout(
                repo,
                head_content=secret,
                merge_uses_base_tree=True,
            )
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("SECRET_SIGNATURE", self.categories(report))
        self.assertIn("BLOCKER", self.severities(report))

    def test_73_exact_synthetic_merge_ref_is_info(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            report = CHECK.audit(repo.root, environment=environment)
        matching = [item for item in report.findings if item.category == "GITHUB_PR_MERGE_REF"]
        self.assertEqual(1, len(matching))
        self.assertEqual("INFO", matching[0].severity)

    def test_74_synthetic_ref_with_wrong_number_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            environment["GITHUB_REF"] = "refs/pull/2/merge"
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_75_synthetic_ref_to_other_oid_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo)
            repo.add_pull_ref("1/merge", fixture["base"])
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_76_pull_head_ref_is_not_authorized(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo)
            repo.git("update-ref", "-d", "refs/remotes/pull/1/merge")
            repo.add_pull_ref("1/head", fixture["source"])
            report = CHECK.audit(repo.root, environment=environment)
        self.assertNotIn("GITHUB_PR_MERGE_REF", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_77_context_without_github_actions_true_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            environment["GITHUB_ACTIONS"] = "false"
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_78_wrong_event_name_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            environment["GITHUB_EVENT_NAME"] = "push"
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_79_invalid_github_ref_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            environment["GITHUB_REF"] = "refs/pull/1/head"
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_80_github_sha_different_from_head_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo)
            environment["GITHUB_SHA"] = fixture["base"]
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_81_absent_event_payload_is_controlled_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, _ = self.github_pr_checkout(repo)
            event_path.unlink()
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root, environment=environment)

    def test_82_invalid_event_payload_json_is_controlled_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, _ = self.github_pr_checkout(repo)
            event_path.write_text("{invalid\n", encoding="utf-8")
            with self.assertRaises(CHECK.HistoryAuditError):
                CHECK.audit(repo.root, environment=environment)

    def test_83_payload_number_mismatch_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, fixture = self.github_pr_checkout(repo)
            payload = json.loads(event_path.read_text(encoding="utf-8"))
            payload["number"] = 2
            payload["pull_request"]["number"] = 2
            event_path.write_text(json.dumps(payload), encoding="utf-8")
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertEqual(40, len(fixture["merge"]))

    def test_84_payload_repository_mismatch_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, _ = self.github_pr_checkout(repo)
            payload = json.loads(event_path.read_text(encoding="utf-8"))
            payload["repository"]["full_name"] = "different/repository"
            event_path.write_text(json.dumps(payload), encoding="utf-8")
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_85_payload_base_sha_mismatch_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, fixture = self.github_pr_checkout(repo)
            payload = json.loads(event_path.read_text(encoding="utf-8"))
            payload["pull_request"]["base"]["sha"] = fixture["source"]
            event_path.write_text(json.dumps(payload), encoding="utf-8")
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_86_payload_head_sha_mismatch_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, event_path, fixture = self.github_pr_checkout(repo)
            payload = json.loads(event_path.read_text(encoding="utf-8"))
            payload["pull_request"]["head"]["sha"] = fixture["base"]
            event_path.write_text(json.dumps(payload), encoding="utf-8")
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_87_single_parent_candidate_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo, parent_count=1)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_88_octopus_merge_candidate_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo, parent_count=3)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_89_multiple_pull_refs_are_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo)
            repo.add_pull_ref("2/merge", fixture["merge"])
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_MERGE_REF", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_90_all_refs_accepts_only_valid_synthetic_ref(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            report = CHECK.audit(repo.root, all_refs=True, environment=environment)
        self.assertNotIn("REVIEW", self.severities(report))
        self.assertNotIn("BLOCKER", self.severities(report))
        self.assertIn("refs/remotes/pull/1/merge", report.selected_refs)

    def test_91_ephemeral_identity_is_absent_from_persistent_identity_count(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo, personal_merge=True)
            report = CHECK.audit(repo.root, environment=environment)
        self.assertEqual(2, report.metrics["persistent_commits"])
        self.assertEqual(3, report.metrics["total_scanned_commits"])
        self.assertEqual(1, len(report.identities))
        self.assertNotIn(fixture["personal"], repr(report.identities))

    def test_92_ephemeral_merge_tree_is_still_analyzed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(
                repo,
                result_content="merged result\n",
            )
            report = CHECK.audit(repo.root, environment=environment)
        merged = [record for record in report.blobs if "merge-only.txt" in record.paths]
        self.assertEqual(1, len(merged))
        self.assertEqual(fixture["merge"], merged[0].introduction_commit)

    def test_93_ephemeral_diagnostics_never_print_complete_personal_email(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, fixture = self.github_pr_checkout(repo, personal_merge=True)
            report = CHECK.audit(repo.root, environment=environment)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                CHECK._print_report(report)
        self.assertNotIn(fixture["personal"], output.getvalue())
        self.assertIn("EPHEMERAL_GITHUB_PR_MERGE=1", output.getvalue())

    def test_94_local_execution_without_github_environment_is_unchanged(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root, environment={})
        self.assertNotIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertEqual(0, report.metrics["ephemeral_pr_merge_commits"])
        self.assertEqual(1, report.metrics["persistent_commits"])

    def test_95_normal_contribution_branch_remains_accepted(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("base.txt")
            repo.commit()
            repo.git("checkout", "--quiet", "-b", "feature/context-independent")
            repo.write("feature.txt")
            repo.commit()
            report = CHECK.audit(repo.root, environment={})
        self.assertIn("CONTRIBUTION_REF", self.categories(report))
        self.assertNotIn("REVIEW", self.severities(report))

    def test_96_current_actions_checkout_shape_passes_all_three_modes(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo, personal_merge=True)
            with mock.patch.dict(os.environ, environment, clear=True):
                normal, normal_output = self.capture_main("--root", str(repo.root))
                complete, complete_output = self.capture_main(
                    "--root", str(repo.root), "--all-refs"
                )
                strict, strict_output = self.capture_main(
                    "--root", str(repo.root), "--fail-on-review"
                )
        self.assertEqual((0, 0, 0), (normal, complete, strict))
        for output in (normal_output, complete_output, strict_output):
            self.assertIn("EPHEMERAL_GITHUB_PR_MERGE=1", output)
            self.assertIn("REVIEW=0 BLOCKER=0", output)
        self.assertTrue(all(key not in os.environ for key in GITHUB_ACTIONS_ENV_KEYS))

    def test_97_github_push_context_keeps_persistent_main_behavior(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            head = repo.commit()
            event_path = repo.root / "push-event.json"
            event_path.write_text(json.dumps({"ref": "refs/heads/main"}), encoding="utf-8")
            environment = {
                "GITHUB_ACTIONS": "true",
                "GITHUB_EVENT_NAME": "push",
                "GITHUB_EVENT_PATH": str(event_path),
                "GITHUB_REF": "refs/heads/main",
                "GITHUB_SHA": head,
                "GITHUB_REPOSITORY": "fixture/fixture",
            }
            report = CHECK.audit(repo.root, environment=environment)
        self.assertNotIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertNotIn("REVIEW", self.severities(report))
        self.assertEqual(1, report.metrics["persistent_commits"])

    def test_98_ordinary_fixture_has_no_github_actions_environment(self) -> None:
        self.assertEqual(
            [],
            [key for key in GITHUB_ACTIONS_ENV_KEYS if key in os.environ],
        )

    def test_99_sanitizer_preserves_non_github_environment(self) -> None:
        marker = "EGX_HISTORY_FIXTURE_MARKER"
        with mock.patch.dict(
            os.environ,
            {
                marker: "preserved",
                "GITHUB_ACTIONS": "inherited",
                "GITHUB_EVENT_NAME": "inherited",
                "GITHUB_EVENT_PATH": "inherited",
                "GITHUB_REF": "inherited",
                "GITHUB_SHA": "inherited",
                "GITHUB_REPOSITORY": "inherited",
            },
            clear=False,
        ):
            sanitized = without_github_actions_environment()
        self.assertEqual("preserved", sanitized[marker])
        self.assertTrue(all(key not in sanitized for key in GITHUB_ACTIONS_ENV_KEYS))

    def test_100_default_audit_uses_sanitized_fixture_environment(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertNotIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))

    def test_101_environment_none_passes_real_process_environment(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("safe.txt")
            repo.commit()
            with mock.patch.object(
                CHECK,
                "_github_pr_context",
                wraps=CHECK._github_pr_context,
            ) as github_context:
                CHECK.audit(repo.root)
        self.assertIs(os.environ, github_context.call_args.args[2])

    def test_102_incomplete_explicit_synthetic_context_is_rejected(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            environment, _, _ = self.github_pr_checkout(repo)
            environment.pop("GITHUB_SHA")
            report = CHECK.audit(repo.root, environment=environment)
        self.assertIn("GITHUB_PR_CONTEXT_INVALID", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_103_main_restores_ordinary_environment_after_synthetic_block(self) -> None:
        synthetic_temporary, synthetic_repo = self.repository()
        ordinary_temporary, ordinary_repo = self.repository()
        with synthetic_temporary, ordinary_temporary:
            environment, _, _ = self.github_pr_checkout(synthetic_repo)
            ordinary_repo.write("safe.txt")
            ordinary_repo.commit()
            with mock.patch.dict(os.environ, environment, clear=True):
                synthetic_code, synthetic_output = self.capture_main(
                    "--root", str(synthetic_repo.root)
                )
            ordinary_code, ordinary_output = self.capture_main(
                "--root", str(ordinary_repo.root)
            )
        self.assertEqual(0, synthetic_code, synthetic_output)
        self.assertEqual(0, ordinary_code, ordinary_output)
        self.assertIn("EPHEMERAL_GITHUB_PR_MERGE=1", synthetic_output)
        self.assertNotIn("GITHUB_PR_CONTEXT_INVALID", ordinary_output)
        self.assertTrue(all(key not in os.environ for key in GITHUB_ACTIONS_ENV_KEYS))


if __name__ == "__main__":
    unittest.main()
