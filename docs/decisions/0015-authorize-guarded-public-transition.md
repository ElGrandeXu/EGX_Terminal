# 0015 — Authorize a guarded public transition

- **Status:** accepted
- **Date:** 2026-07-22

## Context

Decision 0013 correctly kept the canonical repository private for the phase it
observed and correctly separated desired GitHub controls from controls actually
available on the private GitHub Free repository. Its observations and rationale
remain historical facts.

The prepublication audit closed on 2026-07-22 at checkpoint
`23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515`, then 41 commits on `main`. That
count describes this historical checkpoint only; it is never a permanent
counter for the current branch or repository. Git content, pull requests, logs,
workflows, and licenses were audited without a material leak being detected.

Finding F-001 also closed on 2026-07-22: all twelve authorized GitHub Packages
surfaces returned HTTP 200 and reported zero packages.

## Decision

Authorize a controlled transition of `ElGrandeXu/EGX_Terminal` to public
visibility. This decision authorizes the future transition mission; it does not
assert that the visibility change or any target control has already been
applied. Until the post-public verification report is complete, the durable
phase is **`PUBLICATION_TRANSITION`** and the project is not considered
shareable. Effective visibility and protections must be read directly from
GitHub rather than inferred from repository documentation.

The transition mission must first audit the merged `main` HEAD. It must then
verify that the repository is private at preflight, change visibility to public,
activate Private Vulnerability Reporting immediately, and mechanically verify
that confidential reporting is accessible. No confidential reporting channel
is claimed before that activation, and no personal address may be published as
a fallback.

The same atomic mission must apply and verify the target public controls,
including `main-protection`, secret scanning, push protection when available,
vulnerability alerts, minimal Actions permissions, prudent fork-workflow
permissions, and anonymous post-public access. If a critical protection cannot
be applied or verified, the mission must stop safely and retain the explicit
non-shareable status.

`main-protection` must require pull requests, linear history, conversation
resolution, and the checks `repository / ubuntu`, `repository / windows`, and
`licensing / reuse`. It must not require an up-to-date branch, approvals, signed
commits, or Code Owners. It must prohibit deletion and force-push and provide no
bypass actor or role. The historical direct recovery push remains an archived
fact, not a future configuration or precedent.

No tag or GitHub release may be created during the transition. Candidate
`v1.0.1`, including its SSH-signing gate, remains a separate later mission.

## Evidence

- The checkpoint SHA and its 41-commit `main` history were verified locally and
  against `origin/main` on 2026-07-22 with `+0/-0` divergence.
- The repository visibility was observed as private at that checkpoint.
- The prepublication content, pull-request, log, workflow, and license audits
  found no material leak.
- Twelve authenticated and owner-scoped Packages GET surfaces returned HTTP 200
  with zero packages, closing F-001.
- Decision 0013 preserves the dated evidence for controls unavailable or
  inactive during the observed private phase.

## Consequences

Decision 0013 is superseded only for its current choice to remain private. Its
historical observations and justification are preserved in full. Documentation
and schema 5 now distinguish the public target, the dated private observation,
the authorization that is not yet applied, and current GitHub state that must be
verified by API.

This decision changes no experimental file, result, protocol, or verdict.
`REJECT_MICRO`, the neutral-root result, and Decision 0014 remain unchanged.

## Revision triggers

Revisit this decision if the post-merge HEAD audit finds a material leak; if the
repository is not private at transition preflight; if PVR, the no-bypass ruleset,
or another critical protection cannot be applied or verified; if anonymous
post-public checks fail; or before any tag, release, or `v1.0.1` preparation.
