# Status

- **Phase:** **`PUBLICATION_TRANSITION`**. [Decision
  0015](decisions/0015-authorize-guarded-public-transition.md) authorizes a
  controlled public transition but does not assert that it has been applied.
  Effective visibility and protections must be verified directly on GitHub. The
  project is not shareable until post-public verification is complete;
  `v1.0.1` remains a separate later mission.
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
- **Pretransition audit:** on 2026-07-22, checkpoint
  `23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515` contained 41 commits on `main`.
  This is a historical count, not a current counter. Git content, pull requests,
  logs, workflows, and licenses were audited without a material leak being
  detected. F-001 closed after twelve authorized Packages surfaces returned
  HTTP 200 with zero packages.
- **Release state:** at that checkpoint, the canonical repository had no Git tag
  or published release. The transition forbids creating either. `v1.0.0` is a
  historical release withdrawn during privacy
  remediation; its former target, tag object, and release record exist only in
  verified private evidence. The terminal **`REJECT_MICRO`** governance verdict
  it documented remains unchanged; Decision 0014 records the limits of the
  preserved runtime evidence.
- **Local governance:** the release policy, neutral-surface registry, action
  lock, publication plan, hashed REUSE locks, hardened workflow, JSON/TOML, Git
  integrity, REUSE, link checks, and the full active test suite form the current
  gate.
- **Remote settings observed on 2026-07-22:** description, topics, issues, disabled
  projects/wiki/discussions/Pages, squash-only merge, branch cleanup, read-only
  Actions defaults, selected SHA-pinned actions, required full-SHA pinning, and
  vulnerability alerts were applied at the private checkpoint. Private
  Vulnerability Reporting was unavailable, secret scanning was disabled, and
  push protection was not active.
- **Ruleset and branch observed on 2026-07-22:** on the private GitHub Free
  repository, `main-protection` was unavailable and `main` was unprotected.
  Its desired pull-request, conversation-resolution, linear-history, named-check,
  deletion, and force-push rules remain recorded as target configuration only.
  That target has no bypass actor or role. Effective enforcement must be checked
  by API rather than inferred from this dated observation.
- **Repository status:** **`PUBLICATION_TRANSITION`**. The target visibility is
  public, authorization is recorded, and application is not claimed. The future
  mission must audit the merged HEAD, verify a private preflight, change
  visibility, activate and verify PVR immediately, apply and verify critical
  controls, and complete anonymous post-public checks. Failure of a critical
  control stops the mission and preserves the non-shareable status.
- **Email privacy:** the GitHub account setting is
  `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web operations require it
  to remain enabled and the scanner accepts no personal-address fallback.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

PR #2 and the recovery history remain part of the preserved incident record.
During `PUBLICATION_TRANSITION`, no tag or release may be created. Only a later,
separately authorized mission may prepare `v1.0.1`, satisfy the SSH-signing gate,
and create a tag or release.
