# Project charter

## Mission

Build a public, LLM-agnostic workspace model for terminal agents in which
behavior, knowledge, project state, and methods belong to the repository rather
than to a replaceable provider or model.

## Non-negotiable principles

- **Context efficiency:** keep automatically loaded context absent in V1 and load
  detailed project context only when the task makes it relevant.
- **Provider independence:** repository concepts must not require one model,
  vendor, or terminal harness. Any future provider entrypoint must remain a
  replaceable, explicitly enabled adapter.
- **Public by design:** committed material must be publishable without secrets,
  private data, personal paths, or hidden operational assumptions.
- **Traceability:** distinguish evidence, interpretation, and decision. Attribute
  external ideas with exact sources and observed versions or commits.
- **Deliberate adoption:** every rule, skill, or mechanism must justify its
  utility and its context and maintenance cost, then receive an explicit project
  decision before activation.
- **Simple operations:** prefer mechanisms that are inspectable, testable,
  reversible, and easy to remove.

## Objectives

- Preserve the five independent audits and their synthesis as traceable evidence.
- Extract and maintain portable principles without copying external
  implementations blindly.
- Keep the V1 distribution neutral while making project principles and protocols
  available on demand. Enforcement covers the known active project surfaces in
  the dated machine-readable registry, not unknown future harness conventions.
- Prepare a public workspace whose optional mechanisms remain separable,
  inspectable, and provider-neutral.

## Current-phase non-objectives

- Reopening the choice of an always-on behavioral doctrine for V1.
- Building skills, hooks, subagents, MCP integrations, memory automation, routing,
  compression, installation tooling, or other advanced capabilities.
- Replacing, moving, or retroactively signing the immutable `v1.0.0` release, or
  treating the `v1.0.1` consolidation branch as a published release.
- Activating a provider-specific adapter or hidden instruction injection.

## Voluntary mission protocol

When project work needs repository context, a contributor may:

1. consult [`STATUS.md`](STATUS.md);
2. select the smallest set of documents relevant to the mission;
3. expand that context only when needed.

Detailed evidence belongs in the relevant research or decision record. This is a
documented, voluntary protocol, not an automatically loaded behavioral payload.

## Long-term success criteria

The workspace will be successful when a terminal harness can use an explicitly
selected adapter or protocol, recover the current project state with bounded
context, load deeper knowledge only when relevant, trace important decisions to
evidence, and produce reproducible results without depending on private machine
state.
