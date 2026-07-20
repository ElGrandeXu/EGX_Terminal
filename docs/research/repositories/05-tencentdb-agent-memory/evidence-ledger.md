# Evidence ledger

## Convention

Niveaux : **A** = code/artefact directement inspecté; **B** = métadonnée Git,
npm ou doc officielle vérifiable; **C** = issue/PR ou validation rapportée mais
non reproduite; **D** = claim documentaire sans artefact suffisant. « Présence »
distingue `main@45e6e80`, tag/npm et proposition. La confiance porte sur la
lecture, pas sur la qualité du comportement.

## Snapshot, inventaire et delivery

<a id="E-SNAPSHOT"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| HEAD distant `main` = `45e6e80...` au 2026-07-20 | [commit](https://github.com/TencentCloud/TencentDB-Agent-Memory/commit/45e6e80ae2e63b65fad0d89f5e13171229c8f295), `git ls-remote` | main | B / élevée | hash résolu avant clone | snapshot verrouillé |
| Historique cloné complet hors workspace, aucun code exécuté | journal de méthode de cet audit; clone `%TEMP%/EGX_Terminal-audits/tencentdb-agent-memory-45e6e80` | audit | A / élevée | contrôle procédural, non claim upstream | permet audit statique uniquement |

<a id="E-INVENTORY"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| 173 fichiers, 164 textuels, 9 binaires; lignes et chemins exhaustifs | `git ls-files` au commit; [tree GitHub](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/45e6e80ae2e63b65fad0d89f5e13171229c8f295) | main | A / élevée | recomputable au SHA | base de couverture |
| 119 commits toutes refs, 103 sur main, 9 tags, 2 branches | `git rev-list --all`, GitHub branches/tags API | repo | B / élevée | `origin/HEAD` exclu du compte branches | `feat/server` séparée |
| 149 issues (51/98), 382 PR (260/40/82) | GitHub Issues/Pulls API paginée au 2026-07-20 | repo live | B / élevée | état temporel | les nombres changeront après la date |

<a id="E-VERSION"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| `main` déclare 0.3.6 malgré 56 fichiers changés après v0.3.6 | [`package.json`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/package.json), `git diff v0.3.6..45e6e80` | main | A / élevée | version ≠ contenu publié | ne pas identifier par version seule |
| dernière stable GitHub = v0.3.6; v1.0.1 chronologique est prerelease sur `feat/server` | [releases](https://github.com/TencentCloud/TencentDB-Agent-Memory/releases), [v1.0.1](https://github.com/TencentCloud/TencentDB-Agent-Memory/releases/tag/v1.0.1) | release | B / élevée | npm `latest` pointe néanmoins 1.0.1 | ligne de publication incohérente |
| aucune merge-base observée entre `main` et `feat/server` | refs clonées, `git merge-base` | repo | A / élevée | histories disjointes dans les refs accessibles | 1.x non assimilable à main |

<a id="E-NPM"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| npm 0.3.6 intégrité sha512 vérifiée, 146 entrées | [npm package](https://www.npmjs.com/package/@tencentdb-agent-memory/memory-tencentdb/v/0.3.6), archive statique `npm pack --ignore-scripts` | npm 0.3.6 | A+B / élevée | 122 fichiers exacts tag, README différent | paquet partiellement dérivé du tag |
| npm 1.0.1 intégrité vérifiée, contenu tag v1.0.1 | [npm 1.0.1](https://www.npmjs.com/package/@tencentdb-agent-memory/memory-tencentdb/v/1.0.1), [tag](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/v1.0.1) | npm/tag 1.0.1 | A+B / élevée | autre lignée que main | `npm latest` non représentatif de l'audit main |
| les deux archives contiennent un `.pyc` inattendu | manifests `npm pack --json` et tar statique | npm | A / élevée | non source suivie | hygiène packaging insuffisante |

<a id="E-POSTINSTALL"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| npm v0.3.6/v1.0.1 lance un patch shell OpenClaw en postinstall | [`package.json@v0.3.6`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/v0.3.6/package.json), [`package.json@v1.0.1`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/v1.0.1/package.json) | tag/npm | A / élevée | échec masqué par `|| true` | rejet supply-chain |
| main utilise `postinstall.mjs`, conditionnel mais patchant encore OpenClaw | [`scripts/postinstall.mjs`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/scripts/postinstall.mjs), [patch](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/scripts/openclaw-after-tool-call-messages.patch.sh) | main seulement | A / élevée | non publié aux archives inspectées | ne pas importer |

<a id="E-HISTORY"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| pivots 0.2.2/0.3.3/0.3.4 introduisent store, Hermes et offload | [historique](https://github.com/TencentCloud/TencentDB-Agent-Memory/commits/45e6e80ae2e63b65fad0d89f5e13171229c8f295/) et commits `a74b0b3`, `db8f3e5`, `d377b09` | main | B / élevée | commits massifs, granularité faible | architecture évolue vite |
| Unicode, curseur, embedding, filtre, Windows ont nécessité des correctifs | commits `bf58853`, `c6ed755`, `f61c5fd`, `38673b5`, `823b478`, `47341a9` | main | A+B / élevée | bugs antérieurs attestés | maturité par incidents |

## Mémoire longue durée

<a id="E-LONG"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| pipeline L0→L1→L2→L3 implémenté | [`pipeline-manager.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/pipeline-manager.ts), [`tdai-core.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/tdai-core.ts) | main/tag/npm selon époque | A / élevée | exécution non testée ici | boucle réelle, qualité inconnue |
| defaults capture/extraction/trigger/recall | [`config.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/config.ts) | main | A / élevée | manifest/docs parfois dérivent | valeurs de code prioritaires |

<a id="E-L0"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| L0 journalise user+assistant en JSONL journalier | [`l0-recorder.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/conversation/l0-recorder.ts), [`auto-capture.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/hooks/auto-capture.ts) | main | A / élevée | assistant code fenced retiré; pas octets exacts | archive inspectable mais filtrée |
| L0 garde les injections potentielles | [`sanitize.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/sanitize.ts), test `keeps L0...` | main | A / élevée | voulu comme archive brute | nécessite frontière d'autorité |

<a id="E-L1"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| L1 types persona/episodic/instruction + source IDs | [`l1-extraction.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/prompts/l1-extraction.ts), [`l1-extractor.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/record/l1-extractor.ts) | main | A / élevée | preference rabattue persona | taxonomie épistémique insuffisante |
| dédup LLM `store/update/merge/skip`, dual-write JSONL/DB | [`l1-dedup.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/record/l1-dedup.ts), [`l1-writer.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/record/l1-writer.ts) | main | A / élevée | issues #156/#157 rapportent dérive | transaction/reconciliation inconnue |

<a id="E-L2"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| L2 maintient Markdown, index reconstruisible, backups/rollback | [`scene-extractor.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/scene/scene-extractor.ts), [`scene-index.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/scene/scene-index.ts) | main | A / élevée | index rebuild ≠ scène rebuild | dérivé lisible, non déterministe |
| prompt autorise notes/inférences/contradictions | [`scene-extraction.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/prompts/scene-extraction.ts) | main | A / élevée | pas de schéma preuve par assertion | risque de surinterprétation |

<a id="E-L3"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| persona générée depuis scènes, trigger cold start/50 mémoires/demande | [`persona-trigger.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/persona/persona-trigger.ts), [`persona-generator.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/persona/persona-generator.ts) | main | A / élevée | aucune qualité testée | profil automatique à quarantaine |
| prompt demande traits/archetype sans provenance machine | [`persona-generation.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/prompts/persona-generation.ts) | main | A / élevée | phrase de prudence ≠ contrôle | hallucination L3 possible |

<a id="E-TRUTH"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| réponses assistant éligibles à L1 | `l0-recorder.ts` + `l1-extraction.ts` ci-dessus | main | A / élevée | aucune exclusion par rôle | assistant peut auto-valider une erreur |
| absence confidence/TTL/superseded/contradicted/sensitivity/scope workspace dans record L1 | [`types.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/types.ts), [`store/types.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/store/types.ts) | main | A / élevée | contradictions seulement prose L2 | métadonnées à ajouter avant expérimentation |

## Recall, stockage et offload

<a id="E-RECALL"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| stable persona/scènes/guide + L1 dynamique | [`auto-recall.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/hooks/auto-recall.ts), [`index.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/index.ts) | main | A / élevée | cache boundary contestée #120 | budget global absent |
| recherche keyword/embedding/hybrid RRF k=60 | `auto-recall.ts`, [`sqlite.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/store/sqlite.ts), [`tcvdb.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/store/tcvdb.ts) | main | A / élevée | aucun benchmark retrieval | hybrid réel, qualité inconnue |
| `sessionKey` non utilisé comme filtre L1 auto/tool | `auto-recall.ts`, [`memory-search.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/tools/memory-search.ts), [issue #111](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/111) | main | A+C / élevée | L0 conversation search sait filtrer | fuite inter-scope probable/rapportée |

<a id="E-BUDGET"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| `maxResults=5`, deux caps `0` donc off | [`config.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/config.ts), [PR #71](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/71) | main/npm 0.3.6 | A / élevée | #163 conteste anciens chemins; code main applique | jamais injecter avec defaults actuels en prod |
| caps couvrent L1, pas persona/navigation/guide | `auto-recall.ts` | main | A / élevée | aucune enveloppe totale | budget mission requis |

<a id="E-STORAGE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| SQLite local défaut, TCVDB optionnel | [`factory.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/store/factory.ts), `config.ts` | main | A / élevée | README marketing TencentDB | fournisseur non requis |
| retention L0/L1 et offload désactivée à 0, suppression irréversible | [`memory-cleaner.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/memory-cleaner.ts), [`storage.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/storage.ts) | main | A / élevée | changelog cite un test cleaner absent | preuve perdue après purge |

<a id="E-OFFLOAD"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| raw refs → L1 JSONL → L1.5 → L2 Mermaid → L3 mutation | [`offload/index.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/index.ts), [`after-tool-call.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/hooks/after-tool-call.ts), [`l2-mermaid.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/pipelines/l2-mermaid.ts) | main/npm selon version | A / élevée | pas d'E2E fonctionnel | mécanisme réel, résultat non prouvé |
| pas de resolver dédié sur main; drill-down via fichiers génériques | [`mmd-injector.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/mmd-injector.ts), inventaire outils | main | A / élevée | README dit « instantly retrieves » | découvrabilité non démontrée |
| parsers JSON tolérants et prompts stricts | [`json-utils.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/local-llm/parsers/json-utils.ts), [prompts](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/local-llm/prompts) | main | A / élevée | réparation syntaxique seulement | petits modèles à tester |

<a id="E-OFFLOAD-BUDGET"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| ratios mild/aggressive/emergency/MMD et encodage cl100k | [`offload/types.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/types.ts), [`context-token-tracker.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/context-token-tracker.ts) | main | A / élevée | commentaires historiques o200k | estimation provider-specific |
| stale token cache après mutation | [issue #233](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/233), [PR #411](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/411) | bug main/proposition | C + inspection code / élevée | PR ouverte | sur-suppression possible |

## Sécurité et confidentialité

<a id="E-SANITIZE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| filtre regex L1 anglais/chinois, 4 tests | [`sanitize.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/sanitize.ts), [`sanitize.test.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/sanitize.test.ts) | main | A / élevée | faux positifs/négatifs déduits de regex | défense non robuste |
| filtre absent du dist npm 0.3.6 | [issue #158](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/158), [fix #175](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/175) | npm 0.3.6 absent; main présent | C+A / élevée | audit n'a pas exécuté le bundle | paquet publié vulnérable selon source/code |

<a id="E-GATEWAY"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| loopback:8420, Bearer optionnel off, CORS strict par défaut | [`gateway/config.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/gateway/config.ts), [`gateway/server.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/gateway/server.ts) | main | A / élevée | README documente l'opt-in | auth doit devenir exigence hors loopback |
| body JSON sans limite/rate limit/TLS visible | `gateway/server.ts` lignes parseur/router | main | A / élevée | absence dans code inspecté | DoS/local exposure à traiter |

<a id="E-OPIK"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| Opik peut s'activer sans opt-in explicite si module charge | [`opik-tracer.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/offload/opik-tracer.ts), `package.json` optional dep | main | A / élevée | destination par défaut Opik non auditée | quarantaine |
| messages/prompts/réponses complets tracés sans troncature | même source, `serializeMessageForTrace`, `traceOffloadModelIo` | main | A / élevée | émission effective dépend client/config | risque PII/secrets élevé |

<a id="E-SECURITY"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| combinaison injection, scope, Gateway, telemetry insuffisante pour adoption | E-SANITIZE, E-RECALL, E-GATEWAY, E-OPIK, E-POSTINSTALL | transversal | inférence à partir de A / élevée | aucun pentest exécuté | rejet/quarantaine, pas doctrine |
| `offload.dataDir` relatif accepté | [issue #521](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/521), `config.ts` | main | C+A / élevée | test rapporté non lancé ici | validation path requise |

## Portabilité et modèles

<a id="E-PORT"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| `TdaiCore`/HostAdapter/Gateway sépare partiellement le long terme | [`adapters`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/adapters), `tdai-core.ts`, `gateway/server.ts` | main | A / élevée | formats/sessionKey encore host-shaped | service neutre plausible |
| offload dépend des hooks/messages/cache OpenClaw | `src/offload/`, `index.ts` | main | A / élevée | backend ne neutralise pas mutation | réimplémenter adaptateurs |

<a id="E-OPENCLAW"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| OpenClaw fournit hooks prompt/tool/message/session nécessaires | [docs officielles Plugin hooks](https://docs.openclaw.ai/plugins/hooks) | doc courante 2026-07-20 | B / élevée | interfaces évolutives | adaptateur réel mais épais |

<a id="E-HERMES"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| provider Hermes réel dans repo | [`hermes-plugin`](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/45e6e80ae2e63b65fad0d89f5e13171229c8f295/hermes-plugin/memory/memory_tencentdb) | main/npm | A / élevée | 21 tests centrés supervisor/recovery | long terme seulement |
| Hermes courant expose MemoryProvider complet | [source officielle au commit `31c08a9`](https://github.com/NousResearch/hermes-agent/blob/31c08a9aad6e83ded5d0e55dc7d41b94a99f08a1/agent/memory_provider.py) | Hermes main 2026-07-20 | A+B / élevée | signature `sync_turn` plus riche que l'adaptateur | compatibilité à tester |

<a id="E-CODEX"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| aucun adaptateur Codex fusionné; propositions #323/#340/#367 | [#323](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/323), [#340](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/340), [#367](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/367) | PR ouvertes | B / élevée | pas main/npm audité | ne pas créditer |
| Codex courant a session/prompt/tool/compact/stop hooks + MCP | [manuel officiel Codex](https://developers.openai.com/codex/codex-manual.md), source Hooks du manuel | doc courante | B / élevée | hooks locaux de confiance, limites/outils spécialisés | prototype adaptateur possible |

<a id="E-CLAUDE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| aucun adaptateur Claude fusionné; #7 fermé non fusionné | [PR #7](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/7), [#323](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/323) | PR seulement | B / élevée | pas main | ne pas créditer |
| Claude Code expose hooks session/prompt/tool/compact/end | [docs officielles](https://code.claude.com/docs/en/hooks) | doc courante | B / élevée | aucune implémentation testée ici | adaptateur mince plausible |

<a id="E-OPENCODE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| aucun adaptateur OpenCode fusionné; #490 ouvert | [PR #490](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/490) | PR | B / élevée | pas main | ne pas créditer |
| docs OpenCode : outils, tool before/after, events, compaction expérimentale | [docs officielles plugins](https://opencode.ai/docs/plugins/), [tools](https://opencode.ai/docs/tools/) | doc courante | B / moyenne-haute | pas de hook stable général d'injection trouvé sur page | auto-recall à expérimenter |

<a id="E-LOCAL"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| OpenAI-compatible, vLLM/SGLang/DashScope strategies et local embeddings présents | [`no-think-fetch.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/utils/no-think-fetch.ts), [`embedding.ts`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/src/core/store/embedding.ts), standalone runner | main | A / élevée | protocole ≠ qualité | Qwen transport plausible seulement |
| aucun test Qwen/petit modèle/VRAM/latence | inventaire tests et recherche `Qwen` | main | A / élevée | mentions docs/config seulement | expérience obligatoire |

## Cache, benchmarks et tests

<a id="E-CACHE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| #120 est une issue ouverte, pas une PR; chiffres cache auto-rapportés | [issue #120](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/120) | issue | C / moyenne | OpenClaw et plugin changent ensemble | signal, pas causalité démontrée |
| corrections #319/#411/#447/#533 non fusionnées | [#319](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/319), [#411](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/411), [#447](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/447), [#533](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/533) | PR ouvertes | B+C / élevée sur statut | validations de branches non reproduites | main reste affecté selon cas |

<a id="E-BENCH"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| quatre chiffres headline existent | [`README.md`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/README.md) | main/tag/npm docs | D / élevée sur existence | aucun runner/log/resultat ailleurs dans 173 fichiers | claim non reproductible |
| SWE-bench 50 tâches consécutives/session | même README | doc seulement | D / faible sur réalité | aucun ordre/session log | non confirmé |
| coûts auxiliaires/inclusions inconnus | absence d'artefacts + README | repo | D / élevée sur absence | ne peut être reconstitué | token-efficiency non démontrée |

<a id="E-BENCH-HISTORY"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| commit 3cc6d2a remplace WideSearch 8,5→12/174,31→63,46 par 33→50/221,31→85,64 et corrige unités | [commit exact](https://github.com/TencentCloud/TencentDB-Agent-Memory/commit/3cc6d2aa759455f928dea9fa7762a6c296c7a73d) | histoire main | A / élevée | aucune justification/artefact ajouté | correction non reproductible |

<a id="E-PR204"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| #204 est un guide ouvert, explicitement sans runner | [PR #204](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/204) | PR ouverte | C / élevée | pas main, pas lié aux headline artifacts | bonne checklist, aucune validation |

<a id="E-TESTS"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| 6 fichiers/88 cas nommés, couverture surtout utilitaires/Hermes recovery | [tests TS](https://github.com/TencentCloud/TencentDB-Agent-Memory/search?q=repo%3ATencentCloud%2FTencentDB-Agent-Memory+path%3Asrc+test&type=code), [tests Hermes](https://github.com/TencentCloud/TencentDB-Agent-Memory/tree/45e6e80ae2e63b65fad0d89f5e13171229c8f295/hermes-plugin/memory/memory_tencentdb/tests) | main | A / élevée | non exécutés par audit | pas preuve comportementale L0-L3/offload |
| changelog cite un E2E cleaner absent | [`CHANGELOG.md`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/CHANGELOG.md), inventaire | Unreleased claim | A / élevée | fichier non suivi au snapshot | doc décrit du non-livré |

## Issues et licence

<a id="E-ISSUES"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| bugs scope, curseur, dual-write, embedding, recovery et path rapportés | [#111](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/111), [#130](https://github.com/TencentCloud/TencentDB-Agent-Memory/pull/130), [#156](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/156), [#176](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/176), [#236](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/236), [#521](https://github.com/TencentCloud/TencentDB-Agent-Memory/issues/521) | main/issues | C, corroboré code / moyenne-haute | pas reproduits ici | evidence de maturité et limites |

<a id="E-LICENSE"></a>

| Claim | Source exacte | Présence | Preuve / confiance | Contradiction / reproductibilité | Implication / unknown |
| --- | --- | --- | --- | --- | --- |
| racine MIT, copyright Tencent 2026; package MIT | [`LICENSE`](https://github.com/TencentCloud/TencentDB-Agent-Memory/blob/45e6e80ae2e63b65fad0d89f5e13171229c8f295/LICENSE), `package.json` | main/tag/npm | A / élevée | aucun header contradictoire trouvé | code légalement réutilisable sous notice |
| deps critiques déclarent licences permissives | métadonnées npm versions du manifest au 2026-07-20 | registry | B / moyenne-haute | transitives non auditées; sqlite-vec repository metadata `TODO` | audit juridique complet restant |
| benchmark datasets/licences absents | inventaire/recherche exhaustive | main | A / élevée | noms README seulement | claims non reproduisibles/licences inconnues |

## Unknowns consolidés

- Résultat réel de tout benchmark, y compris variance, contamination et coûts
  auxiliaires.
- Sémantique de chaque abstraction avec un petit Qwen local et plusieurs
  langues.
- Taux E2E de drill-down exact après L3 et migration de harness.
- Atomicité crash entre refs/JSONL/SQLite/TCVDB/index/checkpoint.
- Effacement vérifiable dans backups, caches, Opik et services distants.
- Compatibilité de l'adaptateur Hermes avec le commit officiel courant.
- Capacité stable d'OpenCode à injecter automatiquement sans API expérimentale.
- Destination/rétention/redaction réelles d'Opik sans configuration explicite.
- Licences transitives complètes, provenance fine des assets et des prototypes
  de prompts mentionnés.

Ces unknowns sont des résultats de l'audit, pas une invitation à combler les
trous par supposition.
