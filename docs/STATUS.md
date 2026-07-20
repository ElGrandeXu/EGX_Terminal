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
  zero Qwen requests, no retry and complete cleanup. This validates profile
  selection, loading, child-only allocation and the safety gate, not the real
  OpenCode + Qwen path. The active root bootstrap is unchanged and no promotion
  has occurred.
- **Next step:** decide, without loading a model, between a smaller official
  local candidate and a separately authorized CPU/GPU policy; do not rerun the
  4 GiB reservation, adjust automatically to 5 or 6 GiB, start behavioral
  evaluation or promote the kernel.
