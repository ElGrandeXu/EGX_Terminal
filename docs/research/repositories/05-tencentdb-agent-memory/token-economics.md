# Économie de tokens de bout en bout

## Verdict

Le repository démontre des mécanismes qui peuvent réduire le contexte du modèle
principal, mais pas une réduction nette à l'échelle de la session complète. Les
mesures headline ne sont pas reproductibles depuis le repository et aucune ne
documente l'inclusion des LLM auxiliaires, embeddings, retries, judge, recovery
ou correction humaine. La seule conclusion défendable est conditionnelle :
**externaliser un gros résultat puis n'en rappeler qu'un index peut économiser
des tokens du modèle principal si le coût de consolidation et les relectures
restent inférieurs au contexte évité**. [E-BENCH]

## Modèle de coût requis

Pour une mission, le bilan devrait être :

```text
T_total = T_main
        + T_L1_extract + T_L1_dedup
        + T_L2_scene + T_L3_persona
        + T_offload_L1 + T_offload_L1.5 + T_offload_L2 + T_offload_L4
        + T_embeddings_equivalent
        + T_recall + T_resolve_and_reread
        + T_retries + T_judge
```

À comparer non seulement en tokens, mais en latence, coût monétaire, RAM/VRAM,
stockage, cache provider, bande passante, taux d'échec et correction humaine.
Le code reporte quelques compteurs locaux, mais aucun artefact du repository ne
calcule ce total pour les benchmarks annoncés.

## Coûts statiques

Présents à chaque tour lorsque la mémoire long terme et le recall sont actifs :

- `<user-persona>` complet;
- `<scene-navigation>` pour les scènes indexées;
- `<memory-tools-guide>` et descriptions/schémas des outils exposés;
- infrastructure de prompt du plugin/harness;
- en offload agressif, MMD active et/ou historiques.

Ces blocs stables ne sont pas inclus dans `maxTotalRecallChars`, qui ne couvre
que L1. Leur coût dépend du nombre/taille de scènes et de la persona. Le code les
retourne dans `appendSystemContext`; l'issue #120 signale que cette position se
trouve après une cache boundary OpenClaw pour certains providers. #319 et #533
proposent de déplacer/stabiliser ce préfixe, mais sont ouvertes. [E-RECALL]

Le hook `before_message_write` de `main` retire inconditionnellement les blocs
`<relevant-memories>` des messages utilisateur persistés, ce qui limite une
forme d'accumulation. Il ne résout pas le coût du bloc stable ni toutes les
réécritures/mutations de l'offload. La PR #319 ajoute une option de visibilité,
des tests et le mapping de cache boundary; elle ne doit pas être créditée à
`main`.

## Coûts dynamiques par tour

### Modèle principal

- recherche + injection de 0 à 5 L1, sans cap de caractères par défaut;
- lecture de persona/navigation/guide;
- MMD injectées après compression;
- appels supplémentaires de recherche mémoire et lecture de scènes/refs;
- éventuelle relecture du texte brut lorsque le résumé est insuffisant;
- cache miss si la partie stable du prompt change ou arrive après la boundary.

### Recall

Defaults vérifiés sur `main` :

| Paramètre | Valeur | Conséquence |
| --- | ---: | --- |
| `recall.enabled` | `true` | coût avant chaque prompt |
| `recall.maxResults` | `5` | seul plafond actif par défaut |
| `recall.maxCharsPerMemory` | `0` | garde-fou désactivé |
| `recall.maxTotalRecallChars` | `0` | budget total L1 désactivé |
| `recall.scoreThreshold` | `0.3` | filtre résultats |
| `recall.strategy` | `hybrid` | keyword + embedding si disponible |
| `recall.timeoutMs` | `5 000` | latence maximale visée |

La PR #71 applique réellement les deux caps après classement et avant
injection, en conservant l'ordre des scores. `0` signifie explicitement « aucun
plafond ». Une issue ultérieure #163 affirme les champs non câblés dans certains
chemins/version; sur le `main` audité, `src/config.ts` et
`src/core/hooks/auto-recall.ts` les lisent et les appliquent. La lecture
corrigée est donc : **fonctionnalité présente sur `main`, mais protection
inactive par défaut et couverture de tests dédiée absente**. [E-BUDGET]

La recherche hybrid SQLite lance FTS et embedding puis fusionne par RRF; TCVDB
peut exécuter le hybrid côté serveur. Keyword-only évite l'appel embedding et
est la baseline locale la moins coûteuse. La consigne « au plus 3 recherches
mémoire par tour » du guide n'est pas imposée par le code.

## Coûts de consolidation en arrière-plan

### Mémoire longue durée

| Étape | Fréquence/default | Coût non compté dans les claims |
| --- | --- | --- |
| capture L0 | chaque tour | I/O + index + embedding L0 éventuel |
| L1 extraction | warm-up 1→2→4→5, puis 5 tours, ou idle 600 s | prompt sur L0 + génération JSON |
| L1 dédup | chaque batch L1 si activé | second appel LLM + recherche candidats |
| L2 scènes | 10 s après L1, min 900 s, max 3 600 s | lecture L1 + agent/tool calls fichiers + retries |
| L3 persona | cold start/demande/50 nouvelles mémoires | lecture scènes + agent/tool calls + backups |
| embeddings | L0 et L1 selon config | tokens/latence réseau ou CPU/GPU local |
| profile sync | après dérivés selon backend | hash/version + I/O/TCVDB |

Le nombre `maxMemoriesPerSession=20` borne la sortie d'un batch, pas les tokens
du prompt d'entrée ni le cumul historique. Une dédup qui fusionne mal crée un
coût futur de correction et de recall; ce coût humain est absent des mesures.

### Context offload

| Étape | Entrée bornée observée | Sortie/effet | Retry |
| --- | --- | --- | --- |
| L1 | params 500 caractères, résultat preview 2 000 | résumé ≤200 caractères + score | 3 puis fallback |
| L1.5 | contexte récent + MMD/metadata | frontière de tâche JSON | fail-safe après échec |
| L2 | entrées JSONL sans node + MMD actuelle | Mermaid cible ~4 000 caractères + mapping | retry via états `wait` |
| L3 | tous messages comptés | remplacement/suppression, pas d'appel LLM propre | recalculs tiktoken |
| L4 | demande explicite, backend | skill générée et injectée | dépend backend |

L'écriture du ref brut évite d'envoyer l'intégralité au L1 auxiliaire, mais un
drill-down ultérieur la renvoie au modèle principal. Les retries, erreurs JSON,
MMD reconstruites et états `wait` peuvent rendre la consolidation plus coûteuse
que le résultat brut pour des outils courts.

## Defaults offload et budgets

| Paramètre | Défaut | Observation |
| --- | ---: | --- |
| `offload.enabled` | `false` | aucun gain/coût sans opt-in |
| mode | `local` sauf `backendUrl` | modèle host/API compatible |
| `defaultContextWindow` | 200 000 | peut diverger du modèle réel |
| `forceTriggerThreshold` | 4 paires | consolidation fréquente |
| `maxPairsPerBatch` | 20 | borne batch, pas session |
| `l2NullThreshold` | 4 | déclenche MMD |
| `l2TimeoutSeconds` | 300 | déclenchement temporel |
| mild | 0,50 | remplacements relativement tôt |
| mild scan/top/current-task | 0,70 / 0,40 / 0,80 | heuristiques internes |
| aggressive/delete | 0,85 / 0,40 | suppression historique |
| emergency/target | 0,95 / 0,60 | suppression/troncature forte |
| `mmdMaxTokenRatio` | 0,20 | seul budget explicite des MMD |
| overhead système estimé | 0,12 | approximation si mesure host absente |
| retention offload | `0` | nettoyage désactivé |

Le tracker utilise `js-tiktoken` et `cl100k_base` par défaut; il compte messages
et overheads approximatifs. Un tokenizer différent, des champs que le provider
retire ou ajoute, et le cache host peuvent créer un écart. L'issue #233 et la PR
#411 documentent un cache WeakMap obsolète après `splice`; la correction de 7
lignes reste non fusionnée. [E-OFFLOAD-BUDGET]

## Cache provider et inflation historique

Les références demandées ne sont pas toutes des PR :

| Référence | Nature/statut | Lecture au snapshot |
| --- | --- | --- |
| #71 | PR fusionnée | caps recall présents, off par défaut |
| #120 | **issue ouverte** | baisse MiMo 91,1→63,5 %, DeepSeek 95,7→83,3 % auto-rapportée; OpenClaw a aussi changé, causalité non isolée |
| #319 | PR ouverte | strip configurable + stable context avant boundary + tests; proposition |
| #411 | PR ouverte | invalide token cache après suppression `tool_use`; proposition |
| #447 | PR ouverte | task snapshots append-only/cache epoch/MMD complet; proposition |
| #533 | PR ouverte | refonte cache/stabilité, 19 fichiers et 2 075 ajouts; proposition |

L'issue #120 attribue l'inflation au `prependContext`, au replay et au placement
du stable context. `main` possède déjà un strip inconditionnel des blocs rappelés
avant persistance, mais conserve `appendSystemContext`; les PR ouvertes montrent
que la stabilité de bout en bout n'est pas considérée résolue. Aucun chiffre de
cache de ces PR n'est un résultat du snapshot audité. [E-CACHE]

## Benchmarks : audit de reproductibilité

### Claims actuels

| Benchmark | Claim README | Statut de preuve |
| --- | --- | --- |
| WideSearch | succès 33→50 %, 221,31M→85,64M tokens, −61,38 % | non reproductible depuis le repo |
| SWE-bench | 58,4→64,2 %, 3 474,1M→2 375,4M, −33,09 % | non reproductible depuis le repo |
| AA-LCR | 44,0→47,5 %, 112,0M→77,3M, −30,98 % | non reproductible depuis le repo |
| PersonaMem | précision 48→76 % | non reproductible depuis le repo |

La recherche exhaustive des 173 fichiers ne trouve ces noms/chiffres que dans
`README.md` et `README_CN.md`. Sont absents : runner, commit d'évaluation,
dataset/split/licence, nombre de tâches, ordre complet, nombre de runs, seeds,
modèles exacts, version du harness, context window, config, prompts de test,
judge, définition de succès, logs, sorties, résultats par tâche, scripts de
calcul, coûts auxiliaires, échecs, variance et intervalle de confiance.

L'affirmation « 50 tâches SWE-bench consécutives par session » n'est soutenue que
par le README. Aucun artefact ne permet de vérifier les groupes, leur ordre, la
réinitialisation entre groupes, la contamination ou le total de tâches.

Il est inconnu si les tokens incluent :

- modèle agent principal seulement;
- L1/L1.5/L2/L3/persona/dédup;
- embeddings;
- offload et retries;
- judge;
- appels de récupération des preuves;
- tâches échouées.

### Histoire de la correction `3cc6d2a`

Le commit exact
`3cc6d2aa759455f928dea9fa7762a6c296c7a73d` du 2026-05-13, message
`docs: fix benchmark data, replace placeholder links, add EN pyramid image`, ne
modifie que les README et une image.

| Mesure | Avant | Après |
| --- | ---: | ---: |
| headline tokens économisés | 63,59 % | 61,38 % |
| headline pass rate relative | +41,18 % | +51,52 % |
| WideSearch succès | 8,5→12 % | 33→50 % |
| WideSearch tokens | 174,31M→63,46M | 221,31M→85,64M |
| SWE-bench tokens | `3474.1→2375.4` sans `M` | `3474.1M→2375.4M` |
| AA-LCR économie | −31 % | −30,98 % |

Le commit n'ajoute aucune justification, donnée ou formule. `git blame` attribue
encore les valeurs actuelles à ce commit. Aucun artefact servant à la correction
n'est disponible; elle n'est donc pas reproductible. L'absence de preuve ne
signifie pas que les chiffres sont faux, mais interdit de les traiter comme
résultats confirmés. [E-BENCH-HISTORY]

### PR #204

La PR ouverte #204, `docs(eval): add reproducible memory evaluation guide`, est
un guide de 142 ajouts/3 fichiers. Son auteur précise qu'elle évite
intentionnellement tout runner et toute dépendance. Elle propose les métadonnées
qui manquent, mais ne fournit aucun artefact lié aux chiffres headline et n'est
pas sur `main`. [E-PR204]

### Dataset et licences

Aucun dataset n'est vendored et aucune licence WideSearch/SWE-bench/AA-LCR/
PersonaMem n'est déclarée dans le repository. Sans identifiants de version et
splits, on ne peut pas vérifier licence, contamination, changement de données ou
comparabilité. Aucune expérience n'a été lancée pendant cet audit.

## Quand le système peut consommer davantage

- résultat d'outil court : appel L1 + JSONL + MMD coûte plus que le texte brut;
- recall non pertinent : embedding/recherche + 5 mémoires + bloc stable sans
  amélioration;
- petits modèles produisant JSON invalide : retries, fallback et corrections;
- cartes Mermaid instables : mises à jour fréquentes et relecture;
- persona/scènes changeant souvent : invalidation du cache stable;
- drill-down fréquent : résumé **plus** lecture du ref, double coût;
- tokenizer mal calibré : compression trop tôt ou trop tard;
- dual-write/curseur cassé : rescans et reconstructions;
- embeddings distants lents/limités : retries et dégradation keyword;
- faux souvenir : coût humain de diagnostic, correction et purge des dérivés;
- Opik activé : sérialisation, réseau et stockage de traces complets;
- multi-session sans scope : bruit rappelé, tokens et risque augmentés.

## Mesures manquantes à exiger

1. tokens input/output/cache read/write par appel et par modèle;
2. nombre, durée et échec des appels L1/L1.5/L2/L3/dédup/persona;
3. volume et latence embeddings, CPU/GPU/RAM/VRAM local;
4. caractères/tokens injectés séparés L1/persona/navigation/guide/MMD;
5. fréquence et coût de `resolve`, taux de détail réellement retrouvé;
6. tokens avant/après offload mesurés avec tokenizer provider réel;
7. cache hit et stabilité du préfixe sur sessions longues;
8. stockage JSONL/Markdown/SQLite/TCVDB/Opik et bande passante;
9. retries, écritures partielles, recovery et reconsolidation;
10. temps humain pour inspecter/corriger/effacer une mauvaise mémoire;
11. coût des échecs et tâches abandonnées, pas seulement succès;
12. variation par harness, modèle, langue, durée et budget.

Sans ce ledger par run, « token-efficient » reste un objectif plausible et non
un invariant démontré.
