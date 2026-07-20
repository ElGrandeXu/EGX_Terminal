# Repository map

## Snapshot and integrity

| Field | Observation |
|---|---|
| Repository | <https://github.com/ayghri/i-have-adhd> |
| Resolved `main` | `72c33eee81ea439cf01991e93729adfce2ffc99e` |
| Prepared mission SHA | Same; no drift |
| Snapshot date | 2026-07-20 |
| Commit author/date | Ayoub Ghriss, 2026-07-19 09:56:16 -06:00 |
| Commit subject | `Merge pull request #1 from seonghobae/codex-compatible-pr` |
| Default branch | `main` |
| Checkout | Detached at resolved SHA; clean |
| Remote | `https://github.com/ayghri/i-have-adhd.git` |
| Integrity | `git fsck --full` clean; all tracked modes `100644` |
| Tags / releases | None / none |
| Branches in origin | `main` only |
| License | MIT, [`LICENSE`](https://github.com/ayghri/i-have-adhd/blob/72c33eee81ea439cf01991e93729adfce2ffc99e/LICENSE) |

These are verified facts or reproduced measurements [E01-E03, E08].

## Exact tracked tree

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── i-have-adhd/
│       ├── agents/
│       │   └── openai.yaml
│       └── SKILL.md
├── INSTALL.md
├── LICENSE
├── README.md
└── logo.png
```

Total: **10 tracked files**: **9 text files inspected in full**, plus **1 binary
inspected at metadata level** [E03]. There are no submodules.

## File inventory

Sizes are canonical Git blob sizes (LF), not the CRLF-expanded Windows checkout.
Roles are audit interpretations except where a manifest defines them.

| Path | Git bytes | Blob prefix | Type / metadata | Role |
|---|---:|---|---|---|
| `.agents/plugins/marketplace.json` | 414 | `6f0ab8f` | JSON | Codex marketplace catalog; points to repository URL at floating `main`. |
| `.claude-plugin/marketplace.json` | 451 | `a97eee5` | JSON | Claude marketplace catalog; one local-source plugin. |
| `.claude-plugin/plugin.json` | 187 | `0c43bce` | JSON | Minimal Claude plugin identity and description. |
| `.codex-plugin/plugin.json` | 1,278 | `f565918` | JSON | Codex package manifest, version `0.1.0`, skill path, install-surface metadata, logo references. |
| `INSTALL.md` | 2,250 | `05c8f21` | Markdown | Claude/Codex install, verify, update, removal, Claude always-on and troubleshooting claims. |
| `LICENSE` | 1,069 | `19db5f1` | Text | MIT license, copyright 2026 Ayoub Ghriss. |
| `README.md` | 2,806 | `d89308e` | Markdown/HTML | Project pitch, install quickstart, before/after example, ten-rule summary, book credit. |
| `logo.png` | 95,884 | `1ddc33a` | PNG, 256×256, RGBA, 8-bit | Brand/composer image referenced by both README and Codex manifest. |
| `skills/i-have-adhd/SKILL.md` | 5,209 | `fe86823` | Markdown + YAML | Canonical behavioral instructions: premises, ten rules, exceptions, pre-send check. |
| `skills/i-have-adhd/agents/openai.yaml` | 237 | `d16d889` | YAML | Codex UI prompt metadata and implicit-invocation policy. |

The PNG has the valid eight-byte PNG signature, color type 6, and SHA-256
`c462e2b2feb5c03b413edf95f8ca41256cef7d49f88ecef004809980e2904441`.
It was not decoded or executed.

## Sources of truth and duplication

### Behavioral source

`skills/i-have-adhd/SKILL.md` is the only current complete behavioral source
[E04]. It contains all five premises, ten rules, four override conditions, and
the pre-send check. Its blob is unchanged from the first commit [E09].

Partial duplication exists in:

- `README.md`: repeats all ten rule labels and one worked example;
- Claude/Codex manifests: repeat selected benefits for discovery and display;
- `openai.yaml`: repeats action-first positioning in its short description and
  default prompt;
- `INSTALL.md`: the Claude always-on payload names only action-first, numbered
  steps, no preamble/closers, and state restatement.

The summaries are directionally consistent, but not equivalent. Only the skill
contains rules 3, 6, 8, 9, all exceptions, and the final self-check in full.
Exact README/INSTALL overlap is measured in `token-economics.md` [E29].

### Distribution sources

- Claude discovery is rooted in `.claude-plugin/marketplace.json`; its plugin
  `source` is `./`, and `.claude-plugin/plugin.json` supplies identity.
- Codex discovery is rooted in `.agents/plugins/marketplace.json`; the catalog
  points to the Git URL and floating `main`. `.codex-plugin/plugin.json` points
  to `./skills/`.
- The actual instruction payload remains the same `SKILL.md` for both.
- `openai.yaml` affects Codex presentation and invocation policy; it is not a
  second behavioral prompt [E20].

### Description coherence

| Surface | Themes named | Omitted relative to skill | Tension |
|---|---|---|---|
| Claude marketplace | action-first, numbered, no tangents | state, time, progress, errors, list cap, no recap | Short but accurate subset. |
| Claude manifest | action, numbering, tangents, state, wins | time, errors, list cap, no recap | Accurate subset. |
| Codex top description | action, numbering, tangents, progress | state, time, errors, list cap, no recap | Accurate subset. |
| Codex long description | action, numbering, tangents, state, progress | time, errors, list cap, no recap | Accurate subset. |
| OpenAI metadata | action-first only | nine rules | Suitable as short UI copy; broad medical label remains. |
| Skill frontmatter | action, numbering, state, tangents, time, wins, universal trigger | four rule details | Broadest discovery claim; requests near-universal activation. |

No description contradicts the skill directly, but their different subsets mean
that discovery text does not disclose all behavioral tradeoffs.

Claude-specific residue remains after the Codex PR: `INSTALL.md` still introduces
the package as a Claude Code plugin; README's “What it does” still calls it a
Claude Code skill; always-on instructions and most troubleshooting target Claude;
and both `.claude-plugin` files remain necessary only to that distribution path.
PR nº1 appended Codex sections rather than normalizing the provider-neutral prose
[E11-E12].

## Capabilities that are absent

At the audited SHA there are:

- no tests, evals, benchmarks, fixtures, or recorded results;
- no CI/workflow files, hooks, executable scripts, or source code;
- no package/dependency lockfile, runtime dependency, MCP server, or app;
- no changelog, release automation, tag, or release;
- no OpenCode/Cursor/Antigravity adapter in the snapshot.

The repository is therefore a small prompt package plus distribution metadata,
not a program or evidence-backed behavior suite [E03, E16-E17].

## Complete Git history

All 10 reachable commits were inspected in chronological order, including every
patch and the two historical files that are now deleted [E09-E10].

| # | Commit / date | Change and significance |
|---:|---|---|
| 1 | [`d3fb4ab`](https://github.com/ayghri/i-have-adhd/commit/d3fb4ab8b54aa26ed0432bb7e05ba37398a09b5a), 2026-05-13 | Initial Claude marketplace/manifest, 120-line skill, 20-line slash command duplicating the rules, long README, and three installation modes. The current skill text is already complete here. |
| 2 | [`cbb7194`](https://github.com/ayghri/i-have-adhd/commit/cbb719463c07e3042d765655d57dbd4a04c01ca9), 2026-05-13 | Replaces a README clone placeholder with `ayghri`. |
| 3 | [`e22697c`](https://github.com/ayghri/i-have-adhd/commit/e22697cd67a7e0c8040e5cf6ccdd8326432f93ad), 2026-05-13 | Adds `install-user.sh` to copy skill and command under `~/.claude`; documents an overwrite-on-rerun user install. |
| 4 | [`4561747`](https://github.com/ayghri/i-have-adhd/commit/4561747d5ef54f4994000e2dacaee54c0e533d52), 2026-05-13 | Changes documented invocation from `./install-user.sh` to `bash install-user.sh`; file mode stays executable historically, but the documentation no longer depends on direct execution. |
| 5 | [`6b92a90`](https://github.com/ayghri/i-have-adhd/commit/6b92a902b695f4fb778062a2073bf2ca2a6c34c5), 2026-05-13 | Adds the *Adult ADHD Tool Kit* credit and softens one README sentence from “ADHD brain” to “you.” |
| 6 | [`2e125fa`](https://github.com/ayghri/i-have-adhd/commit/2e125fa14f5ec81bb79cecaf97d0a31884076f0f), 2026-05-28 | “Moved to plugin mode”: deletes the user installer and duplicated command; removes project/user manual install paths; drastically shortens README/INSTALL; keeps marketplace install and the unchanged skill. |
| 7 | [`fa361c8`](https://github.com/ayghri/i-have-adhd/commit/fa361c87bb82e490f9430b104eca0b71c8fcc0d0), 2026-05-28 | README formatting-only blank line. |
| 8 | [`d167175`](https://github.com/ayghri/i-have-adhd/commit/d1671755d41685148d1cb0055861b3e572e54afc), 2026-05-28 | Adds MIT license and logo; improves README example; changes clone target from home directory to a relative directory; replaces conversational stop phrases with plugin disable instructions. |
| 9 | [`e3c3d21`](https://github.com/ayghri/i-have-adhd/commit/e3c3d21db2b541c9eba24701579e173a4b37758f), 2026-06-17 | PR nº1 commit: adds Codex marketplace/manifest/OpenAI metadata and Codex install/update/remove docs; behavioral skill unchanged. |
| 10 | [`72c33ee`](https://github.com/ayghri/i-have-adhd/commit/72c33eee81ea439cf01991e93729adfce2ffc99e), 2026-07-19 | Merge commit for PR nº1; two parents; no additional content beyond PR branch. |

### Installer add/remove interpretation

Verified history shows what happened but not a stated rationale. The script
offered global, copy-based installation; the next same-day commit avoided
requiring the executable bit. Fifteen days later, “plugin mode” deleted both the
script and the slash-command duplicate while narrowing docs to marketplace
installation [E10]. The most economical interpretation is consolidation around
provider-managed discovery and removal of copied/duplicated state. It remains an
**Inference**, because neither commit body nor an issue says why.

### Initial versus current behavior

There is no behavioral delta: initial and current `SKILL.md` resolve to the same
blob. What changed is packaging, presentation, license, disabling guidance, and
provider coverage. Early “stop adhd mode”/“normal mode” language came from the
now-deleted slash command; current docs use plugin disable for Claude and removal
for Codex. Codex compatibility adds no new rule and no model-specific adaptation
[E09, E12].

## Issues and pull requests

### Current issues

All five non-PR issues and all six comments were inspected [E14].

| Issue | State / comments | Evidence and audit reading |
|---|---|---|
| [#2 — installation](https://github.com/ayghri/i-have-adhd/issues/2) | Open / 1 | Suggests direct marketplace commands. Owner says cloning first is a personal safety habit against upstream changes. This supports inspectability intent, not a technical requirement. |
| [#3 — task/plan tools](https://github.com/ayghri/i-have-adhd/issues/3) | Open / 1 | Proposes using harness task/plan UI to split walls of text and track state. The comment supplies a private-workflow example. No repository implementation or cross-harness test exists [E15]. |
| [#4 — benchmarks](https://github.com/ayghri/i-have-adhd/issues/4) | Open / 1 | Raises possible quality loss from fewer output tokens. Owner is willing to define and run measurements, but none are present [E16]. |
| [#6 — OpenCode](https://github.com/ayghri/i-have-adhd/issues/6) | Open / 0 | Requests plugin support; confirms a distribution gap, not incompatibility of the Markdown payload [E17]. |
| [#7 — Antigravity CLI](https://github.com/ayghri/i-have-adhd/issues/7) | Open / 3 | Requests another CLI target; owner invites a PR. No adapter exists [E17]. |

### Pull requests

The mission described a unique PR, but GitHub had **two** at observation time.
Both, all four conversation comments, all commits/files, review endpoints, and
reported checks were inspected [E12-E13, E18].

| PR | State | Scope | Validation boundary |
|---|---|---|---|
| [#1 — Codex compatibility](https://github.com/ayghri/i-have-adhd/pull/1) | Merged 2026-07-19 | 1 commit, 5 files, +118/−0; two general comments; no formal or inline review; no reported checks. | Author reports JSON parsing, repository-local validator scripts, temporary-home marketplace add/list, and a fork-side Copilot review with no comments. This validates structure/discovery claims, not behavioral quality, ADHD suitability, implicit invocation frequency, or token savings [E13]. |
| [#5 — Cursor install docs](https://github.com/ayghri/i-have-adhd/pull/5) | Open | 2 commits, 2 files, +115/−2 at API observation; two comments; no reviews/checks. | Claims a local Cursor use and proposes `npx skills` distribution. It is outside the audited SHA and does not change `SKILL.md`; no Cursor support is credited to the snapshot [E18]. |

PR nº5 was created after the audited `main` commit. It explains the mismatch with
the mission's “unique pull request” statement without changing the resolved HEAD.

## Reproduction commands

The following read-only commands are sufficient to reproduce the repository-side
inventory without running upstream code:

```powershell
git ls-remote https://github.com/ayghri/i-have-adhd.git refs/heads/main
git clone --no-checkout https://github.com/ayghri/i-have-adhd.git <temporary-path>
git -C <temporary-path> checkout --detach 72c33eee81ea439cf01991e93729adfce2ffc99e
git -C <temporary-path> ls-tree -r --long HEAD
git -C <temporary-path> log --all --reverse --stat --patch
git -C <temporary-path> fsck --full
```

No upstream script, install command, plugin, skill, or behavioral code was run.
