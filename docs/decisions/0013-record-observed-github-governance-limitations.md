# 0013 — Record observed GitHub governance limitations

- **Status:** superseded in part by 0015
- **Date:** 2026-07-22

Decision 0015 supersedes only this record's current choice to keep the
repository private. The observations, evidence, rationale, and private-phase
limitations below remain the historical record of the state audited on
2026-07-22.

## Context

Canonical recovery is closed, and the sole repository remains private on the
GitHub Free plan. The repository documentation and machine-readable publication
plan still described the desired security and branch controls as active. A
read-only remote audit showed that those claims did not match the effective
GitHub state.

The desired controls remain appropriate for a future public repository, but
their target configuration and present availability are different facts. Local
governance must preserve that distinction without weakening the project or
claiming enforcement that GitHub does not provide in the current configuration.

## Decision

Keep `ElGrandeXu/EGX_Terminal` private and remain on GitHub Free. Do not change
remote settings, upgrade the plan, or simulate unavailable protections in local
documentation.

Use schema 4 of `governance/github-publication-plan.json` to record, separately,
the desired state, observed state, plan or visibility limitation, application
status, and dated GET evidence for each affected control. The overall remote
status is `PARTIALLY_APPLIED`.

Retain the complete desired `main-protection` configuration as a target only.
Until publication is reconsidered, contributors must use pull requests as a
mandatory project convention. This procedural discipline is not represented as
GitHub branch protection: `main` is unprotected and the ruleset is not applied.

Before any change to public visibility, re-audit every remote control and enable
and verify Private Vulnerability Reporting. Secret scanning, push protection,
branch protection, and the desired ruleset must also be reconsidered against the
plan and visibility that will apply at that time.

## Evidence

The 2026-07-22 audit observed:

- `GET /repos/ElGrandeXu/EGX_Terminal/rulesets` returned HTTP 403 because the
  feature requires GitHub Pro or public visibility;
- `GET /repos/ElGrandeXu/EGX_Terminal/branches/main` returned HTTP 200 with the
  branch unprotected, while its protection endpoint returned HTTP 403 under the
  same plan limitation;
- the secret-scanning alerts GET returned HTTP 404 and identified secret
  scanning as disabled;
- the repository settings audit observed push protection as not active;
- the Private Vulnerability Reporting GET returned HTTP 404 while the repository
  was private; and
- the vulnerability-alerts GET returned HTTP 204, confirming security alerts
  remain active.

These are observations of current remote state, not mutative API results or
proof that the desired controls were applied.

## Consequences

Current documentation no longer overstates GitHub enforcement. The governance
checker rejects schema 3, false active or protected observations, unavailable
controls counted as applied, and global success that hides plan limitations.

The repository accepts the operational limitation of an unprotected `main`
while it remains private and single-maintainer. The mandatory pull-request path,
local validation suite, clean-history checks, and explicit commit discipline are
the procedural safeguards during this period. They reduce risk but are not
equivalent to remote enforcement.

The historical recovery evidence and experimental conclusions are unchanged.
No tag, release, pull request, visibility change, plan change, or GitHub settings
mutation is authorized by this decision.

## Revision triggers

Revisit this decision before public publication; when the repository plan or
visibility changes; when GitHub changes control availability; before adding a
maintainer with direct push access; or if the observed GET results no longer
match schema 4. Any revision must re-establish the desired/observed distinction
from fresh read-only evidence before changing remote enforcement.
