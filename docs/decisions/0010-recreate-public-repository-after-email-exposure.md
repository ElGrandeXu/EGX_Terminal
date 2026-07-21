# 0010 — Recreate the public repository after email exposure

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

GitHub selected a personal address for the author metadata of the first squash
merge. The active identity policy correctly classified that persistent public
commit for review and blocked the Ubuntu and Windows CI gates. The tree, parent,
message, diff, paths, modes, and contents of the commit were otherwise correct.

A force-push alone could not establish that the exposed object had disappeared:
the merged pull request and GitHub-managed references could continue to make it
reachable. The incident happened before `v1.0.0`; the repository had no tag,
release, or public fork.

## Decision

Place the former staging repository in permanent private quarantine without
rewriting or deleting it. Recreate `ElGrandeXu/EGX_Terminal` as a new repository
whose object database has never contained the exposed metadata.

Reconstruct only the affected squash commit with its original tree, parent,
complete message, subject, author date, committer date, diff, paths, modes, and
contents. Use the approved GitHub ID-based `noreply` address for both identities,
with `ElGrandeXu` as author and `Maxime Erard` as committer. Add this decision as
a subsequent normal documentation commit, also using only the approved
`noreply` identity.

Future GitHub web operations require account email privacy to be enabled. That
setting is not exposed by the available API and is recorded as
`EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; a personal address is never an
acceptable fallback.

## Evidence

Before quarantine, the remote `main` head and its parent matched the frozen
values, the repository contained 35 commits, and the tree and contribution tip
were identical. Anonymous access to the repository, affected commit, and merged
pull request returned `404` after the visibility change, and anonymous cloning
failed.

The replacement commit comparison produced identical tree, parent, complete
message, subject, both dates, binary diff, raw mode/OID diff, changed-path list,
and content. Only the commit identity envelope and resulting SHA changed. A
verified private bundle, tree snapshot, diff, modes, paths, message, and hashes
remain outside the repository.

The complete local suite, a no-hardlink clean clone, private CI, and an anonymous
clone validate the 36-commit replacement history. The locked `kernel-v1` hash,
both experimental archives, and the ten frozen Mission 24 results remain
unchanged.

## Consequences

The canonical public repository is newly created from the cleaned local
history. It contains no object with the former metadata, no inherited pull
request, and no tag or release. No functional content changed.

The former staging repository retains its runs, pull request, settings, and
original object as private evidence. Its quarantine name and contents are not
part of the public documentation. It must never become public and must not be
deleted as part of ordinary maintenance.

## Revision triggers

Escalate immediately if the quarantined repository becomes anonymously
reachable, the affected object resolves in the canonical repository, a personal
address appears in any public object, an invariant comparison changes, or a
future web-authored commit bypasses the identity gate.
