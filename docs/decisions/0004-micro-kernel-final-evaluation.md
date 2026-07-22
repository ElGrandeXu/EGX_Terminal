# 0004 — Évaluation finale du micro-kernel

- **Status:** rejected
- **Date:** 2026-07-21
- **Behavioral activation:** none
- **Final classification:** `REJECT_MICRO`

> **Avis sur la preuve runtime :** la
> [décision 0014](0014-micro-kernel-evidence-erratum.md) gouverne la lecture des
> affirmations runtime associées à cette décision. Elle documente l'absence des
> données runtime sources et de l'agrégat original sans modifier le verdict
> terminal **`REJECT_MICRO`**.

## Contexte et portée

La [décision 0003](0003-balanced-kernel-rejection.md) a rejeté le kernel
équilibré et autorisé un candidat micro distinct, expérimental et inactif. Le
[protocole final pré-enregistré](../../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md)
a gelé cinq paires, dix cellules, les critères, les budgets et une règle binaire
sans verdict intermédiaire.

La présente décision porte uniquement sur le payload exact de 474 octets
identifié par le SHA-256
`e4e23477afceaa290bdfa040a9087ca53fde9a3bd390499671fd46032b56d6b5`.

## Affirmations historiques publiées

Le [rapport final historique](../../experiments/kernel-micro-v1/behavioral/final-v1/results.md)
publie les affirmations suivantes :

- les dix cellules sont publiées comme valides ;
- les scores publiés donnent à la baseline et au micro 5/5 en réussite
  fonctionnelle et 4/5 au primaire ;
- les cinq paires sont publiées comme des égalités, avec zéro primary win de
  chaque côté ;
- le rapport ne publie aucune régression micro de scope, préservation ou
  sécurité ;
- chaque cellule est publiée comme exécutant une validation pertinente ;
- les deux bras sont publiés avec zéro faux achèvement ;
- les mesures de tokens publiées sont de 229 923 pour la baseline et de 247 972
  pour le micro ;
- l'overhead publié est **7,850019354305572 %**, au-dessus du plafond obligatoire
  de 5 % ;
- les latences agrégées publiées sont de 623,718 s pour la baseline et de
  654,750 s pour le micro ;
- deux incidents purement infrastructurels sont rapportés comme résolus avant
  toute cellule, puis les dix observations comme consommées sans retry
  comportemental.

La cohérence arithmétique interne des nombres publiés reste contrôlable.
Toutefois, les données runtime sources et l'agrégat original sont absents : les
cellules, scores, mesures et incidents ci-dessus ne sont donc plus
indépendamment vérifiables à partir du record conservé.

## Interprétation limitée

Selon les affirmations historiques publiées pour les conditions gelées, le
micro-kernel n'améliore aucun critère primaire et n'entraîne aucune régression
fonctionnelle, de scope, de préservation ou de sécurité. Les valeurs publiées de
tokens, arithmétiquement cohérentes entre elles, placent sa taxe au-dessus du
budget d'acceptation pré-enregistré. La règle ne permet aucune exception
qualitative : la classification mécanique est **`REJECT_MICRO`**.

Cette décision ne conclut pas que les principes reformulés par le payload sont
généralement nuisibles. Elle classe ce payload exact comme politique projet
always-on inacceptable pour la V1 selon la règle et le seuil convenus.

## Décision

1. Le micro-kernel reçoit définitivement le statut **rejected** comme doctrine
   always-on et la classification **`REJECT_MICRO`**.
2. Aucune troisième variante ni nouvelle campagne doctrinale n'est autorisée
   dans la V1.
3. Aucun kernel comportemental n'est promu, distribué ou activé à la racine.
4. La V1 poursuit avec une racine neutre. Les principes restent accessibles
   dans la documentation et les protocoles chargés à la demande.
5. L'auditabilité directe se limite au payload, au protocole et à sa règle de
   décision, aux fixtures, aux graders, au manifeste et aux hashes consignés des
   artefacts conservés. Les affirmations runtime demeurent dans le rapport
   historique sans leurs données sources ni l'agrégat original.

## Conséquences

- `AGENTS.md` et `CLAUDE.md` racine restent inchangés ;
- `doctrine/KERNEL.md`, `.egx/doctrine-lock.json` et `opencode.json` restent
  absents ;
- aucune promotion architecturale ni synchronisation d'adaptateurs n'est lancée ;
- la prochaine mission est directement la préparation du workspace public,
  sans autre benchmark doctrinal.

## Déclencheurs de révision

Le verdict comportemental est terminal pour la V1. Seule une erreur factuelle
ou d'intégrité démontrée dans le record pourrait justifier un record correctif ;
elle n'autoriserait ni une nouvelle campagne, ni une variante supplémentaire,
ni l'activation du payload rejeté.
