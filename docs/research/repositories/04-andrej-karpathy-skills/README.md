# Audit 04 — andrej-karpathy-skills

## Identité et portée

- Repository observé : <https://github.com/multica-ai/andrej-karpathy-skills>
- Branche et snapshot : `main` à `2c606141936f1eeef17fa3043a72095b4765b9c2`
- Date de référence et de vérification : 2026-07-20
- Clone d'inspection : `%TEMP%/EGX_Terminal-audits/andrej-karpathy-skills-2c606141`
- Méthode : analyse statique et en lecture seule du snapshot, des 30 commits accessibles, des 5 branches, des 147 pull requests, des surfaces GitHub accessibles et des documentations officielles des harnesses. Aucun contenu n'a été installé ou exécuté.

Cet audit étudie le dépôt comme proposition comportementale pour agent de code. Il ne constitue ni une adoption, ni une modification de la doctrine d'EGX_Terminal, ni une validation de son branding.

## Résumé exécutif

Le mécanisme utile est un petit ensemble d'instructions qui tente de corriger quatre échecs fréquents : agir sur une compréhension incertaine, sur-construire, modifier hors périmètre et annoncer trop tôt la fin. Le snapshot distribue ces instructions par copies adaptées à Claude Code et Cursor. Il n'apporte ni moteur, ni enforcement, ni protocole expérimental intégré.

L'hypothèse « désambiguïser → simplifier → limiter le périmètre → vérifier » est une compression fidèle de la direction générale, mais pas une doctrine suffisante. Elle perd la mise en évidence des compromis et contradictions, confond facilement simplicité et brièveté, rend mal les changements transversaux causalement nécessaires et ne fixe ni vérification proportionnée ni condition d'arrêt. Une variante conceptuelle plus robuste devrait qualifier chaque étape par la matérialité, la correction, la causalité et le risque. Cette conclusion reste une hypothèse à tester.

Le dépôt n'établit pas que les quatre règles améliorent des sessions réelles. Le README propose des signes à observer, pas des résultats. La PR [#25](https://github.com/multica-ai/andrej-karpathy-skills/pull/25) mesure seulement un score de découvrabilité non reproductible à partir des artefacts fournis. La PR [#186](https://github.com/multica-ai/andrej-karpathy-skills/pull/186), ouverte et absente du snapshot, apporte des micro-évaluations étroites : elle ne permet pas d'attribuer un effet général au texte de `main`.

## Mécanisme réel

1. `CLAUDE.md`, `SKILL.md` et la règle Cursor contiennent trois copies proches des quatre principes ; il n'existe pas de génération ni de source canonique déclarée.
2. Le `CLAUDE.md` est une instruction de projet lorsqu'il est copié dans un projet. Le skill Claude est découvert par métadonnées puis chargé à la demande ; le manifeste et la marketplace organisent sa découverte et son installation, sans être eux-mêmes le payload comportemental.
3. La règle Cursor porte `alwaysApply: true` et devient donc un payload systématique dans les conversations concernées par le projet.
4. `EXAMPLES.md`, les README et leur traduction documentent le projet mais rien dans le snapshot ne démontre leur chargement runtime.
5. Aucun test, benchmark, hook ou contrôle automatique n'est présent sur `main` : l'application dépend de l'interprétation du modèle et du harness.

## Conclusion principale

Le dépôt contient une boucle comportementale générale, intelligible et relativement compacte, mais pas encore assez précise ni assez étayée pour devenir telle quelle un kernel LLM-agnostique. Son apport potentiel est un ordre de contrôle : réduire l'incertitude matérielle, choisir la solution correcte la moins complexe, borner le diff au périmètre causal, puis obtenir une preuve proportionnée avant de conclure. Son apport ne dépend pas de Claude ni de Karpathy ; son packaging, ses formulations absolues, ses duplications et son absence d'évaluation, eux, ne doivent pas être confondus avec ce noyau conceptuel.

## Candidats conceptuels à évaluer plus tard

| Candidat, sans adoption | Comportement observable visé | Destination hypothétique | Réserve principale |
|---|---|---|---|
| Ne demander une clarification que si l'ambiguïté peut changer matériellement le résultat ; sinon avancer avec une hypothèse réversible et peu risquée | Moins de blocages et moins de reprises dues à une mauvaise interprétation | Kernel ou protocole de mission | Le seuil de matérialité doit être testé |
| Choisir la solution correcte la plus simple compatible avec les contraintes connues | Moins de code spéculatif et de complexité accidentelle | Kernel | « Simple » ne doit pas signifier « moins de lignes » |
| Limiter les modifications au périmètre causal nécessaire | Diff explicable, conservation du travail utilisateur, peu de refactors opportunistes | Kernel | Autoriser migrations, lockfiles, génération et prérequis transversaux |
| Définir une preuve observable et proportionnée au risque, puis arrêter lorsque le critère est satisfait ou honnêtement invérifiable | Moins de faux achèvements | Protocole de mission | Coût d'outils, proxy trompeur, boucles sans fin |
| Livrer un noyau neutre par adaptateurs minces propres à chaque harness | Portabilité sans dupliquer la doctrine | Adaptateur | Les mécanismes de chargement diffèrent réellement |

Le détail des formulations neutres, coûts, failure modes, garde-fous et expériences figure dans [behavior-and-delivery.md](behavior-and-delivery.md).

## Rejets et quarantaines

- Ne pas importer textuellement le contenu : le snapshot n'a pas de texte de licence racine complet et le titulaire du copyright n'est pas identifié.
- Ne pas reprendre le branding « Andrej Karpathy Skills » : il dépasse la provenance démontrée et peut suggérer une paternité ou une approbation inexistante.
- Ne pas exiger l'exposition d'une chaîne de pensée privée. Seule une synthèse concise des hypothèses, ambiguïtés, décisions, compromis et vérifications utiles est souhaitable.
- Ne pas transformer « demander si incertain », « pas de gestion des scénarios impossibles » ou « chaque ligne remonte à la demande » en absolus.
- Ne pas adopter les hooks, benchmarks, adaptateurs Codex/OpenCode ou principes additionnels des PR ouvertes comme s'ils appartenaient à `main`.
- Ne pas traiter les indicateurs du README, les étoiles, forks ou témoignages comme preuve comportementale.

## Inconnues principales

- Le texte intégral de la publication X actuelle n'a pas pu être vérifié de façon fiable depuis la source primaire : X expose l'auteur, la date et le début via oEmbed, mais pas l'intégralité sans une surface accessible stable.
- Les citations du README peuvent être comparées à des copies indexées, mais leur exactitude complète demeure partiellement inconnue ; plusieurs sont manifestement condensées ou composites.
- Le moment exact et les conditions du transfert de `forrestchang` vers `multica-ai` ne sont pas documentés dans le snapshot.
- Les issues référencées par des PR historiques ne sont plus accessibles ; le repository expose actuellement 0 issue et désactive les issues.
- Le comportement exact varie avec les versions et politiques de Claude Code, Cursor, Codex et OpenCode ; la vérification présentée est datée du 2026-07-20.
- Aucun résultat de session complète ne permet de conclure à une économie nette de tokens, de latence ou de coût.

## Documents de l'audit

- [repository-map.md](repository-map.md) — inventaire, histoire, branches, PR et duplications.
- [behavior-and-delivery.md](behavior-and-delivery.md) — provenance, sémantique, harnesses, projection et protocole différé.
- [token-economics.md](token-economics.md) — mesures statiques et coûts dynamiques.
- [evidence-ledger.md](evidence-ledger.md) — registre claim par claim, sources et niveau de preuve.
