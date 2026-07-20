# Comportement, confiance et projection neutre

## L0 → L3 : cartographie complète

Les quatre niveaux du README correspondent à des composants présents, mais le
mot « preuve » devient de moins en moins exact à mesure que l'on monte. Les
artefacts sont locaux par défaut; leur sémantique est produite par LLM dès L1.
[E-LONG]

| Propriété | L0 Conversation | L1 Atom | L2 Scenario/Scene | L3 Persona |
| --- | --- | --- | --- | --- |
| Entrée | messages du tour, utilisateur et assistant | L0 d'une `sessionKey` après curseur | L1 incrémentaux d'une session | scènes de toutes les sessions |
| Sortie | une ligne/message | mémoire typée | un ou plusieurs blocs scène | profil synthétique global |
| Format local | `conversations/YYYY-MM-DD.jsonl` | `records/YYYY-MM-DD.jsonl` + lignes DB | `scene_blocks/*.md` + index JSON | `persona.md` |
| Stockage primaire | JSONL + L0 SQLite/TCVDB | SQLite/TCVDB pour recherche, JSONL pour journal/recovery | Markdown | Markdown; profil optionnel en DB |
| Producteur | code déterministe après filtre | LLM extraction, puis LLM dédup | LLM avec outils de fichiers | LLM avec outil de fichier |
| Trigger par défaut | fin de tour/capture | warm-up 1→2→4→5, puis 5 conversations, ou idle 600 s | 10 s après L1, plancher 900 s, rappel 3 600 s si session active | après L2 : cold start, demande, ou 50 mémoires nouvelles |
| Filtre | sanitization, bruit; code fenced assistant supprimé | regex injection + règles de prompt | prompt et limite de scènes | prompt seulement + échappement de quelques tags après génération |
| Dédup/conflit | curseur temporel, pas sémantique | actions `store/update/merge/skip` | le LLM modifie/fusionne/supprime des fichiers | le LLM réécrit le profil |
| Temporalité | `recordedAt`, timestamp message | `createdAt`, `updatedAt`, `timestamps` | timestamps narratifs/metadata Markdown | état courant narratif |
| Provenance | rôle, id, sessionKey/id, timestamps | `source_message_ids`, sessionKey/id | pas de mapping exhaustif imposé vers les L1/L0 | pas de mapping exhaustif vers scènes/L0 |
| Backup/rollback | append-only avant retention | append-only + DB, reconciliation partielle | jusqu'à 10 backups, rollback sur erreur | jusqu'à 3 backups |
| Recall/injection | outil de recherche conversationnelle | auto-recall + outil mémoire | navigation injectée, lecture à la demande | injectée avant prompt |
| Inspection humaine | directe | JSONL/SQLite lisibles avec outil fourni | directe Markdown | directe Markdown |
| Correction sûre | aucune API dédiée | pas d'API `correct`; édition manuelle risque de diverger de la DB | édition de fichier possible mais future réécriture LLM | édition possible mais future régénération |
| Suppression sûre | retention par shard/DB | cleaner ou mécanismes internes, pas de `forget(memory)` public | LLM/manuel + index | manuel/régénération |
| Reconstruction | source elle-même | possible depuis L0 seulement en rappelant le LLM, non déterministe | index reconstruisible; scène non déterministe depuis L1 | non déterministe depuis scènes |

### L0 : capture et frontière de vérité

`recordConversation()` extrait les messages, remplace si possible le texte
injecté par le texte utilisateur original, nettoie les caractères/feedback
loops, retire les blocs fenced des réponses assistant et applique
`shouldCaptureL0`. Le filtre L0 est volontairement permissif : un texte qui
ressemble à une prompt injection reste dans l'archive brute. Cette décision est
cohérente pour une preuve, mais rend obligatoire une séparation forte entre
archive et instruction; cette séparation n'est pas complète plus haut.

Le journal est append-only, mais « immuable » serait excessif : retention et
cleaner peuvent réécrire ou supprimer des shards. L'index L0 SQLite peut être
écrit sans embedding puis complété en arrière-plan; l'issue #236 rapporte une
dégradation silencieuse quand le batch d'un service distant dépasse sa limite.
[E-L0]

### L1 : extraction, déduplication et dual-write

Le prompt L1 lit aussi bien les paroles utilisateur que les réponses assistant.
Il produit `content`, `type ∈ {persona, episodic, instruction}`, `priority`,
`scene_name` et `source_message_ids`; `preference` est rabattue sur `persona`.
Il n'existe aucun type séparé pour hypothèse, décision, citation, événement
temporaire, secret ou sortie d'outil. Le second appel LLM rapproche les
candidats et décide `store/update/merge/skip`.

Pour update/merge, les anciens identifiants peuvent être supprimés de la DB,
mais l'historique JSONL demeure jusqu'au nettoyage et un nouveau record est
ajouté. JSONL et DB sont deux écritures distinctes. Les incidents #156/#157 et
le correctif de curseur #130 montrent que la cohérence et l'avancement ont déjà
échoué en pratique. [E-L1]

### L2 : scènes

Le runner confine les opérations LLM au répertoire `scene_blocks/`, construit
un contexte de capacité (15 scènes par défaut), sauvegarde les fichiers, lance
le modèle avec outils, puis restaure en cas d'échec. L'index
`.metadata/scene_index.json` est reconstructible en rescannant le Markdown. Les
scènes, elles, ne le sont que par une nouvelle inférence; aucune procédure ne
garantit le même contenu.

Le prompt demande de distinguer faits explicites, notes anthropologiques,
évolution et contradictions, mais autorise des inférences implicites. Une règle
de prompt n'est pas un schéma de provenance. Le signal de mise à jour persona
est lui-même extrait de la sortie LLM. [E-L2]

### L3 : persona

La persona est une synthèse globale et non un ensemble de faits versionnés. Le
prompt recherche traits, archetype, préférences, valeurs et contradictions. Il
peut donc surinterpréter, essentialiser et fusionner des contextes personnels et
professionnels. La taille de 2 000 caractères apparaît comme instruction de
prompt plutôt que comme budget d'injection robuste. L'échappement postérieur ne
neutralise que certaines balises XML connues.

Le système peut régénérer après perte du corps de `persona.md` et garde des
backups, mais n'offre ni `correct(persona_fact)` ni état `superseded`. Une erreur
L3 peut être réinjectée à chaque tour jusqu'à correction manuelle ou nouvelle
génération. [E-L3]

## Context offload réel

### Artefacts et étapes

| Niveau du code | Artefact/effet | Entrée envoyée au modèle | Garantie réelle |
| --- | --- | --- | --- |
| brut | `refs/*.md` | aucune pour l'écriture | conservation locale du résultat nettoyé |
| L1 | `offload-<session>.jsonl` | params ≤500 caractères, résultat ≤2 000, contexte récent | résumé ≤200 caractères, score 0–10, `result_ref` |
| L1.5 | frontière `short/long`, cible MMD | messages récents, MMD active, metadata historiques | décision JSON tolérante, fail-safe |
| L2 | `mmds/*.mmd`, `node_mapping` | JSONL nouveau + carte courante | cible ~4 000 caractères, mapping demandé |
| L3 | vue de messages mutée | aucune inférence dédiée | remplacement/suppression selon tokens et scores |
| L4 | `skills/<name>/SKILL.md`, backend seulement | demande explicite `/create-skill` | artefact généré, pas mémoire brute |

Le modèle L1 a trois tentatives; un fallback local écrit un résumé si les trois
échouent. Les parseurs acceptent fences, préfixes et virgules finales. L1.5 et
L2 reposent toujours sur un JSON valide/réparable; L2 passe temporairement
`node_id` à `wait`, ce qui crée une fenêtre d'état partiel. [E-OFFLOAD]

### Hooks, modes et limites

- `local` utilise le provider/modèle résolu par OpenClaw via une interface
  OpenAI-compatible.
- `backend` appelle un service distant pour les consolidations.
- `collect` exécute L1/L1.5/L2 pour collecter les artefacts mais désactive la
  mutation L3/context engine.
- L'offload est désactivé par défaut; fenêtre par défaut 200 000 tokens,
  déclenchement forcé après 4 paires, maximum 20 paires par lot.
- Mild : 0,50, scan 0,70, top score 0,40, exigence tâche courante 0,80.
- Aggressive : 0,85, suppression cible 0,40; emergency : 0,95 vers 0,60.
- Les MMD peuvent occuper 0,20 de la fenêtre. L'overhead système estimé vaut
  0,12 dans les defaults internes.

L'encodage code par défaut est `cl100k_base`, alors que certains commentaires
de types historiques mentionnent `o200k_base`. Même `cl100k_base` ne garantit
pas la précision pour Qwen/DeepSeek/GLM/MiniMax. Les issues #233 et PR #411
montrent qu'une mutation sans invalidation du WeakMap peut surestimer de 519
tokens dans le cas rapporté et provoquer une suppression excessive. [E-OFFLOAD-BUDGET]

### « Lossless recovery » décomposé

| Dimension | Verdict |
| --- | --- |
| Conservation des octets | oui tant que le ref existe; texte nettoyé, pas bit-identique au flux original |
| Accessibilité | oui par fichiers locaux et `result_ref` |
| Découvrabilité | partielle : MMD/JSONL donnent des pistes, sans resolver dédié sur `main` |
| Fidélité sémantique | non garantie : L1/L2 sont des abstractions LLM sur previews |
| Comportement agent | non démontré : aucun E2E de drill-down, détail rare ou raisonnement reconstruit |
| Réversibilité après retention | non : supprimer le ref détruit la dernière preuve |

La chaîne est donc « recoverable by a capable, correctly prompted agent under
retention », pas lossless au sens comportemental.

## Stockage et progressive disclosure

| Support | Données | Local par défaut | Lisible sans runtime | Vectorisé | Export/rebuild |
| --- | --- | --- | --- | --- | --- |
| Markdown | scènes, persona, refs outil, MMD, skill L4 | oui | oui | refs/MMD non; profils selon sync | copie/export simple; dérivés LLM non déterministes |
| JSONL | L0, L1, offload, état/metadata partiels | oui | oui | L0/L1 parallèlement | append/relecture; DB partiellement reconstruisible |
| SQLite | metadata, FTS5, vec0 L0/L1, profils | oui | oui avec outil SQLite | oui si embeddings | export/read scripts, schéma interne |
| TCVDB | L0/L1/profils, dense/sparse/hybrid | non, option cloud | non sans service/API | oui, server-side possible | scripts migration/export présents |
| Opik | traces décisions/messages/prompts | dépend de son client/config | non localement garanti | non pertinent | politique hors repository |

Le principe « lower layers preserve evidence, upper layers preserve structure »
est solide pour refs/JSONL/MMD. Il est plus faible pour L0/L1/L2/L3 : L1 n'est
déjà plus brut, les scènes et persona n'ont pas de liens exhaustifs, et le
cleaner peut rompre la remontée. Les failure modes observés ou directement
inférés sont : index orphelin, JSONL/DB divergents, `wait` persistant, curseur
figé, ref supprimé, scène contredisant L1, persona obsolète et recomputation
impossible après retention. [E-STORAGE]

## Mémoire, profil et vérité

### Qui décide ?

Le code décide qu'un message est capturable; le LLM L1 décide qu'il mérite une
mémoire durable; un second LLM décide les conflits; L2/L3 réinterprètent encore.
Les réponses assistant sont capturées et peuvent devenir des « faits ». Aucun
champ ne distingue :

- préférence, fait et hypothèse au-delà de trois types larges;
- instruction d'utilisateur et texte cité;
- décision stable et événement temporaire;
- secret, donnée personnelle et sortie d'outil;
- confiance, TTL, scope workspace ou sensibilité.

Une L1 possède IDs source et timestamps, mais pas confiance, durée de vie,
version sémantique, `superseded` ou `contradicted`. L2 peut raconter une
trajectoire et des contradictions en prose; ce n'est pas exploitable comme
contrôle. L3 peut écraser les nuances de L0 parce que le rappel automatique
montre d'abord la synthèse et ne fournit pas pour chaque assertion un pointeur
vers les messages. [E-TRUTH]

### Risques de profilage

- surinterprétation et essentialisation encouragées par les notions d'archetype
  et de traits;
- faits dépassés persistants, préférences changées seulement corrigées par une
  future synthèse non déterministe;
- fusion globale de scènes multi-session et de domaines de vie;
- réinjection persistante d'une hallucination;
- absence de scope workspace/user dans le recall L1;
- possibilité que l'assistant se cite lui-même comme source de vérité.

## Recall, injection et correction

Le recall automatique sépare deux sorties :

- stable : `<user-persona>`, `<scene-navigation>`, `<memory-tools-guide>`;
- dynamique : `<relevant-memories>` issu de keyword, embedding ou hybrid.

SQLite utilise FTS5 BM25 et recherche vectorielle puis RRF client avec `k=60`;
TCVDB peut faire le hybrid server-side. En absence d'embeddings, le code retombe
sur keyword. `maxResults=5`, seuil 0,3 et timeout 5 s sont actifs; les caps de
caractères sont désactivés à `0`. Le guide demande au modèle de limiter ses
recherches à trois par tour, mais le code marque cette limite comme TODO.

Le paramètre `sessionKey` reçu par le hook n'est pas transmis comme filtre à
`searchMemories`; les outils mémoire recherchent aussi globalement. C'est une
faille de scope, pas seulement un défaut d'interface. La suppression des blocs
injectés lors de la persistance et la stabilisation avant cache boundary sont
proposées par #319/#533, mais pas fusionnées. [E-RECALL]

## Sécurité et confidentialité

### Filtre d'injection

`looksLikePromptInjection` est un filtre regex anglais/chinois : demandes
d'ignorer/écraser les instructions, changement de rôle, interrogation du system
prompt, tags mémoire connus, et verbes `run/execute/call/invoke` proches de
tool/command/function/shell. Il protège l'entrée L1 sur `main`, pas L0. Npm
0.3.6 l'a tree-shaké car l'appel était commenté; l'issue #158 le documente et le
commit #175 le réactive après publication.

Faux positifs attendus dans un workspace sécurité/documentation :

- « ignore previous instructions » cité dans un test;
- « run this command » dans un guide;
- « system prompt » dans une documentation;
- « execute tool » dans une spécification.

Faux négatifs attendus : homoglyphes, caractères zero-width, encodage, mots
séparés, paraphrases, indirect prompt injection, langues non couvertes et tags
inventés. Les quatre tests couvrent deux payloads usuels, le refus L1, la
permissivité L0 et un texte bénin; aucune campagne adversariale/multilingue.
[E-SANITIZE]

### Délimitation et autorité

`escapeXmlTags` remplace certaines balises dans la persona. Les lignes L1
rappelées et les textes de navigation ne sont pas tous échappés de la même
façon. Même correctement échappée, une balise XML ne sépare pas les autorités
pour un LLM : le contenu reste dans le prompt système ou le contexte utilisateur
et peut influencer le modèle. Toute mémoire doit donc être étiquetée comme
contenu non fiable et son effet borné par politique/outils.

### Gateway

- écoute `127.0.0.1:8420` par défaut;
- auth Bearer optionnelle, désactivée par défaut; comparaison constant-time;
- avertissement si auth absente et plus fort avertissement hors loopback;
- CORS sans headers par défaut, allowlist ou `*` explicite;
- `/health` reste public;
- pas de TLS, rate limit ni limite de taille du body visible;
- le parseur accumule tous les chunks en mémoire avant `JSON.parse`;
- `/search/memories` n'accepte/passe aucun scope, `/seed` peut lancer un travail
  bloquant et coûteux.

Loopback réduit l'exposition réseau, pas les autres processus locaux. Une config
Docker `-p 8420:8420` ou `0.0.0.0` sans clé expose capture/recherche/seed.
[E-GATEWAY]

### Secrets, télémétrie et sorties distantes

Les clés LLM, embeddings, TCVDB et Gateway sont en config/env. Le script de
contrôle masque les champs connus lors de l'affichage, mais L0 et refs peuvent
capturer des secrets présents dans la conversation ou les outils. Un LLM ou
embedding distant reçoit ensuite les données sélectionnées.

Le tracer Opik est particulièrement sensible : si le module se charge, son
calcul `enabled` ne requiert pas une entrée explicitement activée. Il sérialise
les messages complets sans troncature et trace system prompt, user prompt,
réponse et sessionKey. La destination et la retention dépendent d'Opik et de la
configuration hors repository. Quarantaine requise tant qu'un opt-in explicite,
une redaction et une politique de destination ne sont pas démontrés. [E-OPIK]

### Fichiers, cleaner et supply chain

Les noms de session/agent sont nettoyés pour certains chemins, mais l'issue #521
montre que `offload.dataDir` relatif ou vide est accepté. Les refs et JSONL sont
regroupés par agent, donc plusieurs sessions du même agent partagent MMD/state;
aucun scope workspace portable n'est imposé.

La recherche FTS SQLite utilise des statements préparés. `buildFtsQuery`
segmente la requête (mots alphanumériques ou tokens Jieba), cite chaque terme,
puis les relie par `OR`; le texte utilisateur n'est donc pas interpolé comme du
SQL ou de la syntaxe FTS libre. C'est une défense utile contre l'injection de
requête, mais sans effet sur l'empoisonnement sémantique, la fuite de scope ou
la pertinence des résultats. Les `node_id` sont résolus par lookup dans le JSONL
plutôt que transformés directement en chemin; la dernière étape ouvre toutefois
le `result_ref` persisté, dont la sûreté dépend de l'intégrité de cet index.
[E-SECURITY]

Le cleaner L0/L1 est opt-in (`0` = conservation), refuse les TTL 1–2 jours sauf
override, applique des garde-fous minimum et écrit un audit. L'offload cleaner
est aussi opt-in, minimum 3 jours. Une fois les refs supprimés, le chemin de
preuve n'est plus réversible.

Le lifecycle npm qui patche un autre logiciel, les installateurs Hermes, scripts
root/shell et images Docker élargissent fortement la supply chain. Ils sont
hors du core et doivent être rejetés pour un workspace neutre. [E-POSTINSTALL]

### Synthèse des risques

| Risque | État |
| --- | --- |
| poisoning persistant / injection différée | élevé, filtre faible et L0 permissif |
| capture secrets/PII/code privé | élevé, pas de classifieur/redaction général |
| fuite inter-scope | confirmé par chemin de code + issues #62/#111 |
| suppression destructive | opt-in mais irréversible pour les preuves |
| Gateway réseau | loopback sûr par défaut, auth opt-in insuffisante |
| supply chain/postinstall | inacceptable pour adoption neutre |
| provenance abstractions | insuffisante à L2/L3 |
| exfiltration LLM/embedding/Opik | dépend de config; Opik requiert quarantaine |

## Portabilité par harness

### OpenClaw

Adaptateur réel sur `main` : **oui**. Les docs officielles courantes exposent
`before_prompt_build`, `after_tool_call`, `llm_input/output`, `agent_end`,
mutation de prompts, contexte et messages. Le repository utilise précisément
ce genre de surface. L'épaisseur est néanmoins grande pour offload : plugin,
context engine, hooks, outils, format de messages et patch historique.
[E-OPENCLAW]

### Hermes

Adaptateur réel sur `main` : **oui**, en Python via Gateway. L'interface
officielle courante `MemoryProvider` expose `prefetch` avant chaque appel,
`sync_turn` après chaque tour, outils, compression et scope. Le long terme peut
donc être adapté finement. L'offload OpenClaw n'est pas porté; Hermes ne reçoit
que le service long terme. Épaisseur minimale future : un provider qui traduit
scope/query/turn et laisse stockage/consolidation au service. [E-HERMES]

### Codex

Adaptateur réel sur `main` : **non**; #323/#340/#367 sont ouverts. La doc Codex
courante expose `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
`PreCompact`, `PostCompact` et `Stop`, ainsi que MCP. Les hooks peuvent ajouter
du contexte; leur sortie model-visible est bornée à environ 2 500 tokens et les
gros outputs sont externalisés. Ces événements suffisent pour **prototyper**
capture, recall explicite/automatique et offload de résultats locaux, mais pas
pour reprendre sans adaptation la mutation interne OpenClaw ni son cache
boundary. Un service MCP permet dès maintenant mémoire explicite; l'injection
automatique exige des hooks de confiance installés et un protocole propre.
[E-CODEX]

### Claude Code

Adaptateur réel sur `main` : **non**; #7 est fermé non fusionné et #323 ouvert.
La doc officielle expose session, prompt utilisateur, pre/post tool,
pre/post-compact et session end, avec hooks command/HTTP/MCP/prompt/agent. Les
événements requis existent donc pour un adaptateur mince de capture/recall et
offload, sans modifier Claude Code. Une mémoire explicite par outils MCP est la
surface la moins invasive; l'auto-injection doit rester visible, budgétée et
réversible. [E-CLAUDE]

### OpenCode

Adaptateur réel sur `main` : **non**; #490 et #323 sont ouverts. Les docs
officielles exposent plugins TS/JS, outils custom, événements de messages,
sessions et `tool.execute.before/after`, plus un hook expérimental de
compaction. Elles ne documentent pas sur la page consultée un équivalent stable
et général de `before_prompt_build` pour injecter le recall à chaque appel.
Capture/outils explicites sont plausibles; auto-recall transparent reste une
expérience et ne doit pas être affirmé comme capacité acquise. [E-OPENCODE]

### Service neutre et épaisseur minimale

Ce qui devrait vivre dans le service : journal/scopes, validation, stockage,
consolidation, retrieval, budgets, provenance, correction/oubli/export,
résolution de preuve et journal d'audit. Ce qui doit rester dans l'adaptateur :
conversion d'événements, rôles/outils, obtention du budget courant, injection
visible et capture de fin de tour.

Une API OpenAI-compatible n'est qu'une compatibilité protocolaire. Elle ne
garantit ni tool use, ni JSON fiable, ni qualité de synthèse, ni neutralité des
prompts et du stockage.

## Modèles locaux et Qwen

### Chemins réellement présents

- modèle du harness : runner OpenClaw pour L1/L2/L3 et offload local;
- OpenAI-compatible local : Gateway/standalone et offload `local` via AI SDK;
- vLLM/SGLang/DashScope/Qwen : mêmes endpoints, avec stratégies
  `disableThinking` injectant des paramètres provider-specific;
- node-llama-cpp : peer optionnelle principalement pour embeddings locaux;
- embeddings OpenAI-compatible, ZeroEntropy, local node-llama-cpp ou server-side
  TCVDB;
- keyword FTS5 sans embedding, y compris recall explicite/auto.

### Ce qui n'est pas démontré

Les prompts L1/L1.5/L2 demandent du JSON strict, parfois chinois; scène/persona
demandent au modèle d'utiliser des outils de fichiers. Les parseurs tolérants et
retries réparent la syntaxe, pas la vérité. `disableThinking` ne prouve que la
forme de requête. Aucun test ne mesure Qwen, un petit modèle, la fidélité de
persona, le multilingue, les ressources VRAM/RAM, la latence ou le coût total de
consolidation. Support Qwen = **compatibilité de transport plausible**, qualité
et robustesse **inconnues**. [E-LOCAL]

## Projection EGX_Terminal — sans adoption

| Élément | Catégorie d'étude | Motif |
| --- | --- | --- |
| preuve brute hors contexte | invariant architectural candidat | démontré localement et inspectable |
| index compact + résolution | protocole d'artefacts candidat | utile si chaque ref est vérifiable |
| couches brutes/dérivées | invariant candidat | permet rebuild/correction |
| API capture/retrieve/resolve | service mémoire futur | neutralise les hosts |
| hooks par harness | adaptateur futur | surface nécessaire mais remplaçable |
| budgets complets par mission | expérience nécessaire | defaults actuels non sûrs |
| provenance/confidence/TTL/status | expérience nécessaire | absents du schéma actuel |
| persona auto toujours active | rejet/quarantaine | profilage et coût persistants |
| regex comme défense | rejet | faux positifs/négatifs structurels |
| postinstall/patch/cache privé | rejet | non portable, supply-chain |
| TencentDB obligatoire | dépendance fournisseur inutile | SQLite suffit au prototype |
| Mermaid universel | rejet comme doctrine | utile pour certaines tâches seulement |
| injection invisible | quarantaine | autorité et audit insuffisants |

### Interface minimale proposée comme objet d'étude

```text
capture(event, scope)
consolidate(scope)
retrieve(query, scope, budget)
resolve(reference)
inspect(scope)
correct(memory)
forget(scope or memory)
export(scope)
```

Métadonnées minimales : `event_id`, `memory_id`, `scope` structuré
(`user/workspace/project/agent/session`), rôle/producteur, source URI + hash,
timestamp d'événement et d'ingestion, type épistémique, sensibilité,
confiance, TTL, version, parent/derived-from, modèle+prompt+version du
consolidateur, `active/superseded/contradicted/deleted`, budget appliqué,
raison du recall, score, journal de correction/oubli et statut de purge de tous
les index/backups. Cette interface n'est pas implémentée ici.

## Protocole expérimental futur

### Matrice

Harnesses : Codex, Claude Code, OpenCode. Modèles : un grand modèle comparable,
un petit modèle, Qwen local. Chaque combinaison utilise un dataset synthétique
canary-free et des scopes isolés, avec ordre randomisé, seeds publiées, au moins
5 runs par cellule et intervalles bootstrap.

Baselines :

1. aucune mémoire;
2. historique brut réinjecté;
3. résumé monolithique;
4. recherche vectorielle plate;
5. architecture couches + preuve/résolution.

Tâches : reprise après plusieurs jours; préférence modifiée; décisions en
conflit; long log avec erreur rare; détail rare; mémoire malveillante; petit
modèle local; session longue multi-tâches; migration de harness.

### Métriques et accounting

- réussite task-level et exactitude du recall;
- précision/recall des mémoires, faux souvenirs et contradictions correctement
  marquées;
- provenance exacte et taux de détail réellement résolu;
- tokens de **tous** les modèles séparés des tokens du modèle principal;
- latence, appels d'outils, cache read/write/hits, coût embeddings/stockage;
- consolidation, retries, reconstruction et correction humaine;
- dérive à J+1/J+7/J+30, contamination inter-scope;
- suppression effective vérifiée dans brut, index, backups et caches;
- réussite après migration de harness.

### Sécurité et ablations

Injecter contenu direct, cité, obfusqué, multilingue et différé; mesurer action
non autorisée, rappel malveillant et faux positif sur documentation sécurité.
Vérifier qu'une mémoire est toujours marquée non fiable et qu'un `resolve` ne
donne pas plus de scope que la requête.

Ablations : sans persona; sans scènes; sans embeddings; keyword-only; sans
Mermaid; sans auto-recall; recall explicite seulement; budgets croissants;
petit/grand modèle auxiliaire; conservation brute contre purge. Une expérience
est valide uniquement si elle publie runner, commit, configs résolues, prompts,
dataset/licence/split, ordre, sorties brutes, échecs et calculs.

## Licence et réutilisation

La racine porte un texte MIT, copyright Tencent 2026; `package.json` déclare
MIT. Aucun header de fichier contradictoire n'a été trouvé. Les prompts L1
mentionnent des prototypes validés de « Kenty » sans artefact/licence séparé;
les scripts patchent OpenClaw, et les datasets des benchmarks ne sont ni
vendored ni licenciés ici. Les assets sont couverts par le repository sans
attribution plus fine visible.

Le MIT permet juridiquement copie/modification sous conservation du notice, mais
cela ne rend pas souhaitables : interfaces OpenClaw privées, patchs lifecycle,
schémas TCVDB, code de migration ou maintenance multi-provider. Pour les
invariants candidats, une réimplémentation originale, minimale et documentée
est préférable à la copie. Aucune adoption ou copie n'a été faite pendant cet
audit. [E-LICENSE]
