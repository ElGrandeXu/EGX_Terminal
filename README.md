# EGX_Terminal

EGX_Terminal explores how a terminal-agent workspace can keep its behavior,
knowledge, project state, and methods in the repository while allowing the active
LLM, provider, or terminal harness to be replaced.

The project is experimental. Its architecture is not stabilized, and no broad
agent capability is claimed yet.

The current method is deliberately sequential:

1. audit five external repositories independently;
2. extract evidenced principles from each;
3. compare and synthesize only after all audits are complete;
4. design an architecture from the resulting evidence.

Context efficiency is central: keep the automatically loaded behavioral kernel
small, disclose context progressively, and add mechanisms only when their utility
justifies their context and maintenance cost.

This is not a collection of skills, a Codex wrapper, or a clone of any provider's
configuration. The initial provider entrypoints are compatibility choices, not
the final internal architecture.

See [the charter](docs/CHARTER.md) for the project boundaries and
[the current status](docs/STATUS.md) before starting work.
