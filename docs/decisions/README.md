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
