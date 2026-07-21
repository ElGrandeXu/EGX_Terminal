# 0011 — Record the v1.0.0 release and adopt a tag-aware release policy

- **Status:** superseded by [0012](0012-close-canonical-recovery-after-immutable-tag-reservation.md)
- **Date:** 2026-07-21

This record describes the repository state before the privacy-remediation
recreation. Decision 0012 governs the current state: `v1.0.0` is withdrawn, and
the canonical repository has no tag or published release.

## Context

The release of `v1.0.0` was explicitly authorized and executed after commit
`870964a48fc07ff39d65c46255f189d25658ff2c`. That authorization existed in the
release process and its notes, but the resulting state was not brought back into
the repository history.

A post-release audit found three consolidation defects: current documents still
described a pre-release state, `check_git_history.py` classified the legitimate
`refs/tags/v1.0.0` as `UNEXPECTED_TAG`, and the validation workflow did not run
on a release-tag push. Accepting all tags would weaken the publication boundary;
rewriting or replacing the published tag would destroy historical evidence.

## Decision

Keep `v1.0.0` unchanged. Record its exact target commit, annotated tag object,
immutable GitHub release, publication state, and actual unsigned attestation mode
in a strict machine-readable release policy. The history checker accepts a tag
only when its declaration, annotated object, target, version, tagger identity,
and ancestry in canonical `main` all agree. Every unknown, lightweight, moved,
divergent, or mismatched tag remains a review finding.

Run the existing validation workflow on narrow `v*` tag pushes and leave final
acceptance to the repository policy. A tag-push gate must prove two independent
facts: canonical `main` authorizes and cryptographically verifies the tag, and a
separate checkout of the exact tag target passes every applicable content and
REUSE validation. Future release tags require SSH signatures, but `v1.0.1`
remains blocked until a durable public signing key, principal, fingerprint, and
repository-owned allowed-signers record are selected. This decision prepares
that gate; it does not create the `v1.0.1` tag or release.

## Evidence

The existing remote tag object
`a5668506f38dfc73ec6d8236de00a6adad095e25` peels to the declared commit. GitHub
release `357471186` is published, stable, latest, and immutable. The tag object
has an authorized GitHub ID-based `noreply` tagger and no cryptographic
signature. Before this correction, the strict history command produced one
review finding: `refs/tags/v1.0.0 [UNEXPECTED_TAG]`.

The post-release audit also reproduced `sha_pinning_required: false` at the
official repository Actions-permissions endpoint even though the publication
plan claimed the setting was applied. The setting was changed to `true`; the
selected-action allowlist and read-only workflow-token policy were restored and
verified unchanged after the API mutation.

## Consequences

An old valid release tag may remain on an ancestor of `main`; it need not point
to the current head. `v1.0.0` remains immutable and is not retroactively signed.
The source archive still cannot prove Git history, refs, identities, or tag
objects; those checks require a full clone.

This correction belongs to the `v1.0.1` consolidation line. It adds no product
capability, changes no experimental evidence, and reopens no doctrinal decision.

## Revision triggers

Revisit the policy if Git changes its signed-tag verification model, the public
release identity rotates or is revoked, GitHub changes immutable-release or
attestation semantics, a declared tag stops resolving to its locked object, or a
new stable version is prepared.

The schema intentionally supports both the current `KEY_SELECTION_REQUIRED`
state and a future `ACTIVE` state. Activation requires real Git SSH verification;
the presence of a signature marker alone is never accepted as evidence.
