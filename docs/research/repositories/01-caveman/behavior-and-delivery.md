# Behavior and delivery

## System model

Caveman is not one mechanism. It is five layers that are easy to conflate:

1. **Behavioral instruction:** a prompt asks the model to make output denser.
2. **Activation:** hooks, imported files, plugin defaults, or user invocation put
   that instruction in context.
3. **State and measurement:** flags, logs, statusline, and stats remember a mode
   and estimate its effect.
4. **Packaging:** marketplace, extension, skill registry, native adapter, and
   installer distribute different subsets.
5. **Adjacent products:** Cavecrew, persistent-file compression, and MCP schema
   compression extend far beyond output style.

Only the state transitions and file/config mutations are technically enforced.
The model can still ignore, partially obey, or over-apply the style
([E005–E015](evidence-ledger.md#e005)).

## Behavioral doctrine

### Core constraints

The main skill asks the model to:

- remove filler, pleasantries, hedging, redundant setup, articles, and many
  conjunctions;
- prefer fragments and short common words;
- retain domain vocabulary, code, commands, identifiers, paths, numbers, and
  error text exactly;
- answer in the user’s language;
- avoid narrating tool use, decorative tables, emojis, long logs, invented
  abbreviations, and self-announcement of the style;
- use ordinary prose inside generated code, commits, pull requests, reviews, and
  other authored artifacts.

These rules combine three separable techniques: deleting conversational overhead,
raising semantic density, and adopting visibly telegraphic grammar. The first two
can reduce output without the third. “Caveman grammar” is therefore a product
identity, not a demonstrated prerequisite ([E050](evidence-ledger.md#e050)).

### Levels

| Level | Intended transformation | Likely trade-off |
|---|---|---|
| `lite` | Mostly ordinary grammar; remove filler and shorten sentences | Lowest cognitive friction; lowest branded effect |
| `full` | Drop articles/conjunctions where meaning survives; fragments | Default; denser but visibly unnatural |
| `ultra` | Keywords and near-telegraphic output | Maximum ambiguity/fatigue risk |
| `wenyan-lite/full/ultra` | Classical-Chinese-inspired variants | Language/cultural/model-specific; no committed savings coefficient |

The level table is instruction, not a measurable compression algorithm. Only
`full` is wired to the 0.65 stats coefficient; no separate benchmark establishes
the other levels ([E006](evidence-ledger.md#e006)).

### Auto-Clarity and boundaries

Auto-Clarity is the most reusable part of the doctrine. Normal prose temporarily
overrides compression for security, irreversible operations, ambiguous requests,
ordered multi-step instructions, and signs of user confusion. Caveman is also
excluded from code, commit messages, pull requests, and reviews. After the risky
or confusing segment, the style resumes.

This makes safety a higher-order constraint than brevity. It also exposes a
weakness: the same model being compressed must recognize that clarity is needed.
There is no external classifier or validator. Small or poorly aligned models may
miss the escape condition or interpret “resume” inconsistently
([E007](evidence-ledger.md#e007)).

### Human effects

- **Reading speed:** fewer words can speed scanning when concepts are familiar.
- **Fatigue:** sustained fragments remove grammatical cues and may increase the
  effort needed to reconstruct relationships.
- **Precision:** preserved literals help, but removed articles/conjunctions can
  change scope, temporality, negation, or responsibility.
- **Collaboration:** eliminating filler is usually beneficial; eliminating all
  conversational framing can hide uncertainty or make correction feel abrupt.
- **Personality:** the branded persona makes the constraint memorable, but can
  dominate tone and leak into artifacts unless carefully bounded.
- **Model adherence:** repeated, concrete examples may help some models, while
  long rules, exceptions, and stylized examples may compete for attention in
  smaller ones. No cross-model evidence settles the trade-off.

## End-to-end lifecycle

### 1. Detection

The Node installer enumerates provider records with probes for commands, editor
extensions, applications, or conventional directories. “Soft” probes (Junie,
Qoder, Antigravity) do not trigger automatic installation. Detection is a
distribution convenience, not runtime model discovery. The matrix is in
[installer lines 204–260](https://github.com/JuliusBrussee/caveman/blob/0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0/bin/install.js#L204-L260).

### 2. Distribution choice

Claude uses its marketplace/plugin CLI; Gemini its extension CLI; OpenCode and
OpenClaw get native file/config installation; Hermes gets direct skill copies;
many other harnesses delegate to the external skills CLI. Project rule files are
optional via `--with-init`. MCP shrink is independently opt-in.

### 3. Scope and install

The default operation is predominantly global: provider plugin/extension, Claude
config directory, OpenCode config, OpenClaw workspace, or user-level skill
registry. `--with-init` additionally mutates the current project. `--config-dir`
scopes only Claude hook files/settings, not every provider
([INSTALL lines 118–127](https://github.com/JuliusBrussee/caveman/blob/0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0/INSTALL.md#L118-L127)).

### 4. Initial injection and activation

Claude’s SessionStart hook reads the main skill, removes examples and inactive
intensity rows, then emits hidden model context. Default mode is `full`, so it is
automatically active. OpenCode appends the minimal rule through its plugin and
reinforces mode on messages. Gemini points the extension at an import file.
OpenClaw’s `SOUL.md` bootstrap is intended to be always present. Registry skills
normally require invocation.

### 5. Level selection and persistence

Claude’s prompt hook recognizes slash commands and natural-language mode changes.
Resolution order at session start is environment variable, project config, user
config, then `full`. It writes a bounded flag and a JSONL transition log. OpenCode
has its own global flag. Other paths generally have no equivalent dynamic state.

### 6. Suspension, one-shot modes, and disablement

Auto-Clarity is behavioral suspension. `/caveman normal` or `/caveman stop`
removes the active flag. Commit/review/compress save the previous flag to a
secondary file and restore it on the following prompt hook. `off` suppresses
activation. These operations are reliable only where the corresponding hook or
plugin runs.

### 7. Measurement and display

Claude stats parse local session JSONL for output and cache-read counters, combine
them with mode-transition logs, and apply a fixed expected reduction. The
statusline reads a sanitized suffix file. “Saved” is a model-based estimate, not
an observed baseline; see [token economics](token-economics.md).

### 8. Uninstall

The unified uninstaller removes known Claude hooks/files and prunes marked
OpenCode/OpenClaw state. It deliberately leaves externally managed skill-registry
installs and per-project init files for manual/agent-specific removal
([E044](evidence-ledger.md#e044)). Thus “reversible” is true only with a
per-mechanism qualification.

## Harness matrix

| Harness/family | Discovered input | Actually loaded | Loading/scope | Activation and state | Hooks/config mutation | Reversal | Coupling / probable context | Evidence |
|---|---|---|---|---|---|---|---|---|
| Claude Code | `claude` command | Filtered main skill at SessionStart; short reinforcement per prompt; command skills on demand | Persistent session context; global plugin/config | Default `full`; natural/slash switching; global and optional project config; flag + transition/history files | SessionStart, UserPromptSubmit, optional statusline and MCP registration; settings backup | Managed uninstall; skills registry separate | High Claude hook/API coupling; ~728 initial + ~34 per turn before framing | [E008–E009](evidence-ledger.md#e008) |
| Codex | `codex` command | Main skill through registry/plugin when selected; plugin `defaultPrompt` declared | Likely on demand/user-level; exact plugin semantics version-dependent | No proven Caveman flag/tracker in normal install | Installer calls skills CLI; root `.codex` hook exists but is not proven installed | Skills CLI/manager | Medium adapter coupling; full skill ~1,245 when loaded | [E011–E012](evidence-ledger.md#e011) |
| OpenCode | `opencode` command | Minimal static rule plus active-mode reinforcement; copied skills/agents/commands | Global native plugin and global `AGENTS.md` | Auto active; OpenCode flag; message/event handling | Copies plugin tree, patches `opencode.json`, fenced `AGENTS.md`; optional MCP | Marker/file/config pruning and `.bak` | High lifecycle/API coupling; ~163 permanent + ~34 active turn | [E010](evidence-ledger.md#e010), [E049](evidence-ledger.md#e049) |
| Gemini CLI | `gemini` command | Root `GEMINI.md` importing four skills | Global extension; eager/lazy import behavior unknown | No Caveman mode flag or tracker proven | `gemini extensions install` | Gemini extension manager | High Gemini import coupling; up to ~3,632 source tokens if eager | [E013](evidence-ledger.md#e013), [E018](evidence-ledger.md#e018) |
| Skills-registry agents | Command/app/extension probes | Skill directories chosen by harness/registry | Usually user-level, on demand | Usually manual/per-session | `npx skills add ... --skill '*' -a <profile>` | External CLI/IDE manager | Packaging-specific; no common runtime guarantee | [E011](evidence-ledger.md#e011) |
| Static-rule agents | Detected project targets with `--with-init` | 615-byte minimal rule | Always-on, project scope | Implicit on every agent session; no dynamic state | Writes/replaces/appends provider-specific instruction files | Manual; force can overwrite a target | Filename-specific adapters; ~163 tokens whenever loaded | [E015–E016](evidence-ledger.md#e015) |
| OpenClaw | command or workspace directory | Workspace skill plus minimal `SOUL.md` bootstrap | Global workspace; bootstrap intended every turn | Auto via bootstrap; no hook-level mode log | Copies skill and appends marker-fenced block | Marker/file pruning | OpenClaw-specific injection; small permanent bootstrap plus on-demand skill | [E014](evidence-ledger.md#e014) |

“LLM-agnostic” applies to the *idea* of a textual density constraint. Discovery,
activation, state, statusline, installation and removal are an accumulation of
harness adapters ([E060](evidence-ledger.md#e060)).

## Commands, hooks, flags, and agents

### Command surfaces

- `/caveman` changes mode or restores normal prose.
- `/caveman-stats` runs local accounting and displays current/session/lifetime
  estimates.
- `/caveman-compress` invokes the separate LLM-backed file compressor.
- commit and review commands are one-shot ordinary-prose workflows.
- Parallel Markdown/TOML command files serve Claude/OpenCode packaging.

Commands are provider UI surfaces around skills/hooks; they do not make the core
instruction portable by themselves.

### State surfaces

Claude may create `.caveman-active`, `.caveman-active.prev`,
`.caveman-mode-log.jsonl`, `.caveman-history.jsonl`, and
`.caveman-statusline-suffix` under its config directory. OpenCode has a separate
flag under its configuration. The flag helper rejects symbolic-link flags,
bounds reads, validates mode values, writes via temporary file and rename, and
uses mode `0600` where applicable. Statusline implementations similarly sanitize
length/content and reject suspicious link/reparse targets
([E041–E043](evidence-ledger.md#e041)).

Hooks catch errors and return success. This is appropriate for an optional style
feature that must not block an agent, but it also makes broken activation or
accounting easy to miss ([E042](evidence-ledger.md#e042)).

### Cavecrew

Cavecrew defines investigator, builder, and reviewer agents plus a coordinating
skill. The SessionStart model-override helper can rewrite model fields in agent
Markdown according to environment variables. This is a separate orchestration
product: it adds parallel-agent policy and model selection rather than enforcing
brevity. It should not be counted as evidence that the output doctrine itself
requires agents.

## MCP description compression

`caveman-shrink` is an optional stdio proxy. It spawns a configured upstream MCP
server, intercepts list-style responses, and recursively shortens configured
`description` fields. Requests, tool executions, and tool results pass through.
The compressor protects recognizable code fences, inline code, URLs, paths,
versions, calls and identifiers, then applies regex deletion and whitespace
normalization ([E035–E036](evidence-ledger.md#e035)).

This is actual input compression rather than output style. It can matter when a
harness repeatedly injects large tool schemas. However, syntactic protection is
not semantic verification: deleting a hedge, article, or connective from a tool
description can alter preconditions or tool-selection boundaries. The proxy is
pre-1.0, was once published without a required file, and its fixed registry state
was not established ([E037](evidence-ledger.md#e037)).

## Persistent-file compression

`caveman-compress` is not local deterministic minification. It sends a selected
file body to Anthropic through the SDK or Claude CLI, protects YAML frontmatter
outside the model, writes an out-of-tree backup, and checks structural invariants
such as headings, code blocks, URLs, paths, bullets and inline code. Files over
500 KB and suspicious filenames/paths are refused.

Consequences:

- content crosses a third-party boundary even though root security documentation
  says local-only;
- the denylist cannot discover secrets inside a benignly named file;
- validation cannot prove preserved meaning or policy nuance;
- the primary-file write is not atomic;
- the backup key uses limited path identity and can collide, then safely abort;
- adjacent-backup assumptions elsewhere can make savings accounting miss current
  backups.

These contradictions are documented in [E038–E040](evidence-ledger.md#e038).
This product is provider-specific and materially riskier than the style skill.

## Installation, platform handling, and trust

The installer is unusually defensive for a style plugin: Node 18+, no declared
runtime dependency, string-aware JSONC handling, malformed-config refusal,
backups, duplicate-Claude-hook avoidance, atomic settings writes, Windows `.cmd`
handling, WSL/Windows-Node detection, and best-effort symlink protections.
OpenCode migration uses a `.bak` and marker fences.

The trust boundary remains broad:

- recommended shell/PowerShell one-liners fetch moving `main` and execute it;
- shims delegate to an unpinned GitHub `npx` package;
- provider CLIs and registries perform network downloads;
- global Claude, OpenCode, Gemini, OpenClaw, and skills locations may change;
- `--with-init` changes the current project, and `--force` can replace targets;
- internal fallback hook downloads are pinned to a release and checked against a
  committed SHA-256 manifest, but that does not pin the top-level bootstrap;
- the sync workflow pins checkout only to a mutable major action tag.

The committed checksum manifest was independently compared with Git blob bytes
and matched all eight named hook assets. Filesystem hashes on a Windows checkout
can differ after CRLF conversion; Git-blob hashing is the appropriate
reproducible comparison. No telemetry path was found in hooks/proxy, but the
compressor and delegated tools can use network ([E045–E046](evidence-ledger.md#e045),
[E059](evidence-ledger.md#e059)).

## What is instruction, enforcement, measurement, packaging, or product

| Element | Classification |
|---|---|
| Skill rules, levels, Auto-Clarity | Behavioral instruction |
| SessionStart, prompt hook, imports, static rule | Activation/injection |
| Flags, previous-mode file, transition logs | Technical state enforcement |
| Model’s terse response | Behavioral compliance, not enforcement |
| Stats/statusline | Measurement/display, partly estimated |
| Marketplace, manifests, registry, unified installer | Packaging/distribution |
| Cavecrew | Adjacent multi-agent product |
| `caveman-compress` | Adjacent LLM file-rewrite product |
| `caveman-shrink` | Adjacent deterministic MCP-input proxy |

## Security and reversibility verdict

MIT permits use, modification and redistribution provided the copyright and
permission notice is retained; it disclaims warranty and liability. Any borrowed
code would therefore require notice preservation even if its principles can be
independently restated ([E061](evidence-ledger.md#e061)).

The local hook/state implementation shows thoughtful hardening and is largely
inspectable. The installer’s mutation surface and moving bootstrap remain too
broad to adopt as a template without narrowing. The file compressor has a
materially misstated data boundary. Uninstallation is only complete for managed
native artifacts, not registry skills or all project files. These are audit
findings, not vulnerability claims and not project adoption decisions.
