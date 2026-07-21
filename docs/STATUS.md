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
- **Git history:** all commits, trees, blobs, refs, messages, and identities
  reachable from `main` have been inspected. No content blocker was observed,
  but the [history audit](publication/HISTORY_AUDIT.md) classifies the sole
  non-`noreply` author/committer address as **`REVIEW_REQUIRED`**.
- **Publication status:** **`HISTORY_REVIEW_REQUIRED_BEFORE_PUBLICATION`**. The
  content, licensing, and provenance gates are clear; Maxime must explicitly
  accept the masked historical email exposure before final governance review.
  The security result remains a bounded heuristic, not an absolute guarantee.
- **Public entrypoint:** the root README is finalized and the local, deterministic
  [quickstart](QUICKSTART.md) has been created and validated.
- **Public preparation:** there is still no Git remote and no push has occurred.
  The next gate is the explicit history-identity decision. Final governance
  review and GitHub publication preparation remain separate later work.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The next phase records Maxime's decision on the historical and future commit
identity, without rewriting history or beginning publication in this phase.
