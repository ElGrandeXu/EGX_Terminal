# Status

- **Phase:** V1 public-distribution preparation with a neutral repository root.
- **Mission 24:** complete. Its final ten-cell campaign is closed and unchanged.
- **Final doctrine verdict:** **`REJECT_MICRO`**. Baseline used 229,923 tokens;
  micro used 247,972; overhead was 7.850019354305572%, above the frozen 5%
  ceiling. The earlier balanced candidate was already rejected.
- **Benchmark phase:** closed. No kernel adjustment, third variant, payload
  change, threshold reinterpretation, or further V1 doctrine benchmark is
  permitted.
- **V1 architecture:** [Decision 0005](decisions/0005-ship-v1-with-neutral-root.md)
  selects a neutral root with no automatically discovered harness instructions,
  active kernel, adapter, or hidden injection. Principles remain in documentation
  and protocols are selected explicitly on demand.
- **Historical evidence:** `experiments/kernel-v1/` and
  `experiments/kernel-micro-v1/` are immutable experimental archives; neither is
  active doctrine.
- **Publication boundary:** inspected and documented. The active tracked surface
  has no observed blocking violation; the public-surface and neutral-root checks
  pass. Historical runtime, model, loopback, hash, and machine-capacity facts in
  the immutable archives are documented exceptions, not active dependencies.
- **Licensing:** [Decision 0006](decisions/0006-adopt-file-scoped-apache-and-cc-licensing.md)
  is accepted. Original functional artifacts use Apache-2.0; original
  documentation and research use CC-BY-4.0. `REUSE.toml` covers every tracked,
  non-exempt file with exactly one effective license and no third-party exception.
- **License validation:** the dependency-free local control and the official
  `reuse 6.2.0` linter pass on 2026-07-21 against REUSE Specification 3.3.
- **Git history:** 30 historical commits were rewritten once before publication
  to use the approved public GitHub ID-based `noreply` identity. The single
  remediation commit brings `main` to 31 commits, one identity, zero merge, and
  zero private commit identity. The [history audit](publication/HISTORY_AUDIT.md)
  and [remediation report](publication/IDENTITY_REMEDIATION.md) record the checks.
- **Governance commit:** the final local governance commit brings `main` to 32
  commits while retaining the same single author and committer identity.
- **Local governance:** PASS. Community files, deterministic link and GitHub
  governance controls, the action lock, publication plan, and hardened workflow
  are complete.
- **Private staging:** `ElGrandeXu/EGX_Terminal` has been created privately and
  `main` has received its first push. No public visibility, tag, or release was
  created.
- **First remote CI:** GitHub marked Windows and REUSE as passed; Ubuntu failed
  because the archive checker relied on platform-native `Path` ordering. Review
  of the Windows log also found that PowerShell continued after the history gate
  returned nonzero for the normal `origin/main` tracking ref, creating a false
  pass. The targeted correction derives relative POSIX paths with the locked
  canonical order, distinguishes publishable refs from transport refs, and runs
  the Windows validation block through fail-fast Bash. Its new remote run is not
  claimed as passing before the corrective push.
- **Corrective commit:** the single authorized CI correction brings local `main`
  to 33 commits; its remote status remains pending until push and a fresh run.
- **Publication status:** **`PRIVATE_REMOTE_STAGING_CI_REMEDIATION`**. Public
  visibility remains forbidden until all three checks pass on the corrective
  commit and the remaining private staging settings are reviewed.
- **Public entrypoint:** the root README is finalized and the local, deterministic
  [quickstart](QUICKSTART.md) has been created and validated.
- **Public preparation:** `origin` exists and remains private. The next gate is
  a fully green CI run on the corrective commit; security settings, ruleset,
  metadata, public visibility, tags, and releases remain unapplied.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The current phase is private remote staging. This status does not authorize a
public visibility change.
