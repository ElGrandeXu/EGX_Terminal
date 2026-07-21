# 0009 — Publish the V1 repository

- **Status:** accepted
- **Date:** 2026-07-21

## Context

V1 had a neutral root, frozen experimental evidence, file-scoped licensing, one
canonical maintainer identity across its prepublication history, local
governance controls, and a private
staging repository. Publication required proof that the remote workflow behaved
consistently across Ubuntu and Windows without weakening the history scanner.

## Decision

Publish `ElGrandeXu/EGX_Terminal` after a green amended staging run and an
anonymous public clone validation. Keep repository publication separate from a
release: create no tag or GitHub release. Activate the planned `main-protection`
ruleset only after the final documentation commit passes the three public jobs.

## Evidence

Private staging exposed platform-dependent archive ordering, incorrect treatment
of remote-tracking refs, missing Windows fail-fast behavior, and a complete
authenticated-URL fixture in tracked test source. The targeted correction kept
the locked archive hash, distinguished transport refs, selected Bash
`-e -o pipefail`, and constructed the fixture only inside a temporary Git
repository while retaining detection and redaction assertions.

The amended 33rd commit passed `repository / ubuntu`, `repository / windows`,
and `licensing / reuse`. Failed staging runs were then removed. Remote metadata,
features, merge policy, and read-only Actions policy were applied. After the
authorized visibility change, Private Vulnerability Reporting, secret scanning,
push protection, and vulnerability alerts were verified active. An anonymous
clone passed the local controls, 134 tests, REUSE, actionlint, identity and
history checks, and frozen-integrity checks.

The 34th commit then passed the same three checks publicly. The
`main-protection` ruleset was activated with the required pull-request path,
conversation resolution, linear history, deletion and force-push protection,
and the three named checks. The identity and ref-policy correction is delivered
through the first protected pull request without administrative bypass; it
preserves the 34 existing commits while supporting GitHub `noreply`
contributors and the exact GitHub web committer used by squash merges.

## Consequences

The repository is public and inspectable. The private recovery bundle remains
outside the repository. No release exists, and no compatibility is promised
beyond the measured combinations and preserved evidence. The second public CI
and ruleset activation are complete. The repository status is
`PUBLIC_V1_READY_FOR_RELEASE_REVIEW`; the remaining gate is a separate explicit
decision on `v1.0.0`, not an automatic tag or release.

## Revision triggers

Revisit this decision if a private artifact or unapproved identity becomes
reachable, a required public check fails persistently, a security protection is
disabled, the repository boundary changes materially, or a separately
authorized release requires a new evidence review.
