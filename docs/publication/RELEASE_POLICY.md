# Release and tag policy

The canonical machine-readable contract is
[`governance/release-policy.json`](../../governance/release-policy.json). Stable
versions use declared SemVer tags of the form `vMAJOR.MINOR.PATCH`. Every release
tag must be annotated, created by an authorized public `noreply` identity, point
to its declared commit, and remain in the canonical history of `main`. Unknown,
lightweight, moved, divergent, or otherwise mismatched tags are review findings.

## Historical v1.0.0 record

`v1.0.0` is the immutable first release. Its annotated tag object
`a5668506f38dfc73ec6d8236de00a6adad095e25` targets commit
`870964a48fc07ff39d65c46255f189d25658ff2c`; GitHub release `357471186` is
published, stable, latest, and immutable. The tag was not cryptographically
signed. Its actual attestation mode is therefore recorded as an unsigned
annotated tag paired with the immutable GitHub release. It must never be
recreated, replaced, moved, or retroactively signed.

## Future release signatures

Future release tags, beginning with `v1.0.1`, require SSH signatures. SSH was
selected because Git 2.54.0 and OpenSSH 9.5 on the release workstation support
Git's SSH signing and offline verification, while GPG is not installed. GitHub
also documents SSH as the simplest signing option for most individual users.

No durable SSH or GPG signing key was registered for the public maintainer
identity during this consolidation. No key was generated. Before `v1.0.1` can be
tagged, the release mission must:

1. select a durable SSH signing key without changing the maintainer's public Git
   identity;
2. publish only its public key and SHA256 fingerprint to GitHub;
3. record the public key, fingerprint, principal, and activation date in the
   release policy and a repository-owned allowed-signers file; and
4. verify a test signature offline before creating the real tag.

The machine-readable signature policy has two explicit states. In
`KEY_SELECTION_REQUIRED`, there is no active identity and no release at or after
`v1.0.1` may be recorded as published. In `ACTIVE`, the policy names a
repository-owned signing identity with its principal, allowed-signers path,
SHA256 public-key fingerprint, activation date, revocation date, and canonical
`last_trusted_release` boundary. An active identity has neither revocation date
nor trust boundary. A revoked identity requires both, cannot be active, and
retains its public key and repository-owned allowed-signers file. Release
records distinguish the exact unsigned historical exception for `v1.0.0` from
SSH-signed future tags.

After that gate, configure Git with `gpg.format=ssh` and the selected public
signing key, create the annotated tag with `git tag -s`, and verify it offline:

```console
git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile=governance/release-allowed-signers \
  tag -v v1.0.1
```

The release sequence avoids a circular tag-object declaration: create the signed
tag locally without pushing it, record its object and target through the
protected `main` PR path, then push only the declared tag. On a tag event the
workflow uses two isolated checkouts. Canonical `main`, with full history and
tags, authorizes the triggering tag and verifies its SSH signature through Git
with `gpg.format=ssh` and the declared allowed-signers file. A second checkout
resolves the exact triggering tag and runs the content, test, structured-file,
Git-integrity, and hash-locked REUSE validations from that released tree. The
tag-push gate succeeds only when both the authorization and exact-tree proofs
succeed. Publish the immutable GitHub release only after that gate succeeds.

Rotation requires publishing and recording the replacement key before its first
use. Revocation cuts off authority for future releases; it does not invalidate
historical releases at or below the protected `last_trusted_release` SemVer
boundary. Git still verifies every such tag with the retained old public key and
allowed-signers file. Any later release using that identity is rejected, without
relying on the tagger-controlled timestamp.

## Distinct guarantees

The tag signature authenticates the Git tag object and its target. GitHub's
immutable-release setting prevents edits to the published release record, but it
does not replace offline signature verification. A GitHub artifact attestation,
if a future release creates one, binds a built artifact to a GitHub workflow;
checksums detect artifact changes. Neither an attestation nor a checksum replaces
the signed tag, and no separate attestation or checksum set is claimed for the
generated `v1.0.0` source archives.

The relevant current references are GitHub's [signature verification
overview](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification),
[SSH signing configuration](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key),
and [tag signing procedure](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-tags),
verified on 2026-07-21.
