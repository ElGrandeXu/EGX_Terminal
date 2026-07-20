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
  16 384-token context, with one exact response and complete unload/cleanup. The
  OpenCode 1.17.9 provider and discovery path remain untested; the active root
  bootstrap is unchanged and no promotion has occurred.
- **Next step:** prepare an OpenCode 1.17.9 discovery probe with the validated
  loopback runtime, disposable storage/session behavior and loopback-only network
  containment; do not start behavioral evaluation or promotion.
