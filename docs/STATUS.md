# Status

- **Phase:** architecture formalized; balanced kernel rejected and archived;
  static micro candidate experimental and inactive.
- **Research corpus:** five independent audits and cross-repository synthesis
  complete.
- **Synthesis:** `docs/research/synthesis/` contains the decision dossier.
- **Decision:** six functional layers plus external governance adopted as the
  architecture; no behavioral doctrine or optional capability promoted.
- **Experiment:** `experiments/kernel-v1/` contains the measured candidate, the
  adapter contract, a validated static-distribution prototype, and a six-case
  Codex CLI 0.144.6 runtime-discovery validation in disposable fixtures. A
  separate Ollama 0.20.2 smoke test validated local `qwen3.6:35b` at an effective
  16 384-token context, with one exact response and complete unload/cleanup. A
  first isolated OpenCode 1.17.9 smoke run then failed locally with exit code 1
  before any model request or JSONL event. A no-inference diagnostic established
  that an unsupported inline `subagent_depth` key caused the pre-provider exit.
  After the minimal repair, a disposable loopback mock run validated the exact
  configured model, one exact kernel occurrence, zero tools and final JSONL
  `MOCK_OK`, with complete cleanup. The official dense `qwen3.6:27b` Q4_K_M is
  now installed alongside the unchanged 35B, and the probes use a two-profile
  experimental registry. A single 27B load at 16 384 tokens left only 549 MiB
  VRAM, so the 3 GiB gate blocked before OpenCode: zero Qwen requests and complete
  cleanup. A separate authorized run then reserved 4 GiB per GPU through the
  owned child server only. The resulting 55/65 GPU-layer split left 3 683 MiB
  VRAM, 413 MiB below the strict 4 GiB gate, so it also blocked before OpenCode:
  zero Qwen requests, no retry and complete cleanup. The measured decision now
  keeps the 4 GiB requested reservation but uses a 3 GiB hard gate, with 4 GiB
  retained as the comfort target. The unique final run passed that gate at
  3 550 MiB free with the same 55/65 GPU-layer split, then failed because
  OpenCode emitted invalid JSONL before any Qwen request. Mission 18 instrumented
  the binary streams and proved that line was an OpenCode error log caused by a
  stale Python default: the active configuration declared the 27B while the CLI
  still requested the 35B. Resolving the model at call time made the real provider
  path succeed with OpenCode exit 0 and one Qwen request. A second run then spent
  its 64-token output budget before visible text because `think:false` did not
  follow Ollama's OpenAI-compatible contract. Replacing it with
  `reasoningEffort:"none"`, validated on the mock as `reasoning_effort:"none"`,
  produced real text with zero reasoning. That text still omitted punctuation and
  exceeded the requested eight words. That mission therefore retained its
  historical terminal result **BLOCKED**, not PASS, after the authorized maximum
  of three Ollama starts and two Qwen requests. Cleanup was complete throughout.
  The final compatibility resolution now separates proof levels: static
  distribution is **PASS**; Codex CLI 0.144.6 distribution/discovery is **PASS**;
  OpenCode 1.17.9 distribution/discovery against the mock is **PASS**; and the
  real OpenCode → Ollama → `qwen3.6:27b` path is **PASS** for runtime transport.
  Exact canary adherence is **FAIL**. Behavioral effectiveness now has a terminal
  result for the balanced candidate. The first pre-registered pilot remained a
  four-cell null result. The decisive counterbalanced challenge then consumed 12
  runs over six harder fixtures, with zero behavioral retry. Eleven observations
  are available; `reuse-baseline` was lost after scoring during a Windows cleanup
  failure, consumed and never replayed. On the five complete pairs, the kernel
  produced zero primary win and the baseline two. The baseline won verification
  proportionality and transversal completeness; in the latter, the kernel
  modified a visible test, failed functional/scope criteria and declared success.
  This observed functional baseline win independently satisfies the frozen
  rejection threshold: **REJECTED_AS_BALANCED**. A local-package grader false
  positive was corrected and regression-tested without changing the verdict.
  Runtime portability remains **SUPPORTED — EXPERIMENTAL**, OpenCode + Qwen is
  not blocked, and the measured 3 GiB gate remains host-specific. The active root
  bootstrap is unchanged and no kernel promotion occurred. See the
  [runtime compatibility summary](../experiments/kernel-v1/validation/runtime-compatibility-summary.md),
  the [first pilot](../experiments/kernel-v1/behavioral/pilot-v1/results.md), and
  the [decisive challenge](../experiments/kernel-v1/behavioral/challenge-v1/results.md).
  [Decision 0003](decisions/0003-balanced-kernel-rejection.md) now closes that
  exact balanced payload as rejected and preserves `experiments/kernel-v1/` as
  an immutable historical archive. `experiments/kernel-micro-v1/` defines a
  substantively distinct static candidate only. It remains unchanged, inactive,
  unpromoted and behaviorally unvalidated. Its
  [final protocol](../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md)
  is now pre-registered with five new fixtures, ten cells, frozen hashes,
  automated scoring and a strictly binary verdict. No inference, runtime or
  benchmark has been launched, and no micro behavioral result exists. No
  doctrine is promoted and the active root remains unchanged.
- **Next step:** execute exactly the frozen micro campaign without adjusting the
  payload or protocol, then apply its terminal `PROMOTE_MICRO` or `REJECT_MICRO`
  verdict.
