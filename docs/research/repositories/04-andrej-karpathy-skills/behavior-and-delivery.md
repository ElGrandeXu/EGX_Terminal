# Comportement, provenance et livraison

## Cadre de lecture

Les faits ci-dessous sont rattachés au snapshot `2c606141936f1eeef17fa3043a72095b4765b9c2`, sauf mention explicite d'un commit, d'une PR ou d'une source externe. « Interprétation » désigne une lecture de l'audit ; « projection » une hypothèse pour une expérimentation future, jamais une décision d'EGX_Terminal.

## Archéologie de la provenance

### Chaîne de dérivation observée

1. Le commit initial [`8462496`](https://github.com/multica-ai/andrej-karpathy-skills/commit/8462496b34419f20b32778610571ac723e91f94c) rattache le projet à la publication X `1886192184808149383`. L'endpoint oEmbed officiel de X identifie une publication d'Andrej Karpathy du 2025-02-02 commençant par la définition du « vibe coding ». Ce n'est pas la source des notes sur Claude Code.
2. La PR [#1](https://github.com/multica-ai/andrej-karpathy-skills/pull/1) et le commit [`bf5837f`](https://github.com/multica-ai/andrej-karpathy-skills/commit/bf5837f278a8a7b4bff8bce6bc2414a75faa34f7) remplacent ce lien par [`2015883857489522876`](https://x.com/karpathy/status/2015883857489522876). L'oEmbed officiel l'attribue à Karpathy, le 2026-01-26, et expose le début de « random notes from claude coding ». X ne rend toutefois pas le texte complet publiquement vérifiable dans une surface stable lors de l'audit.
3. Le README assemble de courts passages autour de quatre thèmes. Les copies indexées de la publication indiquent que certaines phrases ont été retranchées, raccordées ou condensées. « Quote » dans le README ne doit donc pas être compris comme transcription complète et strictement verbatim certifiée par la source primaire.
4. Les mainteneurs nomment et opérationnalisent les thèmes en `Think Before Coding`, `Simplicity First`, `Surgical Changes` et `Goal-Driven Execution`. Les trois premiers ont une correspondance thématique directe ; le quatrième titre et sa structure « success criteria → loop » sont une synthèse de mainteneur à partir du passage de Karpathy sur le passage de l'impératif au déclaratif, les tests, le navigateur et les boucles.
5. Les quatre règles existaient dès le commit initial, dont le message porte `Co-Authored-By: Claude Opus 4.5`. La PR [#2](https://github.com/multica-ai/andrej-karpathy-skills/pull/2) développe ensuite les explications, indicateurs et tradeoffs, également avec ce trailer. Au total, neuf commits déclarent Opus 4.5 et un Haiku 4.5 ; le rôle exact phrase par phrase demeure inconnu.
6. `EXAMPLES.md` est ajouté par un contributeur via [#7](https://github.com/multica-ai/andrej-karpathy-skills/pull/7). Traduction, support Cursor, packaging et nombreuses adaptations viennent d'autres contributeurs. Le branding final résulte donc d'une chaîne Karpathy → sélection/interprétation des mainteneurs → co-rédaction LLM déclarée → contributions communautaires.

Ce qui peut être attribué directement à Karpathy est l'observation générale de certains échecs de coding agents et l'idée d'exploiter des conditions de réussite déclaratives. Les noms des principes, les injonctions détaillées, le test du « senior engineer », les tables, exemples et packages appartiennent au repository et à ses contributeurs. Rien ne démontre une participation ou une approbation de Karpathy au projet. Sa notoriété n'est pas une preuve d'efficacité.

Le repository est aujourd'hui sous `multica-ai`; les chemins historiques et le snapshot nomment encore `forrestchang`, avec redirection. La PR [#189](https://github.com/multica-ai/andrej-karpathy-skills/pull/189) propose la correction et la PR [#162](https://github.com/multica-ai/andrej-karpathy-skills/pull/162) mentionne le transfert. La date et l'accord de transfert ne sont pas établis par `main`.

## Analyse des quatre principes

### 1. Think Before Coding

**Problème visé.** Un agent peut choisir une interprétation implicite, masquer une incohérence ou produire du code avant de connaître les contraintes qui changent réellement la solution.

**Mécanisme supposé.** Le texte demande d'expliciter les hypothèses, signaler les contradictions, présenter plusieurs interprétations et demander une clarification en cas d'incertitude. L'effet attendu est de déplacer une petite quantité de travail avant l'édition pour éviter une reprise plus coûteuse.

**Opérationnalisation saine, par interprétation.** Il ne faut pas exiger la chaîne de pensée privée ou le raisonnement interne détaillé du modèle. Le contrat utile est une synthèse externe courte : hypothèses qui influencent l'action, ambiguïtés matérielles, choix retenu, compromis significatifs et vérification envisagée. Sur une tâche évidente, cette synthèse peut être nulle ou tenir en une phrase.

**Seuil de clarification.** « If uncertain, ask » est trop absolu. Une question est justifiée lorsque plusieurs interprétations plausibles changent matériellement le résultat, le risque, le coût, une action irréversible ou l'autorité nécessaire. Si une hypothèse est réversible, peu risquée et localement vérifiable, l'agent peut avancer en la signalant seulement si elle aide l'utilisateur. La PR [#169](https://github.com/multica-ai/andrej-karpathy-skills/pull/169) illustre le deadlock possible en mode non interactif, mais son correctif n'est pas dans `main`.

**Coûts et limites.** Le mécanisme augmente les tokens visibles et peut créer de la latence, des questions rituelles ou une paralysie par analyse. Les petits modèles peuvent bénéficier d'un seuil concret, mais cumuler « hypothèses + interprétations + objections » peut aussi consommer leur fenêtre et leur attention. Les grands modèles peuvent sur-produire un plan convaincant sans améliorer l'action. Garde-fou : proportionner la préparation à l'impact de l'ambiguïté et préférer une décision vérifiable à une longue justification.

**Provenance.** Le problème des mauvaises hypothèses est directement relié à la publication actuelle ; la procédure précise, son nom et l'obligation d'énoncer viennent des mainteneurs/co-auteurs.

### 2. Simplicity First

**Problème visé.** Les agents peuvent ajouter abstractions, options, couches de compatibilité et code spéculatif sans besoin démontré.

**Mécanisme supposé.** Limiter le code au minimum nécessaire, refuser les fonctionnalités non demandées et reconsidérer une solution qui paraît gonflée. Le bénéfice attendu est un diff plus lisible, moins de surface de panne et moins de dette accidentelle.

**Ambiguïtés.** Le nombre de lignes n'est qu'un signal : une version plus courte peut être plus opaque, dupliquer une invariant ou déplacer la complexité vers l'exploitation. Une abstraction utilisée une seule fois peut porter une frontière de sécurité, un contrat ou un point de test utile. La bonne distinction est entre complexité essentielle — imposée par le domaine, la compatibilité, la sécurité ou la maintenance — et complexité accidentelle ou spéculative.

**Risque central.** « No error handling for impossible scenarios » est dangereux si l'impossibilité est seulement supposée par le modèle. Un invariant doit être établi par type, validation, frontière de confiance ou preuve locale ; aux frontières réseau, fichier, utilisateur et processus, les échecs ne sont généralement pas impossibles. Une application absolue peut sous-ingénier, déplacer la dette, ignorer observabilité et récupération, ou supprimer une abstraction structurante.

**Garde-fou.** Chercher la solution correcte la plus simple compatible avec les contraintes établies, non la solution ayant le moins de lignes. Demander à chaque élément supplémentaire quel risque ou exigence concret il couvre ; conserver ce qui protège une propriété nécessaire. Petits modèles : une checklist courte et des contraintes explicites sont préférables à « be simple », notion subjective. Grands modèles : éviter le réflexe de produire une architecture générale.

**Provenance.** La critique de l'overengineering et du code gonflé vient directement du thème de Karpathy ; les interdits précis et le test du senior engineer sont des ajouts du dépôt.

### 3. Surgical Changes

**Problème visé.** Une correction locale peut devenir refactor opportuniste, reformatage massif ou nettoyage de code utilisateur, augmentant bruit, risque et conflits.

**Mécanisme supposé.** Modifier seulement ce que la demande exige, préserver le style existant, signaler plutôt que réparer l'adjacent et retirer uniquement les artefacts rendus orphelins par son propre changement. Le test « chaque ligne modifiée remonte à la demande » est un bon audit de responsabilité.

**Limite causale.** « Remonter à la demande » doit signifier appartenir à une chaîne causale nécessaire, pas apparaître dans le fichier initialement nommé. Une migration peut exiger schéma, données, types, appels et documentation ; un changement de dépendance peut produire un lockfile ; un générateur peut modifier plusieurs fichiers ; une API transversale peut requérir tous ses consommateurs. Un problème adjacent doit être corrigé s'il empêche la correction demandée, sa vérification ou la sécurité du résultat. Le lien causal et l'expansion de périmètre doivent alors être expliqués.

**Conservation.** Le principe est particulièrement utile dans un worktree sale : identifier les changements préexistants, ne pas les écraser et différencier son diff. Il ne dispense pas de nettoyer les orphelins créés par son propre changement. Sur-application : contournements locaux, duplication et incohérence parce que le vrai correctif est transversal.

**Garde-fou.** Périmètre causal nécessaire, plus un budget explicite pour les artefacts générés et prérequis. Si l'adjacent est utile mais non nécessaire, le rapporter séparément. Cette règle est observable par le diff et convient aux petits modèles si le chemin causal est court ; une refonte multi-fichiers exige une carte d'impact plus explicite.

**Provenance.** Le thème des changements minimaux est lié à la source ; les règles sur style, dead code et traçabilité ligne par ligne sont des opérationnalisations du dépôt.

### 4. Goal-Driven Execution

**Problème visé.** Une instruction de moyen (« ajoute une validation ») permet à l'agent de terminer l'action syntaxique sans prouver l'effet recherché.

**Transformation.** Le dépôt propose de reformuler l'impératif en objectif observable : définir le succès, agir, mesurer, corriger et boucler. Cela améliore l'autonomie lorsque l'objectif est stable, la mesure représentative, l'action réversible et le coût de boucle borné. Exemple abstrait : « change X » devient « obtenir la propriété Y, vérifiée par Z, sans dégrader W ».

**La preuve n'est pas toujours un test.** Un test unitaire peut passer alors que le build échoue ; un build peut passer alors que le scénario utilisateur est cassé ; les deux peuvent passer avec une mauvaise configuration de production. La vérification doit viser la propriété : scénario utilisateur, reproduction de bug, typecheck, build, schéma, rendu, diff, lien, source primaire, invariants ou absence de mutation selon la tâche. Pour documentation : liens, structure, claims sourcés et diff. Pour configuration : parse/schema et comportement de chargement documenté. Pour recherche : couverture des sources et classification des inconnues. Pour diagnostic : reproduction et preuves causales, sans mutation si aucune correction n'est demandée.

**Risques.** Une métrique proxy peut être optimisée au détriment du besoin réel ; un agent peut sur-tester, multiplier les outils, altérer les tests pour les faire passer, ou boucler sans fin sur une vérification inaccessible. Les tâches triviales peuvent coûter plus cher que le risque évité. Les critères doivent être indépendants de l'implémentation autant que possible, mais pas au point d'exiger une infrastructure absente.

**Arrêt.** Arrêter lorsque les critères proportionnés sont satisfaits ; lorsqu'un rendement décroissant ou un budget explicite l'impose ; lorsque l'autorité nécessaire manque ; ou lorsque la preuve est techniquement inaccessible après des alternatives raisonnables. Dans ces derniers cas, déclarer exactement ce qui a été et n'a pas été vérifié, sans faux achèvement. Ne jamais modifier le test d'acceptation uniquement pour valider sa propre solution sauf si sa correction est elle-même démontrée.

**Provenance.** La source actuelle relie explicitement tests, navigateur, optimisation sous correction et transformation impératif→déclaratif. Le label `Goal-Driven Execution`, les tableaux et la mini-boucle sont une synthèse du dépôt.

## Interactions et contradictions

| Interaction | Gain possible | Échec possible | Garde-fou proposé pour test futur |
|---|---|---|---|
| Penser avant d'agir × tokens | Moins de reprises | Préambule et questions rituels | Seuil de matérialité ; résumé externe minimal |
| Simplicité × correction | Moins de surface | Fragilité et dette déplacée | Protéger complexité essentielle, invariants et frontières |
| Périmètre × transversalité | Diff lisible | Patch local incohérent | Définir le périmètre causal, pas seulement textuel |
| Objectif × outils | Moins de faux achèvements | Boucles, latence, proxy gaming | Vérification proportionnée, indépendante et bornée |
| Clarification × autonomie | Évite la mauvaise cible | Blocage en mode headless | Hypothèse réversible par défaut si risque faible |
| Simplicité × vérification | Solution petite | Batterie de tests disproportionnée | Coût de preuve aligné sur le risque |

Les quatre principes ne sont donc pas indépendants. La quatrième règle peut révéler que la solution la plus courte n'est pas correcte ; la première peut justifier une expansion causale de la troisième ; la troisième peut empêcher la quatrième de réécrire des tests sans rapport. Une boucle cohérente a besoin de priorités : correction et sécurité, demande et contraintes, causalité du diff, puis économie de mécanismes.

## Livraison aux harnesses au snapshot

Vérifications documentaires datées du 2026-07-20 : [Claude Code plugins](https://code.claude.com/docs/en/plugins), [référence plugins](https://code.claude.com/docs/en/plugins-reference), [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces), [skills Claude](https://code.claude.com/docs/en/slash-commands), [règles Cursor](https://docs.cursor.com/context/rules), [AGENTS.md Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills Codex](https://learn.chatgpt.com/docs/build-skills), [plugins Codex](https://learn.chatgpt.com/docs/build-plugins), [skills OpenCode](https://opencode.ai/docs/skills), [plugins OpenCode](https://opencode.ai/docs/plugins) et [providers OpenCode](https://opencode.ai/docs/providers).

| Surface | Installation/placement | Chargement réel | Portée |
|---|---|---|---|
| `CLAUDE.md` | Copie manuelle à la racine d'un projet | Instruction de projet découverte automatiquement par Claude Code | Always-on pour le projet selon hiérarchie Claude |
| `skills/.../SKILL.md` | Plugin au snapshot ; disposition aussi compatible avec un gestionnaire externe, non documenté dans le README courant | Métadonnées découvertes ; corps chargé lorsque la skill est sélectionnée/invoquée | On-demand, puis contexte de session |
| `.claude-plugin/plugin.json` | Plugin installé | Métadonnées et chemins de composants ; pas le comportement lui-même | Découverte/plugin |
| `.claude-plugin/marketplace.json` | Marketplace ajoutée, puis plugin installé séparément | Catalogue ; ajouter une marketplace n'installe pas le plugin | Distribution |
| `.cursor/rules/...mdc` | Repository contenant le fichier | `alwaysApply: true` demande l'inclusion systématique de la règle dans les interactions concernées | Always-on projet |
| `CURSOR.md` | Lecture humaine | Aucun effet runtime documenté | Documentation |
| `README*`, `EXAMPLES.md` | Repository/site | Aucun chemin du snapshot ne les injecte | Documentation |

Un `CLAUDE.md` situé à la racine du plugin n'est pas automatiquement une instruction de plugin selon la documentation Claude : le mode `CLAUDE.md` du README correspond à une copie par projet. Le plugin, lui, est présenté comme installé au niveau utilisateur et disponible dans tous les projets, mais son skill reste on-demand. Le champ `skills` du manifeste courant ajoute un chemin au scan par défaut ; comme `skills/` est déjà l'emplacement conventionnel du plugin, la PR [#136](https://github.com/multica-ai/andrej-karpathy-skills/pull/136) signale un enregistrement potentiellement dupliqué. Cela peut dupliquer les métadonnées de découverte, pas nécessairement injecter deux fois le corps.

La séquence #13→#15→#17→#18 a été nécessaire parce que le premier essai cumulait commande CLI plurielle/ancienne, propriétaire erroné, manifeste au mauvais emplacement, absence de marketplace, chemin relatif incorrect et schéma non conforme. Les commentaires de #18 indiquent que l'installation précédente échouait. #18 a finalement introduit les deux commandes interactives `/plugin marketplace add` puis `/plugin install`, cohérentes avec la documentation actuelle. La PR #41 proposait en plus la forme CLI singulière `claude plugin` mais a été fermée. Séparément, `c488bed` contenait la faute de repository `andrej-karpthy-skills`; #3 avait documenté `npx skills`, puis cette commande a disparu du README courant et #84/#98 cherchent à la réintroduire.

Cursor documente qu'une règle de projet avec `alwaysApply: true` est de type « Always » et est incluse dans le contexte. Cette livraison transforme un texte court en taxe systématique, y compris pour les tâches triviales. `CURSOR.md` est seulement une notice de copie.

## Codex, OpenCode et Qwen : statut réel

`main` n'a ni `AGENTS.md`, ni `.agents/skills`, ni `.codex-plugin`, ni `.opencode`, ni `opencode.json`. Il n'offre donc aucun support Codex ou OpenCode natif au snapshot.

La PR [#97](https://github.com/multica-ai/andrej-karpathy-skills/pull/97) est ouverte. Elle propose `AGENTS.md` pour l'instruction automatique et `.agents/skills/.../SKILL.md` pour la découverte à la demande, deux mécanismes conformes aux docs Codex actuelles dans leur principe. Mais elle ajoute 1 257 lignes dans neuf fichiers, dont plusieurs copies d'exemples et de payload : adaptateur plausible, non mince, à fort risque de drift. Les propositions plus récentes de plugin Codex ne sont pas `main` non plus.

La PR [#96](https://github.com/multica-ai/andrej-karpathy-skills/pull/96) est ouverte. Elle propose un plugin JavaScript de 160 lignes, une installation npm depuis une URL Git non épinglée sous la configuration utilisateur et l'injection intégrale de la skill dans le premier message de chaque session via `experimental.chat.messages.transform`. La documentation OpenCode actuelle décrit les plugins locaux `.opencode/plugins`, les plugins npm déclarés dans `opencode.json`, leurs événements, et la découverte native à la demande de skills dans `.opencode/skills`, `.claude/skills` ou `.agents/skills`. Elle ne documente pas ce hook expérimental. Par inférence, #96 est plus intrusif et moins démontré qu'un adaptateur `.agents/skills`; son installation de code exécutable non épinglé augmente le risque supply-chain et sa mutation du message pollue le contexte systématiquement.

OpenCode sait utiliser divers providers et modèles locaux, et sa documentation présente notamment les providers locaux et Qwen. Cela signifie que le format natif de skill pourrait être découvert dans une session OpenCode utilisant Qwen ; cela ne démontre ni que #96 fonctionne avec Qwen, ni que les quatre règles améliorent un petit modèle, ni que le même dosage est approprié.

## Licence, attribution et branding

Le snapshot ne contient aucun fichier `LICENSE`; l'API GitHub ne détecte aucune licence. `README.md` dit « MIT », le frontmatter du skill porte `license: MIT` et le manifeste plugin porte également `MIT`, mais aucun ne fournit le texte complet, les conditions ni un titulaire de copyright.

La mention README apparaît avec #2, la métadonnée skill avec #3 et le manifeste avec #13. La PR [#47](https://github.com/multica-ai/andrej-karpathy-skills/pull/47) associe son travail à `issue-46` dans son chemin de validation, mais cette issue n'est plus accessible ; #47 et #107 proposaient un texte MIT puis ont été fermées sans fusion. La PR [#156](https://github.com/multica-ai/andrej-karpathy-skills/pull/156) est ouverte et propose un titulaire tout en demandant sa confirmation. Elle ne résout rien pour le snapshot.

Faits et risques, sans avis juridique : la [documentation GitHub sur les licences](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) rappelle qu'en l'absence de licence, le droit d'auteur par défaut s'applique ; publier sur GitHub ne confère donc pas automatiquement un droit général de réutilisation. Les marqueurs MIT suggèrent une intention mais ne remplacent pas clairement un grant complet et attribué. La copie textuelle doit rester en quarantaine avant publication. Une paraphrase originale de principes comportementaux généraux est distincte d'une copie, mais doit encore éviter les expressions propres et conserver une provenance intellectuelle souhaitable. Le branding avec le nom de Karpathy augmente le risque de confusion sur l'auteur ou l'endorsement ; une formulation neutre est préférable pour toute expérimentation future.

## Projection LLM-agnostique — objets d'étude, pas adoption

| Source | Problème | Formulation neutre originale possible | Coût statique cible | Observable | Failure mode | Garde-fou | Emplacement hypothétique | Expérience requise |
|---|---|---|---:|---|---|---|---|---|
| Think Before Coding | Mauvaise interprétation | « Clarifie seulement l'ambiguïté susceptible de modifier matériellement le résultat ; sinon avance avec une hypothèse réversible et peu risquée. » | 25–35 tokens | Questions utiles, moins de reprises | Blocage ou hypothèse cachée | Matérialité, réversibilité, risque | Kernel | Tâches ambiguës/headless, score humain des questions |
| Simplicity First | Sur-construction | « Choisis la solution correcte la plus simple compatible avec la demande et les contraintes établies. » | 18–25 tokens | Moins de mécanismes spéculatifs | Sous-ingénierie | Complexité essentielle, sécurité, maintenance | Kernel | Bugs/refactors avec contraintes cachées |
| Surgical Changes | Diff hors scope | « Limite les modifications au périmètre causal nécessaire et préserve les changements préexistants. » | 18–25 tokens | Diff traçable, peu de bruit | Patch local incohérent | Exceptions migrations/génération/transversal | Kernel | Worktrees sales et changements transversaux |
| Goal-Driven Execution | Faux achèvement | « Définis une preuve observable proportionnée au risque, exécute-la, puis rapporte honnêtement ses limites. » | 22–30 tokens | Critère vérifié et limites explicites | Boucle/coût/proxy gaming | Budget, stop, indépendance du critère | Protocole de mission | Tâches avec/sans tests, docs/config/diagnostic |
| Packaging du dépôt | Livraison multi-harness | « Une source neutre, des adaptateurs minces documentant chargement et portée. » | Adaptateur variable | Pas de drift sémantique | Abstraction factice entre harnesses | Tests de parité, versionnage | Adaptateur | Matrice de versions et context capture |
| Exemples longs | Aide aux petits modèles | Module contextuel ciblé | ~3 800 tokens actuels | Meilleure exécution sur cas difficile | Pollution et imitation mécanique | Charger seulement au besoin | Module contextuel | Ablation exemples/no examples |
| Texte/branding existant | Provenance/licence | Ne pas copier | 0 | Absence de confusion | Réutilisation non autorisée | Quarantaine/revue | Rejet/quarantaine | Clarification licence et marque |

La boucle candidate « ambiguïté matérielle → simplicité correcte → périmètre causal → vérification proportionnée » restitue mieux le mécanisme que quatre slogans absolus. Elle reste cependant une hypothèse de design ; aucune insertion dans le kernel n'est décidée ici.

## Protocole expérimental différé

### Plans et corpus

Comparer au minimum : baseline sans doctrine ; doctrine complète ; quatre ablations retirant chacune un principe ; éventuellement version compacte contre texte original. Utiliser des repositories isolés et réinitialisés, des versions de harness/modèle épinglées, un ordre randomisé/intercalé, plusieurs répétitions et une évaluation tenue à l'écart du prompt.

Le corpus doit couvrir : tâches triviales ; spécifications ambiguës ; corrections de bugs ; refactors ; worktrees sales avec changements utilisateur ; tâches sans tests ; modifications transversales ; documentation ; configuration ; diagnostic sans autorisation de corriger. Exécuter séparément Codex, Claude Code et OpenCode avec Qwen ou un autre modèle local, plus au moins un grand modèle comparable. Ne pas fusionner les résultats entre harnesses ou tailles de modèle sans interaction statistique examinée.

### Critères et instrumentation

- Réussite fonctionnelle évaluée par tests cachés ou scénario utilisateur indépendant.
- Changements hors scope, bruit du diff, conservation du travail utilisateur et complexité ajoutée, évalués aveuglément.
- Nombre, timing et utilité des clarifications ; hypothèses incorrectes non clarifiées.
- Reprises, appels d'outils, tokens d'entrée/sortie, latence et coût de vérification.
- Faux achèvements, tests modifiés abusivement, boucles sans progrès et interventions humaines.
- Pour docs/recherche/config, rubriques spécifiques de traçabilité, exactitude, parse/chargement et inconnues honnêtes.

Capturer séparément tokens statiques injectés, tokens dynamiques générés et effets indirects sur le diff. Pré-enregistrer les hypothèses : la doctrine complète devrait réduire hors-scope et faux achèvements mais peut augmenter tokens/latence sur les tâches triviales ; l'ablation de clarification devrait augmenter certaines reprises ; l'ablation de simplicité peut augmenter la complexité ; l'ablation de scope le bruit ; l'ablation de vérification les faux achèvements. Ces propositions sont des hypothèses, pas des résultats observés.

### Conditions d'interprétation

Une amélioration de découvrabilité n'implique pas une amélioration d'exécution. Un test qui passe n'implique pas la réussite utilisateur. Une économie de complétion n'implique pas une économie totale si le prompt, les outils ou la latence augmentent. Une étude sur trois prompts sans fichiers ni outils ne permet pas de conclure pour un agent de terminal. Toute décision future devrait exiger effets par catégorie, intervalles d'incertitude, artefacts reproductibles et analyse des régressions.
