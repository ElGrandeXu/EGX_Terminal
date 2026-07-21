# GitHub publication record

This record translates the machine-readable
[`github-publication-plan.json`](../../governance/github-publication-plan.json)
into the observed publication sequence. It does not authorize a tag or release.

## Local and private staging validation

The local policy checks, 133 tests, `reuse 6.2.0`, actionlint 1.7.12, JSON and
TOML parsing, locks, Git integrity, Markdown links, archive hash, Mission 24
frozen results, and authenticated-URL searches passed before the corrective
push.

The first private staging run exposed three real defects:

- archive ordering depended on platform-native `Path` ordering;
- the history audit treated the expected `origin/main` transport ref as a
  publishable ref; and
- the Windows multi-command block did not stop after a failing PowerShell
  command.

The corrective commit preserved the archive hash, introduced explicit ref
semantics, and selected Bash fail-fast on Windows. Its test fixture initially
contained a complete fictitious authenticated URL in a tracked source file. The
commit was amended once so that the value is assembled only at runtime in a
temporary Git repository while still proving `AUTHENTICATED_URL` detection and
redaction.

The amended private staging SHA
`ff2111f6b1f7e6ea0e295b2a997d19b1a1dbdd31` passed:

- `repository / ubuntu`;
- `repository / windows`; and
- `licensing / reuse`.

The Windows log showed Bash with `-e -o pipefail`; the history audit accepted
the Actions checkout refs; no complete fixture appeared in the logs. The two
failed staging runs were deleted only after this green run, which was retained.

## Applied repository settings

The description, ten topics, issues, disabled projects/wiki/discussions/Pages,
squash-only merge policy, PR-title-and-body squash messages, merged-branch
cleanup, and disabled auto-merge match the machine-readable record.

Actions is enabled for only `actions/checkout` and `actions/setup-python`.
Repository policy requires full SHA pinning, the default `GITHUB_TOKEN` access
is read-only, and workflows cannot approve pull requests. The workflow itself
declares only `contents: read` and persists no checkout credentials.

## Public transition and security

Maxime explicitly authorized the visibility change. The repository is public,
non-archived, uses `main`, and retained the amended HEAD. Private Vulnerability
Reporting, secret scanning, push protection, and vulnerability alerts are
active. [`SECURITY.md`](../../SECURITY.md) is publicly accessible and publishes
no personal security address.

An HTTPS clone created without Git credentials or local hardlinks passed the
complete local suite. It contained 33 commits before this documentation commit,
only the approved public identity, no old amended commit, no authenticated URL
in reachable blobs, and the locked `kernel-v1` hash. The temporary clone was
removed.

## Remaining publication gate

This documentation commit is the 34th reachable commit. `main-protection` is
`DEFERRED` until its three public CI jobs pass. It will then be activated with a
required pull request, zero required approvals, required conversation
resolution, linear history, deletion and force-push protection, and the three
named checks. The administrator bypass is reserved for repository recovery.

No release or tag has been created. Release preparation remains deferred until
separate authorization and must not claim compatibility beyond the preserved
evidence.
