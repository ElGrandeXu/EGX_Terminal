# Quickstart

This guide validates the public V1 workspace without network access, a model, or
an agent runtime. Run every command from the repository root.

## Prerequisites

- Python 3, available as `python`.
- Git, available as `git`, inside a cloned Git worktree.

This quickstart was verified with Python 3.11.9 and Git 2.54.0. The repository
does not declare lower minimum versions. The active scripts use only the Python
standard library.

## Validate the workspace

Confirm that none of the five forbidden harness-instruction paths is active at
the root:

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
branch. Review findings are reported without exposing a full private address:

```console
python scripts/check_git_history.py
```

Run the tests applicable to the neutral-root V1 distribution:

```console
python -m unittest discover -s tests -v
```

This command runs the active tests under `tests/`. Historical experimental suites
remain part of their archived evidence and are intentionally outside the active
V1 test total.

When the official REUSE tool is available, run this additional standards check:

```console
reuse lint
```

`reuse lint` validates REUSE Specification 3.3. It is not a prerequisite for
offline inspection of the repository and is not a permanent project dependency.

## Recommended reading path

1. [Project charter](CHARTER.md) — mission, principles, and non-objectives.
2. [Current status](STATUS.md) — the present boundary and next gate.
3. [Decision register](decisions/README.md) — then read decisions [0004](decisions/0004-micro-kernel-final-evaluation.md) and [0005](decisions/0005-ship-v1-with-neutral-root.md).
4. [Balanced-kernel archive](../experiments/kernel-v1/README.md) and [micro-kernel archive](../experiments/kernel-micro-v1/README.md) — rejected candidates and retained evidence.
5. [Publication boundary](publication/PUBLICATION_BOUNDARY.md) — inspected surface and documented exceptions.

## Inspect an experiment without rerunning it

Start with the experiment's README, then follow its protocol, results, decision,
and compatibility links. For the final outcomes, use:

- [balanced-kernel challenge results](../experiments/kernel-v1/behavioral/challenge-v1/results.md);
- [micro-kernel final protocol](../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md);
- [micro-kernel final results](../experiments/kernel-micro-v1/behavioral/final-v1/results.md); and
- [runtime compatibility summary](../experiments/kernel-v1/validation/runtime-compatibility-summary.md).

The Markdown reports and tracked JSON artifacts are the evidence. Reading and
parsing them is evidence inspection; it does not reproduce a runtime observation.

## Three different validation scopes

**Inspect existing evidence.** Read the tracked reports, protocols, manifests,
and metrics. This is the default path and has no runtime or network cost.

**Reproduce local V1 validation.** Run the five local commands above. They verify
the current neutral root, tracked public surface, file-scoped licensing,
reachable Git history, and active distribution checks on your machine. They do
not re-evaluate a kernel. The history check returns zero for review-only identity
findings; use `--fail-on-review` when that decision must block automation.

**Rerun a benchmark or runtime-dependent validation.** Historical commands under
`experiments/` can require exact software versions, local models, substantial
compute, and campaign-specific controls. They are not part of this quickstart.
Do not download a model, start Ollama, launch OpenCode, execute Qwen, or rerun a
behavioral campaign as part of standard V1 validation.

The final doctrinal campaigns are closed. Do not rerun them to obtain a more
favorable result: their pre-registered verdicts and negative evidence are part
of the V1 record.
