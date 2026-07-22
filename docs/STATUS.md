# Status

- **Phase:** canonical recovery is closed on a private repository with no Git
  tag or published release. PR 2 is the next step; `v1.0.1` is only the next
  candidate and has not been created.
- **Mission 24:** complete. Its final ten-cell campaign is closed and unchanged.
- **Final doctrine verdict:** **`REJECT_MICRO`**. Baseline used 229,923 tokens;
  micro used 247,972; overhead was 7.850019354305572%, above the frozen 5%
  ceiling. The earlier balanced candidate was already rejected.
- **Benchmark phase:** closed. No kernel adjustment, third variant, payload
  change, threshold reinterpretation, or further V1 doctrine benchmark is
  permitted.
- **V1 architecture:** [Decision 0005](decisions/0005-ship-v1-with-neutral-root.md)
  selects a neutral root with no automatically discovered harness instructions,
  active kernel, adapter, or hidden injection. Principles remain documented and
  protocols are selected explicitly on demand.
- **Historical evidence:** `experiments/kernel-v1/` and
  `experiments/kernel-micro-v1/` remain immutable inactive archives.
- **Licensing:** [Decision 0006](decisions/0006-adopt-file-scoped-apache-and-cc-licensing.md)
  remains accepted. `REUSE.toml` gives every tracked non-exempt file exactly one
  effective license; the dependency-free checker and `reuse 6.2.0` pass.
- **Initial identity remediation:** 30 prepublication commits were rewritten
  once to the approved GitHub ID-based `noreply` identity, with their trees,
  messages, dates, parents, diffs, paths, and modes preserved.
- **Public metadata incident:** after the first squash merge, the identity gate
  detected a personal author address in the 35th public commit and correctly
  blocked Ubuntu and Windows CI. At that incident point the repository had no
  tag, release, or fork.
- **Repository recreation:** [Decision 0010](decisions/0010-recreate-public-repository-after-email-exposure.md)
  records the private replacement of the affected repository. The functional commit was
  reconstructed with the same tree, parent, complete message, dates, diff,
  paths, modes, and contents, using only approved `noreply` identities. The
  recovery-closing documentation brings the clean history to 38 commits.
- **Canonical-object boundary:** the canonical repository was newly created from
  the cleaned history with no object carrying the former metadata and no
  inherited pull request. Temporary recovery repositories were deleted only
  after verified private local backups were retained outside this repository.
- **Integrity:** the locked `kernel-v1` hash, both experimental archives, and the
  ten frozen Mission 24 results are unchanged. Private recovery bundles and the
  Mission 35 capture remain outside the repository.
- **Release state:** the canonical repository has no Git tag and no published
  release. `v1.0.0` is a historical release withdrawn during privacy
  remediation; its former target, tag object, and release record exist only in
  verified private evidence. The experimental conclusions it documented remain
  unchanged.
- **Local governance:** the release policy, neutral-surface registry, action
  lock, publication plan, hashed REUSE locks, hardened workflow, JSON/TOML, Git
  integrity, REUSE, link checks, and the full active test suite form the current
  gate.
- **Remote settings:** description, topics, issues, disabled
  projects/wiki/discussions/Pages, squash-only merge, branch cleanup, read-only
  Actions defaults, selected SHA-pinned actions, required full-SHA pinning, and
  vulnerability alerts are applied. Private Vulnerability Reporting is
  unavailable while private, secret scanning is disabled, and push protection
  is not active.
- **Ruleset and branch:** on the private GitHub Free repository,
  `main-protection` is unavailable on the current plan and `main` is unprotected.
  Its desired pull-request, conversation-resolution, linear-history, named-check,
  deletion, and force-push rules remain recorded as target configuration only.
  Pull requests are a mandatory project convention, not an active GitHub
  protection.
- **Repository status:** **`PRIVATE_RECOVERY_CLOSED`**. The canonical repository
  remains private, has no tag, release, or pull request, and is ready for PR 2.
  `v1.0.1` is not published; its release gate still includes selecting and
  recording a durable SSH signing identity.
- **Email privacy:** the GitHub account setting is
  `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web operations require it
  to remain enabled and the scanner accepts no personal-address fallback.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The active gate is PR 2 under the mandatory project pull-request convention.
The remote controls, including Private Vulnerability Reporting, must be
re-evaluated before public publication. Only a later, separately authorized
mission may satisfy the signing gate and create a `v1.0.1` tag or release.
