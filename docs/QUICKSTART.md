# Quickstart

This guide validates the public V1 workspace without a model or agent runtime.
For the micro-kernel campaign, inspection covers the preserved historical report
and directly auditable definition artifacts; it does not independently verify
the source runtime observations, whose original aggregate and source data are
absent. Run every command from the repository root. A full Git clone and a
GitHub source archive provide different validation scopes and are not
interchangeable.

## Prerequisites

- Python 3, available as `python`.
- Git, available as `git`, for the canonical clone audit.

This quickstart was verified with Python 3.11.9 and Git 2.54.0. The repository
does not declare lower minimum versions. The active scripts use only the Python
standard library.

## Canonical full-clone validation

A complete clone contains `.git`, refs, commit objects, and identity metadata.
It can therefore prove the current history and ref topology, including that no
Git tag exists. The withdrawn historical `v1.0.0` objects are intentionally
absent and are not reconstructed or simulated by the checker.

Confirm that none of the known active project surfaces in the machine-readable
neutral-root registry is present:

```console
python scripts/check_neutral_root.py
```

Inspect tracked files for the documented public-surface blockers:

```console
python scripts/check_public_surface.py
```

Validate the file-scoped license mapping and locked official texts without
network access:

```console
python scripts/check_licensing.py
```

Audit commits, metadata, refs, and blobs reachable from the planned public
branch, then require the identity review gate to be empty. Diagnostics never
expose a full private address:

```console
python scripts/check_git_history.py
python scripts/check_git_history.py --all-refs
python scripts/check_git_history.py --fail-on-review
python scripts/check_markdown_links.py
python scripts/check_github_governance.py
python -m unittest discover -s tests -v
reuse lint
```

This command runs the active tests under `tests/`. Historical experimental suites
remain retained archive artifacts and are intentionally outside the active V1
test total.

The governance checks use only the standard library and make no network
requests. `reuse lint` uses REUSE 6.2.0 to validate REUSE Specification 3.3; CI
builds it from the official sdist using the dedicated hashed build and runtime
locks. It is not a project runtime dependency.

## GitHub source archive: content-only validation

A generated `.zip` or `.tar.gz` source archive has no `.git` directory. It can
check only the content present: registered neutral-root surfaces, publication
heuristics, file-scoped licensing, Markdown links, workflow governance, and
REUSE metadata. It cannot prove history, refs, commit identities, or the absence
of historical Git objects from the canonical object database.

Run only this bounded sequence in an extracted source archive:

```console
python scripts/check_neutral_root.py
python scripts/check_public_surface.py --content-only --root .
python scripts/check_licensing.py --content-only --root .
python scripts/check_markdown_links.py --content-only --root .
python scripts/check_github_governance.py --content-only --root .
reuse lint
```

Do not run `check_git_history.py` there. If invoked, it exits with an intentional
diagnostic stating that a full Git clone is required; it never reconstructs or
simulates missing history.

## Recommended reading path

1. [Project charter](CHARTER.md) — mission, principles, and non-objectives.
2. [Current status](STATUS.md) — the present boundary and next gate.
3. [Decision register](decisions/README.md) — then read the micro-kernel
   evaluation [0004](decisions/0004-micro-kernel-final-evaluation.md), its
   runtime-evidence erratum [0014](decisions/0014-micro-kernel-evidence-erratum.md),
   and the neutral-root decision
   [0005](decisions/0005-ship-v1-with-neutral-root.md).
4. [Balanced-kernel archive](../experiments/kernel-v1/README.md) and
   [micro-kernel archive](../experiments/kernel-micro-v1/README.md) — rejected
   candidates and their retained historical records.
5. [Publication boundary](publication/PUBLICATION_BOUNDARY.md) — inspected surface and documented exceptions.

## Inspect an experiment without rerunning it

Start with the experiment's README, then follow its protocol, results, decision,
and compatibility links. For the final outcomes, use:

- [balanced-kernel challenge results](../experiments/kernel-v1/behavioral/challenge-v1/results.md);
- [micro-kernel final protocol](../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md);
- [micro-kernel final results](../experiments/kernel-micro-v1/behavioral/final-v1/results.md); and
- [runtime compatibility summary](../experiments/kernel-v1/validation/runtime-compatibility-summary.md).

For the micro-kernel, the preserved payload, protocol, fixtures, graders,
manifest, and recorded hashes are directly auditable. The results document is a
historical report: its published totals can be checked for internal arithmetic
consistency, but it is not a substitute for the missing original aggregate or
source runtime data. Reading and parsing the retained record therefore neither
reproduces nor independently verifies a runtime observation.

## Three different validation scopes

**Inspect the existing record.** Read the tracked historical reports and the
preserved protocols, manifests, fixtures, graders, and metrics definitions. This
is the default path and has no runtime or network cost. For the micro-kernel,
only the preserved definition artifacts are directly auditable; the runtime
claims remain historically published rather than independently revalidated.

**Reproduce local V1 validation.** Run the full-clone commands above. They verify
the current neutral root, tracked public surface, file-scoped licensing,
reachable Git history, links, GitHub governance, the strict public identity
policy, and active distribution checks on your machine. They do not re-evaluate a kernel. The
`--fail-on-review` invocation is required before publication.

**Rerun a benchmark or runtime-dependent validation.** Historical commands under
`experiments/` can require exact software versions, local models, substantial
compute, and campaign-specific controls. They are not part of this quickstart.
Do not download a model, start Ollama, launch OpenCode, execute Qwen, or rerun a
behavioral campaign as part of standard V1 validation.

The final doctrinal campaigns are closed. Do not rerun them to obtain a more
favorable result: their terminal verdicts, produced under pre-registered rules,
and their bounded historical record are part of V1. For the micro-kernel, the
bounded negative evidence record comprises directly auditable definition
artifacts, historically published claims, and their internally checkable
arithmetic; it does not comprise recoverable source runtime proof. This
limitation does not weaken **`REJECT_MICRO`** or authorize a new campaign.
