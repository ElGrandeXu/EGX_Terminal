# Status

- **Phase:** canonical recovery is closed on a private repository with no Git
  tag or published release. PR #2 is complete and merged; the next gate is the
  final pre-publication audit. `v1.0.1` remains only the next candidate and has
  not been created.
- **Mission 24:** complete. Its final governance campaign is closed.
- **Final doctrine verdict:** **`REJECT_MICRO`**. The historical report publishes
  totals of 229,923 tokens for the baseline and 247,972 for the micro, with an
  overhead of 7.850019354305572% above the frozen 5% ceiling. These values remain
  internally arithmetically checkable, but the original aggregate and source
  runtime data are irrecoverable; [Decision 0014](decisions/0014-micro-kernel-evidence-erratum.md)
  governs their interpretation. The earlier balanced candidate was already
  rejected.
- **Benchmark phase:** closed. No kernel adjustment, third variant, payload
  change, threshold reinterpretation, or further V1 doctrine benchmark is
  permitted.
- **V1 architecture:** [Decision 0005](decisions/0005-ship-v1-with-neutral-root.md)
  selects a neutral root with no automatically discovered harness instructions,
  active kernel, adapter, or hidden injection. Principles remain documented and
  protocols are selected explicitly on demand.
- **Historical record:** `experiments/kernel-v1/` and
  `experiments/kernel-micro-v1/` remain immutable inactive archives. For the
  micro-kernel, preserved definition artifacts are directly auditable, while
  published runtime claims are not independently verifiable from source data.
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
  recovery-closing documentation preserved that clean history. The PR #2
  squash-merge commit `c708bc6af88b5e98a08fc801e476d4c16248e701`
  established the 40-commit canonical recovery checkpoint.
- **Canonical-object boundary:** the canonical repository was newly created from
  the cleaned history with no object carrying the former metadata and no
  inherited pull request. Temporary recovery repositories were deleted only
  after verified private local backups were retained outside this repository.
- **Integrity:** the locked `kernel-v1` hash, both experimental archives, and the
  ten files listed under `frozen_files` in the [Mission 24
  manifest](../experiments/kernel-micro-v1/behavioral/final-v1/manifest.json) are
  unchanged. Private recovery bundles and the Mission 35 capture remain outside
  the repository.
- **Release state:** the canonical repository has no Git tag and no published
  release. `v1.0.0` is a historical release withdrawn during privacy
  remediation; its former target, tag object, and release record exist only in
  verified private evidence. The terminal **`REJECT_MICRO`** governance verdict
  it documented remains unchanged; Decision 0014 records the limits of the
  preserved runtime evidence.
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
  remains private and has no tag or release. `v1.0.1` is not published. The
  final pre-publication audit is the next gate; only afterward may separate
  preparation select and record a durable SSH signing identity for the
  candidate release.
- **Email privacy:** the GitHub account setting is
  `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web operations require it
  to remain enabled and the scanner accepts no personal-address fallback.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

PR #2 is complete and merged. The active gate is the final pre-publication
audit, including re-evaluation of remote controls and Private Vulnerability
Reporting before public publication. Only a later, separately authorized
mission may prepare `v1.0.1`, satisfy the SSH signing gate, and create a tag or
release.
