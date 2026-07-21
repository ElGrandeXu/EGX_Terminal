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
- **Publication status:** **`READY_WITH_DOCUMENTED_EXCEPTIONS`** for the inspected
  repository contents. This is a bounded heuristic result, not an absolute
  guarantee that no sensitive data can exist.
- **Public entrypoint:** the root README is finalized and the local, deterministic
  [quickstart](QUICKSTART.md) has been created and validated.
- **Public preparation:** there is still no Git remote and no push has occurred.
  The next gate is Maxime's explicit license choice; repository creation and
  publication remain separate work.
- **Deferred capabilities:** memory, hooks, skills, routing, compression, and
  other advanced capabilities remain unimplemented and require demonstrated need
  plus a separate decision.

The next phase records Maxime's explicit license choice without reactivating a
doctrine or expanding optional capabilities.
