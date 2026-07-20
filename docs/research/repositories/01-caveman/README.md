# Audit 01 — JuliusBrussee/caveman

## Identity

| Field | Value |
|---|---|
| Repository | `https://github.com/JuliusBrussee/caveman` |
| Audited branch/commit | `main` at `0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0` |
| Upstream commit date | 2026-07-03 11:08:51 UTC |
| Tag | `v1.9.1` |
| Audit date | 2026-07-20 |
| Auditor | EGX_Terminal audit mission |
| License | [MIT at audited SHA](https://github.com/JuliusBrussee/caveman/blob/0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0/LICENSE) |
| Snapshot | 167 tracked files; full detached clone and history inspected |

The branch resolved to the same SHA recorded when the mission was prepared. The
checkout, origin, tag, license, integrity, and all tracked blobs were verified
without executing repository code ([E001](evidence-ledger.md#e001)).

## Verdict

Caveman is best understood as a **behavioral output-budget experiment wrapped in
a growing distribution product**. Its durable insight is not the branded grammar
or the 65% headline. It is that output density can be made an explicit, selectable
constraint, with normal-prose escape hatches for ambiguity, safety, irreversible
actions, and authored artifacts ([E005–E007](evidence-ledger.md#e005),
[E050](evidence-ledger.md#e050)).

The implementation is substantially deeper than a skill file. Claude gets hooks,
persistent state, per-turn reinforcement, stats, and a statusline. OpenCode gets a
native adapter and global rule. Gemini, Codex, OpenClaw, static-rule agents, and a
large skills-registry matrix each receive different subsets. This is conceptual
portability achieved through adapter accumulation—not one neutral enforcement
layer ([E008–E015](evidence-ledger.md#e008), [E060](evidence-ledger.md#e060)).

The evidence supports meaningful **visible-output reduction on two small Claude
experiments**, but not a universal 65%, preserved accuracy, or net session
savings. The current full skill costs roughly 1,245 estimated input tokens, more
than twice the prompt at the original benchmark commit. A 163-token static rule
captures much of the behavioral thesis at a fraction of the load, though its
relative effectiveness has not been directly tested ([E016–E034](evidence-ledger.md#e016)).

Security engineering around flags, configuration writes, backups, JSONC and
Windows is thoughtful. Counterweights are moving one-line installers, delegated
registry trust, incomplete cross-mechanism uninstall, a material network-boundary
contradiction in the file compressor, and an MCP compressor whose semantic
fidelity is asserted rather than measured ([E035–E046](evidence-ledger.md#e035)).

No EGX_Terminal adoption decision follows from this audit. The candidates below
must remain isolated until all five repository audits are complete.

## Mental model

```text
canonical behavior text
        │
        ├── Claude hooks ── mode flag/log ── stats/statusline
        ├── OpenCode plugin + global rule
        ├── Gemini/Codex/OpenClaw adapters
        ├── skills registry + project static rules
        │
        ├── Cavecrew (separate multi-agent product)
        ├── caveman-compress (LLM persistent-file rewrite)
        └── caveman-shrink (regex MCP-description proxy)
```

The upper branches inject behavioral instructions. Flags enforce only state, not
model obedience. Stats measure real output counters but estimate the avoided
counterfactual. The lower three branches are adjacent products and should not be
treated as necessary parts of the brevity thesis.

## The message after removing the brand

> Make response density an explicit, reversible mode. Preserve exact technical
> literals and the user’s language. Let clarity and safety override compression.
> Measure total cost against the input needed to sustain the behavior.

The first three sentences are strongly evidenced as design intent. The last is
the lesson produced by the audit: Caveman itself measures output better than it
measures net session cost ([E025–E030](evidence-ledger.md#e025)).

## Principal strengths

- Concrete boundaries preserve code, commands, errors, domain vocabulary, and
  user language; Auto-Clarity explicitly outranks style
  ([E005–E007](evidence-ledger.md#e005)).
- A small static rule demonstrates progressive delivery: not every harness needs
  the full skill, examples, hooks, agents, or statistics
  ([E015–E017](evidence-ledger.md#e015)).
- Claude mode state, one-shot restoration, mode-attributed accounting, defensive
  config writes, and silent-fail hooks are inspectable and mostly reversible
  ([E008–E009](evidence-ledger.md#e008), [E025–E026](evidence-ledger.md#e025),
  [E041–E044](evidence-ledger.md#e041)).
- The repository exposes prompts, benchmark code, an eval snapshot, known
  net-negative conditions, and issue-driven corrections instead of hiding all
  uncertainty ([E019–E026](evidence-ledger.md#e019),
  [E032–E033](evidence-ledger.md#e032)).
- Provider differences are made explicit in install code rather than claimed away;
  the result is useful evidence about adapter cost and fragility
  ([E010–E015](evidence-ledger.md#e010), [E049](evidence-ledger.md#e049)).

## Principal limitations

- The current flat 65% message combines a historical benchmark with a newer,
  much larger treatment and suppresses an important versus-terse comparison;
  technical accuracy is untested ([E021–E024](evidence-ledger.md#e021),
  [E033–E034](evidence-ledger.md#e033)).
- Output savings are repeatedly mistaken for broader economics. Input overhead,
  hidden reasoning, cache policy, latency, extra correction turns, and per-request
  billing are not jointly measured ([E027–E032](evidence-ledger.md#e027)).
- “Same product” means different context and behavior per harness. Codex automatic
  activation and Gemini import cost cannot be established statically
  ([E012–E018](evidence-ledger.md#e012), [E058](evidence-ledger.md#e058)).
- Manual copies, stale documentation, legacy installers, and one synchronization
  workflow create divergence surfaces ([E002–E004](evidence-ledger.md#e002),
  [E047](evidence-ledger.md#e047)).
- Persistent-file compression crosses a third-party boundary contradicted by root
  security docs, while MCP regex compression cannot prove semantic preservation
  ([E035–E040](evidence-ledger.md#e035)).
- No local/Qwen or genuine multi-model evidence supports transfer to EGX_Terminal’s
  target environment ([E024](evidence-ledger.md#e024),
  [E055–E056](evidence-ledger.md#e055)).

## Provisional Adopt / Adapt / Reject / Defer matrix

These labels classify ideas for later synthesis; they are not project decisions.

| Disposition | Candidate | Reason |
|---|---|---|
| Adopt as audit principle | Distinguish output reduction from net session economy | Prevents the headline metric from substituting for actual context/cost evidence |
| Adopt as audit principle | Clarity/safety overrides any density mode | Small permanent guardrail with high downside protection |
| Adapt later | Neutral density constraint with exact-literal and language preservation | Keep benefit while avoiding mandatory persona/telegraphic grammar |
| Adapt later | Minimal static/on-demand instruction and explicit break-even measurement | Better aligned with progressive disclosure and small-model context budgets |
| Adapt later | Bounded state files, marker fences, atomic config writes, scoped rollback | Useful implementation qualities if a future demonstrated need exists |
| Reject as template | Flat 65% claim or estimated “saved” counter without controlled session baseline | Evidence does not justify universality |
| Reject as template | Moving `curl\|bash` / `irm\|iex` bootstrap and broad auto-detected mutation | Excessive trust and mutation surface for public/local-first work |
| Reject as doctrine | Caveman persona, dropped grammar, or repeated reinforcement in the always-loaded kernel | Branding and cognitive cost are not necessary to state the core constraint |
| Reject as generic mechanism | LLM rewrite of canonical persistent doctrine | Structural checks do not preserve normative meaning; data crosses a provider boundary |
| Defer | MCP-description minimization | Relevant only if schema cost is material and tool-choice fidelity can be evaluated |
| Defer | Mode persistence, statusline, stats, agents | Each adds machinery and context; need must precede mechanism |
| Defer | Qwen/local-model use | No applicable evidence; test per model and task class |

This matrix follows [candidate principles E051–E054](evidence-ledger.md#e051).

## Controlled projection to EGX_Terminal

1. **What is the real message?** Explicit output constraints can remove habitual
   verbosity; make them reversible and subordinate to clarity. The grammar is a
   mnemonic, not the invariant ([E050](evidence-ledger.md#e050)).

2. **Which layer does it address?** Primarily visible output. Hooks and state make
   the style persistent; MCP shrink touches input descriptions; file compression
   touches stored context; Cavecrew touches orchestration. These extensions do
   not make the benchmark a whole-harness result.

3. **What survives deleting Caveman-specific files/phrasing?** A neutral density
   budget, no filler/tool narration, preservation of technical literals and user
   language, normal prose for safety/ambiguity/artifacts, explicit disablement,
   and measured break-even.

4. **What is genuinely LLM-agnostic?** Plain textual constraints, task-class
   escape hatches, deterministic accounting formulas, bounded local state, and
   the concept of on-demand loading.

5. **What is multi-harness only through adapters?** Detection, plugin/extension
   install, hook events, command syntax, config paths, statusline, flags, skill
   registry profiles, OpenClaw `SOUL.md`, and OpenCode event APIs
   ([E060](evidence-ledger.md#e060)).

6. **What is toxic in an always-loaded kernel?** Persona examples, six intensity
   variants, marketing claims, provider commands/paths, stats prices, agent roles,
   compressor instructions, per-turn reinforcement, and duplicated adapter text.

7. **What should remain a permanent guardrail?** Compression never outranks
   safety, irreversible confirmation, ambiguity resolution, exact technical
   literals, or clear authored artifacts. This is an audit candidate, not adopted
   doctrine ([E051](evidence-ledger.md#e051)).

8. **What should be on demand?** Aggressive density levels, wenyan modes, stats,
   benchmark interpretation, MCP shrink, file compression, installer guidance,
   Cavecrew, and provider-specific delivery.

9. **Is Caveman grammar useful?** It makes the mode memorable and can reduce
   function words, but no experiment isolates it from ordinary density
   constraints. It can be unpleasant or ambiguous. Evidence supports density,
   not the necessity of the persona.

10. **How can density remain pleasant?** Prefer short complete sentences; remove
    repetition before grammar; keep relation words where scope matters; state
    uncertainty; mirror the user’s language/tone; expand automatically for risk,
    ambiguity, teaching, or confusion.

11. **What might work with a small local model?** A single short neutral rule,
    explicit exact-literal preservation, and a simple clarity override. Smaller
    context is promising; actual adherence is unknown ([E055](evidence-ledger.md#e055)).

12. **What requires tests?** Every output ratio, every model/quantization, repeated
    reinforcement, mode detection, terse grammar, multilingual behavior, cache
    assumptions, correction turns, tool choice, and all local/Qwen claims.

13. **Is MCP description compression relevant?** Potentially, when schemas are a
    repeated dominant input. First prefer concise source descriptions; if a proxy
    is tested, measure token reduction and tool-selection/argument fidelity, not
    syntax alone ([E054](evidence-ledger.md#e054)).

14. **Is persistent-file compression safe?** Not generically. Canonical doctrine
    can lose exceptions or normative force even when headings and code survive.
    Require semantic invariants, human diff review, provenance, deterministic
    rollback, and no silent third-party transfer ([E053](evidence-ledger.md#e053)).

15. **What does full skill versus small rule teach?** Delivery cost differs by
    roughly 7.6× (~1,245 versus ~163 estimated tokens). Most context is levels,
    examples, metadata and nuance; the repository never directly measures their
    marginal benefit ([E016–E017](evidence-ledger.md#e016)).

16. **Can a much shorter instruction capture the benefit?** Plausibly much of it,
    but the only two-word control is a noisy single snapshot and did not reduce
    output there. A neutral intermediate rule must be tested rather than assumed
    ([E023](evidence-ledger.md#e023)).

17. **What proof would EGX_Terminal need?** Multi-arm, repeated, per-model and
    per-task trials measuring input, cached input, output, reasoning if exposed,
    latency, local prefill/KV cost, correctness, ambiguity, human preference,
    correction turns, and session totals. Report distributions and break-even
    bands, not one percentage.

18. **What must not be copied?** Branding as doctrine; provider-coupled canonical
    files; the 65% constant; estimated savings presented as observed; moving
    executable bootstrap; broad auto-mutation; hand-synchronized rule copies;
    unsafe compression of normative files; the compressor’s inaccurate network
    statement; or any adapter before demonstrated need.

## Important unknowns

- Whether the fixed `caveman-shrink` package was published and interoperates with
  current MCP transports ([E057](evidence-ledger.md#e057)).
- Exact current Codex plugin/hook loading and Gemini import expansion semantics
  ([E058](evidence-ledger.md#e058)).
- Effects on hidden reasoning, correctness, human correction turns, and full
  session latency/cost ([E027](evidence-ledger.md#e027),
  [E056](evidence-ledger.md#e056)).
- Transfer to Qwen/OpenCode and other small local models, including quantization
  sensitivity ([E055](evidence-ledger.md#e055)).
- Semantic failure rate of regex MCP description compression and LLM persistent
  compression on real doctrinal/tool corpora.
- Runtime results of the repository tests and installers; they were deliberately
  not executed under the mission’s trust boundary ([E048](evidence-ledger.md#e048)).

## Audit template coverage

| `AUDIT_TEMPLATE.md` rubric | Location |
|---|---|
| Repository identity, scope, version, license | This file: Identity; [repository map](repository-map.md#acquisition-and-inspection-boundary) |
| Executive summary and verdict | This file: Verdict, strengths, limitations, disposition matrix |
| Repository map and source-of-truth analysis | [repository-map.md](repository-map.md) |
| Installation, activation, lifecycle, harness matrix | [behavior-and-delivery.md](behavior-and-delivery.md#end-to-end-lifecycle) |
| Behavioral doctrine and boundaries | [behavior-and-delivery.md](behavior-and-delivery.md#behavioral-doctrine) |
| Context/token economics and break-even | [token-economics.md](token-economics.md) |
| Benchmarks/evals and claim validation | [token-economics.md](token-economics.md#benchmark-audit) |
| History, contradictions, issues/counter-evidence | [repository-map.md](repository-map.md#pivot-history); [token economics](token-economics.md#claims-and-corrections) |
| Security, trust, supply chain, reversibility | [behavior-and-delivery.md](behavior-and-delivery.md#installation-platform-handling-and-trust) |
| Portability and controlled project relevance | This file: Controlled projection |
| Adopt / Adapt / Reject / Defer | This file: Provisional matrix |
| Facts, claims, measurements, inferences, unknowns | [evidence-ledger.md](evidence-ledger.md) |
| Open questions and confidence | This file: Important unknowns; ledger confidence column |
| Reproducibility and methodology | [repository-map.md](repository-map.md#acquisition-and-inspection-boundary); [token-economics.md](token-economics.md#scope-and-accounting-model) |

No gap requiring a change to the shared audit template was found. A useful future
template refinement would be an explicit row for *treatment drift*—whether the
prompt measured historically is byte-identical or semantically equivalent to the
current one. This is methodological feedback only.

## Annex navigation

- [Repository map](repository-map.md): complete inventory, source/copy topology,
  distribution, tests/CI, pivot commits and issues.
- [Behavior and delivery](behavior-and-delivery.md): doctrine, lifecycle, harness
  matrix, hooks/state, agents, MCP, compressor, security and uninstall.
- [Token economics](token-economics.md): static footprints, recalculated evidence,
  benchmark/eval critique, thresholds, cache/billing/local-model implications.
- [Evidence ledger](evidence-ledger.md): claim-by-claim epistemic classification,
  pinned evidence, confidence, and notes.
