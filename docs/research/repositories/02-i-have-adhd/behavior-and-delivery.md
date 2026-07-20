# Behavior and delivery

## Mechanism in one sentence

The repository packages one unchanged Markdown instruction set behind provider
discovery metadata: the harness advertises a short description, loads the full
skill when selected, and asks the model to make answers immediately actionable,
ordered, state-aware, and low in conversational filler [E04, E19-E24].

That is an instruction mechanism, not enforcement. It has no hook, validator,
runtime state, test, or benchmark [E03, E16].

## Delivery reconstruction

Official harness documentation was consulted on **2026-07-20**. No plugin or
adapter was installed, and no runtime behavior test was performed.

### Harness matrix

| Harness | Support declared | Support verifiable | Entry | Loading | Scope | Limits |
|---|---|---|---|---|---|---|
| Claude Code | Yes, as a marketplace plugin and optional user-level always-on reminder. | Packaging layout matches current plugin docs. Invocation string and update claim are not fully current/verifiable. | Repo says `/i-have-adhd`; current official plugin namespace implies `/i-have-adhd:i-have-adhd`. Model may also invoke from description. | Skill description is discovery context; full `SKILL.md` loads on invocation and persists in that session. | Install defaults to user; official CLI also supports project/local. Always-on `~/.claude/CLAUDE.md` is global to local Claude sessions. | No alias file remains; `/i-have-adhd` may fail. Marketplace installs are cached. No behavior enforcement or eval. |
| Codex | Yes, added by PR nº1. | Manifest/catalog schema and current CLI syntax are verifiable; PR validation did not test responses. | Explicit `$i-have-adhd`; implicit selection allowed and description-driven. | Initial context has name/description/path; full `SKILL.md` only when selected. New session required after plugin install. | CLI/desktop install is kept in Codex configuration/cache; repo catalog can also be discovered at repo scope. | Universal trigger is only a description claim. README omits non-destructive browser toggle. Version is fixed at `0.1.0` while source ref floats at `main`. |
| OpenCode | Requested, not declared as delivered. | The frontmatter is structurally compatible after manual placement, but the snapshot is not in a discovered path. | Theoretical native `skill` tool after copying to a supported skill directory. | Name/description listed; body loaded on demand. | Project or global according to `.opencode/skills`, `.claude/skills`, or `.agents/skills`. | Root `skills/` is not scanned; no OpenCode adapter, install docs, manifest, or test. Issue nº6 remains open. |

Sources: OpenAI [skills](https://developers.openai.com/codex/skills),
[plugins](https://developers.openai.com/codex/plugins), and
[plugin authoring](https://learn.chatgpt.com/docs/build-plugins); Anthropic
[skills](https://code.claude.com/docs/en/slash-commands),
[plugins](https://code.claude.com/docs/en/plugins), and
[plugin reference](https://code.claude.com/docs/en/plugins-reference); OpenCode
[Agent Skills](https://opencode.ai/docs/skills) [E19-E26].

### Claude Code path

1. **Installation.** README clones the repository locally, registers that root as
   a marketplace, and installs `i-have-adhd@i-have-adhd`. Current Anthropic docs
   confirm local marketplace sources and plugin install; default scope is user,
   with project/local alternatives [E11, E24-E25].
2. **Discovery.** Enabled plugin components are indexed. The skill description is
   present in regular-session discovery context. The full 1,299-token body is not
   loaded until the user or model invokes it [E23, E27].
3. **Explicit invocation.** The repository says `/i-have-adhd`. Current official
   docs namespace plugin skills as `/plugin-name:skill-name`, giving
   `/i-have-adhd:i-have-adhd`. The earlier flat command that provided the shorter
   name was deleted in `2e125fa`; therefore the short form is **Unknown** without
   a prohibited runtime installation [E10, E24].
4. **Implicit invocation.** Claude may invoke skills based on their description
   unless model invocation is disabled. The frontmatter's “ANY user message” is
   visible routing text, but model choice is not deterministic enforcement [E05,
   E23].
5. **Always-on.** `INSTALL.md` asks the user to place a 39-token payload in
   `~/.claude/CLAUDE.md`. That global instruction persists across local sessions.
   It mentions five themes and refers to the skill but does not embed/import its
   complete ten rules. Whether the reference itself forces full skill loading is
   unverified; broad implicit matching may do so [E28].
6. **Disable.** Official `claude plugin disable`/`enable` accepts a name or
   `plugin@marketplace` and can detect install scope. Repository syntax is
   plausible. Disabling removes the plugin's discovery contribution but would not
   remove a separately copied always-on `CLAUDE.md` instruction.
7. **Update.** The repo says `git pull` and that the next session re-reads the
   local checkout. Current docs say marketplace installs are copied into a cache
   and expose `claude plugin update`. The exact behavior of this local path plus
   relative source was not runtime-tested, so the README's automatic refresh
   sentence is **Unknown** and potentially outdated [E25].
8. **Uninstall.** `claude plugin uninstall` plus marketplace removal matches the
   current management model. Removing the plugin still leaves any user-added
   always-on text; the README does not call out that cleanup.
9. **Persistence.** Installed/enabled state survives sessions at its configured
   scope. Once invoked, rendered skill content stays in the current conversation;
   it is not automatically a durable cross-session work ledger.

### Codex path

1. **Marketplace.** `.agents/plugins/marketplace.json` describes one Git-backed
   plugin at floating `main`; `.codex-plugin/plugin.json` declares `./skills/`,
   version `0.1.0`, and presentation metadata [E12].
2. **Installation.** `codex plugin marketplace add ayghri/i-have-adhd --ref main`
   and `codex plugin add i-have-adhd@i-have-adhd` match official docs and local
   `codex-cli 0.144.6 --help` [E21]. No install was run.
3. **Discovery versus load.** Codex initially exposes name, description, and path
   under a bounded skill-list budget. Full `SKILL.md` loads only on invocation.
   `.codex-plugin/plugin.json` is install-surface metadata; `openai.yaml` adds UI
   copy and invocation policy. Neither replaces the body [E19-E20].
4. **Explicit invocation.** `$i-have-adhd` is the documented CLI/IDE mention form
   and matches official skill documentation.
5. **Implicit invocation.** `allow_implicit_invocation: true` preserves the
   default and the description explicitly targets nearly every request. Codex can
   still decline to select it; “always” is declared, not enforced [E05, E20].
6. **Update.** Marketplace `upgrade` refreshes the snapshot; remove/add refreshes
   the installed plugin, matching the current CLI help. The catalog ref is
   `main`, so refresh can bring unreviewed upstream changes; version `0.1.0` does
   not identify the audited SHA.
7. **Disable and uninstall.** Official `/plugins` browser permits toggling an
   installed plugin off; the README only documents `remove`. CLI `plugin remove`
   plus marketplace removal is valid uninstall. Removing the marketplace before
   the plugin would make later refresh/reinstall unavailable.
8. **Scope and persistence.** Installed bundles are cached and enable/disable
   state is stored in Codex configuration. Newly installed skills appear in a new
   session. Conversation state generated while using the skill is not a
   cross-session repository record [E22].
9. **What PR nº1 proves.** It proves that a contributor created parseable package
   metadata and reports a temporary-home add/list exercise. It does not prove
   implicit routing frequency, rule adherence, improved task completion, ADHD
   accessibility, or reduced tokens [E13].

`policy.authentication: ON_INSTALL` is required marketplace policy metadata in
current examples, even though this instruction-only plugin has no app or external
authentication dependency. It should not be read as evidence of a credentialed
service.

### OpenCode path

OpenCode's official Agent Skills mechanism would accept the existing `name` and
`description`, and its native skill tool would disclose the body on demand.
However, it scans `.opencode/skills`, `.claude/skills`, and `.agents/skills`, not
the snapshot's root `skills/` directory [E26]. Therefore:

- cloning this repository alone does not provide documented discovery;
- manual copying into a supported directory is theoretically sufficient, but no
  such operation was performed and the repo does not document it;
- `opencode plugin` refers to a different npm-plugin mechanism and is not
  provided by this repository;
- issue nº6 correctly describes missing official distribution, not proven
  behavioral incompatibility [E17].

## Ten rules, decomposed

The “permanent” and “conditional” columns are audit dispositions, not project
decisions. “Small model” is an inference about instruction complexity; Qwen or
another local model was not run.

| Rule | Problem and expected mechanism | Potential benefit | Token/cognitive cost | Failure risks | Small-model fit | Permanent? | Conditional? | Evaluation needed |
|---|---|---|---|---|---|---|---|---|
| 1. Lead with next action | Reduce action-selection friction by placing an executable step first. | Fast scanning in procedural help; clearer initiation. | Often saves preamble, but can add a command plus later explanation. Reader may act before seeing constraints. | Ambiguous when the task is informational; can hand work to the user that an agent should perform; can suppress prerequisites or warnings. | Simple imperative is easy; role confusion (“who acts?”) is dangerous. | No, not for all messages. | Yes, for user-owned or approval-blocked action; agent-owned action should be executed. | Task completion, premature actions, safety-warning retention, needless handoffs. |
| 2. Number multi-step tasks | Chunk ordered work into bounded actions. | Sequence and resume point become visible. | Markers add few tokens; over-segmentation increases length and makes prose mechanical. | False ordering for independent facts; “one action” can hide dependencies. | Good if phrased as “only when order matters.” | Candidate short default for genuine procedures, still deferred. | Yes for ordered work, not ordinary exposition. | Step omission, reorder errors, comprehension and output length. |
| 3. End with one next action | Turn open work into one low-friction continuation. | Reduces choice overload during interactive work. | Adds a tail to every incomplete answer and can duplicate the first action. | Creates needless user handoff, ignores multiple critical branches, or invents a next step after completion. | Easy syntax, but conflicts with autonomous completion. | No. | Only when work is genuinely blocked on user action or user requested coaching. | Handoff rate, unnecessary questions, autonomy completion. |
| 4. Suppress tangents | Preserve focus by separating secondary issues. | Limits scope drift and mid-fix interruption. | Can save tokens; asking “want me to handle it?” adds a turn/retry. | Critical security, data-loss, or dependency information may be mislabeled a tangent; one-issue serialism can be inefficient. | Good with an explicit “never omit blockers/safety.” | Candidate principle, not literal rule. | Prioritize; defer non-blocking extras, surface critical constraints now. | Critical-information recall, extra turns, scope adherence. |
| 5. Restate state every turn | Externalize current step and completed outcome in chat. | Helps resume after interruption and makes progress inspectable. | Recurring output tax proportional to turns and state size; reader must rescan duplicates. | Stale state, contradiction with disk/plan truth, clutter, false completion. | Repetition may reinforce; long state competes with task instructions. | No. | State delta plus next unresolved item in long collaborative work; full state only when requested or UI unavailable. | State accuracy, duplicate tokens, recovery after interruption. |
| 6. Specific time estimates | Replace vague effort language with concrete ranges. | Can support planning when grounded in measured work. | Adds text and estimation effort. | False precision/hallucination, especially without environment, user speed, tests, or queue information. | Smaller models may fabricate confident numbers. | Reject as unconditional. | Only with evidence, explicit assumptions/range, or observed duration. | Calibration error, user trust, sensitivity to missing variables. |
| 7. Make completed work visible | State the verified outcome rather than burying it. | Improves auditability and confidence; supports handoff. | Adds a progress line; repeated “wins” can become celebratory noise. | Claims success without validation; tension with “no recap”; reward framing may infantilize. | Good if “report verified result” replaces “make wins.” | Candidate as factual completion reporting, deferred. | At milestones/final handoff; state evidence and remaining uncertainty. | False-success rate, verification citation, recap duplication. |
| 8. Matter-of-fact errors | Replace affective filler with cause, evidence, and fix. | High signal; avoids dramatization and blame. | Usually neutral or saving; diagnosis detail may add useful tokens. | A premature “cause” can overstate uncertainty; deleting calibrated hedging is unsafe. | Good with explicit uncertainty vocabulary. | Strong kernel candidate, not adopted. | Default when reporting failures; distinguish observation, hypothesis, fix. | Root-cause accuracy, uncertainty calibration, tone preference. |
| 9. Cap lists at five | Force prioritization and chunk long enumerations. | Can make the first action set scannable. | Splitting into “now/later” adds headings and may increase tokens. | A sixth critical constraint can disappear; arbitrary cap confuses completeness tasks. | Hard numeric constraint is easy but can dominate content quality. | Reject hard cap. | Prefer ranked/chunked lists when long; never cap required exhaustive output. | Omission rate, scan success, critical sixth-item tests. |
| 10. No preamble/recap/closers | Remove social and meta filler; start/end on content. | Direct answers and fewer low-value tokens. | Saves filler, but a necessary warning/context/handoff summary is not filler. | Conflicts with final verification, informed consent, safety warning, and “make completed work visible.” | Multiple prohibitions and phrase bans can consume attention and cause brittle deletion. | Adapt only the filler-removal intent. | Remove non-informative phrasing; preserve necessary framing and final handoff. | Token savings, missing caveats, handoff completeness, user preference. |

Risk levels make the three requested failure dimensions explicit for every rule:

| Rule | Ambiguity | False precision | Important-information suppression | Why |
|---|---|---|---|---|
| 1 | High | Low | High | “Action” and actor are unspecified; prerequisites can arrive after the command. |
| 2 | Medium | Low | Medium | Artificial ordering/bounds can conceal dependencies or parallelism. |
| 3 | High | Low | High | One action can erase legitimate branches and force a user handoff. |
| 4 | High | Low | High | “Tangent” is subjective; a secondary security fact may be critical. |
| 5 | Medium | Medium | Low | State can become stale or falsely declare completion; main risk is duplication. |
| 6 | Medium | High | Medium | Concrete units look authoritative and can displace uncertainty/dependencies. |
| 7 | Medium | Medium | Medium | “Works” may overclaim validation and omit remaining failures. |
| 8 | Medium | High | Medium | A crisp cause/fix can hide that the cause is only a hypothesis. |
| 9 | Low | Low | High | The numeric cap directly risks dropping required item six and beyond. |
| 10 | Medium | Low | High | Blanket deletion can remove warnings, caveats, and final verification. |

## Three operating contexts

| Rule | A. Informative response | B. Collaborative work | C. Autonomous execution | Guard condition |
|---|---|---|---|---|
| 1 | Lead with the answer, not necessarily an action. | Lead with what the agent is doing or the user decision truly needed. | Execute safe in-scope next action instead of prescribing it. | Assign the action to the actor who owns it. |
| 2 | Number only procedures or ordered arguments. | Useful for short plans and checkpoints. | Keep plan internal/tool-backed; final output need not replay every step. | Use ordering only when dependency/order exists. |
| 3 | Usually omit; answer can end complete. | Ask one concrete user action only at a real dependency. | Usually harmful: continue until terminal or blocked. | No synthetic handoff. |
| 4 | Defer optional sidebars, retain qualifications. | Park non-blocking scope; mention impact. | Record later work without abandoning required mission items. | Safety/blockers are never tangents. |
| 5 | Usually unnecessary. | Report changed state and next unresolved item. | Persist state in plan/files when useful; avoid narration for every tool call. | Delta, not full replay. |
| 6 | Give no estimate unless asked and grounded. | Range plus assumptions can aid coordination. | Do not pause work to invent duration; report actual progress. | Evidence and uncertainty required. |
| 7 | Not applicable unless explaining a result. | Report verified milestones. | Final handoff must state validations and remaining unknowns. | “Works” requires evidence. |
| 8 | State uncertainty/failure plainly. | Same, with diagnostic evidence. | Same; continue fixing if authorized rather than handing off immediately. | Separate symptom, hypothesis, cause, remedy. |
| 9 | Exhaustiveness controls length, not five. | Chunk/prioritize long option sets. | Never omit requirements from a mission checklist. | Completeness overrides presentation preference. |
| 10 | Remove filler; retain definitions and caveats. | Brief updates may need orientation. | Final recap/handoff is necessary for verification. | Informative framing is allowed. |

These guards resolve the mission's named failure modes:

- “next action” becomes actor-aware, so an agent does agent-owned work;
- a final next action appears only at a genuine user dependency;
- state is reported as a delta and anchored to a plan/file when durable state is
  necessary;
- time ranges require evidence and assumptions;
- list chunking never licenses omission;
- final recaps remain when they provide verification or transfer state;
- progress is evidence-based, not a repeated reward slogan.

## Five cognitive premises

The repository labels these as “facts,” but they range from group-level research
findings to clinical/pedagogical simplifications and metaphors [E06]. The analysis
below is not medical advice.

| Exact repo claim | Identifiable support | Scientific support and variation | Reasonable ergonomic implication | Unsupported deduction | Neutral universal reformulation |
|---|---|---|---|---|---|
| “Working memory is small” | Adult meta-analysis found moderate average verbal/visuospatial working-memory differences across 38 studies [E30]. NIMH lists remembering tasks as one possible difficulty [E32]. | Moderate group difference; tasks/moderators vary and deficits were not uniform. Every human has bounded working memory; not every person with ADHD forgets all off-screen information. | Keep prerequisites and current state easy to recover; use durable references for long work. | Repeat the entire state every turn for every diagnosed reader. | “Keep the current goal and next unresolved step easy to recover.” |
| “Knowing the answer is not doing the answer” | Routledge describes difficulty turning intentions into action as the book's organizing problem [E35]; NIMH lists procrastination and incomplete projects [E32]. | Clinically plausible functional difficulty, but this aphorism is not a measured universal law and is not specific to ADHD. | Reduce the gap between explanation and an appropriate executable step. | Every response must begin/end with a user action. | “When action is requested, make ownership and the next executable step clear.” |
| “Starting is the hardest step” | Book table of contents includes getting started; NIMH describes procrastination/large-task difficulty [E32, E35]. | Initiation can be difficult, but “hardest” is an absolute ranking unsupported across people/tasks. Anxiety, ambiguity, environment, motivation, and task value can change the bottleneck. | Offer a small first step when the user is responsible for starting. | Always reduce work to a sub-two-minute action, including autonomous agent work. | “If initiation is the blocker, reduce the first user-owned step.” |
| “Time estimates feel uniform” | A 2024 meta-analysis finds a mean time-perception difference with moderators [E31]; NIMH lists time-management difficulty [E32]. | Supports an average difference in experimental time perception, not semantic equivalence of vague and long durations or universal benefit from minute estimates. | Avoid vague effort claims; expose uncertainty and dependencies. | Fabricate precise minutes without calibration. | “Use measured durations or ranges with assumptions; otherwise describe dependencies.” |
| “Dopamine is scarce” | PET and fMRI literature studies selected dopamine/reward measures [E33-E34]. | This phrase collapses regional binding, reward anticipation, motivation, medication, and heterogeneous samples into a global quantity. Visible progress may be useful, but the repo provides no dopamine-mediated interface evidence. | Make verified progress discoverable and acknowledge completion neutrally. | Progress text raises dopamine or benefits every ADHD reader. | “Report verified outcomes and remaining work at useful checkpoints.” |

### Book-reference boundary

The identifiable source is the first edition of *The Adult ADHD Tool Kit: Using
CBT to Facilitate Coping Inside and Out*, J. Russell Ramsay and Anthony L. Rostain,
Routledge, copyright 2015. Its publisher frames it as a consumer coping guide and
companion to a professional CBT manual [E35]. The repository says only “loosely
based” and provides no page/chapter mapping. A clinically informed self-help book
does not by itself validate these five exact premises, their universal wording,
or the ten LLM rules derived from them.

### Risks of the medical framing

- Five selected traits do not define ADHD, which NIMH describes through varied
  inattention, hyperactivity, impulsivity, severity, persistence, and functional
  impairment [E32].
- Accessibility is not identical to brevity. Some readers need examples,
  definitions, redundant cues, or complete option sets.
- “The reader cannot hold…” and “dopamine is scarce” can infantilize or reduce a
  person to a diagnosis.
- A universal procedural style can make conceptual, emotional, exploratory, or
  casual exchanges unnatural.
- Individual preferences and task demands should control presentation. A neutral,
  user-configurable framing is more portable than assuming a diagnosis.

## Behavioral quality tensions

| Tension | Audit resolution to test |
|---|---|
| Action-first vs context | Answer/outcome first; action first only when action is the requested outcome and its actor is clear. |
| Brevity vs exhaustiveness | Remove filler; never remove requirements, caveats, evidence, or safety constraints. |
| Visible state vs duplication | Show state delta; link or read durable state rather than replaying it. |
| Temporal precision vs hallucination | Measured range + assumptions, or no numerical estimate. |
| Priority vs forgetting | Rank/chunk all required items; do not impose a hard count. |
| Visible progress vs noise | Report milestone changes and evidence, not every microstep. |
| No preamble vs warning | Warnings and necessary orientation are content, not preamble. |
| No recap vs verifiable handoff | Final validation/status/unknowns are required operational state, not filler. |
| Universal invocation vs relevance | Keep discovery description bounded; activate richer behavior for long/procedural work or explicit preference. |

The repo's near-universal description is technically a routing signal, not a
guarantee [E05, E20, E23]. It is compatible with progressive disclosure at the
mechanical level—the body is on demand—but undermines it behaviorally if almost
every request matches and causes a 1,299-token load. Short factual questions and
casual exchanges have little opportunity to amortize that cost [E27-E28].

A smaller kernel could capture the plausible core without the medical absolutes:

```text
Give the answer or verified outcome first. For ordered work, use short numbered
steps. Perform safe agent-owned steps yourself. Report only changed state and the
next real dependency. Keep required context, safety constraints, and final
verification; remove non-informative filler.
```

This is a **Candidate principle formulation**, not adopted doctrine and not yet
tested on any model.

## Externalizing work state

Issue nº3 proposes plan/task tools as a mechanism separate from the current skill
[E15]. Five locations have different semantics:

| State location | Context/token cost | Human recovery | Persistence | Portability / failure mode |
|---|---|---|---|---|
| Conversation history only | Already consumes context; compaction can summarize/drop detail. | Requires scrolling/search. | Session-dependent. | Broadly available but ephemeral and provider-shaped. |
| Repeated in every output | Recurring cost proportional to turns and state length. | Immediately visible. | Only while transcript exists. | Portable prose, but noisy, stale, and self-contradictory. |
| Harness plan/task tool | Compact UI can avoid prose replay; tool state may still enter context. | High while UI is visible. | Harness/session-specific unless exported. | Useful ergonomics, low provider neutrality, tool may be absent to a local model. |
| Workspace file | Paid when read/updated, not every reply; diffable. | Inspectable outside chat. | Durable across sessions and models. | Most portable, but risks stale/bloated state and requires explicit ownership/update rules. |
| Cross-session handoff | Compact summary plus pointer can bound reload cost. | Designed for fresh sessions. | Durable if stored outside transient chat. | Portable if format is plain and canonical; lossy if summary is the only truth. |

The hypothesis “externalize working state outside human memory and ephemeral
conversation” survives this comparison as a useful candidate [E37], with two
qualifications:

1. externalization is not synonymous with repetition;
2. a harness plan is a view/cache unless it has defined persistence and transfer.

For EGX_Terminal, a portable principle may be stronger than any one plan-tool
implementation, but this audit does not select the storage layer or architecture.

## Isolated projection to EGX_Terminal

1. **True message without the label.** Reduce the distance between an agent's
   response and the next correct action while keeping progress recoverable [E36].
2. **Cognitive accessibility.** Chunk ordered work, expose priority and state,
   reduce irrelevant prose, and support resumption—when they match the user's
   needs.
3. **General agent communication.** Plain failures, actor-aware next steps,
   verified outcomes, scope control, and concise handoff are broadly useful.
4. **Likely token reducers.** Removing social filler and irrelevant tangents;
   avoiding full-state recaps when a delta/pointer suffices.
5. **Likely token increasers.** Full skill invocation, state on every turn,
   progress lines, numbered microsteps, estimates, repeated next actions, and
   extra question/answer turns.
6. **Possible minimal-kernel candidates.** Answer/outcome first, actor-aware
   autonomy, factual failure reporting, safety/exhaustiveness overrides, and
   state delta—not the ten-rule bundle.
7. **Conditional rules.** Numbering, visible progress, state restatement, a next
   user action, and estimates.
8. **Keep outside the kernel.** Medical claims, universal trigger, hard five-item
   cap, mandatory time estimates, blanket recap ban, and diagnosis-specific tone.
9. **Chatbot versus worker.** A chatbot may recommend; a worker should act within
   scope, validate, and hand off only on a real dependency.
10. **Avoid needless handoffs.** Before asking, test whether the action is safe,
    authorized, and executable by the agent; if yes, do it.
11. **Externalize without replay.** Maintain one canonical ledger and report only
    the changed item plus a pointer; refresh full state on request or session
    transfer.
12. **Likely Qwen-friendly formulations.** Short positive imperatives with actor,
    trigger, and override: “Do safe agent-owned steps”; “Number steps only when
    order matters”; “Never omit safety or required constraints.”
13. **Likely small-model hazards.** Ten simultaneous prohibitions, arbitrary
    numbers, universal `ANY`, phrase deletion, contradictory no-recap/progress,
    mandatory estimates, and implicit exceptions far from the rule.
14. **Tests required.** Rule-by-rule ablation across three contexts; completion,
    omissions, retries, handoffs, token totals, state accuracy, time calibration,
    safety, and user comprehension; include a selected Qwen model.
15. **Do not copy.** Clinical absolutes, “dopamine is scarce,” diagnosis assumed
    from skill selection, fake precision, hard list cap, universal activation,
    or a claim that concise output is clinically validated.
16. **Value of the medical label.** It communicates intent and may help users find
    a preferred style, but it is less precise than the underlying interface
    principles and overstates their diagnostic specificity. Prefer opt-in
    preferences and neutral mechanisms unless clinical claims are actually
    sourced and evaluated.

All of these are provisional to this audit. No mechanism is adopted [E39].
