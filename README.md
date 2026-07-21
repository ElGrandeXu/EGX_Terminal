# EGX_Terminal

EGX_Terminal is a public research and governance workspace for designing
inspectable, token-conscious terminal environments that remain LLM-, harness-,
and provider-agnostic. Its V1 boundary preserves the evidence, decisions, and
validation methods behind that work; it does not contain a universal agent
runtime.

## Why this exists

Terminal-agent environments can become structurally dependent on one provider,
model, or harness convention. Instructions, hooks, skills, and memory can also
accumulate until their always-on cost and behavioral effect are difficult to
inspect. A plausible mechanism is not necessarily a demonstrated one.

This repository uses a bounded progression: audit the available evidence, state
a hypothesis, isolate a prototype, pre-register the protocol, test it, record a
decision, and preserve both positive and negative results. Complexity is promoted
only after its value has been shown under explicit criteria.

## What V1 actually ships

V1 contains:

- a project [charter](docs/CHARTER.md) and current [status](docs/STATUS.md);
- repository audits, cross-repository research, and an architecture synthesis;
- decision records with evidence, consequences, and revision conditions;
- immutable archives of two rejected kernel experiments;
- experimental protocols, fixtures, graders, and compatibility reports;
- local verification scripts and their applicable tests; and
- a neutral repository root.

A clone does not automatically inject project-owned behavioral instructions into
Codex, Claude Code, OpenCode, or another harness. No kernel, adapter, or behavioral
payload is active at the root.

## Key V1 decision

V1 is prepared for publication with a neutral root. Useful principles remain
available as documentation, while any future capability or adapter must be
explicit and opt-in. Hidden instruction injection is outside the V1 boundary.

The final reasoning is recorded in the [micro-kernel evaluation
(0004)](docs/decisions/0004-micro-kernel-final-evaluation.md) and the [neutral-root
decision (0005)](docs/decisions/0005-ship-v1-with-neutral-root.md). The underlying
evidence remains in the [micro-kernel final
results](experiments/kernel-micro-v1/behavioral/final-v1/results.md) and the
[balanced-kernel challenge
results](experiments/kernel-v1/behavioral/challenge-v1/results.md).

## Experimental results

| Experiment | Verdict | Functional success (baseline / candidate) | Primary wins (baseline / candidate) | Ties | False completions (baseline / candidate) | Token overhead | Pre-registered ceiling |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Balanced kernel | `REJECTED_AS_BALANCED` | One baseline cell unavailable after scoring | 2 / 0 | 3 complete pairs | 0/5 / 2/6 | +19.166% on the five complete pairs | n/a |
| Micro-kernel | `REJECT_MICRO` | 5/5 / 5/5 | 0 / 0 | 5 | 0 / 0 | +7.85% ([exact value: 7.850019354305572%](experiments/kernel-micro-v1/behavioral/final-v1/results.md)) | 5% |

The micro-kernel produced complete behavioral ties across all five pairs, but it
failed the pre-registered token budget. The balanced result's +19.166% is a
descriptive total for the five complete pairs; the six-pair overhead is
unavailable because one baseline observation was lost after scoring. Neither
rejection is presented as a promotion.

## Compatibility evidence

The archived experiments established the following bounded evidence:

- deterministic static distribution into disposable targets;
- instruction discovery by Codex CLI 0.144.6 in the measured fixtures;
- mock OpenCode 1.17.9 discovery and single injection of the expected kernel;
- a direct Ollama 0.20.2 inference with a precisely identified Qwen model; and
- real OpenCode 1.17.9 → Ollama 0.20.2 → `qwen3.6:27b` transport.

The resulting compatibility classification is **SUPPORTED — EXPERIMENTAL** for
the measured cells. The [runtime compatibility
summary](experiments/kernel-v1/validation/runtime-compatibility-summary.md)
separates static distribution, instruction discovery, runtime transport, formal
output adherence, and behavioral effectiveness. Qwen is a model served by a
runtime; OpenCode is a harness. Validating one combination does not establish
universal compatibility, and transport success does not establish behavioral
effectiveness. Claude Code was not installed and was not validated.

## Repository map

| Path | Purpose |
| --- | --- |
| [`docs/CHARTER.md`](docs/CHARTER.md) | Defines the mission, constraints, and current non-objectives. |
| [`docs/STATUS.md`](docs/STATUS.md) | Records the current phase, closed decisions, and next gate. |
| [`docs/research/`](docs/research/) | Contains the external audits, evidence ledgers, and synthesis. |
| [`docs/decisions/`](docs/decisions/) | Contains consequential project decisions and their evidence. |
| [`docs/publication/`](docs/publication/) | Defines the inspected public boundary and documented exceptions. |
| [`experiments/kernel-v1/`](experiments/kernel-v1/) | Archives the rejected balanced-kernel prototype and evidence. |
| [`experiments/kernel-micro-v1/`](experiments/kernel-micro-v1/) | Archives the rejected micro-kernel and final campaign. |
| [`scripts/`](scripts/) | Provides lightweight, deterministic V1 checks. |
| [`tests/`](tests/) | Tests the checks applicable to the neutral-root distribution. |

## Quickstart

The local validation path requires Python 3 and Git. It was verified with Python
3.11.9 and Git 2.54.0; the repository does not declare lower minimum versions.
The checks use only the Python standard library and require no network, model, or
agent runtime.

From the repository root:

```console
python scripts/check_neutral_root.py
python scripts/check_public_surface.py
python scripts/check_licensing.py
python -m unittest discover -s tests -v
```

Then read the [charter](docs/CHARTER.md), [status](docs/STATUS.md), [decision
register](docs/decisions/README.md), [experimental archives](experiments/), and
[publication boundary](docs/publication/PUBLICATION_BOUNDARY.md), in that order.
The [detailed quickstart](docs/QUICKSTART.md) explains how to inspect existing
evidence without relaunching a benchmark.

## What is intentionally deferred

V1 does not implement memory, hooks, skills, routing, compression, active
adapters, packaging, model distribution, cloud integrations, telemetry, or
automated publication. These remain deferred until a concrete need and new
evidence justify their ongoing cost and maintenance surface.

V1 is also not an installable universal agent, a complete orchestration
framework, a model distribution, a memory system, a large skills collection, a
hooks or routing system, a guarantee across all harnesses and models, or an
automatically injected behavioral doctrine.

## Design constraints

- Prefer explicit mechanisms over invisible ones.
- Make capabilities opt-in rather than always-on.
- Keep evidence local, inspectable, and attributable.
- Degrade cleanly when an optional mechanism is unavailable.
- Keep abstractions reconstructible rather than structurally provider-bound.
- Treat providers, runtimes, models, and harnesses as distinct roles.
- Keep complexity proportional to demonstrated value.
- Preserve existing user work.
- Scale verification with risk and reversibility.

These are documented project principles, not an automatically injected payload.

## Current status

EGX_Terminal is in V1 pre-publication. The root is neutral, the public surface has
been inspected, and no blocking violation was observed. The boundary is
classified
[`READY_FOR_FINAL_PUBLICATION_REVIEW`](docs/publication/PUBLICATION_BOUNDARY.md).
Historical runtime facts in the immutable archives remain documented evidence,
not licensing exceptions. No public remote exists and no push has occurred. The
remaining gate is final governance review and GitHub publication preparation.

## License

Licensing is determined per file: original code and functional artifacts use
[Apache-2.0](LICENSES/Apache-2.0.txt), while original documentation and research
use [CC-BY-4.0](LICENSES/CC-BY-4.0.txt). This is not a choice between two licenses
for the same file. See the short [license summary](LICENSE), machine-readable
[REUSE metadata](REUSE.toml), and detailed [licensing
policy](docs/publication/LICENSING.md).

Validate the complete local mapping offline with:

```console
python scripts/check_licensing.py
```
