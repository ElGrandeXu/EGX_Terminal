# GitHub publication plan

This procedure translates the machine-readable
[`github-publication-plan.json`](../../governance/github-publication-plan.json)
into an operator checklist. It authorizes no remote action by itself. Every
remote setting is `PLANNED_NOT_APPLIED`.

## Phase 1 — Local validation

Run the complete sequence in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md),
confirm a clean worktree, 32 public-identity commits, immutable archives, no
remote, and no target-repository collision.

Stop if any check fails, the target repository already exists unexpectedly, the
GitHub account is not `ElGrandeXu` with ID `177521250`, or publication authority
is ambiguous.

Workflow syntax was validated with actionlint 1.7.12 from the official
[`rhysd/actionlint` release](https://github.com/rhysd/actionlint/releases/tag/v1.7.12).
The Windows AMD64 archive SHA-256 was
`6e7241b51e6817ea6a047693d8e6fed13b31819c9a0dd6c5a726e1592d22f6e9`, the
extracted binary SHA-256 was
`54ca21be3de4c7cfa26914aa8b61bd76bf573ef3caac5f80d110558cdf241718`, and the
syntax result was `PASS`. The temporary tool was removed after validation.

## Phase 2 — Create and stage a private remote

Only after separate explicit authorization, create an empty private repository.
Do not initialize it with a README, license, or `.gitignore`.

Planned commands, not executed by this mission:

```console
gh repo create ElGrandeXu/EGX_Terminal --private --disable-wiki
git remote add origin https://github.com/ElGrandeXu/EGX_Terminal.git
git push -u origin main
```

Push `main` only. Verify the pushed identity and commit count, wait for all three
checks (`repository / ubuntu`, `repository / windows`, and `licensing / reuse`),
then create a clean remote clone without local object sharing and run every local
check there.

Apply the planned description, topics, features, merge policy, and read-only
Actions policy. Enable Private Vulnerability Reporting before public visibility,
plus secret scanning, push protection, and security alerts where available.
After the first successful CI run has registered the check names, apply the
active `main-protection` ruleset exactly as planned.

## Phase 3 — Public transition

Review the Community Profile without claiming complete coverage. Change
visibility only with Maxime's explicit authorization. Then verify the repository,
files, links, license display, security entrypoint, and anonymous read access in
an unauthenticated session.

If staging fails before public visibility, keep the repository private, disable
or remove incorrect settings, remove the local `origin` if the staging attempt
is abandoned, and delete the private remote only with explicit authorization.
Do not rewrite or force-push published history. A security-driven exception
requires a separate documented decision.

## Phase 4 — Release

Public visibility and a release are distinct decisions. Only after public
validation, prepare the `v1.0.0` tag and release notes, validate the source
archive and checks again, publish the release, and optionally pin the repository
on the GitHub profile.

Stop at any phase for a failing check, unexpected identity or object count,
private-data exposure, license or provenance ambiguity, unavailable private
security reporting, ruleset mismatch, or lack of explicit authorization.
