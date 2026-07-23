# Status

## Present state

- **Phase:** **`PUBLIC_REPOSITORY_VERIFIED`**. The sole canonical repository is
  public at `ElGrandeXu/EGX_Terminal`, repository ID `1308085094`, with `main`
  as its default branch.
- **Verified publication checkpoint:** on 2026-07-23,
  `1d79ea37a1c614728cc7651c4d611218eaca174a` had 43 linear commits. This is the
  checkpoint of the final public verification, not a live commit counter.
- **Public protections observed at that checkpoint:** Private Vulnerability
  Reporting, secret scanning, push protection, vulnerability alerts, and the
  active `main-protection` ruleset were verified. The ruleset had no bypass and
  required pull requests, conversation resolution, linear history, deletion
  and force-push prevention, and the three named status checks.
- **Repository counts observed at final verification:** zero open pull requests,
  Git tags, GitHub releases, packages, and forks.
- **Release state:** no tag or release is active. `v1.0.0` is only a withdrawn
  historical record; `v1.0.1` is not prepared and remains a separate later
  mission.
- **Observation boundary:** these are dated GitHub API observations from the
  final public verification. The offline governance checker validates their
  internal consistency and does not claim to query GitHub in real time.
- **V1 closure hardening:** the active `main-protection` ruleset now requires
  each pull-request branch to be up to date with `main` before the three named
  checks can satisfy the merge gate. This later hardening does not rewrite the
  final-publication checkpoint or its historical observation.

## Final publication verification

- Public run
  [`30002915548`](https://github.com/ElGrandeXu/EGX_Terminal/actions/runs/30002915548)
  was created by `workflow_dispatch` at `2026-07-23T11:23:01Z`, was recorded
  successful by its `2026-07-23T11:26:08Z` update, and succeeded on its only
  attempt at checkpoint `1d79ea37a1c614728cc7651c4d611218eaca174a`.
- `repository / ubuntu`, `repository / windows`, and `licensing / reuse` all
  succeeded.
- Anonymous Level A, external-account Level B, and owner Level C verification
  all passed. Anonymous REST log downloads remained HTTP 403 and were classified
  `INFO` / `PLATFORM_AMBIGUITY`; this was non-blocking because Levels B and C
  succeeded.
- The final verification found no secret, private path, private email, retained
  signed URL, unauthorized tag, or release.

## Historical facts

- **Mission 24:** complete. Its final governance campaign is closed.
- **Final doctrine verdict:** **`REJECT_MICRO`**. The historical report publishes
  totals of 229,923 tokens for the baseline and 247,972 for the micro, with an
  overhead of 7.850019354305572% above the frozen 5% ceiling. These values remain
  internally arithmetically checkable, but the original aggregate and source
  runtime data are irrecoverable; [Decision
  0014](decisions/0014-micro-kernel-evidence-erratum.md) governs their
  interpretation. The earlier balanced candidate remains
  **`REJECTED_AS_BALANCED`**.
- **Initial identity remediation:** 30 prepublication commits were rewritten
  once to the approved GitHub ID-based `noreply` identity, with their trees,
  messages, dates, parents, diffs, paths, and modes preserved.
- **Public metadata incident and first return to private:** after the first
  squash merge, the identity gate detected a personal author address in the
  35th public commit and correctly blocked Ubuntu and Windows CI. The affected
  repository was made private, then the canonical repository was recreated from
  a content-identical clean history. At that incident point there was no tag,
  release, or fork.
- **Repository recreation:** [Decision
  0010](decisions/0010-recreate-public-repository-after-email-exposure.md)
  records the private replacement. The functional commit was reconstructed with
  the same tree, parent, complete message, dates, diff, paths, modes, and
  contents, using only approved `noreply` identities. PR #2 squash commit
  `c708bc6af88b5e98a08fc801e476d4c16248e701` established the 40-commit
  recovery checkpoint.
- **Pretransition audit:** the 2026-07-22 checkpoint
  `23cd5c596159fda6866e0fdc6ef0ba7bcf0d2515` contained 41 commits. Its initial
  executive verdict was **`PUBLICATION_BLOCKED`**. F-001 later closed after all
  twelve authorized Packages surfaces returned HTTP 200 with zero packages;
  schema 5 remediated F-002 through F-005. The historical merged-HEAD re-audit
  requirement was subsequently satisfied by the publication missions.
- **First controlled public transition and rollback:** checkpoint
  `c887949cbc3c6fe8aade34b2675b39545c365905` had 42 linear commits and no open
  pull request, tag, release, package, or fork. It was public from
  `2026-07-23T08:02:57.4503878Z` until rollback completed at
  `2026-07-23T08:34:32.3856142Z`, approximately 31 minutes and 35 seconds.
  Repository identity, branch, SHA, and content were unchanged. No material
  leak was detected, but third-party viewing or copying during that interval
  cannot be excluded.
- **First-window controls:** PVR and no-bypass `main-protection` were active and
  verified; secret scanning, push protection, vulnerability alerts, the minimal
  Actions policy, and approval for all external contributors were active. The
  three required checks succeeded, with zero secret-scanning alerts, packages,
  tags, releases, or forks observed.
- **Rollback diagnosis:** anonymous REST downloads of Actions logs returned HTTP
  403, which required rollback under the protocol then in force. Public controls
  in `actions/checkout`, `cli/cli`, and `astral-sh/ruff` behaved the same way.
  The result remains `GENERAL_GITHUB_ANONYMOUS_LOG_RESTRICTION` and
  `PLATFORM_AMBIGUITY`, with no evidence of an EGX-specific vulnerability or a
  private-origin restriction on historical run `29951087998`.
- **Historical run:** run `29951087998`, successful attempt 2, remains retained,
  non-reusable, and distinct from final run `30002915548`.
- **Historical post-rollback observation:** on the private GitHub Free
  repository, PVR and `main-protection` were unavailable, secret scanning was
  disabled, push protection was inactive, and `main` was unprotected. This
  dated state is preserved as history and does not describe the repository
  after final publication.
- **Withdrawn release:** `v1.0.0` is not a current tag or published release. Its
  former target, tag object, and release record exist only in verified private
  evidence. The terminal **`REJECT_MICRO`** verdict it documented remains
  unchanged.
- **Canonical-object boundary:** no object carrying the former personal metadata
  entered the recreated repository. Temporary recovery repositories were
  deleted only after verified private backups were retained outside it.

## Durable V1 invariants

- [Decision 0005](decisions/0005-ship-v1-with-neutral-root.md) selects a neutral
  root with no automatically discovered harness instructions, active kernel,
  adapter, or hidden injection. Principles remain documented and opt-in.
- The benchmark phase is closed. No kernel adjustment, third variant, payload
  change, threshold reinterpretation, aggregate reconstruction, or further V1
  doctrine benchmark is permitted.
- `experiments/kernel-v1/` and `experiments/kernel-micro-v1/` remain immutable
  inactive archives. Preserved micro definition artifacts are directly
  auditable; the published runtime claims are not independently verifiable from
  source data.
- The locked experimental hashes, neutral-surface registry, action lock,
  publication plan, release policy, hashed REUSE locks, workflow, JSON/TOML,
  Git-integrity, link, licensing, and active test checks form the local gate.
- [Decision 0006](decisions/0006-adopt-file-scoped-apache-and-cc-licensing.md)
  remains accepted. `REUSE.toml` assigns every tracked non-exempt file exactly
  one effective Apache-2.0 or CC-BY-4.0 license.
- Email privacy remains `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`; future web
  operations require the setting to stay enabled, and the scanner accepts no
  personal-address fallback.

## Possible next steps

Only a separately authorized future mission may prepare `v1.0.1`, satisfy its
SSH-signing gate, and create a tag or release. Memory, hooks, skills, routing,
compression, and other advanced capabilities remain unimplemented and require
demonstrated need plus a separate decision. Third-party adoption has not yet
been demonstrated.
