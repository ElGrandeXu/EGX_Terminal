# Token economics

## Measurement method

All content was read from Git blobs at
`72c33eee81ea439cf01991e93729adfce2ffc99e`, preserving canonical LF bytes.
Lines use `splitlines`; words are non-whitespace sequences; token estimates use
the already-installed `tiktoken 0.12.0` `o200k_base` encoding. No package was
installed [E27-E29].

`o200k_base` is a reproducible approximation, not a promise about Claude,
OpenCode/Qwen, or a particular Codex model. Harness-added wrappers and system
metadata were not available for measurement.

## Static measurements

| Item | Lines | UTF-8 bytes | Words | `o200k_base` tokens |
|---|---:|---:|---:|---:|
| `.agents/plugins/marketplace.json` | 21 | 414 | 36 | 123 |
| `.claude-plugin/marketplace.json` | 16 | 451 | 45 | 125 |
| `.claude-plugin/plugin.json` | 4 | 187 | 27 | 48 |
| `.codex-plugin/plugin.json` | 39 | 1,278 | 122 | 354 |
| `skills/i-have-adhd/agents/openai.yaml` | 7 | 237 | 26 | 57 |
| `skills/i-have-adhd/SKILL.md` | 120 | 5,209 | 898 | 1,299 |
| `SKILL.md` frontmatter, delimiters included | 4 | 481 | 70 | 94 |
| `README.md` | 99 | 2,806 | 403 | 776 |
| `INSTALL.md` | 98 | 2,250 | 295 | 647 |
| `LICENSE` | 21 | 1,069 | 169 | 224 |
| Claude always-on fenced block, lines 85–88 | 4 | 154 | 23 | 41 |
| Claude always-on payload, excluding closing fence | 3 | 150 | 22 | 39 |

The binary logo is excluded from token counts. The full text corpus is not loaded
as one prompt by either claimed harness; README, INSTALL, license, and manifests
primarily serve humans or install surfaces.

## Discovery, invocation, and always-on costs

### Discovery cost

Official Codex and Claude documentation agree on progressive disclosure:
regular discovery exposes a skill's identifying/listing text; full instructions
load when selected [E19, E23]. Therefore:

- **measured lower-level input:** 94 tokens for the skill's complete frontmatter;
- **actual discovery input:** harness-dependent name/description/path/list wrapper,
  not directly measured;
- **Codex-specific UI metadata:** 57 tokens in `openai.yaml`, but official docs
  describe it as optional appearance/policy metadata, not necessarily all model
  context;
- **plugin manifests:** 48+125 Claude tokens or 123+354 Codex tokens exist at
  installation/discovery surfaces, but there is no evidence that their complete
  JSON is injected into every model request.

It would be incorrect to sum all repository metadata and call it automatic model
context.

### On-invoke cost

The complete skill is approximately **1,299 tokens** before any harness wrapper
[E27]. For Claude, current docs say the rendered content enters the conversation
once and stays for the session; identical re-invocation adds a short note rather
than a second full copy. Codex likewise documents full loading on selection, but
this audit did not measure reinjection or compaction behavior.

### Always-on cost

The optional Claude `CLAUDE.md` payload is only **39 tokens**, but that figure is
not the full behavioral cost:

1. it becomes launch context in every applicable Claude session;
2. it names five themes, not all ten rules;
3. its reference to the installed skill may prompt implicit invocation, adding
   the approximately 1,299-token body once in the session;
4. the behavioral rules then shape later outputs, creating output-side costs even
   without repeated input injection.

The repo supplies no Codex or OpenCode always-on adapter. Codex's broad skill
description may cause frequent implicit selection, but “use on ANY message” is
not technically enforced [E05, E20].

## Duplication

An exact, whitespace-stripped, nonblank-line comparison found seven unique lines
shared by README and INSTALL, totaling 278 UTF-8 bytes and 91 tokens as a
de-duplicated set [E29]:

- two provider headings;
- one clone command;
- two Claude install commands;
- two Codex install commands.

Those lines occur 7 times in README and 14 times in INSTALL because provider
headings recur across lifecycle sections. Exact matching is a lower bound:

- README semantically repeats all ten skill rule names;
- before/after examples restate rules 1–4 and 10;
- five manifest/metadata descriptions paraphrase overlapping subsets;
- the always-on payload repeats five themes;
- install/disable prose is similar but not byte-identical.

This duplication mostly affects repository maintenance and human reading. Only
discovery descriptions, invoked skill content, and always-on instructions have a
plausible direct model-context cost.

## Output-side costs and savings

### Potential savings

- deleting non-informative openers, closers, and sidebars;
- avoiding irrelevant tangents;
- replacing verbose status narration with a short verified delta;
- ranking work so fewer clarification/recovery turns are needed.

### Potential additions

- numbers and one-action-per-step formatting;
- state repeated on every turn;
- a completion/progress sentence;
- a numerical estimate and its assumptions;
- an ending next action, even when the first line already gives it;
- extra user turns caused by “want me to handle that next?”;
- retries after omitted context, false precision, or an unnecessary handoff.

The repository measures none of these. “No filler” can save tokens while the
other rules increase them in the same response; net direction is task-dependent
[E16, E38].

## Break-even model

For one session, define:

```text
net gain = avoided output
         - discovery instructions
         - invoked instructions
         - repeated state/progress/structure/estimate output
         - retry or recovery output
```

More explicitly:

```text
G = O_avoided - I_discovery - n_invoke·I_skill
              - Σ(R_state + R_steps + R_progress + R_estimate + R_next)
              - O_retries
```

Known static inputs are `I_skill ≈ 1,299` tokens and a frontmatter upper-content
measurement of 94 tokens. `n_invoke` is normally expected to be one per session
after selection, but actual harness behavior was not measured. Every `O` and `R`
term requires observed model output; no number is invented here.

Break-even occurs only when avoided filler/tangents/retries exceed the instruction
and added-structure/repetition/retry costs. A low token count is not itself a
quality result: omitted constraints or more retries can make a shorter first
answer more expensive overall.

## Scenario analysis

| Scenario | Cost drivers | Possible benefit | Provisional net direction | Main unknown |
|---|---|---|---|---|
| Short factual question | A full 1,299-token invocation dwarfs a naturally short answer; next-action framing may be inapplicable. | Removes a sentence of filler at most. | Likely negative if invoked; discovery-only may be small. | Implicit invocation rate under the universal description. |
| Long explanation | Full instruction cost amortizes across a long body; headers and examples remain allowed. | Tangent/filler pruning and answer-first organization. | Indeterminate; could be positive if completeness is preserved. | Whether the rule bundle omits nuance or just reorganizes it. |
| Multi-step mission | Numbering, progress, and state add output each turn. | Better resume points, fewer lost requirements or recovery turns. | Indeterminate; state delta could help, full replay likely hurts. | Retry reduction and plan-tool versus prose cost. |
| Repetitive debugging | Repeated state/diagnostics add tokens; the three-failure exception adds a diagnostic question. | Suppressed random edits and clearer hypothesis changes may reduce retries. | Potentially positive only if it shortens the spiral. | Fix rate, number of turns, diagnostic accuracy. |
| Autonomous execution | Next-action and ending handoff rules may stop work early and create extra user turns. | Matter-of-fact errors and milestone evidence help verification. | Likely negative without actor-aware overrides. | Unnecessary handoff frequency and incomplete missions. |
| Small local model through OpenCode | Manual on-demand load plus 10 rules/4 exceptions/4 checks compete for limited instruction following; tokenizer differs from `o200k_base`. | Simple action/number/state primitives may be easy to follow. | Unknown; conflicting absolutes raise risk. | Qwen model/context size, prompt precedence, rule compliance, omissions. |

## “Reapplication every message”

Three meanings must be separated:

1. **Input reinjection:** not demonstrated. Claude documents one persistent
   invocation in a conversation; Codex does not say the full file is appended to
   every message.
2. **Behavioral influence:** intended on every later answer in the session; this
   can add state/progress/estimate/next-action tokens each turn.
3. **New session discovery:** always-on or broad descriptions recur across
   sessions, and a fresh invocation pays the body cost again.

Calling all three “the skill costs 1,299 tokens per message” would be unsupported.

## Evaluation status

There is no test directory, CI, benchmark, eval dataset, result table, telemetry,
or verified performance claim. Issue nº4 explicitly acknowledges the gap and
contains only an offer to define measurements [E16]. PR nº1's manifest validators
do not close it [E13].

## Deferred experimental protocol

Before adoption, run a factorial/ablation study rather than comparing the ten-rule
bundle only:

1. **Tasks:** balanced short information, long explanation, collaborative plan,
   repetitive debug, autonomous file change, and safety/exhaustive inventory.
2. **Conditions:** baseline; each rule alone; proposed neutral mini-kernel; full
   upstream skill; state-in-chat versus plan tool versus durable file.
3. **Models/harnesses:** selected frontier models and at least one named Qwen
   checkpoint through OpenCode, with fixed versions and temperatures/settings.
4. **Measures:** task correctness, required-item recall, unsafe omission,
   autonomous completion, user handoffs, turns/retries, input/output tokens,
   wall time, state accuracy, estimate calibration, and blinded human preference.
5. **Reporting:** prompts, fixtures, rubrics, confidence intervals, failure cases,
   tokenizer/model versions, and no medical efficacy conclusion from interface
   preference alone.

This protocol is deferred. No benchmark or adoption was added in this audit.
