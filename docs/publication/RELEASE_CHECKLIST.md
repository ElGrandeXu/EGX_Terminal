# First publication and release checklist

Each checked item is backed by a command result, API response, or remote run.

## Local and private staging

- [x] The 34 commits predating the protected PR use the canonical maintainer
  identity; policy schema 2 also accepts attributable GitHub `noreply`
  contributors and the exact web committer.
- [x] Canonical checks, full tests, `reuse lint`, and `actionlint` pass.
- [x] Archive and Mission 24 hashes match their locked values.
- [x] The private recovery bundle is absent from the repository.
- [x] Only `main` was pushed; no tag was created.
- [x] The amended private-staging SHA passed all three named CI checks.
- [x] Failed staging runs were deleted after the green run was retained.
- [x] Description, topics, features, merge settings, and Actions policy match
  the machine-readable record.

## Public transition

- [x] Maxime explicitly authorized the visibility change.
- [x] Visibility is public and anonymous browsing, `ls-remote`, and cloning work.
- [x] The anonymous clone passed local checks, tests, REUSE, links, licensing,
  identity, history, and frozen-integrity validation.
- [x] Private Vulnerability Reporting is active and discoverable.
- [x] Secret scanning, push protection, and vulnerability alerts are active.
- [x] No personal address, secret, authenticated URL blob, or private bundle was
  found in the published surface.
- [x] The 34th documentation commit passed the three public CI checks.
- [x] `main-protection` is active and verified after that green CI.
- [x] The first protected pull-request path requires the same three checks and a
  squash merge without administrative bypass.

## Release

- [ ] A release is separately authorized.
- [ ] A release commit and notes describe only validated evidence.
- [ ] A release source archive passes the applicable checks.
- [ ] An annotated tag and GitHub release are created.

No release or tag exists. The next gate is a separate explicit decision on
`v1.0.0`; the completed repository checks do not authorize it.
