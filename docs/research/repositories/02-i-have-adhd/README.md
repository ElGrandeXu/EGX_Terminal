# Repository audit — ayghri/i-have-adhd

## Observation identity

- **Repository:** <https://github.com/ayghri/i-have-adhd>
- **Observed commit:**
  [`72c33eee81ea439cf01991e93729adfce2ffc99e`](https://github.com/ayghri/i-have-adhd/commit/72c33eee81ea439cf01991e93729adfce2ffc99e)
- **Observation date:** 2026-07-20
- **Auditor:** EGX_Terminal mission 2
- **License:** MIT, from the pinned [`LICENSE`](https://github.com/ayghri/i-have-adhd/blob/72c33eee81ea439cf01991e93729adfce2ffc99e/LICENSE)
  [E01, E08]
- **Snapshot:** prepared SHA unchanged; clean detached checkout; 10 files, 10
  commits, 5 issues, and 2 pull requests inspected [E01-E03, E09, E14, E18].

## Verdict

This is a small, legible instruction package with a useful general idea: reduce
action-selection friction, make ordered work scannable, and keep progress
recoverable. Its strongest rules are ordinary agent communication principles,
not ADHD-specific mechanisms. Its clinical framing overgeneralizes group-level
findings, and its universal trigger turns progressive disclosure into near-
automatic loading without evidence of benefit [E30-E38].

**Provisional disposition:** extract and test a shorter, neutral, actor-aware set
of principles; reject the medical absolutes, hard list cap, fabricated time
precision, blanket recap ban, and universal invocation. No element is adopted as
EGX_Terminal doctrine by this audit [E39].

## What it is

- **Contents:** one 120-line `SKILL.md`, Claude and Codex plugin/catalog metadata,
  install prose, MIT license, README, and one logo. There is no executable current
  code [E03-E04].
- **Problem sought:** answers that bury an executable step, overload the reader
  with tangents, or make progress hard to recover [E06].
- **Behavior sought:** action-first responses, numbered procedures, one next
  action, focused scope, repeated state, concrete estimates, visible completion,
  plain errors, short lists, and no filler [E06].
- **Boundaries in the skill:** long explanations remain allowed; safety,
  destructive actions, repeated failed debugging, and real ambiguity override
  brevity [E07].
- **Explicit audience boundary:** README says no diagnosis is required, while the
  skill itself assumes “the reader has ADHD.” That mismatch broadens use but does
  not neutralize the clinical claims [E05-E06].

## Maturity

**Experimental prompt package.** The behavioral body has never changed from the
initial commit, while distribution evolved from copied user files to Claude
plugin mode and then Codex packaging. There are no tags, releases, tests,
benchmarks, CI, dependencies, or verified behavioral results [E08-E10, E12-E16].
An open Cursor PR appeared after the audited `main`, showing that provider
packaging remains active and that the mission's “unique PR” premise is now stale
[E18].

## Repository message

Once the ADHD label is removed, the repository argues that a useful agent should
minimize the reader's work of finding, ordering, and resuming the next relevant
action. It should distinguish verified progress from conversational ceremony and
keep secondary information from interrupting the current objective [E36].

This message divides into two parts:

- **cognitive accessibility candidates:** recoverable state, chunked ordered work,
  visible priority, and reduced irrelevant prose;
- **general agent quality:** actor-aware next steps, factual failures, verified
  outcomes, scope control, and complete final handoff.

Neither part requires assuming a diagnosis.

## Mechanism map

| Dimension | Finding |
|---|---|
| Main mechanism | Provider metadata makes one Markdown skill discoverable; the model follows it when selected. No enforcement exists [E04, E19-E24]. |
| Automatically visible | Skill name/description/path or listing text, bounded and harness-shaped; optional always-on text if the user adds it [E19, E23, E28]. |
| On demand | Full `SKILL.md`, explicitly by `$i-have-adhd` in Codex or a namespaced slash command in current Claude docs, or implicitly from the broad description [E20, E23-E24]. |
| Static cost | Full skill: 5,209 bytes, 898 words, about 1,299 `o200k_base` tokens; frontmatter: about 94 tokens; Claude always-on payload: about 39 tokens [E27-E28]. |
| Dependencies | No runtime/package/service dependency. Installation depends on Claude or Codex plugin infrastructure; manual OpenCode placement would depend on its native skill tool [E03, E21-E26]. |
| Provider coupling | Two provider manifests, two marketplaces, OpenAI metadata, provider-specific commands/naming/caches. The behavioral Markdown is largely portable [E11-E12, E24-E26]. |
| Model assumptions | Assumes strong compliance with ten interacting rules, four exceptions, and a pre-send deletion check. No model or Qwen evaluation exists [E16, E38]. |

## Strongest contributions

- **Instruction-only progressive disclosure:** one canonical behavioral file can
  be packaged behind thin provider metadata [E04, E19, E23].
- **Action ownership as the missing refinement:** the repo surfaces action
  friction, while the audit shows that workers must perform agent-owned work
  rather than hand it back [E36, E38].
- **State recoverability:** issue nº3 exposes a stronger possible principle—keep
  work state outside human memory and ephemeral chat—but its plan-tool proposal
  is not implemented or portable by itself [E15, E37].
- **Filler versus information distinction:** removing ceremony can save tokens;
  warnings, evidence, exhaustive constraints, and final verification must remain
  [E27-E29, E38].

## Principal risks

- **Clinical overreach:** moderate group differences and heterogeneous symptoms
  do not validate “anything off screen is forgotten,” uniform time perception,
  or “dopamine is scarce” [E30-E35].
- **Universal routing:** the description asks for invocation on virtually every
  message, including casual chat, so a 1,299-token body can be loaded where a
  one-line answer needs none [E05, E19-E20, E27].
- **Worker handoff failure:** “lead/end with an action” can tell the user to run a
  command the agent should run itself [E38].
- **Information loss/false precision:** a five-item cap, tangent suppression,
  recap ban, and mandatory estimates can omit a sixth critical fact or invent
  timing [E31-E32, E38].
- **Internal tension:** “restate state” and “make wins visible” add recaps that the
  final rule forbids; the exceptions do not fully resolve this [E06-E07].
- **Delivery drift:** current Claude docs namespace plugin skills and cache
  installs, while the repo documents a short command and checkout re-read; these
  require runtime verification [E24-E25].

## Provisional disposition matrix

Marks express this audit's recommendation for later synthesis, not adoption.

| Element | Adopt | Adapt | Reject | Defer | Reason |
|---|:---:|:---:|:---:|:---:|---|
| One canonical instruction body behind adapters |  | ✓ |  |  | Portable principle; current manifests remain provider-specific [E04, E11-E12]. |
| Answer/outcome before filler |  | ✓ |  |  | General value; use answer rather than action for informative tasks [E36, E38]. |
| Number ordered multi-step work |  | ✓ |  |  | Helpful when order matters; avoid proceduralizing prose. |
| End with one user action on every incomplete task |  |  | ✓ |  | Creates unnecessary handoffs in autonomous work [E38]. |
| Suppress non-blocking tangents |  | ✓ |  |  | Preserve safety, blockers, and required exhaustive information. |
| Restate full state every turn |  |  | ✓ |  | Recurring token/noise cost and stale-state risk [E27-E29, E37]. |
| Report only changed state plus durable pointer |  |  |  | ✓ | Strong candidate; storage/update design remains open [E37]. |
| Mandatory specific time estimates |  |  | ✓ |  | Encourages false precision; allow calibrated ranges with evidence only [E31, E38]. |
| Verified completion made visible |  | ✓ |  |  | Replace “wins/dopamine” with evidence-based milestone reporting [E33-E34]. |
| Matter-of-fact errors |  | ✓ |  |  | Preserve calibrated uncertainty; do not assert an unverified cause. |
| Hard five-item cap |  |  | ✓ |  | Arbitrary and unsafe for exhaustive/critical constraints [E38]. |
| Remove empty preambles/closers |  | ✓ |  |  | Token benefit plausible; do not remove warnings or handoff evidence. |
| Blanket no-recap rule |  |  | ✓ |  | Conflicts with verifiable final delivery and state transfer [E38]. |
| Universal implicit invocation |  |  | ✓ |  | Defeats relevance-based context economy and is not enforced anyway [E05, E19-E20]. |
| Plan/task tool as state store |  |  |  | ✓ | Useful UI but harness-specific and not necessarily cross-session [E15, E37]. |
| ADHD diagnosis as default framing |  |  | ✓ |  | Principles are broader; clinical absolutes and user assumption are unsupported [E30-E36]. |
| Rule-by-rule eval including Qwen |  |  |  | ✓ | Required before any behavioral decision [E16, E38]. |

## Portability assessment

### Portable principles

- load a detailed behavior profile only when relevant;
- make ordered work and current dependencies recoverable;
- report errors and verified outcomes plainly;
- remove filler without removing evidence or constraints;
- bind next actions to the actor responsible for them.

These are candidate interpretations, not demonstrated outcomes [E36-E38].

### Non-portable mechanisms

- Claude/Codex marketplace schemas, command syntax, cache and scope behavior;
- `openai.yaml` and `$skill` mention syntax;
- Claude plugin slash-command namespacing and user `CLAUDE.md` always-on text;
- plan/task UIs as the only state record.

These couplings follow the current provider discovery and persistence mechanisms
[E19-E26, E37].

### Hidden coupling

- selection depends on model interpretation of an unusually broad description;
- the `main` ref floats while the Codex manifest version is static;
- user-level installation and always-on settings live outside the repository;
- the skill presumes a conversational reader, not an autonomous worker;
- smaller local models may struggle with interacting absolutes and exceptions.

The final two points are inferences awaiting rule-level and Qwen evaluation
[E38].

## Unknowns

- Does the audited Claude package expose `/i-have-adhd` as an alias, or only the
  current documented `/i-have-adhd:i-have-adhd`? [E40]
- Does `git pull` alone refresh the cached Claude install, or is explicit plugin
  update/reload required for this local marketplace layout? [E40]
- How often do Claude and Codex implicitly invoke the near-universal description?
  [E41]
- What are actual discovery/on-invoke tokens for each harness/model wrapper?
  [E41]
- Do any rules improve completion, comprehension, resumption, or preference for
  ADHD users, non-ADHD users, or either group? [E42]
- Which individual rules cause omissions, retries, or unnecessary handoffs?
  [E42]
- How does a specified Qwen checkpoint behave through OpenCode after a legitimate
  adapter exists? [E42]
- Will open PR nº5 merge, and will issues nº6/nº7 result in new provider files?
  [E18]

## Audit conclusion

- **Strongest evidenced contribution:** a clear demonstration that action
  selection, ordered presentation, and visible state can be expressed in one
  small on-demand behavioral file [E04, E27, E36].
- **Largest context/maintenance cost:** universal selection of a 1,299-token rule
  bundle plus repeated state/progress/next-action output and duplicated
  provider-facing descriptions [E27-E29, E38].
- **Recommended disposition before synthesis:** retain only neutral candidate
  principles and rule-level test hypotheses; reject universal/clinical absolutes;
  defer state architecture and model-specific wording [E37-E39].
- **Deferred post-audit question:** can an actor-aware, delta-state mini-kernel
  outperform both baseline and the full ten-rule bundle across informational,
  collaborative, and autonomous tasks?

## Navigation

- [Repository map](repository-map.md): complete tree, files, history, manifests,
  duplication, issues, and both PRs.
- [Behavior and delivery](behavior-and-delivery.md): ten rules, five premises,
  three contexts, harness paths, scientific review, state externalization, and
  isolated EGX projection.
- [Token economics](token-economics.md): static measures, loading costs,
  break-even model, scenarios, and deferred experiment.
- [Evidence ledger](evidence-ledger.md): categorized evidence and source set.

## `AUDIT_TEMPLATE.md` coverage

| Required rubric | Where satisfied |
|---|---|
| Observation identity | `README.md` → Observation identity; `repository-map.md` → Snapshot and integrity |
| What it is | `README.md` → What it is; `repository-map.md` → File inventory |
| Mechanism map | `README.md` → Mechanism map; `behavior-and-delivery.md` → Delivery reconstruction |
| Automatic/on-demand context and cost | `token-economics.md` → Discovery, invocation, and always-on costs |
| Dependencies/provider/model assumptions | `README.md` → Mechanism map and Portability assessment |
| Portability assessment | `README.md` → Portability assessment; harness matrix in `behavior-and-delivery.md` |
| Disposition | `README.md` → Provisional disposition matrix |
| Risks, contradictions, unknowns, runtime claims | `README.md` → Principal risks and Unknowns; `behavior-and-delivery.md` → tensions |
| Evidence register | `evidence-ledger.md` |
| Repository message | `README.md` → Repository message |
| Audit conclusion | `README.md` → Audit conclusion |

The template itself was not modified. This audit remains isolated; it makes no
cross-repository comparison and no architecture decision [E39].
