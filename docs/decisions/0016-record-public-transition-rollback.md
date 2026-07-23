# 0016 — Record the first public transition and rollback

- **Status:** accepted
- **Date:** 2026-07-23

## Context

Decision 0015 authorized one atomic public transition from the canonical
checkpoint `c887949cbc3c6fe8aade34b2675b39545c365905`. The private preflight found
42 linear commits, no open pull request, tag, release, package, or fork, and
returned `PUBLICATION_READY` only for that bounded atomic mission.

The repository became public at `2026-07-23T08:02:57.4503878Z`. Rollback to
private visibility completed at `2026-07-23T08:34:32.3856142Z`, after
approximately 31 minutes and 35 seconds. Repository ID `1308085094`, default
branch `main`, checkpoint SHA, and repository content remained unchanged. No
material leak was detected. That observation cannot prove that no third party
viewed or copied the public surface during the exposure.

During the public window, Private Vulnerability Reporting was active and
verified; ruleset `main-protection` was active with no bypass; secret scanning,
push protection, and vulnerability alerts were active; the Actions policy
remained minimal; and approval was required for all external contributors. The
three checks `repository / ubuntu`, `repository / windows`, and
`licensing / reuse` succeeded. Zero secret-scanning alerts, packages, tags,
releases, or forks were observed. After rollback, controls that GitHub Free does
not provide for private repositories became unavailable or inactive again.

The protocol then in force treated anonymous REST log download as a critical
public-access gate. Anonymous downloads of run, attempt, and job logs returned
HTTP 403, so rollback was mandatory. Later controls against public runs in
`actions/checkout`, `cli/cli`, and `astral-sh/ruff` returned the same behavior.
The result is classified `GENERAL_GITHUB_ANONYMOUS_LOG_RESTRICTION` and
`PLATFORM_AMBIGUITY`. The evidence does not connect the result to the private
origin of EGX run `29951087998`; it also conflicts with some wording in current
GitHub REST documentation. This is not classified as an EGX_Terminal
vulnerability.

During private local diagnosis, GitHub's `temp_clone_token` field was briefly
displayed. GitHub defines it as a temporary credential for cloning. No public
exposure, malicious use, or persistence in Git or Actions was detected, and the
old value is absent from retained evidence. Its exact TTL and revocation
mechanism are undocumented, so this project proves neither that the value
expired nor that it remains active. It does not assert
`CREDENTIAL_ROTATION_REQUIRED` without additional evidence. The durable
correction is to exclude credential-like fields at collection time, before any
write or display. This is an evidence-bounded governance decision, not a
general guarantee about GitHub tokens.

## Decision

Adopt **`PUBLICATION_RETRY_PREPARATION`** as the durable phase. The repository is
currently private, the first transition was executed and rolled back, the
project is not shareable, and a second transition has not been applied.

At most one further public transition is conditionally authorized. It may occur
only after this pull request is merged, the merged HEAD passes a new private
audit, a pre-existing Level B account is prepared, the corrected harness is
verified, and no new blocker exists. A third attempt requires a new ADR.

Public verification is divided into three levels:

1. **Level A — anonymous internet without a GitHub account.** Verify repository
   API metadata, HTTPS clone, ZIP and TAR archives, README, pull requests and
   commits, workflow run and job metadata, tags and releases, and the ruleset
   when GitHub exposes it publicly. Retest anonymous REST log downloads against
   EGX and public controls. A generalized HTTP 403 is `INFO` and
   `PLATFORM_AMBIGUITY`, not an absolute blocker when Levels B and C pass.
2. **Level B — external GitHub account.** Use a pre-existing account distinct
   from `ElGrandeXu`, with no collaboration, invitation, team, or private
   permission. Verify the Actions page, all three jobs, and readable or
   downloadable logs, then verify again that the account received no repository
   right. Store no account token in the repository or retained evidence. A
   Level B failure is critical and requires rollback.
3. **Level C — authenticated owner.** Download and privacy-scan complete logs;
   verify administrative controls, rules and protections, alerts, and the
   absence of secrets, personal paths, and private email; retain no temporary
   signed URL.

The next public attempt must dispatch `.github/workflows/validate.yml` on
`main` through `workflow_dispatch`, consume the API response fields
`workflow_run_id`, `run_url`, and `html_url`, and obtain a new run ID created
after public visibility. It must verify the same three named jobs. Historical
run `29951087998` remains evidence: it must not be rerun, reused, or deleted.
No empty commit or temporary branch may be created for dispatch.

API evidence collection must use an allowlist and must never blindly serialize
a complete GitHub response. Before writing or displaying, exclude
`temp_clone_token`, authorization and cookie data, tokens, credentials, and
temporary signed URLs. Replace a signed URL with `[SIGNED_URL_REDACTED]`;
record only the presence and name of a removed field; hash only after
sanitization; and make sanitized evidence immutable. Do not intentionally keep
a raw original containing an active credential, and never silently sanitize
evidence already declared sealed. An accidentally dangerous capture must be
quarantined privately, recorded in redacted form, explicitly retained or
destroyed, and never published.

No tag, release, `v1.0.1` preparation, or weakening of protections is authorized
by this decision.

## Evidence

- Canonical checkpoint: `c887949cbc3c6fe8aade34b2675b39545c365905`
  with 42 linear commits.
- Public exposure: `2026-07-23T08:02:57.4503878Z` through
  `2026-07-23T08:34:32.3856142Z`.
- Historical Actions evidence: run `29951087998`, attempt 2, completed
  successfully with the three required jobs.
- Public control repositories: `actions/checkout`, `cli/cli`, and
  `astral-sh/ruff`.
- Machine-readable record:
  [`github-publication-plan.json`](../../governance/github-publication-plan.json),
  schema 6.

Schemas 4 and 5 remain valid historical records for their respective audit and
pretransition phases; schema 6 records the later execution, rollback, and
conditional retry state.

## Consequences

The first public exposure and its irreversible uncertainty are permanent audit
facts. Anonymous REST log HTTP 403 alone no longer forces rollback when it is
generalized by controls and Levels B and C pass. Level B failure remains
critical. The repository remains private and non-shareable until every gate of
the single conditional retry succeeds.

The incident remains a bounded publication-governance result. It does not add a
generic GitHub security framework, evidence scanner, workflow, agent capability,
or experimental claim.

## Revision triggers

Reconsider this decision if GitHub documents or changes anonymous log access,
if evidence establishes a repository-specific restriction or credential
exposure, if Level B cannot read the public logs without collaboration, if a
new blocker appears, or before any third public-transition attempt.
