# EGX_Terminal

EGX_Terminal explores how a terminal-agent workspace can keep its behavior,
knowledge, project state, and methods in the repository while allowing the active
LLM, provider, or terminal harness to be replaced.

The project is LLM-agnostic. Its V1 will ship with a neutral root: it does not
install any automatically discovered behavioral instruction for Codex, Claude
Code, OpenCode, or another compatible harness, and it imposes no always-on
behavioral doctrine.

The five external-repository audits and the architecture synthesis are complete.
Two candidate kernels were then evaluated independently and rejected as V1
always-on doctrine:

- [`experiments/kernel-v1/`](experiments/kernel-v1/) archives the rejected
  balanced candidate and its evidence;
- [`experiments/kernel-micro-v1/`](experiments/kernel-micro-v1/) archives the
  rejected micro candidate and its final `REJECT_MICRO` result.

Project principles remain available in documentation and may be used through
explicitly selected, on-demand protocols. Advanced capabilities such as memory,
hooks, skills, routing, and compression remain optional and unimplemented unless
a demonstrated need and a separate decision justify them.

Preparation of the public distribution is in progress. The final public README,
license choice, remote repository, and publication are separate future steps.

See [the charter](docs/CHARTER.md) for the project boundaries and
[the current status](docs/STATUS.md) for the latest project state. Consequential
choices are recorded in the [decision register](docs/decisions/README.md).
