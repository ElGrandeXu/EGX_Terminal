# Decision records

Use one short Markdown file per consequential project decision. Prefer evidence
and revision criteria over ceremony.

## Required fields

- **Status:** proposed, provisional, accepted, superseded, or rejected.
- **Context:** the bounded problem and constraints.
- **Decision:** what the project will do now.
- **Evidence:** direct sources, observations, and measurements.
- **Consequences:** benefits, costs, limitations, and follow-up effects.
- **Revision triggers:** concrete conditions that require reconsideration.

Keep facts, interpretations, and project choices visibly distinct. Link evidence
directly and record observed versions or commits when relevant.

## Records

- [0001 — Bootstrap entrypoints](0001-bootstrap-entrypoints.md) — superseded by
  the neutral V1 root decision
- [0002 — Architecture du kernel LLM-agnostique](0002-llm-agnostic-kernel-architecture.md)
  — accepted architecture, no behavioral activation
- [0003 — Rejet du kernel équilibré](0003-balanced-kernel-rejection.md) — rejected
  balanced payload; archived evidence; inactive static micro candidate
- [0004 — Évaluation finale du micro-kernel](0004-micro-kernel-final-evaluation.md)
  — `REJECT_MICRO`; no always-on doctrine and no further V1 doctrine benchmark
- [0005 — Publication de la V1 avec une racine neutre](0005-ship-v1-with-neutral-root.md)
  — accepted; no automatically discovered root instructions in V1
- [0006 — Adopter des licences Apache et CC par fichier](0006-adopt-file-scoped-apache-and-cc-licensing.md)
  — accepted; exhaustive file-scoped Apache-2.0 and CC-BY-4.0 governance
- [0007 — Remédier l'identité publique des commits](0007-remediate-public-commit-identity.md)
  — accepted; one controlled pre-publication rewrite to the approved ID-based
  GitHub `noreply` identity
- [0008 — Finalize public repository governance](0008-finalize-public-repository-governance.md)
  — accepted; maintainer-led community files, hardened CI, and private staging
- [0009 — Publish the V1 repository](0009-publish-v1-repository.md) — superseded;
  records the initial publication sequence before repository recreation
- [0010 — Recreate the public repository after email exposure](0010-recreate-public-repository-after-email-exposure.md)
  — superseded in part; recreate the canonical surface from a content-identical
  `noreply` history, with remote-quarantine retention later replaced by verified
  private backup and deletion
- [0011 — Record the v1.0.0 release and adopt a tag-aware release policy](0011-record-v1.0.0-release-and-tag-policy.md)
  — superseded current-release state; retains the contemporaneous release-policy
  rationale before privacy remediation
- [0012 — Close canonical recovery after immutable tag reservation](0012-close-canonical-recovery-after-immutable-tag-reservation.md)
  — superseded in part by 0013; retain the recovery and withdrawn-release facts,
  while replacing the protected-path assumption with procedural pull-request
  discipline
- [0013 — Record observed GitHub governance limitations](0013-record-observed-github-governance-limitations.md)
  — accepted; keep the repository private on GitHub Free, separate desired from
  observed controls, and use procedural pull-request discipline until the
  pre-publication re-evaluation
