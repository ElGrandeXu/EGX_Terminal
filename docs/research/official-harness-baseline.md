# Official harness baseline

Consulted on **2026-07-20**. Scope is limited to current official OpenAI and
Anthropic documentation needed for the bootstrap entrypoints.

## 1. Documented facts

### Codex instruction discovery and hierarchy

- At global scope, Codex reads `AGENTS.override.md` when present, otherwise
  `AGENTS.md`, from the Codex home directory; it uses the first non-empty match.
- At project scope, Codex starts at the project root and walks toward the current
  working directory. Per directory it checks `AGENTS.override.md`, `AGENTS.md`,
  then configured fallback names, and includes at most one file.
- Files are concatenated root-first. Guidance closer to the working directory
  appears later and therefore takes precedence when instructions conflict.
- Empty files are skipped. The combined project guidance stops at
  `project_doc_max_bytes`, whose documented default is 32 KiB.
- Codex normally detects a Git directory as the project root. The root markers,
  fallback filenames, and byte limit are configurable outside this repository's
  current bootstrap.

Sources:

- <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- <https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery>

### Claude Code instruction discovery and imports

- Claude Code accepts project instructions at `./CLAUDE.md` or
  `./.claude/CLAUDE.md`; `CLAUDE.local.md` is the local project scope.
- `CLAUDE.md` files in the hierarchy above the working directory load in full at
  launch. Files below it load when Claude works with files in those directories.
- A `CLAUDE.md` file can import another file with `@path`. Relative imports resolve
  from the importing file, are expanded into launch context, and can recurse up
  to four hops.
- Anthropic distinguishes instruction memory (`CLAUDE.md`) from JSON settings.
  Project settings and local settings have separate shared and private scopes.

Sources:

- <https://code.claude.com/docs/en/memory>
- <https://code.claude.com/docs/en/settings>

### Automatic context cost and enforcement

- Codex automatically places discovered project instructions in model context and
  bounds their combined size with a configurable byte limit.
- Claude Code loads applicable `CLAUDE.md` content and imports into the context
  window. Imported files therefore incur launch-context cost even when their
  details are irrelevant to the current task.
- Anthropic documents `CLAUDE.md` instructions as context, not enforced
  configuration, and points to a `PreToolUse` hook when an action must be blocked.
  This project has not created hooks or other enforcement.

Source:

- <https://code.claude.com/docs/en/memory>

## 2. Project interpretations

- A short root kernel provides the smallest useful automatic baseline for both
  current harnesses.
- A one-line `CLAUDE.md` import prevents duplicated behavior and makes its context
  cost explicit: Claude loads the same canonical kernel once through its adapter.
- Detailed research and decisions should remain demand-loaded because automatic
  inclusion spends context before task relevance is known.
- Initializing Git on `main` gives Codex a stable default project root without
  requiring project-specific Codex configuration.
- Behavioral instructions guide model choices; they are not a security boundary.
  Any future hard guarantee needs a separately evaluated technical control.

## 3. Deferred decisions

- Reconsider the canonical filename and all provider adapters after five audits.
- Measure actual instruction and import token costs across selected harness versions.
- Decide later whether hooks, settings, skills, memory, or routing justify their cost.
- Determine compatibility behavior for other terminal agents only after evidence.
- Recheck discovery order, size limits, and import behavior before stabilization;
  official documentation and client implementations can evolve.

## Uncertainty boundary

These pages describe current products, not a permanent cross-provider standard.
Behavior may vary by installed client version, user-level configuration, managed
policy, or future documentation changes. No runtime cross-version compatibility
test was part of this bootstrap.
