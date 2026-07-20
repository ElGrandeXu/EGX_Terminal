# Project charter

## Mission

Build a public, LLM-agnostic workspace model for terminal agents in which
behavior, knowledge, project state, and methods belong to the repository rather
than to a replaceable provider or model.

## Non-negotiable principles

- **Context efficiency:** keep the default behavioral core short; load detailed
  context only when the task makes it relevant.
- **Provider independence:** repository concepts must not require one model,
  vendor, or terminal harness. Provider entrypoints remain adapters.
- **Public by design:** committed material must be publishable without secrets,
  private data, personal paths, or hidden operational assumptions.
- **Traceability:** distinguish evidence, interpretation, and decision. Attribute
  external ideas with exact sources and observed versions or commits.
- **Deliberate adoption:** every rule, skill, or mechanism must justify both its
  utility and its context and maintenance cost.
- **Simple operations:** prefer mechanisms that are inspectable, testable,
  reversible, and easy to remove.

## Objectives

- Audit five external repositories independently and comparably.
- Extract portable principles without copying implementations blindly.
- Measure automatic versus on-demand context and its probable token cost.
- Synthesize the evidence only after all individual audits are complete.
- Design and validate a minimal architecture that preserves project continuity
  across supported harnesses.

## Current-phase non-objectives

- Choosing the final architecture or doctrine.
- Building skills, hooks, subagents, MCP integrations, memory automation, routing,
  installation tooling, dependencies, application code, or CI.
- Selecting a license or publishing a remote repository.
- Treating any audited repository or provider convention as a template.

## Long-term success criteria

The workspace will be successful when a new supported terminal harness can enter
through a thin adapter, recover the current project state with bounded context,
load deeper knowledge only when relevant, trace important decisions to evidence,
and produce reproducible results without depending on private machine state.
