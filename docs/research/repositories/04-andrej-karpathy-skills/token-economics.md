# Économie de tokens

## Méthode

Mesures effectuées sur le snapshot `2c606141936f1eeef17fa3043a72095b4765b9c2`, le 2026-07-20, sans installer de tokenizer. Les octets sont les tailles Git du blob ; les lignes sont les lignes physiques ; les mots sont les séquences séparées par espaces. L'estimation de tokens est `ceil(nombre de caractères / 4)` pour le texte anglais/code. Pour `README.zh.md`, `ceil(caractères / 2)` est utilisé à cause du chinois, avec le caveat qu'il contient aussi du code et de l'anglais. Ce sont des approximations de capacité, pas des comptes fournisseur.

## Mesures statiques

| Surface | Octets | Lignes | Mots | Tokens estimés | Chargement réel probable |
|---|---:|---:|---:|---:|---|
| `CLAUDE.md` | 2 422 | 65 | 358 | ~603 | Automatique si copié comme instruction de projet Claude ; à chaque contexte concerné |
| `skills/karpathy-guidelines/SKILL.md` | 2 585 | 67 | 371 | ~644 | Corps à la demande après découverte/sélection |
| `.cursor/rules/karpathy-guidelines.mdc` | 2 708 | 70 | 393 | ~674 | Automatique dans le projet car `alwaysApply: true` |
| `README.md` | 6 369 | 171 | 865 | ~1 584 | Documentation ; pas de chargement runtime établi |
| `CURSOR.md` | 1 983 | 28 | 241 | ~495 | Documentation ; pas de chargement runtime établi |
| `EXAMPLES.md` | 15 360 | 522 | 1 859 | ~3 828 | Documentation ; aucun lien runtime dans le snapshot |
| `README.zh.md` | 6 213 | 171 | 316 | ~1 614 | Traduction documentaire ; estimation très approximative |
| `.claude-plugin/plugin.json` | 401 | 11 | 38 | ~101 | Manifeste lu par le harness ; pas nécessairement présenté au modèle |
| `.claude-plugin/marketplace.json` | 787 | 29 | 73 | ~197 | Catalogue/distribution ; pas nécessairement présenté au modèle |

Total disque textuel : 38 828 octets, 1 134 lignes physiques, 4 514 mots et environ 9 740 tokens selon ces approximations hétérogènes. Ce total n'est pas un coût de session.

### Métadonnées de découverte du skill

| Champ | Octets/caractères | Mots | Tokens estimés |
|---|---:|---:|---:|
| `name` | 19 | 1 | ~5 |
| `description` | 219 | 28 | ~55 |
| `license` | 3 | 1 | ~1 |

Un harness peut exposer nom, description et chemin pour la découverte sans charger les ~644 tokens du corps. Le coût exact inclut enveloppe, sérialisation et éventuelle politique du harness, non mesurées ici. Le champ `skills` explicite du manifeste Claude peut faire enregistrer deux fois le même skill en plus du scan conventionnel ; ce serait principalement une duplication de métadonnées jusqu'à sélection.

## Payloads comportementaux et duplication

Les trois copies comportementales occupent environ 1 921 tokens estimés sur disque : ~603 (`CLAUDE.md`), ~644 (skill) et ~674 (Cursor). Après retrait des frontmatters et titres, le cœur de `CLAUDE.md` et de la règle Cursor est identique sur 2 395 caractères. Le skill diffère légèrement : introduction de provenance supplémentaire, footer observable absent.

Il n'existe ni include commun ni génération. La duplication sur disque crée donc un risque de drift et un coût de maintenance, mais pas automatiquement 1 921 tokens dans une conversation :

- Projet Claude avec `CLAUDE.md` copié : ~603 tokens always-on, plus l'enveloppe du harness.
- Plugin/skill Claude sans copie de `CLAUDE.md` : ~60 tokens de métadonnées estimées lors de la découverte, puis ~644 lorsque sélectionné.
- Si le projet cumule `CLAUDE.md` et la skill invoquée : jusqu'à ~1 247 tokens de contenu fortement redondant.
- Projet Cursor : ~674 tokens à chaque contexte où la règle Always s'applique.
- `EXAMPLES.md`, README, traduction et `CURSOR.md` représentent environ 7 521 tokens estimés, mais sont hors coût runtime tant qu'un humain ou un agent ne les ouvre pas.
- Les manifests totalisent ~298 tokens textuels sur disque ; ils organisent la livraison, sans preuve qu'ils soient injectés au modèle.

Le mode skill est donc potentiellement plus économique sur les tâches non pertinentes, tandis que le `CLAUDE.md` projet et Cursor paient une taxe systématique. « Universel » dans le marketing du contenu ne signifie pas que le SKILL est toujours injecté : la documentation Claude actuelle décrit les skills comme chargées à la demande.

## Coûts dynamiques possibles

### Surcoûts

- `Think Before Coding` peut produire listes d'hypothèses, mini-plans, alternatives et questions. Une clarification impose au moins un tour utilisateur supplémentaire et recharge souvent une partie du contexte.
- `Goal-Driven Execution` peut multiplier recherche, tests, build, navigation, captures ou reprises. Les sorties d'outils peuvent dépasser largement les ~600 tokens du prompt statique.
- L'inclusion always-on affecte les tâches triviales où le bon comportement tiendrait en une action locale.
- Des critères trop absolus peuvent faire réécrire une solution courte, demander des validations indisponibles ou boucler sur un proxy.
- La duplication `CLAUDE.md` + skill ou l'injection automatique proposée par des adaptateurs de PR peut augmenter le contexte sans information nouvelle.
- Pour un petit modèle, une règle dense peut concurrencer la tâche et les fichiers pour l'attention, même si son nombre brut de tokens est modeste.

### Économies hypothétiques

- Une ambiguïté matérielle clarifiée avant édition peut éviter un diff complet et sa reprise.
- Une solution non spéculative peut réduire code généré, sorties de patch, lectures ultérieures et tests associés.
- Un périmètre causal peut éviter les analyses, edits et comptes rendus de refactors adjacents.
- Une vérification bien choisie peut éviter un faux achèvement suivi d'un nouveau tour de diagnostic.
- Un skill réellement on-demand évite le payload complet lorsque la tâche ne le justifie pas.

Ces économies sont plausibles, pas mesurées. Réduire les tokens de complétion tout en augmentant prompt, appels d'outils ou tours ne prouve pas une économie totale. Inversement, un surcoût initial peut être rentable s'il évite une reprise coûteuse.

## Ce que montrent et ne montrent pas les PR d'évaluation

La PR [#25](https://github.com/multica-ai/andrej-karpathy-skills/pull/25) annonce un score de découvrabilité passant de 84 à 96 après réécriture de la description. Ses artefacts accessibles sont une image et un JSON de 136 octets avec les deux scores ; ils n'exposent ni prompts, corpus, version d'outil, configuration, sorties brutes, rubric ni procédure de reproduction. L'auteur déclare travailler pour l'outil utilisé. Même si le score était reproduit, il mesurerait la sélection de la skill, pas l'efficacité de son contenu une fois chargé.

La PR ouverte [#186](https://github.com/multica-ai/andrej-karpathy-skills/pull/186) est le seul effort quantitatif substantiel trouvé, mais elle n'appartient pas au snapshot. Chacun de ses jeux comparatifs récents contient 30 appels au total, soit 15 par bras : 3 tâches × 5 répétitions × 2 bras. Sur un microbenchmark GPT-5.3-Codex sans édition de fichiers ni outils, les artefacts de la doctrine complète déclarent baseline 10/15 contre skill 15/15, avec +203,6 % de tokens visibles de requête et +34,6 % de latence ; ceux d'une variante adaptative fortement réécrite déclarent aussi 15/15, avec −45,1 % de tokens visibles et −12,5 % de latence face à sa baseline. Les tokens cachés/fournisseur n'étaient pas disponibles. Un ancien jeu Gemini n'a qu'une répétition par bras, ordre baseline-first et graders par mots-clés/lignes ; il rapporte +59,2 % prompt+completion malgré une complétion plus courte.

Ces chiffres sont confirmés comme présents dans la branche de PR, pas comme généralisation valide. Le corpus est minuscule et conçu autour des règles ; les graders sont étroits ; aucune session terminal complète, modification de repository, worktree sale, tâche transversale ou évaluation humaine aveugle n'est présente. La branche réécrit en outre fortement la doctrine et mélange d'autres inspirations : elle ne permet pas d'isoler les quatre règles de `main`.

## Mesures nécessaires pour conclure

Une décision token-efficiency exigerait, pour chaque harness et modèle :

1. tokens de système/instructions réellement injectés, métadonnées de découverte comprises ;
2. tokens de toutes les requêtes et réponses sur la session, pas seulement la complétion finale ;
3. volume et coût des sorties d'outils, nombre de tours et latence wall-clock ;
4. taux de réussite indépendant, reprises et intervention humaine ;
5. taille et bruit du diff, code ajouté/évité et complexité ;
6. ventilation par tâche triviale, ambiguë, sans tests, transversale et worktree sale ;
7. baseline, doctrine complète et ablations, répétées avec ordre randomisé ;
8. intervalles d'incertitude et publication des artefacts reproductibles.

Conclusion : le payload statique utile est petit, autour de 600–675 tokens par surface, mais son mode de chargement domine son coût. Le dépôt peut économiser du travail par réduction des reprises et du scope, ou en coûter davantage par verbalisation, clarifications et boucles de vérification. Aucune économie nette n'est démontrée.
