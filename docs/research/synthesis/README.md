# Synthèse contradictoire des cinq audits

## Statut et portée

Cette synthèse confronte les cinq audits terminés au 20 juillet 2026. Elle
prépare une décision : elle ne promeut aucune doctrine, n'installe aucune
capacité et n'implémente aucune architecture. Les propositions ci-dessous sont
donc des verdicts de recherche, non des comportements actifs.

Sources auditées :

- [Caveman](../repositories/01-caveman/README.md), commit
  `0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0` ;
- [i-have-adhd](../repositories/02-i-have-adhd/README.md), commit
  `72c33eee81ea439cf01991e93729adfce2ffc99e` ;
- [Ponytail](../repositories/03-ponytail/README.md), commit
  `16f29800fd2681bdf24f3eb4ccffe38be3baec6b` ;
- [andrej-karpathy-skills](../repositories/04-andrej-karpathy-skills/README.md),
  commit `2c606141936f1eeef17fa3043a72095b4765b9c2` ;
- [TencentDB Agent Memory](../repositories/05-tencentdb-agent-memory/README.md),
  commit `45e6e80ae2e63b65fad0d89f5e13171229c8f295`.

## Résumé exécutif

Les cinq dépôts ne décrivent pas un système à réunir. Ils exposent quatre
problèmes différents : densité de réponse, friction d'action, choix de solution
et maîtrise du diff, continuité et mémoire. Leur intersection utile est plus
petite que chacune de leurs doctrines : comprendre les conséquences avant
d'agir, ne demander que les clarifications qui changent matériellement la
décision, réutiliser avant d'ajouter, viser le minimum **correct**, borner le
changement par sa causalité, définir une réussite observable et calibrer
communication et vérification au risque.

Cette réduction reste hypothétique. La meilleure preuve comportementale est le
signal `native-first` de Ponytail sur douze tâches Haiku choisies, avec données
brutes et complétude manquantes ; Caveman montre une réduction de sortie sur de
petits jeux Claude, sans établir la correction ni le gain de session ; les deux
petits dépôts de règles n'ont pas d'évaluation pertinente sur `main` ; TencentDB
démontre une architecture et des risques, pas ses claims de benchmark
([Ponytail E40–E48](../repositories/03-ponytail/evidence-ledger.md#ledger),
[Caveman E019–E034](../repositories/01-caveman/evidence-ledger.md#e019),
[i-have-adhd E16](../repositories/02-i-have-adhd/evidence-ledger.md),
[andrej-karpathy-skills — efficacité](../repositories/04-andrej-karpathy-skills/evidence-ledger.md#comportement-et-efficacité),
[TencentDB E-BENCH](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-BENCH)).

La recommandation principale est d'expérimenter le **kernel équilibré** de
[doctrine-candidates.md](doctrine-candidates.md), estimé à environ 200–300
tokens, face à la baseline, au micro-kernel et au kernel explicite. Il est assez
court pour rester toujours chargé, mais porte les garde-fous qui empêchent
densité artificielle, sous-ingénierie, scope minimaliste et boucle sans fin. Il
ne doit pas être installé avant la campagne décrite dans
[validation-plan.md](validation-plan.md).

## Conclusions transversales

### Convergences utiles

1. **Réduire la friction, pas l'information.** Caveman et i-have-adhd convergent
   sur la suppression du remplissage ; leurs propres exceptions montrent que
   sécurité, preuve, contrainte et transfert final ne sont pas du remplissage
   ([Caveman E005–E007](../repositories/01-caveman/evidence-ledger.md#e005),
   [i-have-adhd E36–E38](../repositories/02-i-have-adhd/evidence-ledger.md)).
2. **Le minimum est qualifié par la correction.** Ponytail et les quatre règles
   attribuées au dépôt Karpathy convergent sur réutilisation, simplicité et
   scope ; les contre-exemples imposent de préserver la complexité essentielle
   et les changements transversalement nécessaires
   ([Ponytail E07–E09](../repositories/03-ponytail/evidence-ledger.md#ledger),
   [analyse Simplicity/Surgical](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#2-simplicity-first)).
3. **La fin doit être observable.** Goal-driven execution, le reporting de
   résultat vérifié et les artefacts de reprise pointent vers un critère de
   réussite visible plutôt que vers une simple action effectuée
   ([andrej-karpathy-skills — Goal-Driven](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#4-goal-driven-execution),
   [i-have-adhd E37](../repositories/02-i-have-adhd/evidence-ledger.md)).
4. **Le détail doit être chargé selon le besoin.** Les skills à la demande, le
   petit payload Caveman et les couches de preuve TencentDB soutiennent la
   progressive disclosure ; ils montrent aussi qu'une description trop large ou
   un auto-recall sans budget annule ce bénéfice
   ([Caveman E016–E018](../repositories/01-caveman/evidence-ledger.md#e016),
   [i-have-adhd E19–E29](../repositories/02-i-have-adhd/evidence-ledger.md),
   [TencentDB E-BUDGET](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-BUDGET)).
5. **La neutralité est sémantique, la livraison est adaptée.** Chaque dépôt
   multi-harness accumule des chemins spécifiques et des dérives. Une source
   neutre et des adaptateurs minces doivent être séparés
   ([Caveman E049/E060](../repositories/01-caveman/evidence-ledger.md#e049),
   [Ponytail E10–E14](../repositories/03-ponytail/evidence-ledger.md#ledger),
   [andrej-karpathy-skills — livraison](../repositories/04-andrej-karpathy-skills/evidence-ledger.md#livraison-et-portabilité)).

### Contradictions résolues provisoirement

- **Densité contre clarté :** supprimer répétition et cérémonie tant que les
  relations, hypothèses, risques, preuves et inconnues restent explicites. La
  grammaire télégraphique et toute persona permanente sont exclues.
- **Clarification contre autonomie :** demander seulement si plusieurs lectures
  plausibles changent matériellement résultat, risque, périmètre ou autorité ;
  sinon choisir une hypothèse réversible et vérifiable.
- **Simplicité contre correction :** optimiser le nombre de mécanismes inutiles,
  jamais le nombre de lignes. Types, frontières de confiance, migrations,
  observabilité et tests peuvent être de la complexité essentielle.
- **Scope chirurgical contre transversalité :** le bon périmètre est la chaîne
  causale nécessaire au résultat vérifié, y compris lockfile, migration,
  consommateurs, tests et documentation lorsqu'ils sont réellement causés.
- **Action immédiate contre compréhension :** exécuter immédiatement une action
  sûre, évidente et réversible ; effectuer un prévol court dès que ambiguïté,
  impact ou irréversibilité augmentent.
- **Autonomie contre boucle infinie :** poursuivre tant qu'un critère observable,
  un progrès mesurable et un budget subsistent ; arrêter sur réussite, rendement
  décroissant, autorité manquante, budget atteint ou preuve inaccessible, puis
  déclarer exactement la limite.
- **Doctrine minimale contre mémoire complexe :** le kernel peut exiger un état
  récupérable, jamais une mémoire automatique. Capture, consolidation, recall,
  correction et oubli appartiennent à un service séparé, optionnel et borné.

Le raisonnement détaillé et les contre-exemples figurent dans
[doctrine-candidates.md](doctrine-candidates.md#arbitrages-contradictoires) et
[architecture-and-boundaries.md](architecture-and-boundaries.md).

## Architecture en sept couches proposée

Chaque concept reçoit une couche principale unique ; les dépendances entre
couches ne changent pas cette propriété.

| Couche | Responsabilité | Exclusions structurantes |
| --- | --- | --- |
| 1. Kernel comportemental | Invariants courts toujours utiles | pas de workflow, persona, outil, état ni provider |
| 2. Protocole de mission | Procédure déclenchée par type/risque de tâche | pas de chargement permanent |
| 3. État récupérable | Contrat minimal de reprise d'une mission longue | pas d'historique brut ni de profil utilisateur |
| 4. Capacités optionnelles | Skill, outil, évaluateur, hook ou compresseur justifié | pas d'activation universelle implicite |
| 5. Adaptateurs | Découverte, inclusion, événements et formats du harness | aucune sémantique doctrinale propre |
| 6. Infrastructure mémoire | Capture, dérivation, recherche, provenance, correction, oubli, export | jamais injectée dans le kernel |
| 7. Rejets/quarantaines | Éléments dangereux, non licenciés, trompeurs ou prématurés | aucune promotion sans nouvelle preuve/décision |

Cette séparation évite trois confusions observées : instruction contre
enforcement, état de mission contre mémoire utilisateur, et neutralité
conceptuelle contre compatibilité de harness
([Caveman — modèle système](../repositories/01-caveman/behavior-and-delivery.md#system-model),
[TencentDB — service neutre](../repositories/05-tencentdb-agent-memory/behavior-and-delivery.md#service-neutre-et-épaisseur-minimale)).

## Décisions proposées pour la revue

Ce sont les décisions que la prochaine mission devrait accepter, modifier ou
refuser explicitement :

- retenir la taxonomie à sept couches comme cadre de décision ;
- choisir le kernel équilibré comme **traitement expérimental recommandé**, non
  comme doctrine active ;
- retenir la méta-règle de proportionnalité dans le kernel sous une formulation
  courte, puis détailler ses seuils dans les protocoles de mission ;
- définir le scope comme périmètre causal nécessaire ;
- traiter l'état récupérable comme artefact de mission portable, distinct d'une
  mémoire ;
- préférer une source canonique neutre, des adaptateurs minces et, lorsque
  l'include manque, des copies générées vérifiées ;
- exiger une fiche de promotion et un budget avant toute skill, hook, outil ou
  mémoire ;
- maintenir toute mémoire automatique en expérimentation isolée jusqu'à preuve
  de scope, provenance, oubli et valeur nette.

## Décisions différées

- formulation finale et installation éventuelle du kernel ;
- nom, chemin et format exacts de la source canonique ;
- mécanisme de génération/hash des adaptateurs ;
- support et versions minimales de Codex, Claude Code, OpenCode et Qwen ;
- création du contrat d'état récupérable et emplacement concret ;
- tout hook d'enforcement ;
- toute skill ou politique de routing ;
- tout service mémoire, backend, base, embeddings, auto-recall ou persona ;
- politique de licence et publication du repository.

## Rejets et quarantaines principaux

- Personas Caveman et Ponytail, grammaire artificielle et branding médical ou
  de célébrité : rejet du kernel ; la persona automatique L3 est en quarantaine.
- Limite fixe de cinq éléments, estimation temporelle obligatoire, recap interdit
  et prochaine action artificielle : rejet.
- Réécriture automatique de doctrine, compression sémantique par regex,
  injection invisible, postinstall qui patche un harness et installateur distant
  mutable : rejet ou quarantaine selon la surface.
- Texte d'andrej-karpathy-skills : quarantaine juridique, faute de licence racine
  complète et de titulaire établi au snapshot
  ([audit licence](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#licence-attribution-et-branding)).
- Auto-recall non borné, profilage automatique, recherche sans scope et
  télémétrie intégrale : quarantaine sécurité
  ([TencentDB E-SECURITY](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-SECURITY)).
- Claims fixes de réduction, de sécurité ou de tokens : rejet comme preuve
  générale.

## Inconnues décisives

- Effet marginal de chaque règle et interaction entre règles.
- Transfert aux petits Qwen, selon taille, quantification, template et harness.
- Coût réel d'instruction, cache, reasoning, outils et reprises par session.
- Seuil optimal de clarification et calibration pratique de la proportionnalité.
- Qualité de reprise depuis un état compact dans une session et un harness neufs.
- Support fiable des includes, hooks et skills selon versions des trois harnesses.
- Fidélité, contamination inter-scope, correction et purge d'un futur service
  mémoire.
- Droits exacts sur le texte et le branding d'andrej-karpathy-skills.

## Prochaine étape recommandée

Tenir une revue utilisateur de décision sur les sept propositions ci-dessus,
figer les formulations candidates et le protocole, puis lancer une campagne
pilote reproductible sans modifier la doctrine active. La promotion ne devrait
être envisagée qu'après résultats par tâche et par harness, analyse des
régressions et validation explicite de l'architecture.
