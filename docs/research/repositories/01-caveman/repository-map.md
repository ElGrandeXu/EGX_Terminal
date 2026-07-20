# Repository map

## Acquisition and inspection boundary

The default branch was resolved read-only before cloning. Both the mission’s
previously observed SHA and the newly resolved SHA were
`0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0`; no upstream drift occurred. A full,
non-recursive clone was detached at that commit. `origin`, detached `HEAD`, clean
checkout, `git fsck`, default branch, tags, commit date, and license were checked.
No submodule or tracked symbolic link exists.

All 167 tracked blobs were inventoried and statically read. Focused semantic
inspection covered behavior, installers, hooks, tools, MCP proxy, manifests,
tests, benchmarks, evals, documentation, workflows, and selected history. No
installer, hook, repository test, benchmark, eval, or product script was run.

| Property | Observed value |
|---|---|
| Repository | `JuliusBrussee/caveman` |
| Default branch | `main` |
| Audited commit | `0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0` |
| Commit date | 2026-07-03 11:08:51 UTC |
| Commit subject | `chore: sync SKILL.md copies [skip ci]` |
| Nearest tag | annotated `v1.9.1`, peeled to audited commit |
| License | MIT, Julius Brussee, 2026 |
| History | 252 commits reachable from audited HEAD |
| Tracked files | 167 |
| Tracked bytes | 851,072 |
| Text/binary | 164 / 3 |
| Text lines | 17,626 |

These are [verified facts](evidence-ledger.md#e001).

## Structural inventory

### Files by top-level area

| Area | Files | Function |
|---|---:|---|
| `tests/` | 32 | Hook, stats, installer, security and integration fixtures/tests |
| `src/` | 31 | Rules, hooks, initializer, OpenCode plugin, MCP proxy |
| `skills/` | 22 | Canonical skills and compressor implementation |
| `plugins/` | 20 | Claude/Codex distribution mirrors and manifests |
| repository root | 17 | Entry points, manifests, install shims, policy/docs |
| `commands/` | 10 | Claude Markdown and OpenCode TOML command surfaces |
| `docs/` | 9 | Website, honest-numbers note, assets |
| `evals/` | 6 | Three-arm/multilingual snapshot evaluation |
| `.github/` | 4 | One workflow plus issue/pull templates |
| `benchmarks/` | 4 | Runner, prompt set, requirements, empty results directory |
| `bin/` | 4 | Unified Node installer and config helpers |
| `agents/` | 3 | Cavecrew roles |
| `.claude-plugin/` | 2 | Marketplace and Claude plugin metadata |
| `.codex/` | 2 | Repository-level Codex config and hook definition |
| `dist/` | 1 | Packaged ZIP skill |

### Files by suffix

| Suffix | Count | Suffix | Count |
|---|---:|---|---:|
| `.md` | 64 | `.py` | 24 |
| `.js` | 21 | `.json` | 12 |
| `.mjs` | 9 | `.svg` | 7 |
| `.toml` | 6 | `.ps1` | 4 |
| `.sh` | 4 | `.png` | 2 |
| `.txt` | 2 | `.yml` | 2 |
| `.yaml` | 1 | `.skill` | 1 |
| `.editorconfig` | 1 | `.nojekyll` | 1 |
| `.html` | 1 | `.gitkeep` | 1 |
| `.gitignore` | 1 | `.gitattributes` | 1 |
| `.sha256` | 1 | no suffix | 1 |

The three binary blobs are `dist/caveman.skill` and two PNG assets. The archive
is a ZIP containing only `caveman/SKILL.md` and `caveman/README.md` beneath a
directory entry; its skill member matches the canonical skill hash.

### Largest tracked files

| Path | Bytes | Role |
|---|---:|---|
| `bin/install.js` | 76,308 | Cross-harness installer/uninstaller |
| `evals/snapshots/results.json` | 37,821 | Committed eval output |
| `tests/test_caveman_stats.js` | 30,314 | Stats tests |
| `tests/installer/e2e.freshinstall.test.mjs` | 28,065 | Installer E2E test source |
| `CLAUDE.md` | 24,512 | Maintainer/development instructions |
| `src/hooks/caveman-stats.js` | 24,625 | Usage parsing and estimated savings |
| `docs/index.html` | 23,863 | Website distribution |
| `docs/assets/caveman-logo-banner.png` | 19,193 | Binary asset |
| `tests/installer/opencode.test.mjs` | 17,408 | OpenCode installer tests |
| `bin/lib/settings.js` | 17,316 | JSON/JSONC configuration helper |

## Conceptual tree

```text
behavior
├─ skills/caveman/SKILL.md              canonical full doctrine
├─ src/rules/caveman-activate.md        canonical small static rule
├─ skills/caveman-{stats,compress,...}/ adjacent products/commands
└─ agents/cavecrew-*.md                 specialized agent prompts

delivery
├─ .claude-plugin/ + plugins/caveman/   Claude marketplace/plugin
├─ plugins/caveman/.codex-plugin/       Codex plugin metadata
├─ gemini-extension.json + GEMINI.md    Gemini adapter
├─ src/plugins/opencode/                OpenCode runtime adapter
├─ src/rules/*                          project/OpenClaw rule payloads
├─ bin/install.js                       detection, installation, removal
└─ dist/caveman.skill                   packaged skill archive

runtime support
├─ src/hooks/                           Claude activation, tracking, stats
├─ commands/                            mode/stats/compress entrypoints
└─ src/mcp-servers/caveman-shrink/      optional MCP description proxy

evidence and assurance
├─ benchmarks/                          API benchmark source, no raw results
├─ evals/                               methodology and one committed snapshot
├─ tests/                               32 test files
├─ docs/HONEST-NUMBERS.md               qualifications
└─ .github/workflows/sync-skill.yml     mirror/build workflow only
```

## Sources of truth and copies

The project does not have one universal canonical document. It has several
domain-specific sources:

| Concern | Effective source | Distributed/embedded copies | Synchronization |
|---|---|---|---|
| Full style doctrine | `skills/caveman/SKILL.md` | plugin skill, ZIP member | Workflow copy/build |
| Static always-on rule | `src/rules/caveman-activate.md` | initializer constant, Codex hook text, installed agent files | Manual |
| Cavecrew doctrine | `skills/cavecrew/SKILL.md` | plugin skill | Workflow |
| Cavecrew agents | `agents/cavecrew-*.md` | plugin agents | Workflow |
| Compressor | `skills/caveman-compress/` | plugin skill/scripts | Workflow, except ancillary docs |
| Stats skill | `skills/caveman-stats/SKILL.md` | plugin skill | Currently equal, not in workflow |
| OpenClaw bootstrap | `src/rules/caveman-openclaw-bootstrap.md` | fallback constant in `bin/lib/openclaw.js` | Manual |
| OpenCode behavior | `src/plugins/opencode/plugin.js` plus static rule | installed global copy | Installer copy, no build-time mirror |
| Provider detection/config | `bin/install.js` and `bin/lib/*` | published npm/GitHub package | Packaging |
| Marketing descriptions | README/manifests/site | repeated prose | Manual |

The workflow’s actual copy list is directly visible in
[lines 33–70](https://github.com/JuliusBrussee/caveman/blob/0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0/.github/workflows/sync-skill.yml#L33-L70).
Independent blob hashing confirmed every copy it names at HEAD. It also confirmed
that `AGENTS.md` equals `GEMINI.md`, and that the two stats skill copies happen to
be equal. This establishes current equality, not durable ownership
([E002–E004](evidence-ledger.md#e002)).

### Divergence risks

- The static rule has multiple hand-maintained paraphrases. A safety exception
  added to one need not reach the others.
- The stats plugin copy is outside the sync job despite currently matching.
- Root `.codex` files are not under `plugins/caveman/.codex-plugin/` and are not
  copied by the installer, making their publication/runtime role ambiguous.
- Root `AGENTS.md`/`GEMINI.md` import four skills, while Claude injects a filtered
  main skill and OpenCode injects a much smaller rule. “Caveman installed” thus
  has materially different context cost and behavior by harness.
- Documentation still describes older OpenCode callbacks and adjacent compressor
  backups in places. Code and product narrative can drift independently.
- `src/hooks/install.sh` and `.ps1` remain tracked legacy paths after the unified
  installer superseded them; their moving-branch download path is stale relative
  to the current `src/hooks/` layout.

## Distribution and publication surfaces

- GitHub repository and release/tag.
- Claude plugin marketplace via `.claude-plugin/marketplace.json` and
  `.claude-plugin/plugin.json`.
- Codex plugin metadata via `plugins/caveman/.codex-plugin/plugin.json`.
- Gemini extension via `gemini-extension.json`.
- Skills registry through `npx skills add` and the skill directories.
- npm/GitHub execution of the installer package.
- npm package declaration for `caveman-shrink`.
- `dist/caveman.skill` ZIP artifact.
- Static website in `docs/`.

The package declares Node 18+ and no runtime npm dependencies. This reduces the
local dependency graph, but installation delegates to provider CLIs, npm, GitHub,
and the skills registry ([E045–E046](evidence-ledger.md#e045)).

## Tests, benchmarks, evals, and CI

The 32 tracked test files cover meaningful installer, hook, stats, OpenCode,
MCP, security, and platform cases. Static inspection found 210 JavaScript test
declarations, excluding Python `unittest` methods. This audit did not execute
them. `benchmarks/results/` contains only `.gitkeep`; the benchmark’s raw API
responses are absent. `evals/snapshots/results.json` is committed and was
arithmetically recalculated independently.

The sole workflow is `sync-skill.yml`. It copies mirrors, rebuilds the ZIP, and
commits changes. No tracked workflow runs tests, benchmarks, or evals, despite a
documentation statement that the measurement script runs in CI
([E047–E048](evidence-ledger.md#e047)). Its use of `actions/checkout@v4` is a
mutable major-version reference rather than an immutable action commit.

## Pivot history

Eighteen commits were selected after reading the reachable history. They are not
an exhaustive changelog; each materially changes the thesis, evidence, delivery,
or safety posture.

| Commit | Change | What it reveals |
|---|---|---|
| [`af5375d`](https://github.com/JuliusBrussee/caveman/commit/af5375d6f0151b1441f638d855f6829f5e6724df) | Initial skill/claim | Product began as a behavioral prompt, not infrastructure. |
| [`6c3e2f6`](https://github.com/JuliusBrussee/caveman/commit/6c3e2f6147dbacd4e34d1800cd900c6c109a1054) | Benchmark and ~75% claim | Early evidence used a much smaller treatment. |
| [`d84127c`](https://github.com/JuliusBrussee/caveman/commit/d84127c35f8eb62b13a94aa6db431ca29e617b86) | Auto-Clarity | Readability/safety damage was recognized as a necessary escape hatch. |
| [`fbfe83b`](https://github.com/JuliusBrussee/caveman/commit/fbfe83b3e2dafc8d851559bd03b151c53f4e7294) | Skill compressed | The project optimized its own input footprint. |
| [`2b10489`](https://github.com/JuliusBrussee/caveman/commit/2b10489888fd433e31ac8f182a9b6c1e814906e1) | Three-arm eval | A terse control was introduced. |
| [`4e91954`](https://github.com/JuliusBrussee/caveman/commit/4e919547fbe44accc43d8cf395e67003bc68a946) | SessionStart injection | Manual style became persistent Claude behavior. |
| [`3ed7b73`](https://github.com/JuliusBrussee/caveman/commit/3ed7b732b02e6eaaefb92d4bdc60f29b4d9e743e) | Per-turn reinforcement | Persistence added repeated prompt cost. |
| [`5ad8f6d`](https://github.com/JuliusBrussee/caveman/commit/5ad8f6d684135b45e227e95a9c37c1d57098c7f9) | Security hardening | Symlink/config threats became explicit. |
| [`31fa954`](https://github.com/JuliusBrussee/caveman/commit/31fa95478d8c08a27a0685319539cbff5a9cca2c) | Stats/statusline | Estimated savings became a product surface. |
| [`4f2314a`](https://github.com/JuliusBrussee/caveman/commit/4f2314ae43c987a77a236b493c41dcae50140aeb) | Unified installer | Adapter accumulation centralized in Node. |
| [`8b8068d`](https://github.com/JuliusBrussee/caveman/commit/8b8068d8ca0d0f0f60d5bd02c3f48b1ec183bf9b) | Native OpenCode | Cross-harness support required a dedicated runtime adapter. |
| [`7b2bed2`](https://github.com/JuliusBrussee/caveman/commit/7b2bed2d0b7237ebc8f3e980258e5a8bdd821da1) | OpenClaw | Another harness added another injection mechanism. |
| [`f06348c`](https://github.com/JuliusBrussee/caveman/commit/f06348cbd36e16b5c142a930b87878c7868a499a) | Language/self-reference guard | Output defects were corrected doctrinally. |
| [`335ab56`](https://github.com/JuliusBrussee/caveman/commit/335ab56dea99cb224822fe1ef26384cb83d2aa93) | Honest numbers | Scope limits and net-negative cases became first-class docs. |
| [`6919dc2`](https://github.com/JuliusBrussee/caveman/commit/6919dc2c4fb068eb4586c113985b1a14326c356d) | Stats label correction | Displayed “savings” needed qualification. |
| [`a884696`](https://github.com/JuliusBrussee/caveman/commit/a8846964b5ab10629ded5e3111ddf293810b7c15) | MCP package fix | Published file lists can invalidate otherwise correct source. |
| [`e9cb843`](https://github.com/JuliusBrussee/caveman/commit/e9cb8435d69a7611fa510ed0f1780aab5629b29f) | Mode attribution fix | Current-state attribution had overstated historical savings. |
| [`e2c09c9`](https://github.com/JuliusBrussee/caveman/commit/e2c09c9a7e66d6bb30cadb5f955bd8a36b0e8d9a) | Flat 65% messaging | Marketing simplification removed an important control comparison. |

Nine issues and one directly relevant pull request were studied: issues
[#145](https://github.com/JuliusBrussee/caveman/issues/145),
[#234](https://github.com/JuliusBrussee/caveman/issues/234),
[#249](https://github.com/JuliusBrussee/caveman/issues/249),
[#392](https://github.com/JuliusBrussee/caveman/issues/392),
[#418](https://github.com/JuliusBrussee/caveman/issues/418),
[#506](https://github.com/JuliusBrussee/caveman/issues/506),
[#550](https://github.com/JuliusBrussee/caveman/issues/550),
[#597](https://github.com/JuliusBrussee/caveman/issues/597), and
[#601](https://github.com/JuliusBrussee/caveman/issues/601), plus
[#261](https://github.com/JuliusBrussee/caveman/pull/261). They were selected as
counterexamples or evidence about claims, Windows/config safety, duplicate hooks,
OpenCode lifecycle, packaging, pinning, and attribution—not as a popularity
sample.

Status below was observed on the audit date; issue pages are living records, not
commit-pinned source snapshots.

| Thread | Observed status | Counter-evidence or correction |
|---|---|---|
| [#145](https://github.com/JuliusBrussee/caveman/issues/145) | Closed | User reported roughly 1–1.5k instruction overhead and net-negative terse Q&A; not a controlled reproduction. |
| [#234](https://github.com/JuliusBrussee/caveman/issues/234) | Open | Challenged the ~75% claim using the repository’s own versus-terse eval; drove the temporary 50–65% wording. |
| [#249](https://github.com/JuliusBrussee/caveman/issues/249) | Closed | PowerShell quoting broke a Windows settings merge; later unified Node handling addresses the class of failure. |
| [#392](https://github.com/JuliusBrussee/caveman/issues/392) | Closed | Plugin plus standalone hook wiring caused duplicate injection; current installer avoids it by default. |
| [#418](https://github.com/JuliusBrussee/caveman/issues/418) | Closed | OpenCode callbacks did not fire; the adapter migrated to the current event/plugin shape. |
| [#506](https://github.com/JuliusBrussee/caveman/issues/506) | Open | Shorter output did not reduce a per-request/credit charge. |
| [#550](https://github.com/JuliusBrussee/caveman/issues/550) | Open | User reported higher token counters and elapsed time; configuration/workload details are insufficient to reproduce it. |
| [#597](https://github.com/JuliusBrussee/caveman/issues/597) | Open | npm package omitted `spawn-options.js`; source package list is fixed, publication remains unknown. |
| [#601](https://github.com/JuliusBrussee/caveman/issues/601) | Open | Stats credited a mixed session to the current mode; current code attributes per transition, old history remains unrepairable. |
| [PR #261](https://github.com/JuliusBrussee/caveman/pull/261) | Open | Proposed immutable download references; current internal fallback pins hooks, but headline bootstraps still follow moving `main`. |
