# Recovery closure and future release checklist

Each checked item is backed by a command result, API response, remote run, or
verified private artifact. This checklist does not authorize `v1.0.1`.

## Canonical recovery

- [x] The pre-closing `main` HEAD is the expected 37th clean commit.
- [x] Local `main`, `origin/main`, and remote `main` agree before mutation.
- [x] The canonical repository ID and private visibility match governance.
- [x] The canonical repository has no GitHub tag, release, or pull request.
- [x] The affected commit and former pull-request refs were not imported.
- [x] The functional commit retains its tree, parent, complete message, dates,
  and diff under the approved GitHub `noreply` identity.

## Private evidence and repository cleanup

- [x] Both temporary repositories were private and had the expected IDs.
- [x] Each repository has an independent mirror, complete bundle, private API
  metadata capture, ref inventory, and summary outside the canonical repository.
- [x] Each bundle passes `git bundle verify`.
- [x] Each mirror passes `git fsck --full`.
- [x] SHA-256 covers the bundles and captures, and the complete private manifest
  verifies.
- [x] Metadata captures contain no unredacted email address.
- [x] The temporary repositories were deleted only after those checks passed.
- [x] Authenticated API reads, account listing, and repository URLs confirm their
  absence while the canonical repository remains intact.

## Historical v1.0.0 state

- [x] `v1.0.0` is declared as withdrawn during privacy remediation, not current.
- [x] Its former target, tag object, and GitHub release ID are retained only as
  private historical metadata backed by a verified bundle.
- [x] The canonical policy expects no `v1.0.0` ref.
- [x] The checker rejects the withdrawn tag if it reappears.
- [x] The checker does not read, reconstruct, or simulate absent historical
  objects.
- [x] GitHub's immutable-release reservation is recorded as blocking reuse of
  the tag name; no workaround or Support request is pursued.

## Canonical current state

- [x] `current_releases` is empty.
- [x] The canonical repository has zero Git tags and zero GitHub releases.
- [x] `v1.0.1` is recorded only as `next_candidate`.
- [x] No `v1.0.1` tag or release is created by recovery closure.
- [x] PR 2 is not created or started by recovery closure.
- [x] The SSH policy remains `KEY_SELECTION_REQUIRED`, with no active identity
  and no key added.

## Closing commit and current workflow

- [x] One intentional closing commit uses the approved GitHub `noreply` author
  and committer identity and has the former clean HEAD as its sole parent.
- [x] The push is a direct non-force fast-forward to private `main`, documented
  as a one-time recovery exception before final ruleset activation.
- [x] The three private checks pass on the closing commit.
- [x] Repository metadata, topics, features, merge policy, Actions policy, and
  vulnerability alerts match governance.
- [x] The observed limitations are recorded: `main` is unprotected, rulesets are
  unavailable on the current private GitHub Free repository, Private
  Vulnerability Reporting is unavailable while private, secret scanning is
  disabled, and push protection is not active.
- [x] The desired `main-protection` rules remain target configuration only; pull
  requests are a mandatory project convention rather than active GitHub
  enforcement.
- [x] The final clean clone and content-only archive validations pass.
- [x] The final history contains 38 clean commits and no experimental change.

## Future v1.0.1 mission — not authorized here

- [ ] Complete PR 2 under the mandatory project pull-request convention.
- [ ] Re-evaluate remote controls and enable Private Vulnerability Reporting
  before any public publication.
- [ ] Select and record a durable SSH public signing identity.
- [ ] Verify the repository-owned allowed-signers record offline.
- [ ] Prepare and separately authorize the exact `v1.0.1` tag.
- [ ] Run the tag event gates and publish a release only after they succeed.
