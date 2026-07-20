# Économie des tokens et preuves expérimentales

## Méthode

Les tailles exactes sont des octets/caractères UTF-8 au snapshot. Les tokens sont une estimation statique `caractères / 4`, pas un tokenizer de provider. Les payloads par mode ont été dérivés sans exécuter le repository : retrait du frontmatter et application indépendante des règles de filtrage lisibles dans le builder. Aucun hook, test, modèle ou benchmark upstream n'a été lancé [E35–E36].

## Empreinte statique

| Surface | Lignes | Caractères | Tokens estimés | Moment de chargement |
|---|---:|---:|---:|---|
| `skills/ponytail/SKILL.md` complet | 121 | 6 736 | 1 684 | si skill lue directement |
| frontmatter Ponytail | 20 | 956 | 239 | découverte skill |
| corps Ponytail | 102 | 5 780 | 1 445 | à la demande ou builder |
| payload `lite` | 100 | 5 202 | 1 300 | hook/session/tour selon host |
| payload `full` | 100 | 5 229 | 1 307 | idem, défaut |
| payload `ultra` | 100 | 5 267 | 1 317 | idem |
| fallback condensé | — | 2 680 | 670 | seulement si lecture de skill échoue |
| `AGENTS.md` compact | 33 | 2 622 | 656 | toujours visible instruction-tier |
| `ponytail-review` | — | 2 428 | 607 | à la demande |
| `ponytail-audit` | — | 1 693 | 423 | à la demande |
| `ponytail-debt` | — | 1 747 | 437 | à la demande |
| `ponytail-gain` | — | 1 875 | 469 | à la demande |
| `ponytail-help` | — | 2 859 | 715 | à la demande |

Les trois intensités changent moins de 65 caractères entre elles : table et exemple uniquement. Le coût permanent est pratiquement identique, alors que le stockage, les commandes, le statusline et les transitions multiplient les états [E15–E18, E36]. `review` est différent : le builder Node injecte un pointeur, Hermes le corps complet, et l'invocation skill peut ajouter le corps dans un autre tour.

## Modes de chargement

| Niveau | Métadonnées | Corps | Réinjection | Cache/compaction |
|---|---|---|---|---|
| instruction-tier | fichier entier | toujours | selon politique du host | généralement reconstitué par le host |
| skill-tier | nom/description | à la sélection | nouvelle lecture possible | contenu peut être compacté puis rechargé |
| plugin/hook-tier session | manifest/hook | ~1 300 tokens au démarrage | `resume/clear/compact` pour Node | réinjecté explicitement |
| plugin OpenCode | plugin + skills | ~1 300 | chaque prompt | cache provider inconnu |
| sous-agent | hook metadata | ~1 300 par spawn | chaque sous-agent | fenêtre du worker, pas celle du parent |

Codex documente la découverte progressive des skills et l'approbation des hooks ; Claude confirme que les sous-agents n'héritent pas automatiquement du system prompt [E26–E27]. Cela justifie des mécanismes distincts, mais pas l'envoi du corps complet à tous les workers.

### Coût par harness

- **Codex/Claude.** Une injection de session, de nouveau après événements de cycle de vie, plus une injection par sous-agent. Le hook mode-tracker n'ajoute pas normalement le corps à chaque prompt hors Qoder.
- **OpenCode.** Reconstruction et concaténation à chaque tour ; le coût facturé dépend du cache et du provider. Fusionner le message ne supprime aucun token [E22–E24].
- **Qoder.** `AGENTS.md`/rule peut déjà être présent, puis le hook ajoute le payload complet à chaque prompt : risque de duplication instruction + plugin.
- **Gemini/générique.** Environ 656 tokens toujours visibles via `AGENTS.md`, sans état.
- **Pi.** Corps complet avant chaque `agent_start`; l'état transcript est natif.
- **Hermes.** Corps reconstruit avant chaque appel LLM, avec code Python séparé.
- **MCP.** Aucun coût tant que prompt/tool non appelé, puis corps complet dans un message utilisateur/tool.

Le dépôt ne mesure pas systématiquement la duplication lorsque plusieurs surfaces sont actives simultanément. L'issue #595 rapporte même une interaction de bannières/instructions sans prompt utilisateur, mais elle reste un rapport externe au snapshot [E19, E25].

## Sous-agents

Avec `full`, chaque spawn ajoute environ 5 229 caractères/~1 307 tokens [E21]. Un parent qui crée 50 workers paierait donc environ 65 000 tokens estimés dans les fenêtres des workers. Cette multiplication ne réduit pas directement la fenêtre principale, mais affecte coût, latence et attention de chaque worker. Les 37–240 spawns rapportés dans #597 ne sont pas une mesure reproduite.

Le matcher actuel réduit le nombre de destinataires, pas la taille ; son fail-open signifie qu'une erreur de regex ou un type absent maximise le coût. Le fallback de 2 680 caractères contient déjà ladder et garde-fous, mais il n'est pas volontairement sélectionnable [E12, E20–E21]. Une expérimentation EGX ultérieure devrait comparer : aucun payload, kernel neutre ~200–400 tokens, fallback ~670, corps ~1 300, séparément pour implémentation, recherche et review.

## Générations de benchmark

| Génération | Ce qu'elle apporte | Statut et limite |
|---|---|---|
| single-shot initial | cinq tâches, plusieurs Claude, LOC/tokens/coût/temps | **superseded pour les claims globaux** : baseline conversationnelle, `n=1`, texte compté comme code |
| critique baseline #126 | agent réel et prompt court comme contrôles demandés | critique valide, a forcé la reconstruction |
| local Llama | petit modèle quantifié, médianes `n=5` | résultat négatif, variance élevée, données brutes absentes |
| coût multi-provider | 30 reps Claude, 10 OpenAI, correctness | tables seulement ; Gemini incomplet ; direction inversée sur reasoning models |
| agentique 17 juin | isolation/session réelle et sécurité | **superseded** : baseline contaminée par hooks |
| agentique corrigé 18 juin | 12 features, 6 surgical, quatre bras, `n=4` | headline actuel ; un modèle, tâches orientées over-build, timeouts |
| safety | checks déterministes adversariaux | cinq axes sécurité mis en avant ; observation 20/20, pas preuve universelle |
| completeness | juge ajouté après le runner initial | aucun score committé pour le résultat headline |

### Single-shot et corrections

Le premier compteur ne considérait que les fences, donnant zéro aux sorties de petits modèles sans fence ; la version corrigée traite aussi le code nu [E39]. D'autres corrections ont ajouté un gate de correction, rectifié une incompatibilité debounce, nettoyé les commentaires de LOC et testé des prompts de robustesse. Ces améliorations renforcent le processus, mais rendent les anciennes cartes de gain historiques.

Le résultat initial 80–94 % était aussi gonflé par une baseline bavarde : le document agentique le reconnaît explicitement. La skill `ponytail-gain` continue pourtant de l'afficher comme score principal et conserve l'ancien coût 47–77 % au lieu de 42–75 % [E34, E47].

### Petit modèle local

Le benchmark local est précisément limité : `llama3.2:latest`, 3,2B, Q4_K_M, Ollama, Windows 11, température 0,7, cinq tâches et médiane `n=5` [E37]. Les totaux publiés sont :

| Arm | LOC médian total | Temps total |
|---|---:|---:|
| baseline | 109 | 19,4 s |
| Caveman | 133 | 21,1 s |
| Ponytail | 137 | 21,8 s |

Ponytail varie de −17 % à +50 % face à la baseline ; une campagne `n=3` donnait −17 %, celle à `n=5` +26 %. Le seul signal cohérent rapporté est une latence ~10–15 % supérieure [E38]. Les données soutiennent donc « aucun transfert stable démontré ici », pas « Ponytail échoue sur tous les petits modèles ».

Ce résultat ne se généralise pas à Qwen : taille, architecture, quantification, chat template et provider diffèrent. La correction OpenCode/Qwen règle une erreur de forme avant l'inférence, alors que le benchmark Llama mesure un comportement après inférence [E23–E24].

Expérience Qwen minimale ultérieure : SHA plugin fixé incluant #301/#536 ; OpenCode et provider fixés ; Qwen de plusieurs tailles/quantifications ; baseline, kernel neutre condensé, persona complète et ablations ; température basse puis 0,7 ; ≥20 répétitions si variance ; tâches native-first et tâches où la dépendance est légitime ; completeness, safety, tests, LOC, input/output/reasoning/cache, tools et temps séparés.

### Benchmark agentique corrigé

La campagne headline emploie Claude Code 2.1.177/Haiku 4.5, un template FastAPI+React épinglé, 12 tickets feature et quatre répétitions par cellule [E40]. Six tickets frontend possèdent explicitement une alternative HTML native ; six tickets backend ont moins de marge. C'est un bon test mécanistique de `native-first`, pas un échantillon représentatif de tout développement.

Le script indépendant temporaire a recalculé les sommes des moyennes de tâches publiées :

| Arm | Somme des 12 moyennes | Moyenne | Écart baseline |
|---|---:|---:|---:|
| baseline | 2 217 | 184,75 | — |
| Caveman | 1 813 | 151,08 | −18,22 % |
| Ponytail | 1 015 | 84,58 | **−54,22 %** |
| YAGNI one-line | 1 438 | 119,83 | −35,14 % |

Le −54 % est reproduit depuis les valeurs arrondies publiées [E41]. Les chiffres Caveman et one-line diffèrent du résumé (−20/−33) parce que le calcul original utilisait les cellules sous-jacentes non arrondies, absentes du dépôt. Aucun recalcul de tokens/coût/temps n'est possible sans les données brutes.

Les tâches date/color/dropzone expliquent une forte part du gain via inputs natifs ; les backend convergent [E42]. Quatre cellules LOC ont timeout, et `n=4` est faible face à la variance de 300–570 lignes annoncée. Le runner interdit Bash/serveur : il mesure le diff écrit, pas la validation par l'agent. Les checks déterministes exécutent ensuite seulement les fonctions surgical.

### Safety et completeness

La campagne observe 20/20 passes pour baseline, Caveman et Ponytail, 19/20 pour le prompt one-line [E43]. L'intervalle Wilson 95 % de 20/20 vaut environ 83,9–100 % ; « 100 % safe » est acceptable comme taux observé sur ces checks, excessif comme propriété générale. Le résultat couvre cinq axes sécurité × quatre runs, la sixième tâche surgical étant un axe de correction/cache.

Le juge completeness existe et possède un selftest, mais le rapport du 18 juin n'en donne aucun score et aucun workspace brut n'est committé [E45–E46]. La réduction LOC n'est donc pas accompagnée, dans les preuves publiées, d'une mesure de completeness sur les douze features. La safety protège seulement les tâches surgical connues.

### Coût et providers

Les tables rapportent sur Claude −63,1 % Haiku, −74,5 % Sonnet et −42,3 % Opus. Sur OpenAI, gpt-4.1-mini est −39,6 %, mais gpt-5.4-mini +26,2 % et gpt-5.5 +38,7 % ; Gemini est resté en attente de quota [E47]. Les modèles reasoning peuvent donc dépenser plus de contexte et de raisonnement que le code court n'économise.

L'issue Cursor #121 rapporte un autre mécanisme : output parfois plus court, mais davantage de lectures/outils/tokens et coût selon modèle [E48]. Il faut séparer six comptes :

```text
contexte ajouté
output ajouté ou évité
reasoning ajouté ou évité
tool calls ajoutés ou évités
code écrit ou évité
maintenance future potentiellement évitée
```

Les LOC évitées ne sont pas convertibles en tokens sans hypothèse arbitraire. La maintenance future est une hypothèse de design, pas une mesure des campagnes.

## Claims confirmés, corrigés ou non démontrés

| Claim | Statut | Portée défendable |
|---|---|---|
| le builder Node produit les mêmes règles par mode | confirmé statiquement | Node/Pi/MCP/OpenCode, pas Hermes |
| les copies instruction-tier sont alignées | confirmé par checksum | huit corps compacts au snapshot |
| Ponytail réduit ~54 % LOC | recalculé | moyenne de 12 tâches Haiku choisies, valeurs publiées |
| Ponytail garde 100 % safety | confirmé comme observation | 20/20 checks, pas propriété générale |
| 80–94 % de réduction globale | corrigé/superseded | plafond par tâche native, pas moyenne agentique |
| 47–77 % moins cher | corrigé | 42–75 % rapporté sur Claude |
| coût réduit universellement | réfuté par contre-preuves | dépend du modèle/provider/tâche |
| correction Qwen rend Ponytail efficace | non démontré | elle rend le format compatible dans un cas rapporté |
| doctrine transférable aux petits modèles | non démontré ; négatif sur Llama 3.2 3B | aucune généralisation Qwen |
| persona nécessaire | non démontré | pas d'ablation sémantiquement contrôlée |
| « un check » suffit | non démontré | plancher de doctrine, pas stratégie de test |
| moins de code = meilleure maintenance | plausible, non mesuré | dépend de correction, lisibilité et évolution |

## Limites de mesure

- Pas de raw data committée pour refaire les distributions, coûts, exclusions ou scores.
- `n=4` agentique et `n=5` local, modèles et environnements uniques.
- `llama3.2:latest` est mutable ; plugin installé du benchmark agentique n'est pas identifié par SHA dans les données.
- Judge LLM à modèle fixe, seulement auto-testé sur quelques paires ; 300 tokens de sortie ont fait l'objet de #426.
- LOC reste un proxy : le compteur retire commentaires par regex et peut confondre syntaxe et chaînes.
- Le rapport actuel mélange résultats historiques et harness enrichi après la campagne.
- Le caching effectif OpenCode/Qwen, les reasoning tokens comparables et l'adhérence aux rungs ne sont pas isolés.

Conclusion expérimentale limitée : Ponytail démontre un signal fort sur Claude/Haiku quand la tâche contient un piège d'over-build remplaçable par une primitive native. Il démontre aussi ses limites : aucun signal stable sur Llama 3.2 3B, coût parfois inversé, et protocole Qwen corrigé sans mesure comportementale.
