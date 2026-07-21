# First publication and release checklist

Each checked item is backed by a command result, API response, remote run, or
anonymous validation.

## Metadata incident and quarantine

- [x] The former public HEAD, parent, tree, message, dates, and 35-commit count
  matched the frozen values before mutation.
- [x] No tag, release, or public fork was observed.
- [x] The former repository was made private before any other remote mutation.
- [x] Anonymous repository, commit, and pull-request access returned `404`; an
  anonymous clone failed.
- [x] The former repository was renamed to an unpublished private quarantine,
  remains unarchived, and retains its runs, pull request, settings, and history.
- [x] GitHub email privacy is recorded as
  `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web operations require it.

## Cleaned local history

- [x] The replacement commit preserves the tree, parent, complete message,
  subject, author and committer dates, binary diff, paths, modes, and contents.
- [x] The replacement uses `ElGrandeXu` as author, `Maxime Erard` as committer,
  and only the approved GitHub ID-based `noreply` address.
- [x] The contribution branch, transport refs, reflogs, and unreachable objects
  were removed; the old commit no longer resolves locally.
- [x] Private bundles and the incident capture remain outside the repository.
- [x] The remediation documentation is the 36th commit.
- [x] Canonical checks, 188 tests, JSON, TOML, locks, `reuse lint`, actionlint,
  Markdown links, `git diff --check`, and `git fsck --full` pass.
- [x] The locked `kernel-v1` hash, both archives, and the ten Mission 24 results
  are unchanged.
- [x] A clean clone created without hardlinks passes the same validations.

## New private repository

- [x] `ElGrandeXu/EGX_Terminal` was created empty and private with `main` as its
  only pushed branch.
- [x] The initial push was non-force and contained 36 commits, zero tags, zero
  releases, zero pull requests, no old object, and no personal identity.
- [x] `repository / ubuntu`, `repository / windows`, and `licensing / reuse`
  passed privately with `REVIEW=0`, `BLOCKER=0`, fail-fast Windows, and intact
  archives.
- [x] Description, topics, features, merge policy, Actions policy, and security
  settings match the machine-readable record.

## Public transition

- [x] Maxime explicitly authorized the visibility change.
- [x] Visibility is public and anonymous browsing, `ls-remote`, and cloning work.
- [x] The anonymous clone contains 36 commits and passes the complete suite.
- [x] The former commit and pull request are absent from the canonical repository.
- [x] The quarantined repository remains inaccessible anonymously.
- [x] Private Vulnerability Reporting where available, secret scanning, push
  protection, and vulnerability alerts are active.
- [x] `main-protection` is active with the three required checks, pull requests,
  zero required approvals, resolved conversations, linear history, and deletion
  and force-push protection.

## Historical v1.0.0 release

- [x] The release was separately and explicitly authorized after commit
  `870964a48fc07ff39d65c46255f189d25658ff2c`.
- [x] The release target and notes describe only the validated V1 evidence and
  preserve the existing compatibility limits.
- [x] Annotated tag object `a5668506f38dfc73ec6d8236de00a6adad095e25`
  and immutable GitHub release `357471186` were created for `v1.0.0`.
- [ ] A generated GitHub source archive was validated after publication using a
  documented archive-only sequence. This was not recorded for `v1.0.0`.
- [ ] CI ran from the tag-push event. The workflow did not yet have that trigger,
  so this proof is intentionally not claimed for `v1.0.0`.

## Policy prepared on main for v1.0.1

- [x] The exact historical tag and release are declared in the release policy.
- [x] Unknown, lightweight, moved, divergent, or mismatched tags fail review.
- [x] The validation workflow has a narrow `v*` tag-push trigger and retains its
  three names, read-only permissions, SHA-pinned actions, and Windows gate.
- [x] The future tag gate separately validates authorization from canonical
  `main` and all applicable content from the exact triggering tag target.
- [x] The history checker supports an `ACTIVE` SSH policy and verifies signed
  tags cryptographically with Git and a repository-owned allowed-signers file.
- [x] REUSE 6.2.0 and its Python 3.11/Ubuntu dependency chain install from
  dedicated SHA256-hashed locks.
- [ ] A durable SSH signing public key, fingerprint, principal, and offline
  allowed-signers record are selected and published.
- [ ] A `v1.0.1` tag or GitHub release is created. This consolidation PR does not
  authorize or perform either action.
