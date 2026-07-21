# 0012 — Close canonical recovery after immutable tag reservation

- **Status:** accepted
- **Date:** 2026-07-21

## Context

The consolidation pull request was technically validated. Its GitHub squash
merge nevertheless created a commit whose author metadata used a personal
address. The identity gate detected the exposure immediately. The repository was
made private and replaced with a canonical repository containing only the clean
history.

The functional commit was reconstructed with the approved GitHub `noreply`
identity. Its tree, parent, complete message, author and committer dates, and
diff are identical to the affected commit. No affected commit or pull-request
ref was imported into the recreated repository.

The former `v1.0.0` release was withdrawn as part of that remediation. GitHub's
immutable-release protection reserves its tag name even though the recreated
repository has no corresponding ref. Reusing the exact name is therefore not an
available operation on the new repository.

## Decision

Do not pursue a workaround or a GitHub Support request to republish `v1.0.0`.
Treat it as a historical release withdrawn during privacy remediation. Preserve
its former tag object, target, and release record only in verified private
bundles outside the repository. Those private artifacts are evidence, but are
not part of the public or canonical verification surface.

The canonical repository has no current release and no Git tag. Its next
candidate is `v1.0.1`; this decision neither creates nor authorizes that tag or
release. PR 2 remains the next repository step and will occur separately.

Temporary recovery repositories were deleted only after independent local
mirrors, complete bundles, private metadata captures, `git bundle verify`,
`git fsck --full`, and SHA-256 manifest verification succeeded.

The recovery-closing documentation may be pushed directly to private `main` as
a one-time exception before activation of the final protection ruleset. It must
be a non-force fast-forward. This exception does not authorize any future direct
push; ordinary work resumes through the protected pull-request path.

## Evidence

The recreated canonical `main` contained 37 clean commits before this closing
decision, no Git tag, no GitHub release, and no pull request. Its remote identity
and private visibility were checked before mutation. The two temporary
repositories returned `404` after their verified backups were retained, and the
account repository list contained only the canonical project repository.

The release-policy checker accepts an absent historical release ref, rejects a
withdrawn tag if it reappears, rejects undeclared or unsigned future releases,
and never attempts to read or reconstruct the absent historical objects.

## Consequences

Users must not interpret `v1.0.0` as an active, latest, downloadable, or current
release in the recreated repository. Its experimental conclusions remain
unchanged because this decision alters publication state, not experimental
evidence. No file in either experimental archive is modified.

Future release preparation starts from candidate `v1.0.1` only after PR 2 and a
separately authorized signing-key decision. Until then, the SSH signature policy
remains `KEY_SELECTION_REQUIRED` with no active identity.

## Revision triggers

Revisit this decision only if GitHub changes the immutable-release reservation
semantics, private evidence fails integrity verification, or a later authorized
release mission changes the candidate or signing policy. Do not revise it merely
to recreate the withdrawn tag name.
