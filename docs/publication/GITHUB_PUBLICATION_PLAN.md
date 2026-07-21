# GitHub recovery and publication record

This record explains the machine-readable
[`github-publication-plan.json`](../../governance/github-publication-plan.json).
It describes the canonical repository after privacy-remediation recovery and
does not authorize a tag, release, visibility change, or new pull request.

## Canonical repository

`ElGrandeXu/EGX_Terminal`, repository ID `1308085094`, is the sole repository
retained for this project. Its default branch is `main` and its visibility is
private. Recovery began from 37 clean commits at
`dee7a7c97ad6991746d7de35f6d7ddb290bb895e`; the single closing commit brings the
history to 38 commits.

The repository was recreated after the first consolidation squash merge used a
personal author address. The incident was detected immediately. The functional
commit was rebuilt with the approved GitHub `noreply` identity while preserving
its tree, parent, complete message, author and committer dates, and diff. The
affected object and the former pull-request refs were not imported.

## Private evidence and temporary repositories

Historical Git objects and incident records remain outside this repository in
private evidence. Before deleting either temporary GitHub repository, the
recovery process captured accessible repository metadata, branches, tags,
releases, pull requests, issues, Actions runs, and settings; created independent
mirror clones and complete bundles; ran `git bundle verify` and
`git fsck --full`; and verified every retained file through a SHA-256 manifest.

The temporary repositories were then deleted through GitHub. Authenticated API
reads and their URLs return `404`, the owner repository list no longer contains
them, and the canonical repository remains intact. Their private names, local
storage paths, and sensitive contents are intentionally absent from this record.

## Current release state

The canonical repository has no Git tag and no GitHub release. `v1.0.0` is a
historical release withdrawn during privacy remediation, not a current or
downloadable release. Its former target, tag object, and GitHub release record
are retained only in verified private bundles. GitHub's immutable-release
reservation prevents reuse of its tag name in the recreated repository.

The next candidate is `v1.0.1`. No `v1.0.1` tag or release exists, this recovery
does not authorize either, and PR 2 remains a separate future step. Future
release tags still require the declared SSH-signature gate.

## Repository metadata and features

The canonical description is:

> Evidence-led research for inspectable, LLM-agnostic terminal environments.

The homepage is empty. The ten repository topics are `llm`, `developer-tools`,
`cli`, `llm-agnostic`, `ai-governance`, `reproducible-research`, `opencode`,
`ollama`, `qwen`, and `open-source`.

Issues are enabled. Projects, wiki, discussions, Pages, and sponsorship are not
enabled. Merge settings allow squash merges only, use the pull-request title and
body, delete merged branches, and keep auto-merge disabled.

## Actions and security

Actions is limited to `actions/checkout@*` and `actions/setup-python@*`.
GitHub-owned and verified-action broad allowances are disabled, full SHA pinning
is required, the default workflow token is read-only, and workflows cannot
approve pull requests.

Private Vulnerability Reporting, secret scanning, push protection, and
vulnerability alerts are active. No personal security address is published.

## Protected main

The `main-protection` ruleset is activated only after the closing commit has
produced the three private green checks:

- `repository / ubuntu`;
- `repository / windows`; and
- `licensing / reuse`.

The active ruleset blocks deletion and force-push, requires linear history and a
pull request, requires conversation resolution, and requires those three checks
with zero mandatory approvals. No ordinary bypass is permitted.

The direct fast-forward push of the closing commit is a one-time recovery
exception while the repository is private and before ruleset activation. It is
not precedent or authorization for future direct pushes.

## Validation boundary

The local and clean-clone gates cover the neutral root, public-surface heuristic,
licensing, Git history and all refs, Markdown links, GitHub governance, tests,
REUSE, JSON and TOML parsing, Git integrity, the locked experimental archive
hash, and the ten frozen Mission 24 results. A source archive without `.git`
runs only the content-applicable subset and never simulates absent history or
historical release objects.
