# EGX_Terminal

EGX_Terminal is a research and governance workspace for designing
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

A clone exposes none of the known active Codex, Claude Code, or OpenCode project
surfaces recorded in
[`neutral-root-surfaces.json`](governance/neutral-root-surfaces.json). No kernel,
adapter, or behavioral payload is active at the root. This is a bounded registry
of current conventions, not a claim about every future harness convention.

The Git history has been audited and remediated. After GitHub selected a
personal author address for the first squash merge, the affected repository was
made private and the canonical repository was recreated from a content-identical
clean history. PR #2 is complete and was squash-merged as commit
`c708bc6af88b5e98a08fc801e476d4c16248e701`, establishing a 40-commit
linear-history checkpoint. All commits in that checkpoint use approved GitHub
`noreply` metadata; the affected object was not imported. The active policy
continues to accept attributable GitHub `noreply` contributors and the exact
GitHub web committer used for squash merges, without accepting personal email
addresses or undeclared bots; see the [identity remediation
report](docs/publication/IDENTITY_REMEDIATION.md) and run
`python scripts/check_git_history.py --fail-on-review` to verify the gate.

At the 2026-07-22 pretransition checkpoint
`23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515`, `main` contained 41 commits and
the canonical repository had no Git tag or published release. This count is a
historical checkpoint, not a current counter. `v1.0.0` is retained only as a
historical release record withdrawn during the
privacy remediation; its terminal governance conclusions remain in force, while
[Decision 0014](docs/decisions/0014-micro-kernel-evidence-erratum.md) records the
limits of the preserved micro-kernel runtime evidence. Its former release
metadata is preserved only in verified private evidence outside this
repository. GitHub's immutable-release reservation prevents reuse of that
tag name in the recreated repository. [Decision
0016](docs/decisions/0016-record-public-transition-rollback.md) records the
first controlled public transition and its rollback. The corrected final
publication was subsequently applied and verified: the repository is public,
Levels A, B, and C passed, and public run
[`30002915548`](https://github.com/ElGrandeXu/EGX_Terminal/actions/runs/30002915548)
succeeded. No tag or release is active; `v1.0.1` and its SSH-signing gate remain
a separate later mission.

## Key V1 decision

V1 is maintained with a neutral root. Useful principles remain
available as documentation, while any future capability or adapter must be
explicit and opt-in. Hidden instruction injection is outside the V1 boundary.

The final reasoning is recorded in the [micro-kernel evaluation
(0004)](docs/decisions/0004-micro-kernel-final-evaluation.md), its [runtime-evidence
erratum (0014)](docs/decisions/0014-micro-kernel-evidence-erratum.md), and the
[neutral-root decision
(0005)](docs/decisions/0005-ship-v1-with-neutral-root.md). For the micro-kernel,
the payload, protocol, fixtures, graders, manifest, and recorded hashes of
preserved artifacts remain directly auditable. The [micro-kernel final
results](experiments/kernel-micro-v1/behavioral/final-v1/results.md) preserve the
published historical claims, but the original aggregate and source runtime data
are irrecoverable. The [balanced-kernel challenge
results](experiments/kernel-v1/behavioral/challenge-v1/results.md) remain a
separate historical record.

## Experimental results

The micro-kernel scores, ties, token totals, and overhead shown below are values
published in the historical report. Their internal arithmetic remains
checkable, but the irrecoverable original aggregate and source runtime data prevent
independent verification of the underlying runtime observations; see [Decision
0014](docs/decisions/0014-micro-kernel-evidence-erratum.md).

| Experiment | Verdict | Functional success (baseline / candidate) | Primary wins (baseline / candidate) | Ties | False completions (baseline / candidate) | Token overhead | Pre-registered ceiling |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Balanced kernel | `REJECTED_AS_BALANCED` | One baseline cell unavailable after scoring | 2 / 0 | 3 complete pairs | 0/5 / 2/6 | +19.166% on the five complete pairs | n/a |
| Micro-kernel | `REJECT_MICRO` | 5/5 / 5/5 | 0 / 0 | 5 | 0 / 0 | +7.85% ([exact value: 7.850019354305572%](experiments/kernel-micro-v1/behavioral/final-v1/results.md)) | 5% |

According to the historical micro-kernel report, all five pairs were behavioral
ties and the published token overhead exceeded the pre-registered budget. The
terminal governance verdict remains **`REJECT_MICRO`**; this summary does not
revalidate the unavailable runtime sources. The balanced result's +19.166% is a
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

The canonical local validation path requires Python 3 and a full Git clone. It
was verified with Python 3.11.9 and Git 2.54.0; the repository does not declare
lower minimum versions.
The checks use only the Python standard library and require no network, model, or
agent runtime.

From the repository root:

```console
python scripts/check_neutral_root.py
python scripts/check_public_surface.py
python scripts/check_licensing.py
python scripts/check_git_history.py --fail-on-review
python scripts/check_markdown_links.py
python scripts/check_github_governance.py
python -m unittest discover -s tests -v
reuse lint
```

Then read the [charter](docs/CHARTER.md), [status](docs/STATUS.md), [decision
register](docs/decisions/README.md), [experimental archives](experiments/), and
[publication boundary](docs/publication/PUBLICATION_BOUNDARY.md), in that order.
The [detailed quickstart](docs/QUICKSTART.md) distinguishes the complete clone
audit from the smaller content-only sequence available in a GitHub source
archive, and explains how to inspect evidence without relaunching a benchmark.

## Community and publication

See [contribution guidelines](CONTRIBUTING.md), [governance](GOVERNANCE.md), and
the [security policy](SECURITY.md). The SHA-pinned, read-only
[validation workflow](.github/workflows/validate.yml) defines the public checks.
The [GitHub publication record](docs/publication/GITHUB_PUBLICATION_PLAN.md) and
[release policy](docs/publication/RELEASE_POLICY.md) distinguish repository
publication, immutable releases, tag signatures, and future release gates.

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

The sole canonical repository is
[`ElGrandeXu/EGX_Terminal`](https://github.com/ElGrandeXu/EGX_Terminal). Its
durable phase is **`PUBLIC_REPOSITORY_VERIFIED`**. The final publication was
validated at checkpoint `1d79ea37a1c614728cc7651c4d611218eaca174a` with 43
linear commits: public `workflow_dispatch` run `30002915548` passed
`repository / ubuntu`, `repository / windows`, and `licensing / reuse`, and
Levels A, B, and C succeeded. PVR, secret scanning, push protection,
vulnerability alerts, and the no-bypass `main-protection` ruleset were observed
active. Anonymous REST log downloads remained HTTP 403 and were classified
`INFO` / `PLATFORM_AMBIGUITY`, consistently with the earlier diagnosis.

The first public transition and rollback remain historical facts, as do the
identity remediation and repository recreation. The dated remote observations
are not a claim that the offline checker queries GitHub in real time. No tag or
release is active, and `v1.0.1` preparation remains outside this mission.

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
