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
  After the minimal repair, one disposable loopback mock run validated the exact
  configured model, one exact kernel occurrence, zero tools and final JSONL
  `MOCK_OK`, with complete cleanup. This validates OpenCode request construction
  and transport only; the OpenCode + Qwen smoke remains unvalidated. The active
  root bootstrap is unchanged and no promotion has occurred.
- **Next step:** conditionally retest the single OpenCode 1.17.9 + local Qwen smoke
  under a separate inference authorization and the existing one-request/no-retry
  guards; do not start behavioral evaluation or promote the kernel.
