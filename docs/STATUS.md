# Status

- **Phase:** `v1.0.0` is published and immutable; `main` prepares the `v1.0.1`
  post-release governance consolidation without adding product capability.
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
  quarantines the former staging repository privately. The 35th commit was
  reconstructed with the same tree, parent, complete message, dates, diff,
  paths, modes, and contents, using only approved `noreply` identities. The
  documentation commit brings the cleaned history to 36 commits.
- **Public-object boundary:** the canonical repository was newly created from
  the cleaned history with no object carrying the former metadata and no
  inherited pull request. The old staging repository is private, unarchived,
  retained as evidence, and must never become public.
- **Integrity:** the locked `kernel-v1` hash, both experimental archives, and the
  ten frozen Mission 24 results are unchanged. Private recovery bundles and the
  Mission 35 capture remain outside the repository.
- **Release:** `v1.0.0` is the stable, latest, immutable GitHub release. Annotated
  tag object `a5668506f38dfc73ec6d8236de00a6adad095e25` targets
  `870964a48fc07ff39d65c46255f189d25658ff2c`. The tag remains unchanged and is
  now accepted only through the declared release policy.
- **Local governance:** the release policy, neutral-surface registry, action
  lock, publication plan, hashed REUSE locks, hardened workflow, JSON/TOML, Git
  integrity, REUSE, link checks, and the full active test suite form the current
  gate.
- **Remote settings:** description, topics, issues, disabled
  projects/wiki/discussions/Pages, squash-only merge, branch cleanup, read-only
  Actions defaults, selected SHA-pinned actions, required full-SHA pinning, PVR,
  secret scanning, push protection, and vulnerability alerts are applied.
- **Ruleset:** `main-protection` is active on `main`. It requires a pull request,
  resolved conversations, linear history, and the three named checks; deletion
  and force-push are blocked. The administrator bypass is reserved for recovery.
- **Publication status:** **`PUBLIC_V1_RELEASED`**. The canonical repository is
  public and `v1.0.0` is immutable. `v1.0.1` is not published; its remaining
  release gate includes selecting and recording a durable SSH signing identity.
- **Email privacy:** the GitHub account setting is
  `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web operations require it
  to remain enabled and the scanner accepts no personal-address fallback.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The active gate is to merge the consolidation through the protected PR path,
then separately satisfy the recorded signing and release checks before any
`v1.0.1` tag is created.
