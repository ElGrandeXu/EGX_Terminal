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


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_git_history.py"
POLICY_NAME = "Fixture Author"
POLICY_EMAIL = "123456+fixture-user@users.noreply.github.com"
POLICY_LOGIN = "fixture-user"
POLICY_USER_ID = 123456
sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("check_git_history", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class HistoryRepository:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "--quiet", "--initial-branch=main")
        self.git("config", "user.name", POLICY_NAME)
        self.git("config", "user.email", POLICY_EMAIL)
        self.write_policy()

    def write_policy(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "schema_version": 1,
            "name": POLICY_NAME,
            "email": POLICY_EMAIL,
            "github_login": POLICY_LOGIN,
            "github_user_id": POLICY_USER_ID,
            "scope": "all public repository commits",
            "privacy_mode": "github-id-based-noreply",
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


class GitHistoryTests(unittest.TestCase):
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
            {"EXPECTED_PUBLIC_IDENTITY"},
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

    def test_31_username_only_noreply_is_distinct_and_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "fixture-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("USERNAME_ONLY_NOREPLY", self.categories(report))
        self.assertIn("REVIEW", self.severities(report))

    def test_32_incorrect_public_name_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.name", "Different Name")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("PUBLIC_NAME_MISMATCH", self.categories(report))

    def test_33_incorrect_noreply_user_id_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "654321+fixture-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("NOREPLY_USER_ID_MISMATCH", self.categories(report))

    def test_34_incorrect_noreply_login_is_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.git("config", "user.email", "123456+different-user@users.noreply.github.com")
            repo.write("safe.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("NOREPLY_LOGIN_MISMATCH", self.categories(report))

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
        self.assertEqual("EXPECTED_PUBLIC_IDENTITY", report.commits[0].author.classification)
        self.assertEqual("PRIVATE_EMAIL_REVIEW_REQUIRED", report.commits[0].committer.classification)
        self.assertIn("PRIVATE_EMAIL_REVIEW_REQUIRED", self.categories(report))

    def test_36_multiple_identities_are_reviewed(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write("one.txt")
            repo.commit()
            repo.git("config", "user.name", "Different Author")
            repo.git("config", "user.email", "different@personal.test")
            repo.write("two.txt")
            repo.commit()
            report = CHECK.audit(repo.root)
        self.assertIn("MULTIPLE_AUTHOR_IDENTITIES", self.categories(report))
        self.assertIn("MULTIPLE_COMMITTER_IDENTITIES", self.categories(report))

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

    def test_39_inconsistent_policy_identity_is_an_error(self) -> None:
        temporary, repo = self.repository()
        with temporary:
            repo.write_policy(github_user_id=999999)
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


if __name__ == "__main__":
    unittest.main()
