# Status

- **Phase:** architecture formalized; experimental kernel quarantined and inactive.
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
  OpenCode emitted invalid JSONL before any Qwen request. There was no retry and
  cleanup was complete. This validates the machine-specific material margin,
  not the real OpenCode + Qwen path. The active root bootstrap is unchanged and
  no promotion has occurred.
- **Next step:** do not rerun inference or promote the kernel. A separately
  authorized mission would first need to explain the pre-provider OpenCode JSONL
  failure without assuming the measured 3 GiB gate generalizes to other hosts.
