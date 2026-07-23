# Release and tag policy

The canonical machine-readable contract is
[`governance/release-policy.json`](../../governance/release-policy.json). Its
schema separates current releases, historical releases withdrawn during
remediation, and the next candidate.

## Current releases

`current_releases` lists only releases that are presently published in the
canonical repository and whose Git refs must exist and pass the full object,
identity, ancestry, and signature checks. It is currently empty. The canonical
repository therefore expects and accepts no release tag.

Every future current release must use a declared SemVer tag of the form
`vMAJOR.MINOR.PATCH`. The tag must be annotated, created by an authorized public
`noreply` identity, point to its declared commit in canonical `main`, and match
its locked tag object. Unknown, lightweight, moved, divergent, or otherwise
mismatched tags are review findings.

## Withdrawn historical release

`v1.0.0` is recorded under `historical_releases` with status
`WITHDRAWN_DURING_PRIVACY_REMEDIATION`. It is not a current, latest,
downloadable, or published release in the recreated canonical repository. Its
former target, former tag object, and former GitHub release ID are identifiers
for private evidence only.

The evidence classification is `PRIVATE_VERIFIED_BUNDLE`; its visibility is
explicitly private and the policy makes no public-verification claim. The
checker validates the historical record's shape and consistency but never reads,
resolves, reconstructs, or simulates those absent objects. If `v1.0.0` appears as
a ref, the checker rejects it because `expected_ref_present` is false.

GitHub's immutable-release reservation blocks reuse of the `v1.0.0` tag name in
the recreated repository. The project does not pursue a workaround or Support
request. The experimental conclusions associated with the former release remain
valid because no experimental evidence was changed.

## Next candidate

`next_candidate` is `v1.0.1`. This field is a planning constraint, not a tag or
release declaration. `v1.0.1` does not currently exist. The verified public
repository state does not authorize its preparation; that requires a separate
later mission.

The checker requires the candidate to be a valid version, absent from both the
current and historical sets, and later than every recorded release. A tag named
`v1.0.1` remains unexpected until a later policy change declares it as a current
release through the protected workflow.

## Future release signatures

Future release tags beginning with `v1.0.1` require SSH signatures. The
signature policy remains `KEY_SELECTION_REQUIRED`: no active identity exists,
no signing key was added, and every current release at or after `v1.0.1` is
rejected while that gate is blocked.

Before a future release mission can proceed, it must:

1. select a durable SSH signing key without changing the maintainer's public Git
   identity;
2. publish only its public key and SHA-256 fingerprint to GitHub;
3. record the public key, principal, fingerprint, activation date, and
   repository-owned allowed-signers file; and
4. verify a test signature offline before creating the real tag.

In `ACTIVE` state, Git verifies each SSH-signed annotated tag against the exact
repository-owned allowed-signers record. Rotation and revocation retain explicit
SemVer trust boundaries; they do not relax identity, ancestry, object, or
cryptographic verification for future releases.

## Tag-event validation

The workflow keeps a narrow `v*` push trigger for a separately authorized future
release. Canonical `main` authorizes and verifies the tag, while an isolated
checkout of the exact tag target runs applicable content, test, structured-file,
Git-integrity, and hash-locked REUSE checks. Keeping this future gate does not
create a tag and does not imply that a current release exists.

A source archive without `.git` cannot verify refs, commit identities, tag
objects, ancestry, or signatures. It runs only content-applicable checks and
must never fabricate the missing Git evidence.
