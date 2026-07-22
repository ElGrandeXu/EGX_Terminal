# 0014 — Erratum sur les preuves du micro-kernel

- **Status:** accepted
- **Date:** 2026-07-22
- **Behavioral activation:** none
- **Final classification:** `REJECT_MICRO`

## Contexte et portée

La [décision 0004](0004-micro-kernel-final-evaluation.md) s'appuie sur le
[rapport historique](../../experiments/kernel-micro-v1/behavioral/final-v1/results.md)
de la campagne finale V1. Selon ce rapport, l'agrégat JSON original a existé,
mesurait 58 708 octets et avait le SHA-256
`3fd1de3b591a049302023a771a85d06c2729b5dbc672d5fc57f137d80d422398`.
Ses octets ne sont plus disponibles. La recherche exhaustive dans toutes les
preuves privées autorisées a couvert les fichiers privés matérialisés, les
bundles Git uniques et les archives historiques ZIP et TAR. Elle n'a retrouvé
aucune copie exacte.

Le présent erratum distingue ce qui est encore directement auditable de ce qui
n'est conservé que comme affirmation historique. Il ne modifie aucune archive
expérimentale et ne remplace pas les données manquantes.

## Faits conservés

Les éléments présents dans le repository restent directement auditables :

- le [payload exact](../../experiments/kernel-micro-v1/KERNEL.md) et les hashes
  consignés des artefacts conservés ;
- le [protocole pré-enregistré](../../experiments/kernel-micro-v1/behavioral/final-v1/protocol.md),
  son ordre, ses budgets et sa règle de décision ;
- les [fixtures](../../experiments/kernel-micro-v1/behavioral/final-v1/fixtures.py),
  les [graders](../../experiments/kernel-micro-v1/behavioral/final-v1/graders.py)
  et le [manifeste](../../experiments/kernel-micro-v1/behavioral/final-v1/manifest.json).

Cette auditabilité porte sur le contenu conservé et sur la définition de la
campagne. Elle ne démontre pas que les observations runtime publiées peuvent
être reproduites, ni que leurs données sources subsistent.

## Affirmations historiques publiées

Les résultats par cellule, les scores, les événements outils, les mesures de
tokens et de latence, ainsi que les totaux présentés dans le rapport sont des
affirmations historiques publiées. Le rapport demeure la source de ces
affirmations, mais il n'est pas un substitut à l'agrégat source absent.

Il est interdit de reconstruire un JSON à partir de `results.md`, puis de le
présenter comme l'agrégat original, comme une copie exacte ou comme une preuve
runtime récupérée. Le hash et la taille de l'agrégat absent sont eux-mêmes des
valeurs rapportées historiquement ; sans ses octets, son identité ne peut plus
être vérifiée indépendamment.

## Cohérence arithmétique

Les totaux, les deltas et l'overhead publiés peuvent encore être contrôlés pour
leur cohérence arithmétique interne à partir des nombres du rapport. Par
exemple, les totaux de 229 923 tokens pour la baseline et de 247 972 pour le
micro donnent un delta de 18 049 et un overhead de
**7,850019354305572 %**.

Ce recalcul établit seulement que les valeurs publiées sont arithmétiquement
cohérentes entre elles. Il ne vérifie ni les mesures sources, ni leur collecte,
ni leur attribution aux cellules.

## Preuve runtime irrécouvrable

En l'absence de l'agrégat original et de toute copie exacte, ne sont plus
indépendamment vérifiables :

- les cellules runtime et leurs scores sources ;
- les événements outils ;
- les mesures sources de tokens et de latence ;
- les snapshots et checkpoints qui ne sont plus présents.

Ces lacunes interdisent de qualifier les observations runtime comme entièrement
auditables ou reproductibles à partir du record conservé.

## Décision

1. `REJECT_MICRO` reste la décision de gouvernance définitive pour la V1.
2. Cet erratum ne revalide pas empiriquement le verdict. Il documente la limite
   de preuve sans modifier la classification terminale déjà adoptée.
3. Le payload rejeté reste distribué uniquement comme artefact expérimental
   historique ; il n'est ni promu ni activé comme doctrine comportementale ou
   politique always-on.
4. Aucune nouvelle campagne, reconstruction d'agrégat, troisième variante ou
   nouvelle exécution modèle n'est autorisée pour la V1.
5. Les archives sous `experiments/**` restent historiques, immuables et
   inchangées.

## Conséquences de gouvernance

- La décision 0004 conserve son effet normatif terminal, mais ses affirmations
  runtime doivent être lues comme des affirmations historiques publiées, et non
  comme des observations encore appuyées par leurs données sources complètes.
- La distinction entre faits conservés, affirmations historiques publiées,
  cohérence arithmétique et preuve runtime irrécouvrable doit être préservée
  dans toute référence future à la campagne.
- Aucun document ne doit prétendre que l'agrégat original a été récupéré ou que
  le record runtime est complet.
- Les documents courants concernés devront être qualifiés dans une mission
  ultérieure, sans modification rétroactive des archives expérimentales.

## Déclencheurs de révision

Seule la découverte d'une copie dont les octets correspondent exactement à la
taille et au SHA-256 publiés pourrait réviser l'état de disponibilité de la
preuve. Une telle découverte ne modifierait pas automatiquement le verdict,
n'autoriserait aucune nouvelle campagne et exigerait une décision séparée.
