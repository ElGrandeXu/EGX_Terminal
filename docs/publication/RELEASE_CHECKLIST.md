# First publication and release checklist

Each item requires the named command, API response, settings export, or captured
review result as evidence.

## Local

- [ ] `git status --short` is empty and `git remote` is empty.
- [ ] `git log --format='%an <%ae>|%cn <%ce>'` shows only the approved identity.
- [ ] The canonical checks, full tests, `reuse lint`, and `actionlint` pass.
- [ ] `git rev-list --count HEAD` reports 32 and history checks pass on all refs.
- [ ] Archive and Mission 24 hashes match their locked values.
- [ ] The private recovery bundle exists outside `git rev-parse --show-toplevel`.

## Private remote staging

- [ ] The target is created empty, private, and without generated starter files.
- [ ] Only `main` is pushed; remote commit count and identity equal the local proof.
- [ ] All three named CI checks pass on GitHub.
- [ ] A clean remote clone passes all local checks without source-workspace files.
- [ ] Description, topics, features, merge settings, and Actions policy match the JSON plan.
- [ ] Private Vulnerability Reporting and available secret protections are enabled.
- [ ] `main-protection` is active with the three required checks and documented bypass.

## Public transition

- [ ] Maxime has explicitly authorized the visibility change.
- [ ] Visibility is public and anonymous cloning and browsing work.
- [ ] README and documentation links resolve from the public repository.
- [ ] GitHub displays the intended file-scoped license materials and Community Profile files.
- [ ] A final unauthenticated review finds no personal address, secret, or private artifact.

## Release

- [ ] The `v1.0.0` annotated target and release notes describe the validated commit.
- [ ] The release source archive reproduces the expected files and passes applicable checks.
- [ ] Release checks pass before publication; no tag or release is created prematurely.
- [ ] The repository is pinned on the profile only after successful publication.
