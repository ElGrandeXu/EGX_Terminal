# 0008 — Finalize public repository governance

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The neutral-root V1 has completed content, provenance, licensing, public-surface,
and history remediation. Before a first remote exists, it needs governance that
matches a single-maintainer research repository and a reproducible private
staging path.

## Decision

Governance remains maintainer-led. The repository adds concise governance,
contribution, and security policies; two purpose-built issue templates; and one
pull request template. A Code of Conduct is
`DEFERRED_UNTIL_ENFORCEABLE` until a confidential, non-personal reporting route
can support actual enforcement. SUPPORT, CODEOWNERS, CLA, DCO, generic feature
requests, funding, Dependabot, deployment, publication, and release automation
remain deferred.

A single validation workflow exposes three stable checks on Ubuntu and Windows.
It uses Python 3.11, REUSE 6.2.0, read-only contents permission, no secrets,
full Git history, and no persisted checkout credentials. External actions are
limited to official GitHub `checkout` and `setup-python`, pinned to full verified
commit SHAs recorded in a lock file. Local standard-library controls validate
Markdown links and the known V1 GitHub governance structure.

The first remote will be empty and private. Public visibility requires successful
CI, a clean remote clone, metadata and security configuration, and explicit
authorization. Private Vulnerability Reporting is a prerequisite. The planned
`main-protection` ruleset prevents deletion and force pushes, requires linear
pull-request history, conversation resolution, and all three checks. It requires
zero approvals for the sole maintainer and documents administrative recovery
bypass. Signed commits, Code Owner review, and strict up-to-date branches are not
required in V1.

## Consequences

The project gains portable Linux/Windows validation and an auditable publication
procedure without adding a runtime dependency or changing the neutral root.
Maintenance cost includes keeping action SHAs and their provenance current,
maintaining two deterministic controls, and revisiting settings when GitHub or
the contributor population changes.

Governance evolves through a new ADR. A Code of Conduct, broader review rules,
or additional automation is added only when an enforceable process and concrete
need justify it.
