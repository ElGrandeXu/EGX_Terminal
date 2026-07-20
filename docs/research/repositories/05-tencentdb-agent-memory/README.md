# Audit indépendant — TencentDB Agent Memory

> État au 2026-07-20. Audit statique de recherche, sans installation, exécution,
> benchmark, appel LLM, migration ni adoption. Les références `E-*` renvoient à
> l'[evidence ledger](evidence-ledger.md).

## Identité et snapshots

| Élément | Valeur observée | Statut |
| --- | --- | --- |
| Repository | `TencentCloud/TencentDB-Agent-Memory` | source externe non fiable |
| `main` audité | `45e6e80ae2e63b65fad0d89f5e13171229c8f295` | snapshot de l'audit |
| Version de `package.json` sur `main` | `0.3.6` | non alignée sur les publications 1.x |
| Dernière release stable GitHub | `v0.3.6`, commit `438869bec84711fb09b12185d46702d98eeaf90e`, 2026-05-28 | ancêtre de `main` |
| Dernier tag/release chronologique | `v1.0.1`, commit `505877cc5160d3ea5cdb5bbd72902db03c97dd10`, 2026-07-14, marquée prerelease | branche sans ancêtre commun avec `main` dans les refs publiées |
| Branche de la release 1.x | `feat/server` à `c81c70b68c516ba79eba6dd9a706f0302401fa12` | lignée distincte, non auditée comme `main` |
| npm `latest` | `@tencentdb-agent-memory/memory-tencentdb@1.0.1` | contenu de `v1.0.1`, pas de `main` |
| npm demandé pour comparaison | `0.3.6` | archive inspectée statiquement, intégrité vérifiée |

Le nom de version `0.3.6` ne suffit donc pas à identifier un contenu : le tag
`v0.3.6`, npm `0.3.6` et `main` divergent. `main` contient 56 fichiers modifiés
depuis le tag, mais conserve la même version déclarée. Les releases 1.x et npm
`latest` proviennent d'une autre histoire Git. [E-VERSION]

## Portée

Le repository a été traité comme sept objets séparés : mémoire longue durée,
context offload, stockage/recherche, extraction LLM, adaptateurs OpenClaw et
Hermes, skill/installateurs, option TencentDB/TCVDB, puis claims et benchmarks.
L'audit n'a ni lu ni comparé les audits 01–04 et ne constitue pas une synthèse
inter-repository.

Documents détaillés :

- [Cartographie, inventaire et delivery](repository-map.md)
- [Comportement, sécurité, portabilité et protocole expérimental](behavior-and-delivery.md)
- [Économie de tokens et benchmarks](token-economics.md)
- [Registre des preuves, contradictions et unknowns](evidence-ledger.md)

## Résumé exécutif

Le code démontre deux architectures différentes.

La mémoire longue durée conserve une couche conversationnelle L0 en JSONL,
produit des atomes L1 en JSONL et SQLite/TCVDB, demande ensuite à un LLM de
maintenir des scènes Markdown L2, puis une persona Markdown L3. Avant un tour,
elle injecte persona, navigation de scènes, guide d'outils et résultats L1. Le
principe « couches basses = preuves, couches hautes = structure » existe donc
réellement, mais n'est que partiellement réversible : L2/L3 sont lisibles et
reproductibles en principe, pas déterministiquement ; les liens L1→L0 sont des
identifiants de messages, tandis que L2/L3 ne maintiennent pas une provenance
exhaustive et machine-vérifiable. [E-LONG] [E-TRUTH]

Le context offload archive d'abord chaque résultat d'outil dans `refs/*.md`,
écrit un résumé L1 en JSONL, construit une carte Mermaid L2 avec des `node_id`,
puis remplace ou supprime des messages selon un tracker de tokens et réinjecte
des cartes MMD. Les octets bruts peuvent être conservés jusqu'au nettoyage ; il
n'existe toutefois sur `main` aucun outil de résolution dédié qui garantisse le
drill-down. Le modèle doit découvrir qu'un détail manque, retrouver le bon
`node_id`, ouvrir le JSONL, suivre `result_ref`, puis lire le fichier brut.
« Lossless » décrit donc principalement la conservation et l'adressabilité des
octets, pas une récupération comportementale prouvée. [E-OFFLOAD]

Les budgets de recall existent et sont appliqués, mais leurs deux garde-fous en
caractères valent `0` par défaut, donc sont désactivés. La persona, la navigation
et le guide d'outils ne sont pas inclus dans ce budget L1. Les chiffres de gains
de tokens du README excluent toute méthodologie reproductible présente dans le
repository ; aucun runner, log brut, résultat par tâche, seed, variance ou coût
des modèles auxiliaires n'est fourni. Ils restent des **claims numériques non
reproductibles depuis le repository**. [E-BUDGET] [E-BENCH]

La frontière de confiance est insuffisante pour une adoption. L0 capture les
réponses de l'assistant comme les messages utilisateur ; L1 peut transformer les
deux en mémoire durable. Le filtre d'injection est une liste de regex, absente du
paquet npm 0.3.6 publié, et n'a que quatre tests directs. Les résultats rappelés
ne sont pas systématiquement échappés. Le Gateway est loopback par défaut mais
sans authentification par défaut, sans TLS ni limite de corps visible. La
recherche L1 ne filtre pas par session. Enfin, Opik peut charger sans opt-in
explicite et sérialise prompts, réponses et messages complets. [E-SECURITY]

## Mécanisme réel : mémoire longue durée

1. `agent_end`/`capture` écrit les messages utilisateur **et assistant** en L0
   journalier append-only et les indexe éventuellement ; l'assistant perd ses
   blocs de code fenced, mais L0 garde volontairement les textes ressemblant à
   une injection.
2. Après 1→2→4→5 conversations au warm-up, puis toutes les 5 conversations, ou
   après 600 s d'inactivité, un LLM extrait au plus 20 L1 par session et un
   second passage LLM décide `store/update/merge/skip`.
3. L2 lit les L1 incrémentaux par curseur et demande au LLM de créer/mettre à
   jour/supprimer jusqu'à 15 scènes Markdown ; sauvegarde et rollback protègent
   les fichiers, non leur exactitude sémantique.
4. Après L2, L3 est évaluée : cold start, demande explicite ou 50 nouvelles
   mémoires depuis la persona précédente ; un LLM réécrit `persona.md`.
5. Avant le prompt, le système cherche jusqu'à 5 L1 par keyword, embedding ou
   hybrid/RRF, puis injecte les L1 dynamiques et le bloc stable L2/L3 ; deux
   outils de recherche explicite sont aussi exposés.

## Mécanisme réel : context offload

1. Le hook d'outil écrit le résultat brut dans `refs/*.md` avant de demander un
   résumé ; le texte envoyé au modèle L1 est tronqué, le fichier brut ne l'est
   pas à ce stade.
2. L1 écrit un JSONL `{tool_call, summary, result_ref, tool_call_id, score,
   node_id}` ; trois essais sont suivis d'un résumé fallback.
3. L1.5 examine le contexte récent et les cartes pour décider d'une frontière
   de tâche ; L2 produit/actualise Mermaid et mappe chaque `tool_call_id` vers un
   `node_id`.
4. L3 applique des seuils de contexte : remplacement doux, suppression
   agressive, puis urgence, et injecte les MMD sous un budget par ratio.
5. La récupération suit `node_id → JSONL → result_ref → refs/*.md`; elle dépend
   d'outils de fichiers du host et n'est ni atomique ni prouvée E2E.

## Conclusion principale sur la progressive disclosure

L'hypothèse

`preuve brute externe → index compact → abstraction progressive → rappel budgété → preuve`

est **partiellement démontrée** :

- oui pour l'externalisation locale, les artefacts lisibles, les identifiants et
  une navigation compacte ;
- oui, sous configuration explicite, pour un budget L1 et pour le budget MMD ;
- non pour une provenance exhaustive de chaque abstraction L2/L3 ;
- non pour la reconstruction déterministe après rétention ou suppression ;
- non pour la découvrabilité et le comportement effectif de drill-down ;
- non pour une réduction nette de tokens tous modèles et toute session compris.

L'invariant le plus solide n'est pas Mermaid ni la persona : c'est la séparation
entre une preuve brute inspectable et des dérivés remplaçables, avec résolution
explicite d'une référence. Pour être sûr et portable, cet invariant exige des
métadonnées et contrôles que l'implémentation actuelle ne fournit pas encore.

## Candidats conceptuels, sans adoption

- Externaliser les preuves volumineuses hors contexte tout en les gardant
  locales, inspectables et adressables.
- Séparer journal brut append-only, index compact et abstractions dérivées.
- Exiger une référence résoluble pour tout résumé et conserver les dérivés
  reconstruisibles.
- Budgéter **chaque** injection par mission : L1, persona, navigation et guide.
- Rendre capture, consolidation, rappel, correction, oubli et export explicites
  et auditables.
- Porter le cœur dans un service neutre ; limiter les adaptateurs aux événements
  et formats propres au harness.
- Ajouter à chaque mémoire `scope`, provenance, timestamp, confiance, TTL,
  version, statut `active/superseded/contradicted`, producteur et preuve.
- Traiter toute mémoire rappelée comme données non fiables, jamais comme
  instruction d'autorité.

## Rejets et quarantaines

- **Rejet** : postinstall qui patche OpenClaw, scripts installant/modifiant le
  harness, ou dépendance à une cache boundary privée.
- **Quarantaine sécurité** : auto-capture et auto-recall invisibles, regex comme
  défense principale, recherche sans isolation, Gateway sans auth explicite,
  télémétrie de contenu intégral, profilage automatique toujours actif.
- **Rejet** : abstraction LLM traitée comme vérité, persona non budgétée,
  nettoyage qui détruit la dernière preuve, Mermaid imposé comme format
  universel.
- **Dépendance fournisseur inutile** : TCVDB n'est pas requis pour l'invariant ;
  SQLite/Markdown/JSONL démontrent déjà un chemin local. L'API
  OpenAI-compatible ne démontre ni neutralité LLM ni qualité locale.

## Unknowns décisifs

- Exactitude, variance et coût total des quatre benchmarks annoncés.
- Taux de récupération réussie d'un détail rare après compression.
- Fidélité L1/L2/L3 avec petits Qwen locaux, notamment multilingues.
- Robustesse aux écritures partielles, collisions de refs et crashs entre
  JSONL, SQLite/TCVDB et index.
- Politique exacte de réseau/rétention d'Opik quand il est chargé sans
  configuration explicite.
- Isolation multi-utilisateur et multi-workspace dans un déploiement réel.
- Compatibilité durable de l'adaptateur Hermes avec l'interface Hermes courante.
- Sémantique d'injection automatique réalisable dans OpenCode sans s'appuyer sur
  une API expérimentale ou non documentée.

Ces unknowns interdisent de conclure à une architecture prête à adopter. Ils
définissent seulement les expériences futures décrites dans
[behavior-and-delivery.md](behavior-and-delivery.md#protocole-expérimental-futur).
