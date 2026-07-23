# GitHub recovery and publication record

This record explains the machine-readable
[`github-publication-plan.json`](../../governance/github-publication-plan.json).
The durable phase is **`PUBLIC_REPOSITORY_VERIFIED`**. The canonical repository
is public, and the corrected final publication was applied and verified at
`1d79ea37a1c614728cc7651c4d611218eaca174a`. The first public transition and
rollback remain historical facts. This record authorizes no tag or release.

## Canonical repository and historical recovery

`ElGrandeXu/EGX_Terminal`, repository ID `1308085094`, is the sole canonical
repository and uses `main`. Its recreated history excludes the personal author
address that caused the earlier identity incident. Private recovery evidence
and backups remain outside this repository.

The 2026-07-22 pretransition audit at
`23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515` recorded 41 commits and initially
returned `PUBLICATION_BLOCKED`. Its Packages gap later closed with twelve HTTP
200 surfaces and zero packages; schema 5 remediated the remaining governance
findings. Schemas 4 and 5 remain accurate historical records for their phases.

## First public transition and rollback

The atomic mission began from
`c887949cbc3c6fe8aade34b2675b39545c365905`: 42 linear commits, no open pull
request, tag, release, package, or fork, and a private-audit verdict of
`PUBLICATION_READY` limited to that mission.

Public exposure began at `2026-07-23T08:02:57.4503878Z`. Rollback to private
visibility completed at `2026-07-23T08:34:32.3856142Z`, approximately 31
minutes and 35 seconds later. Repository ID, branch, SHA, and content remained
unchanged. No material leak was detected. This does not guarantee that no third
party viewed or copied the surface during the public interval.

During the interval:

- Private Vulnerability Reporting was active and verified;
- `main-protection` was active with no bypass;
- secret scanning, push protection, and vulnerability alerts were active;
- the minimal Actions policy and approval for all external contributors held;
- `repository / ubuntu`, `repository / windows`, and `licensing / reuse`
  succeeded; and
- zero secret-scanning alerts, packages, tags, releases, or forks were observed.

After return to GitHub Free private visibility, PVR and `main-protection` became
unavailable, secret scanning was disabled, push protection became inactive, and
`main` was observed unprotected. Vulnerability alerts and the minimal Actions
policy remained applied. The manifest preserves these as dated post-rollback
observations, distinct from both the first public window and final publication.

## Anonymous log diagnosis

Anonymous REST downloads of run, attempt, and job logs returned HTTP 403. The
then-current fail-closed protocol required rollback. Subsequent equivalent tests
against recent public runs in `actions/checkout`, `cli/cli`, and
`astral-sh/ruff` produced the same result.

The finding is **`GENERAL_GITHUB_ANONYMOUS_LOG_RESTRICTION`** and
**`PLATFORM_AMBIGUITY`**. No evidence connects it to the fact that EGX run
`29951087998` originated while private, and it is not an EGX_Terminal
vulnerability. Observed platform behavior conflicts with some GitHub REST
documentation wording; the record does not turn that contradiction into an
unsupported causal claim.

Historical run `29951087998`, including successful attempt 2 and its three jobs,
is retained as evidence. It must not be rerun, reused for retry, or deleted.

## Corrected public verification model

### Level A — anonymous internet

Without a GitHub account, verify repository API metadata, HTTPS clone, ZIP and
TAR archives, README, pull requests and commits, workflow run and job metadata,
tags and releases, and the ruleset when GitHub exposes it publicly. Anonymous
REST log downloads remain a test and must be compared with at least three
public control repositories.

A generalized HTTP 403 is `INFO` and `PLATFORM_AMBIGUITY`, not an absolute
blocker if Levels B and C pass.

### Level B — external GitHub account

Use a pre-existing account distinct from `ElGrandeXu`. It must have no
collaboration, invitation, team membership, or private permission. Verify access
to the Actions page, the content of all three jobs, and readable or downloadable
logs; then verify again that the account has no repository right. A Level B
failure is critical and requires rollback. No token for this account may enter
the repository or retained evidence.

### Level C — authenticated owner

Download and privacy-scan complete logs. Verify administrative controls, rules
and protections, alerts, and the absence of secrets, personal paths, and private
email. Retain no temporary signed URL.

## Safe GitHub API evidence

Collection uses an allowlist of required fields and never blindly serializes a
complete response. Before writing or displaying, exclude `temp_clone_token`,
authorization and cookie data, tokens, credentials, and temporary signed URLs.
Replace a signed URL with `[SIGNED_URL_REDACTED]`. Record only the presence and
name of a removed field, and hash only after sanitization.

Sanitized evidence becomes immutable. Do not intentionally retain a raw
original containing an active credential, and never silently sanitize evidence
already declared sealed. An accidentally dangerous capture is quarantined
privately, recorded only in redacted form, explicitly retained or destroyed,
and never published. The governance checker verifies these declarations; it is
not a general evidence scanner and does not inspect temporary directories.

GitHub's `temp_clone_token` field was briefly displayed in a private local
terminal. GitHub classifies it as a temporary clone credential. No public
exposure, misuse, or persistence in Git or Actions was detected, and the old
value is absent from retained evidence. Its exact TTL and revocation mechanism
are undocumented. The project therefore claims neither that it is active nor
that it expired, and does not assert `CREDENTIAL_ROTATION_REQUIRED` without new
evidence. Future captures exclude the field at collection time.

## Corrected protocol and final result

The one permitted corrected attempt required:

1. merge the governance pull request;
2. audit the resulting merged HEAD while private;
3. prepare the pre-existing Level B account;
4. verify the corrected collection and verification harness; and
5. confirm that no new blocker exists.

After public visibility and restoration of the verified public protections,
`.github/workflows/validate.yml` was dispatched on `main`. Public run
`30002915548` was created at `2026-07-23T11:23:01Z`, was recorded successful by
its `2026-07-23T11:26:08Z` update, and used `workflow_dispatch`, attempt 1, at
checkpoint `1d79ea37a1c614728cc7651c4d611218eaca174a`. The three named jobs and
Levels A, B, and C passed. The generalized anonymous HTTP 403 result remained
non-blocking `INFO` / `PLATFORM_AMBIGUITY`.

At final verification, the repository was public; PVR, secret scanning, push
protection, vulnerability alerts, and active no-bypass `main-protection` were
observed; and there were zero open pull requests, tags, releases, packages, or
forks. These are dated observations, not live claims by the offline checker.

Historical run `29951087998` remains retained and non-reusable. The corrected
attempt did not weaken protections or create a tag or release. `v1.0.1`,
including its SSH-signing gate, remains a separate later mission and is not
prepared.

## Validation boundary

The local gate covers the neutral root, public-surface heuristic, licensing, Git
history and refs, Markdown links, GitHub governance, tests, REUSE, JSON and TOML,
Git integrity, and preserved experimental hashes. It verifies file integrity,
not the missing source runtime observations governed by
[Decision 0014](../decisions/0014-micro-kernel-evidence-erratum.md). The first
transition and authorization for the corrected attempt are governed by
[Decision 0016](../decisions/0016-record-public-transition-rollback.md); the
verified final result is recorded in the schema 6 manifest.
