# Cartographie du repository et du delivery

## Méthode et périmètre

Snapshot : `main@45e6e80ae2e63b65fad0d89f5e13171229c8f295`, résolu et
cloné avec son historique complet le 2026-07-20. L'inventaire ci-dessous vient
de `git ls-files`; les lignes sont des lignes physiques et non vides calculées
statiquement. Aucun fichier du projet n'a été exécuté. [E-SNAPSHOT]

## Inventaire exact

- 173 fichiers suivis : 164 textuels et 9 binaires.
- 2 branches distantes réelles : `main` et `feat/server` ; 9 tags ; 9 releases.
- 119 commits uniques sur toutes les refs, dont 103 atteignables depuis le
  `main` audité et 8 commits de merge ; 25 auteurs observés.
- 149 issues : 51 ouvertes, 98 fermées.
- 382 pull requests : 260 ouvertes, 40 fusionnées, 82 fermées sans fusion.
- 31 PR fusionnées vers `main`; 9 vers `feat/server`.
- 7 chemins sous un nom de test, dont `tests/__init__.py`; 6 fichiers de tests
  exécutables statiquement identifiés, 88 cas nommés (67 Vitest, 21 unittest).
- Dépendances déclarées : 11 runtime, 5 dev, 1 optionnelle, 2 peers optionnelles.

| Extension/langage | Fichiers | Lignes physiques | Lignes non vides |
| --- | ---: | ---: | ---: |
| TypeScript `.ts` | 117 | 36 503 | 32 548 |
| Markdown `.md` | 15 | 3 809 | 2 812 |
| Python `.py` | 6 | 2 969 | 2 549 |
| shell `.sh` | 7 | 2 798 | 2 458 |
| JSON | 5 | 362 | 362 |
| YAML `.yml` + `.yaml` | 5 | 309 | 273 |
| batch `.bat` | 1 | 217 | 188 |
| JavaScript `.mjs` | 4 | 133 | 105 |
| Dockerfile `.hermes` | 1 | 106 | 89 |
| autres textuels | 3 | 95 | 76 |

Les 9 binaires sont exclusivement les images sous `assets/images/`.
[E-INVENTORY]

## Composants et responsabilités

| Composant | Chemins | Responsabilité | Couplage principal |
| --- | --- | --- | --- |
| Entrée plugin | `index.ts`, `openclaw.plugin.json` | enregistrement config, hooks, outils, CLI | OpenClaw Plugin SDK |
| Core long terme | `src/core/tdai-core.ts`, `conversation/`, `record/`, `scene/`, `persona/`, `profile/` | L0→L3, capture, consolidation, recall | `HostAdapter`, stockage, LLM runner |
| Recherche/stockage | `src/core/store/`, `src/core/tools/` | SQLite/FTS/vec, TCVDB, BM25, embeddings, outils | sqlite-vec, TCVDB optionnel |
| Orchestrateur | `src/utils/pipeline-manager.ts`, `checkpoint.ts`, `backup.ts` | triggers, files, files d'attente, curseurs, reprise | timers/process host |
| Offload | `src/offload/` | refs, JSONL, L1/L1.5/L2/L3, Mermaid, token tracking | hooks et format de messages OpenClaw |
| OpenClaw adapter | `src/adapters/openclaw/` | runner embarqué, chemins et hooks host | interfaces OpenClaw |
| Standalone/Gateway | `src/adapters/standalone/`, `src/gateway/` | service HTTP long terme et runner OpenAI-compatible | HTTP local, config propre |
| Hermes adapter | `hermes-plugin/...`, `docker/opensource/` | `MemoryProvider` Python devant le Gateway | API Hermes + sous-processus Gateway |
| CLI et données | `src/cli/`, `bin/`, `scripts/read-*`, migration/export | seed, lecture, migration, export | schémas internes/TCVDB |
| Installation/patch | `scripts/*.sh`, `.bat`, `postinstall.mjs`, `SKILL.md` | installation, patch OpenClaw, exploitation | environnement utilisateur |
| Observabilité | `src/core/report/`, `src/offload/opik-tracer.ts` | rapport local/TCVDB et traces Opik | contenu potentiellement sensible |

## Arborescence logique

```text
plugin OpenClaw
├── TdaiCore
│   ├── L0 JSONL + index L0
│   ├── L1 extractor/dedup + records JSONL + SQLite|TCVDB
│   ├── L2 scene_blocks/*.md + .metadata/scene_index.json
│   ├── L3 persona.md + profile sync
│   └── recall + memory/conversation tools
├── context offload (OpenClaw-specific)
│   ├── refs/*.md
│   ├── offload-<session>.jsonl
│   ├── mmds/*.mmd + metadata/state
│   ├── L1/L1.5/L2 local or backend
│   └── L3 message mutation + MMD injection
└── lifecycle/install
    ├── postinstall → patch OpenClaw
    ├── CLI seed/migrate/export/read
    └── cleaner/checkpoints/backups

Gateway standalone → TdaiCore
Hermes MemoryProvider → HTTP Gateway → TdaiCore
```

## Flux de données

### Long terme

```text
messages host
  → sanitize/filter L0
  → conversations/YYYY-MM-DD.jsonl
  → SQLite|TCVDB L0 index
  → L1 extraction JSON
  → LLM dedup store|update|merge|skip
  → records/YYYY-MM-DD.jsonl + SQLite|TCVDB L1
  → L2 LLM file operations → scene_blocks/*.md + scene_index.json
  → L3 LLM file operation → persona.md
  → before_prompt: stable L2/L3 + dynamic L1 recall
```

### Context offload

```text
after_tool_call
  → raw result → refs/<timestamp>.md
  → L1 prompt (result preview) → offload-<session>.jsonl
  → L1.5 task-boundary decision
  → L2 prompt → Mermaid MMD + tool_call_id↔node_id
  → token tracker/reclaimer
  → replace/delete tool history + inject MMD
  → model-initiated drill-down: node_id → JSONL → result_ref → raw ref
```

## Frontières core/adapters

Le long-term core a une frontière réelle : `TdaiCore` accepte un `HostAdapter`,
un `LLMRunner` et un `IMemoryStore`; le Gateway standalone réutilise ce core.
Il est donc plausible d'en extraire un service neutre, mais les types gardent
des `sessionKey`, conventions de rôle et attentes de fichiers issues des hosts.

L'offload n'a pas cette neutralité. Il s'enregistre directement sur les hooks
OpenClaw, manipule les objets messages et leurs attributs internes, compte avec
un encodage choisi, dépend des événements `after_tool_call`, `llm_input`,
`before_prompt_build`, du contexte window du host et de son cache. Le backend
externalise les appels L1/L2/L4, pas la décision/mutation de contexte. [E-PORT]

Le provider Hermes est un adaptateur réel sur `main`. Il supervise ou rejoint le
Gateway et implémente `initialize`, `system_prompt_block`, `prefetch`,
`sync_turn`, outils et shutdown. L'interface officielle Hermes au commit
`31c08a9...` accepte désormais aussi `messages` dans `sync_turn` et plusieurs
hooks/scope additionnels; la compatibilité de l'adaptateur audité n'est pas
testée contre ce snapshot Hermes courant. [E-HERMES]

## Histoire et commits pivots de `main`

| Commit | Date | Interprétation sourcée |
| --- | --- | --- |
| `7a5fce9` | 2026-04-09 | import initial |
| `7645183` | 2026-04-23 | release 0.1.4 |
| `3cc6d2a` | 2026-05-13 | correction documentaire des chiffres benchmark, sans artefacts |
| `a74b0b3` | 2026-05-13 | TCVDB, BM25 hybride, refactor pipeline 0.2.2 |
| `db8f3e5` | 2026-05-13 | Hermes, context offload et refactor core 0.3.3 |
| `d377b09` | 2026-05-13 | LLM local offload et retour CLI 0.3.4 |
| `1bdcf28` | 2026-05-26 | budgets recall PR #71 |
| `438869b` | 2026-05-27 | release 0.3.6 |
| `c6ed755` | 2026-06-02 | troncature recall par code point |
| `32ba4d3` | 2026-06-04 | timestamps configurables |
| `f61c5fd` | 2026-06-15 | avance du curseur L2 même sans record produit |
| `823b478` | 2026-06-15 | active le filtre regex L1 absent de npm 0.3.6 |
| `9fac8bc` | 2026-06-24 | prompts scène selon langue du dialogue |
| `38673b5` | 2026-06-24 | retry/backoff embeddings |
| `e9c1af0` | 2026-06-24 | stratégies `disableThinking` multi-provider |
| `47341a9` | 2026-07-17 | installation Hermes Windows |
| `fa830fa` | 2026-07-17 | tests de recovery Hermes |
| `45e6e80` | 2026-07-19 | dernier README, snapshot audité |

Les nombreux correctifs de curseur, Unicode, recovery, stockage et cache sont
une preuve de maturation par incidents, mais aussi la preuve que les invariants
étaient fragiles. [E-HISTORY]

## Versions, tags, releases et archives npm

### Lignées

- `main`: 103 commits, `package.json` 0.3.6, 56 fichiers changés depuis
  `v0.3.6` (2 581 insertions, 402 suppressions).
- `v0.3.6`: dernière release GitHub stable, base historique de npm 0.3.6.
- `feat/server`: branche distante distincte, sans merge-base trouvé avec le
  `main` audité; elle porte les tags/releases 1.x.
- npm `latest=1.0.1`, `beta=1.0.1-beta.2`; npm ne représente donc pas `main`.

### npm 0.3.6

- Archive : 696 603 octets, 2 599 118 décompressés, 146 entrées.
- SHA-1 : `8070874dba41ee6a0ae44b7f780405ce160419ba`.
- Intégrité vérifiée :
  `sha512-1Vpp2XeMzvDi9m+yIKnN+wdtclOlZmc5GWoSynYLjBWgJR8gEjGcVo96f9CHZW8unrCIkzjFXIaGVGeScBv98g==`.
- 122 fichiers correspondent octet pour octet au tag `v0.3.6`; le README
  diffère; 23 fichiers sont générés/propres au paquet; 41 fichiers du tag sont
  absents du paquet.
- Le paquet inclut un bytecode Python inattendu
  `hermes-plugin/.../__pycache__/__init__.cpython-313.pyc`.
- Son lifecycle est le shell
  `bash scripts/openclaw-after-tool-call-messages.patch.sh ... || true`.
- Il contient les budgets #71, mais pas l'activation du filtre L1 #175, fusionnée
  après publication. [E-NPM]

### npm 1.0.1

- Archive : 997 916 octets, 3 764 949 décompressés, 256 entrées.
- SHA-1 : `dafa3f0e4797b4a3ea6b32c65dea59de4dfd8bf5`.
- Intégrité vérifiée :
  `sha512-gwN1xHBUP1Uu4mgWL6Yd+QrdY+y+ZW+kDJ1B1K2LeRXXcKBBvewz2e0Q4F0c++OPCZOMBRrMjliG1lj/GuVOPg==`.
- 225 fichiers correspondent au tag `v1.0.1`, 31 sont générés/propres au
  paquet, 94 fichiers du tag sont absents; le même bytecode Python est présent.
- Le lifecycle shell de patch est encore déclaré.

Le nouveau `postinstall.mjs` de `main` évite Windows/Hermes et accepte une
variable de skip, mais appelle toujours le script de patch OpenClaw sur les
plateformes compatibles et masque l'échec. Il n'est dans aucun de ces paquets
publiés. [E-POSTINSTALL]

## Issues et pull requests importantes

La classification de titres, mécanique et non sémantique, répartit les 382 PR :
39 docs/traduction/images/liens, 94 adaptateurs, 98 mémoire/recherche, 72
offload/tokens/cache, 8 sécurité, 8 tests, 4 packaging, 59 autres. Elle sert à
éviter de confondre volume communautaire et maturité architecturale.

| Référence | Statut au 2026-07-20 | Ce qu'elle prouve |
| --- | --- | --- |
| PR #71 | fusionnée `main` | budgets L1, `0` = désactivé |
| issue #120 | ouverte | régression cache observée, attribution non isolée |
| PR #319 | ouverte | proposition anti-inflation et cache boundary; pas `main` |
| PR #411 | ouverte | invalidation manquante du WeakMap après mutation |
| PR #447 | ouverte | snapshots append-only/cache epoch proposés |
| PR #533 | ouverte | correction cache beaucoup plus large, pas `main` |
| PR #204 | ouverte | guide de reproductibilité uniquement, aucun runner |
| issue #62 / #111 | ouvertes | recherche transversale utilisateur/agent |
| issue #98 / PR #130 | fermée/fusionnée | curseur L2 bloqué sur sortie vide puis corrigé |
| issue #156 | fermée | perte/dérive lors des écritures doubles |
| issue #157 | ouverte | compteurs checkpoint divergents après nettoyage |
| issue #158 / PR #175 | fermée/fusionnée | npm 0.3.6 sans filtre d'injection |
| issue #176 | ouverte | L1 vide avec clean workspace sur certains hosts |
| issue #233 / PR #411 | ouvertes | stale token count pouvant sur-supprimer |
| issue #236 | ouverte | batch embeddings DashScope trop grand, dégradation silencieuse |
| issue #416 | ouverte | timer L2/L3 cassé sur la lignée 1.x Gateway |
| issue #521 | ouverte | `offload.dataDir` relatif/ vide accepté |
| PR #7 | fermée non fusionnée | ancien adaptateur Claude Code proposé |
| PR #323/#340/#367/#490 | ouvertes | adaptateurs Codex/Claude/OpenCode proposés seulement |

Une PR ouverte ne corrige pas le snapshot. Une issue est un signal empirique,
pas une reproduction effectuée par cet audit. [E-ISSUES]

## Tests statiquement identifiés

| Fichier | Cas | Classe |
| --- | ---: | --- |
| `src/utils/time.test.ts` | 38 | unité date/timezone |
| `src/utils/no-think-fetch.test.ts` | 20 | unité transformation requête |
| `src/offload/auth-profile-key.test.ts` | 5 | unité fallback secret |
| `src/utils/sanitize.test.ts` | 4 | unité regex/capture |
| `test_memory_tencentdb_recovery.py` | 16 | recovery/supervision Hermes simulée |
| `test_gateway_shutdown_leak.py` | 5 | shutdown/processus/WAL, dont validations d'intégration déclarées |

Couverture absente sur `main` : vérité L1, qualité L2/L3, dédup sémantique,
conflits, provenance, budget recall, recherche/isolation, cleaner, restore du
core, SQLite/TCVDB E2E, pipeline offload, Mermaid, résolution `node_id`, Gateway
auth/CORS/body limit, Windows réel, Qwen/petits modèles et benchmarks. Le
`vitest.e2e.config.ts` ne constitue pas un test. Le changelog `Unreleased`
mentionne un `__tests__/cleaner/verify-cleaner-safety.ts` absent des 173 fichiers
du snapshot. [E-TESTS]

## Dépendances

Runtime (11) : `@ai-sdk/openai`, `@node-rs/jieba`,
`@tencentdb-agent-memory/tcvdb-text`, `ai`, `js-tiktoken`, `json5`,
`sqlite-vec`, `tsx`, `undici`, `yaml`, `zod`.

Dev (5) : `@types/node`, `@vitest/coverage-v8`, `tsdown`, `typescript`,
`vitest`. Optionnelle : `opik`. Peers optionnelles : `node-llama-cpp`,
`openclaw`.

Les métadonnées npm correspondant aux dépendances directes et aux ranges du
manifest, consultées le 2026-07-20 (aucun lockfile ne fige une résolution),
indiquent Apache-2.0 pour AI SDK/AI,
MIT pour jieba/tcvdb-text/js-tiktoken/json5/tsx/undici/zod/node-llama-cpp et
OpenClaw, ISC pour yaml, `MIT OR Apache` pour sqlite-vec, Apache-2.0 pour Opik.
`sqlite-vec` publie toutefois une URL de repository `https://TODO`, ce qui
réduit l'auditabilité des métadonnées npm. Les dépendances transitives n'ont pas
été auditées. Ces licences permettent souvent la réutilisation, mais ne valident
ni interfaces privées ni maintenance. [E-LICENSE]

## Inventaire exhaustif des chemins suivis

```text
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/question.yml
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/pr-ci.yml
.gitignore
.npmignore
assets/images/flowchart1.cn.png
assets/images/flowchart1.png
assets/images/flowchart2.cn.png
assets/images/flowchart2.png
assets/images/logo.png
assets/images/logo2.png
assets/images/memory-pyramid-en.jpg
assets/images/memory-pyramid.png
assets/images/star-helper.png
bin/export-tencent-vdb.mjs
bin/migrate-sqlite-to-tcvdb.mjs
bin/read-local-memory.mjs
CHANGELOG.md
CONTRIBUTING_CN.md
CONTRIBUTING.md
docker/opensource/Dockerfile.hermes
docker/opensource/README-hermes.md
hermes-plugin/memory/memory_tencentdb/__init__.py
hermes-plugin/memory/memory_tencentdb/client.py
hermes-plugin/memory/memory_tencentdb/plugin.yaml
hermes-plugin/memory/memory_tencentdb/README.md
hermes-plugin/memory/memory_tencentdb/supervisor.py
hermes-plugin/memory/memory_tencentdb/tests/__init__.py
hermes-plugin/memory/memory_tencentdb/tests/test_gateway_shutdown_leak.py
hermes-plugin/memory/memory_tencentdb/tests/test_memory_tencentdb_recovery.py
index.ts
LICENSE
openclaw.plugin.json
package.json
README_CN.md
README.md
scripts/bugfix-20260423/bugfix-20260423-full.sh
scripts/bugfix-20260423/BUGFIX-20260423-SOP.md
scripts/bugfix-20260423/bugfix-20260423.sh
scripts/export-diagnostic.sh
scripts/export-tencent-vdb/export-tencent-vdb.ts
scripts/export-tencent-vdb/tsconfig.json
scripts/install_hermes_memory_tencentdb.sh
scripts/memory-tencentdb-ctl.sh
scripts/migrate-sqlite-to-tcvdb/cli-entry.ts
scripts/migrate-sqlite-to-tcvdb/config-write.ts
scripts/migrate-sqlite-to-tcvdb/manifest-write.ts
scripts/migrate-sqlite-to-tcvdb/node-llama-cpp.d.ts
scripts/migrate-sqlite-to-tcvdb/README.md
scripts/migrate-sqlite-to-tcvdb/sqlite-to-tcvdb.ts
scripts/migrate-sqlite-to-tcvdb/tsconfig.json
scripts/openclaw-after-tool-call-messages.patch.sh
scripts/postinstall.mjs
scripts/read-local-memory/read-local-memory.ts
scripts/read-local-memory/tsconfig.json
scripts/README.memory-tencentdb-ctl.md
scripts/setup-hermes-memory-tencentdb.bat
scripts/setup-offload.sh
SKILL-DIAGNOSTIC-EXPORT.md
SKILL-MIGRATION.md
SKILL.md
src/adapters/index.ts
src/adapters/openclaw/host-adapter.ts
src/adapters/openclaw/index.ts
src/adapters/openclaw/llm-runner.ts
src/adapters/standalone/host-adapter.ts
src/adapters/standalone/index.ts
src/adapters/standalone/llm-runner.ts
src/cli/commands/seed.ts
src/cli/index.ts
src/cli/README.md
src/config.ts
src/core/conversation/l0-recorder.ts
src/core/hooks/auto-capture.ts
src/core/hooks/auto-recall.ts
src/core/index.ts
src/core/persona/persona-generator.ts
src/core/persona/persona-trigger.ts
src/core/profile/profile-sync.ts
src/core/prompts/l1-dedup.ts
src/core/prompts/l1-extraction.ts
src/core/prompts/persona-generation.ts
src/core/prompts/scene-extraction.ts
src/core/record/l1-dedup.ts
src/core/record/l1-extractor.ts
src/core/record/l1-reader.ts
src/core/record/l1-writer.ts
src/core/report/reporter.ts
src/core/scene/filename-normalizer.ts
src/core/scene/scene-extractor.ts
src/core/scene/scene-format.ts
src/core/scene/scene-index.ts
src/core/scene/scene-navigation.ts
src/core/seed/input.ts
src/core/seed/seed-runtime.ts
src/core/seed/types.ts
src/core/store/bm25-client.ts
src/core/store/bm25-local.ts
src/core/store/embedding.ts
src/core/store/factory.ts
src/core/store/search-utils.ts
src/core/store/sqlite.ts
src/core/store/tcvdb-client.ts
src/core/store/tcvdb.ts
src/core/store/types.ts
src/core/tdai-core.ts
src/core/tools/conversation-search.ts
src/core/tools/memory-search.ts
src/core/types.ts
src/gateway/config.ts
src/gateway/server.ts
src/gateway/types.ts
src/offload/auth-profile-key.test.ts
src/offload/auth-profile-key.ts
src/offload/backend-client.ts
src/offload/benchmark-token-estimate.ts
src/offload/context-token-tracker.ts
src/offload/fast-token-estimate.ts
src/offload/hooks/after-tool-call.ts
src/offload/hooks/before-agent-start.ts
src/offload/hooks/before-prompt-build.ts
src/offload/hooks/llm-input-l3.ts
src/offload/hooks/llm-output.ts
src/offload/index.ts
src/offload/l3-helpers.ts
src/offload/l3-token-counter.ts
src/offload/l3-token-helpers.ts
src/offload/local-llm/index.ts
src/offload/local-llm/llm-caller.ts
src/offload/local-llm/parsers/json-utils.ts
src/offload/local-llm/parsers/l1-parser.ts
src/offload/local-llm/parsers/l15-parser.ts
src/offload/local-llm/parsers/l2-parser.ts
src/offload/local-llm/prompts/l1-prompt.ts
src/offload/local-llm/prompts/l15-prompt.ts
src/offload/local-llm/prompts/l2-prompt.ts
src/offload/mmd-injector.ts
src/offload/mmd-meta.ts
src/offload/opik-tracer.ts
src/offload/pipelines/l2-mermaid.ts
src/offload/reclaimer.ts
src/offload/session-registry.ts
src/offload/state-manager.ts
src/offload/state-reporter.ts
src/offload/storage.ts
src/offload/time-utils.ts
src/offload/types.ts
src/offload/user-id.ts
src/utils/backup.ts
src/utils/checkpoint.ts
src/utils/clean-context-runner.ts
src/utils/ensure-hook-policy.ts
src/utils/env.ts
src/utils/managed-timer.ts
src/utils/manifest.ts
src/utils/memory-cleaner.ts
src/utils/no-think-fetch.test.ts
src/utils/no-think-fetch.ts
src/utils/openclaw-state-dir.ts
src/utils/pipeline-factory.ts
src/utils/pipeline-manager.ts
src/utils/sanitize.test.ts
src/utils/sanitize.ts
src/utils/serial-queue.ts
src/utils/session-filter.ts
src/utils/text-utils.ts
src/utils/time.test.ts
src/utils/time.ts
tsdown.config.ts
vitest.config.ts
vitest.e2e.config.ts
```
