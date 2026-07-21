# 0004 — Évaluation finale du micro-kernel

- **Status:** rejected
- **Date:** 2026-07-21
- **Behavioral activation:** none
- **Final classification:** `REJECT_MICRO`

## Contexte et portée

La [décision 0003](0003-balanced-kernel-rejection.md) a rejeté le kernel
équilibré et autorisé un candidat micro distinct, expérimental et inactif. Le
[protocole final pré-enregistré](../../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md)
a gelé cinq paires, dix cellules, les critères, les budgets et une règle binaire
sans verdict intermédiaire.

La présente décision porte uniquement sur le payload exact de 474 octets
identifié par le SHA-256
`e4e23477afceaa290bdfa040a9087ca53fde9a3bd390499671fd46032b56d6b5`.

## Éléments de preuve observés

Le [rapport final](../../experiments/kernel-micro-v1/behavioral/final-v1/results.md)
établit les faits suivants :

- les dix cellules sont valides ;
- baseline et micro réussissent fonctionnellement 5/5 et au primaire 4/5 ;
- les cinq paires sont des égalités, avec zéro primary win de chaque côté ;
- aucune régression micro de scope, préservation ou sécurité n'est observée ;
- chaque cellule exécute une validation pertinente ;
- les deux bras produisent zéro faux achèvement ;
- la baseline consomme 229 923 tokens et le micro 247 972 ;
- l'overhead exact est **7,850019354305572 %**, au-dessus du plafond obligatoire
  de 5 % ;
- la latence agrégée est 623,718 s baseline contre 654,750 s micro ;
- deux incidents purement infrastructurels ont été résolus avant toute cellule,
  puis les dix observations ont été consommées sans retry comportemental.

## Interprétation limitée

Dans les conditions gelées, le micro-kernel n'améliore aucun critère primaire et
n'entraîne aucune régression fonctionnelle, de scope, de préservation ou de
sécurité. Sa taxe token dépasse toutefois le budget d'acceptation pré-enregistré.
La règle ne permet aucune exception qualitative : la classification mécanique
est **`REJECT_MICRO`**.

Ce résultat ne démontre pas que les principes reformulés par le payload sont
généralement nuisibles. Il démontre que ce payload exact ne peut pas être une
politique projet always-on acceptable pour la V1 selon le seuil convenu.

## Décision

1. Le micro-kernel reçoit définitivement le statut **rejected** comme doctrine
   always-on et la classification **`REJECT_MICRO`**.
2. Aucune troisième variante ni nouvelle campagne doctrinale n'est autorisée
   dans la V1.
3. Aucun kernel comportemental n'est promu, distribué ou activé à la racine.
4. La V1 poursuit avec une racine neutre. Les principes restent accessibles
   dans la documentation et les protocoles chargés à la demande.
5. Le payload, le protocole, les fixtures, les graders et les preuves historiques
   restent auditables ; le correctif d'identité Ollama et ses anciens et nouveaux
   hashes sont consignés dans le rapport final.

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
