# 0001 — Bootstrap entrypoints

- **Status:** provisional
- **Date:** 2026-07-20

## Context

The research workspace needs a minimal shared behavioral entrypoint before its
internal architecture is known. It must work with Codex and Claude Code without
duplicating the kernel or introducing provider configuration.

## Decision

- Use root `AGENTS.md` as the canonical minimal bootstrap entrypoint.
- Keep the active content of root `CLAUDE.md` to the single import `@AGENTS.md`.
- Use a regular file, not a symbolic link, for Windows compatibility.
- Add no other provider adapter or provider-specific configuration now.
- Revisit this decision after all five external repository audits are complete.

This is a compatibility decision, not a commitment to a Codex-dependent internal
architecture.

## Evidence

### Documented facts

- Codex discovers root and nested `AGENTS.md` guidance and builds an instruction
  chain: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Claude Code supports `@path` imports in `CLAUDE.md`, with relative paths resolved
  from the importing file: <https://code.claude.com/docs/en/memory>

### Project interpretation

A one-line Claude adapter imports one canonical kernel, reducing duplication and
drift while keeping both entrypoints explicit and inspectable.

## Consequences

- The canonical kernel is stored once.
- Both harnesses automatically load the same bootstrap guidance.
- The adapter adds negligible repository complexity but remains provider-shaped.
- Other harnesses have no adapter during the audit phase.

## Revision triggers

- Completion of all five repository audits.
- Evidence that a supported harness cannot reliably load this arrangement.
- A measured context, portability, or maintenance cost that outweighs its benefit.
- Selection of the repository's final internal instruction architecture.
