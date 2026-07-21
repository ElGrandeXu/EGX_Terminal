# Status

- **Phase:** V1 repository published with a neutral repository root and the
  protected pull-request path active; release review remains separate.
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
  to use the approved public GitHub ID-based `noreply` identity. The 34 commits
  predating the first protected pull request retain that canonical maintainer
  identity and zero private commit identity. Policy schema 2 accepts attributable
  GitHub `noreply` contributors and the exact GitHub web committer used for
  squash merges; it no longer demands artificial author uniformity. The
  [history audit](publication/HISTORY_AUDIT.md) and [remediation
  report](publication/IDENTITY_REMEDIATION.md) record the checks.
- **Governance commit:** the final local governance commit brought `main` to 32
  commits while retaining the same single author and committer identity.
- **Local governance:** PASS. Community files, deterministic link and GitHub
  governance controls, the action lock, publication plan, and hardened workflow
  are complete.
- **Private staging:** `ElGrandeXu/EGX_Terminal` was created privately and
  `main` received its first push. The failed staging runs were removed only
  after the amended corrective run passed all three required jobs.
- **CI defects discovered in staging:** the first run marked Windows and REUSE
  as passed while Ubuntu failed
  because the archive checker relied on platform-native `Path` ordering. Review
  of the Windows log also found that PowerShell continued after the history gate
  returned nonzero for the normal `origin/main` tracking ref, creating a false
  pass. The targeted correction derives relative POSIX paths with the locked
  canonical order, distinguishes publishable refs from transport refs, and runs
  the Windows validation block through fail-fast Bash.
- **Corrective commit:** the single authorized amend produced
  `ff2111f6b1f7e6ea0e295b2a997d19b1a1dbdd31` with 33 commits and the same parent
  and subject. Its private staging run passed `repository / ubuntu`,
  `repository / windows`, and `licensing / reuse`; Windows used Bash with
  `-e -o pipefail` and the history check accepted the Actions transport refs.
- **Publication status:** **`PUBLIC_V1_READY_FOR_RELEASE_REVIEW`**. The
  repository is public, anonymous validation passes, the second public CI passed
  all three required jobs, and the first protected pull-request correction is
  delivered without bypass. There were 34 reachable commits before that pull
  request. No tag or release exists.
- **Public entrypoint:** the root README is finalized and the local, deterministic
  [quickstart](QUICKSTART.md) has been created and validated.
- **Remote settings:** description, topics, issues/projects/wiki/discussions,
  merge policy, branch cleanup, read-only Actions token defaults, selected
  SHA-pinned actions, PVR, secret scanning, push protection, and vulnerability
  alerts are applied. Pages and auto-merge remain disabled.
- **Ruleset:** `main-protection` is active. Ordinary changes require a pull
  request, resolved conversations, linear history, and the three named checks;
  deletion and force-push are blocked. The administrator bypass remains reserved
  for recovery and is not used by the protected workflow.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The repository publication and protected pull-request path are complete. A
release remains a distinct, unauthorized future action. The next gate is an
explicit decision on whether to create `v1.0.0`.
