# Token economics

## Scope and accounting model

Caveman’s headline number concerns visible output. A session has at least five
separate quantities:

```text
net effect = output avoided
           - instructions added
           - repeated activation/reinforcement
           - unchanged or changed reasoning
           - tool/schema and state overhead
           ± cache, price, latency, and billing-policy effects
```

Only the first two can be approximated from the committed corpus. Reasoning is
not observed. Cache behavior and prices are provider/version/account specific.
For a local model, money can be zero while prefill latency, KV memory, energy and
context displacement remain real costs ([E027](evidence-ledger.md#e027)).

## Static prompt footprint

Counts below use exact Git blob bytes and LF line structure. “Words” are
whitespace-delimited. Token columns are estimates from locally available
`o200k_base` and `cl100k_base`; neither is the exact tokenizer for every Claude,
Gemini, Qwen, or local model. Harness framing and dynamically generated text are
excluded unless stated.

| Input | Lines | Bytes | Words | `o200k` est. | `cl100k` est. | Loading role |
|---|---:|---:|---:|---:|---:|---|
| `skills/caveman/SKILL.md` | 78 | 5,227 | 674 | 1,245 | 1,296 | Full behavioral source |
| `src/rules/caveman-activate.md` | 15 | 615 | 86 | 163 | 166 | Minimal always-on rule |
| root `AGENTS.md` | 4 | 131 | 16 | 49 | 48 | Four imports |
| root `CLAUDE.md` | 306 | 24,512 | 3,117 | 6,173 | 6,158 | Maintainer-only repository context |
| root `GEMINI.md` | 4 | 131 | 16 | 49 | 48 | Four imports |
| Claude plugin manifest | 34 | 899 | 66 | 232 | 231 | Packaging, not necessarily model context |
| Marketplace manifest | 17 | 559 | 56 | 155 | 156 | Packaging |
| Codex plugin manifest | 39 | 1,327 | 122 | 376 | 375 | Metadata/default prompt |
| Gemini extension manifest | 6 | 240 | 29 | 68 | 68 | Packaging/context pointer |
| Claude `/caveman` command | 6 | 364 | 47 | 94 | 94 | Command description/prompt |
| OpenCode `/caveman` TOML | 2 | 325 | 43 | 81 | 81 | Command description/prompt |
| Cavecrew skill | 82 | 3,936 | 507 | 984 | 999 | On-demand orchestration |
| Cavecrew investigator | 57 | 1,610 | 216 | 474 | — | Agent prompt |
| Cavecrew builder | 47 | 1,458 | 194 | 387 | — | Agent prompt |
| Cavecrew reviewer | 48 | 1,554 | 215 | 434 | — | Agent prompt |
| Compressor skill | 111 | 4,535 | 621 | 1,063 | — | On-demand file rewrite |
| Commit skill | 65 | 2,588 | 354 | 654 | — | One-shot workflow |
| Review skill | 55 | 2,739 | 397 | 670 | — | One-shot workflow |

Additional derived loads:

- Default Claude SessionStart payload after the hook’s level/example filtering:
  3,213 bytes, 442 words, approximately 728 `o200k` tokens.
- Per-active-turn reinforcement: 121 bytes, 16 words, approximately 34 tokens.
- Imported contents referenced by Gemini’s four-line adapter: 15,092 bytes,
  2,046 words, approximately 3,632 tokens if expanded eagerly.
- Three Cavecrew agent prompts together: 4,624 bytes, approximately 1,295 tokens.
- `Answer concisely.`: 17 bytes and approximately five tokens.

These are [reproduced measurements](evidence-ledger.md#e016), not claims of exact
API input usage. The root `CLAUDE.md` is development context when working inside
the source repository; it should not be charged to an end-user plugin session.
No MCP description corpus or before/after snapshot is committed; the proxy can
emit per-field deltas only when run in debug mode. Its input savings therefore
cannot be reproduced from repository data.

## Benchmark audit

### Protocol actually implemented

`benchmarks/run.py` defines ten prompts spanning code explanation, debugging,
design, security, Git, and conceptual answers. It calls one Claude model (default
`claude-sonnet-4-20250514`) with temperature zero and maximum 4,096 output
tokens. Baseline system text is “You are a helpful assistant”; treatment is the
entire skill. Default trials are three; token counts are reduced to the median per
prompt, and prompt reductions are averaged.

Strengths: prompts are visible, temperature is fixed, multiple trials reduce one
source of randomness, and normal/treatment outputs can in principle be inspected.
Weaknesses: one model/vendor, ten hand-selected prompts, no terse control, no
quality or task-success judge, no input/reasoning/latency/session metric, and no
committed raw results under `benchmarks/results/`. The README table can be
recalculated, but its upstream calls and medians cannot be independently
reproduced from the snapshot ([E019–E021](evidence-ledger.md#e019)).

### Recalculated README table

| Metric | Result |
|---|---:|
| Baseline total | 12,140 output tokens |
| Caveman total | 2,939 output tokens |
| Baseline arithmetic mean | 1,214.0 |
| Caveman arithmetic mean | 293.9 |
| Pooled reduction, `1-sum(C)/sum(B)` | 75.79% |
| Mean of ten per-prompt reductions | 64.52% |
| Median per-prompt reduction | 76.42% |
| Range | 22.22%–86.80% |

The current “65%” corresponds approximately to the unweighted mean of prompt
percentages, not the aggregate token ratio. Both are legitimate summaries but
answer different questions. Neither measures total session savings.

The treatment changed materially: the main skill at the benchmark commit was
approximately 552 `o200k` tokens; it is approximately 1,245 now. The historical
output table therefore does not validate the present prompt’s input cost,
behavior, or accuracy ([E021](evidence-ledger.md#e021)).

## Eval audit

The committed snapshot identifies Claude Code 2.1.97, `claude-opus-4-6`, ten
prompts, and arms for baseline, a five-token terse prefix, Caveman, language
variants, and compression. Each prompt/arm has one generated sample at the
default model temperature. `evals/measure.py` uses `tiktoken` `o200k_base`, so
the committed counts themselves are estimates for Claude rather than provider
billing-token ground truth.

Independent recalculation of the three relevant arms:

| Arm | Total | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| Baseline | 1,948 | 194.8 | 181.0 | 104 | 330 |
| `Answer concisely.` | 2,045 | 204.5 | 187.5 | 82 | 339 |
| Caveman | 1,026 | 102.6 | 92.5 | 41 | 226 |

| Comparison | Pooled reduction | Mean per-prompt | Median per-prompt | Range |
|---|---:|---:|---:|---:|
| Caveman vs baseline | 47.33% | 46.04% | 44.59% | 10.67%–87.58% |
| Caveman vs terse | 49.83% | 46.13% | 50.26% | 0.44%–87.91% |

The terse arm produced 4.98% more tokens than baseline in this one snapshot. That
does not prove the two-word instruction is counterproductive; it demonstrates
that a one-sample comparison at uncontrolled/default temperature is noisy.
Conversely, the
Caveman deltas are large but still do not establish preserved task quality
([E022–E024](evidence-ledger.md#e022)).

The snapshot includes `caveman-cn` and `caveman-es`, while those skill directories
are absent at current HEAD. It is historical evidence, not a complete current
release eval. There is no Qwen, OpenCode, Gemini, local-model, multi-model,
reasoning-token, tool-use, latency, or longitudinal session coverage.

## Claims and corrections

| Surface | Statement/status | Audit result |
|---|---|---|
| Main skill/manifests/README | Roughly 65% fewer output tokens, full technical accuracy | Reduction depends on aggregation/treatment/model; accuracy is not judged |
| `HONEST-NUMBERS.md` | Input/reasoning unchanged; short tasks can be net-negative | Important and consistent with accounting |
| Stats/statusline | Estimated tokens/dollars saved | Applies fixed 0.65 to observed output; not counterfactual observation |
| MCP docs | Same accuracy/semantics | Regex implementation has no semantic judge |
| Benchmark docs | Results committed/reproducible | Table committed; raw benchmark results absent |
| Eval docs | Versus-terse is honest incremental delta | Raw data supports ~49.83%; current headline docs removed the row |

History matters. The headline moved from about 75%, to 50–65%, then to a flat
65%. Commit `e2c09c9` flattened the message and removed the versus-terse row from
the “honest numbers” document even though the snapshot remained. This is a
marketing/evidence contradiction, not evidence of fabricated data
([E033–E034](evidence-ledger.md#e033)).

## What `/caveman-stats` measures

The stats hook reads actual output-token and cache-read-token fields from Claude
session JSONL. It now attributes messages to mode-transition intervals and
excludes unknown spans. For each known `full` span, it computes a hypothetical
normal output from the fixed ratio:

```text
estimated_saved = round(observed_output / (1 - 0.65)) - observed_output
```

The display can therefore truthfully report observed usage while only estimating
the “saved” counterfactual. Lite, ultra, and wenyan modes have no coefficient.
Hard-coded price tables can age. The fix for issue #601 prevents attributing an
entire mixed-mode session to the current flag, but cannot repair already-recorded
history ([E025–E026](evidence-ledger.md#e025)).

The compressor-related stats path searches for adjacent `*.original.md` pairs;
the current compressor stores backups in a platform data directory. That measure
can miss current compressor work ([E040](evidence-ledger.md#e040)).

## Break-even thresholds

### Token-count-neutral model

Let `C` be extra input tokens per request, `r` the fraction of visible output
avoided, and `N` baseline output tokens. With equal token weight, no cache
discount, and no quality loss, break-even is:

```text
N = C / r
```

| Treatment/load assumption | C | At 65% | At 47.33% | Interpretation |
|---|---:|---:|---:|---|
| Full current skill | 1,245 | 1,915 | 2,632 | On-demand full doctrine |
| Claude filtered start + first reinforcement | 762 | 1,172 | 1,611 | First modeled request; variable nudge excluded |
| Static rule + reinforcement | 197 | 303 | 417 | OpenCode-like active path |
| Static rule only | 163 | 251 | 345 | Always-on project rule |
| “Answer concisely.” | 5 | — | — | Snapshot supplies no positive empirical `r` |

For illustration only, if the two-word instruction achieved 10%, its threshold
would be 50 baseline output tokens. That is a hypothetical sensitivity case, not
a measured result.

These thresholds are deliberately plural. They change with the treatment,
observed task class, cache, prices, and whether instruction content repeats
([E028–E029](evidence-ledger.md#e028)).

### Price- and cache-weighted sensitivity

If output tokens cost five times input tokens, divide `C` by five before comparing
to avoided output. The current full skill at 47.33% then crosses monetary
break-even near 526 baseline output tokens. If 90% of its input is also billed at
a cached rate equivalent to one-tenth, the illustrative threshold becomes about
53. These figures are sensitivities, not current universal prices.

Caching does not make a persistent rule free. The text still occupies the model’s
context and participates in attention; client/harness behavior may resend it; a
cache miss restores full prefill; and long-lived cached doctrine can still
interfere with task instructions ([E030](evidence-ledger.md#e030)).

### Billing model

- **Per-token API:** shorter output can save money after input overhead and price
  asymmetry are included.
- **Per-request/credit:** output length may not change the charged unit, as issue
  #506 illustrates.
- **Subscription:** user-visible savings may be quota-, latency-, or context-based
  rather than monetary.
- **Local inference:** no token invoice, but prompt prefill, memory, energy,
  throughput, and context capacity remain limited.

## Input versus output versus reasoning

| Quantity | Caveman evidence |
|---|---|
| Added input | Statistically measurable from instruction files; varies by adapter |
| Visible output | Reduced in one benchmark table and one Claude eval snapshot |
| Hidden reasoning | Unobserved; may be unchanged, shorter, or longer |
| Tool results | Unchanged by style; MCP proxy passes call results through |
| Tool descriptions | Optional regex shrink can reduce them, fidelity unproved |
| Persistent files | LLM compressor can shorten them, but creates semantic/data-boundary risk |
| Session total | Not measured end to end |
| Human correction turns | Not measured; ambiguity could add turns and erase savings |

This is why “65% fewer output tokens” must never be rewritten as “65% cheaper
agent sessions.”

## Implications for small local models

A local Qwen through OpenCode removes direct per-token billing but not context
economics. The 163-token static rule is much more plausible than the 1,245-token
full skill as a permanent load. Yet model capacity matters: fragments, exception
hierarchies, and multiple mode names may decrease compliance or make terse errors
harder to diagnose. No repository evidence measures Qwen or any local model
([E024](evidence-ledger.md#e024), [E055](evidence-ledger.md#e055)).

Required tests before considering any principle:

- at least no-instruction, two-word concise, small neutral density rule, and full
  doctrine arms;
- task classes split into short factual, code/debug, planning, safety-sensitive,
  tool-heavy, and long synthesis;
- visible output, total input, cached input, reasoning where observable, latency,
  peak context/KV use, task correctness, ambiguity, and correction turns;
- multiple model sizes/quantizations and repeated trials with confidence
  intervals;
- human preference/readability and exact-literal preservation;
- session-level accounting, not isolated answer length only.

## Economic conclusion

The evidence supports a narrower claim: on the sampled Claude prompts, a detailed
style treatment often reduced visible output substantially. It does not establish
a fixed reduction, technical accuracy, or a positive total-session return across
harnesses/models. The strongest context-efficiency result in the repository is
not the 65% headline; it is the large cost gap between the 1,245-token full skill
and the 163-token minimal rule, coupled with the absence of evidence that every
example, level, and persona element is necessary.
