# GitHub recovery and publication record

This record explains the machine-readable
[`github-publication-plan.json`](../../governance/github-publication-plan.json).
It describes the canonical repository after privacy-remediation recovery and
the durable **`PUBLICATION_TRANSITION`** phase. It authorizes a guarded public
transition without asserting that the visibility change or target controls have
already been applied. It authorizes no tag or release.

## Canonical repository

`ElGrandeXu/EGX_Terminal`, repository ID `1308085094`, is the sole repository
retained for this project and its default branch is `main`. On 2026-07-22, the
pretransition checkpoint `23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515` was
observed private with 41 commits on `main`. This is a historical checkpoint, not
a permanent current-commit count. Effective visibility and protections must be
verified directly through the GitHub API.

Recovery had begun from 37 clean commits at
`dee7a7c97ad6991746d7de35f6d7ddb290bb895e`; its single closing commit created
the separate historical 38-commit checkpoint.

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

## Release state

The pretransition checkpoint had no Git tag and no GitHub release. `v1.0.0` is a
historical release withdrawn during privacy remediation, not a current or
downloadable release. Its former target, tag object, and GitHub release record
are retained only in verified private bundles. GitHub's immutable-release
reservation prevents reuse of its tag name in the recreated repository.

The transition prohibits tag and release creation. `v1.0.1` and its declared
SSH-signature gate remain a separate later mission; PR #2 remains part of the
preserved recovery history.

## Repository metadata and features observed on 2026-07-22

The canonical description was:

> Evidence-led research for inspectable, LLM-agnostic terminal environments.

The homepage was empty. The ten repository topics were `llm`, `developer-tools`,
`cli`, `llm-agnostic`, `ai-governance`, `reproducible-research`, `opencode`,
`ollama`, `qwen`, and `open-source`.

Issues were enabled. Projects, wiki, discussions, Pages, and sponsorship were
not enabled. Merge settings allowed squash merges only, used the pull-request
title and body, deleted merged branches, and kept auto-merge disabled.

## Actions and security

At the checkpoint, Actions was limited to `actions/checkout@*` and
`actions/setup-python@*`. GitHub-owned and verified-action broad allowances were
disabled, full SHA pinning was required, the default workflow token was
read-only, and workflows could not approve pull requests.

At the 2026-07-22 private checkpoint, vulnerability alerts were active, PVR was
unavailable, secret scanning was disabled, and push protection was inactive.
These are dated observations, not claims about current remote state.

The future atomic mission must verify a private preflight, switch visibility to
public, activate PVR immediately, and mechanically verify its accessibility. No
confidential channel is claimed before activation and no personal security
address is published as a substitute. Failure to apply or verify PVR or another
critical control stops the mission and leaves the project non-shareable. The
same mission retains minimal Actions permissions, prudent fork-workflow policy,
vulnerability alerts, secret scanning, push protection when available, and
anonymous post-public checks.

## Desired and observed branch governance

The desired `main-protection` configuration would require these three checks:

- `repository / ubuntu`;
- `repository / windows`; and
- `licensing / reuse`.

It would also block deletion and force-push, require linear history and a pull
request, require conversation resolution, use zero mandatory approvals, not
require an up-to-date branch, signed commits, or Code Owners, and contain no
bypass actor or role. At the private checkpoint, the configuration was not
applied because rulesets were unavailable on GitHub Free, and `main` was
observed unprotected. Current enforcement must be verified by API.

The direct fast-forward push of the closing commit is a one-time recovery
exception while the repository is private and before ruleset activation. It is
not precedent or authorization for future direct pushes.

Until the no-bypass ruleset is verified, using a pull request remains a mandatory
project convention. Schema 5 records the public target, dated private
observation, authorization-not-application state, current API source of truth,
desired post-public controls, and actually observed pretransition controls
separately.

## Closed prepublication audit

At checkpoint `23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515`, Git content, pull
requests, logs, workflows, and licenses were audited without a material leak
being detected. F-001 closed on 2026-07-22 after twelve authorized Packages
surfaces returned HTTP 200 with zero packages. A fresh audit of the merged HEAD
is mandatory before executing the transition.

## Validation boundary

The local and clean-clone gates cover the neutral root, public-surface heuristic,
licensing, Git history and all refs, Markdown links, GitHub governance, tests,
REUSE, JSON and TOML parsing, Git integrity, the locked experimental archive
hash, and the byte identity of the ten files listed under `frozen_files` in the
Mission 24 manifest. This gate verifies the integrity of preserved files, not
the source runtime observations or the absent original aggregate; see
[decision 0014](../decisions/0014-micro-kernel-evidence-erratum.md). A source
archive without `.git` runs only the content-applicable subset and never
simulates absent history or historical release objects.
