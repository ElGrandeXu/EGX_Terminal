# Contributing

## Suitable contributions

The project accepts factual corrections, documentation improvements, script or
test fixes, stronger deterministic controls, independent reproductions, narrow
experimental proposals, and reports about provenance, licensing, or security.

Before starting, read the [README](README.md), [charter](docs/CHARTER.md), and
[status](docs/STATUS.md), then search existing issues. Open an issue before a
structural change. Do not rerun a closed doctrinal campaign merely to seek a
different verdict.

## Branch and pull request workflow

Use a fork or a dedicated branch and submit one coherent change per pull
request. State the intended outcome, scope, evidence, and validation. Declare
all affected files and consumers; do not include unannounced changes.

## Required local validation

Run the canonical sequence from the repository root:

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

## Archives

Do not modify files directly under `experiments/kernel-v1/` or
`experiments/kernel-micro-v1/`. A new experiment belongs in a new space with its
own provenance, protocol, observable success condition, and stopping criterion.

## Licensing and provenance

Follow `REUSE.toml`, identify third-party sources, never relicense third-party
material, and do not add an unclassified file. A human contributor remains
responsible for AI-assisted work. Automated generation does not remove the need
to verify accuracy, provenance, and licensing.

## Security and privacy

Never publish a secret. Redact logs and personal paths. Do not open a public
issue for a vulnerability; follow [SECURITY.md](SECURITY.md).

## Acceptance

Submission does not guarantee merge. Review weighs project scope, evidence,
simplicity, and continuing maintenance cost.
