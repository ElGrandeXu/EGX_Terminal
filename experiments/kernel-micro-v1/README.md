# Kernel micro v1

## Statut

Ce répertoire contient un candidat statique **expérimental, inactif et non
validé comportementalement**. Son payload autoritatif est [`KERNEL.md`](KERNEL.md).
Il n'est ni une doctrine promue, ni un remplacement actif du
[kernel équilibré rejeté](../../docs/decisions/0003-balanced-kernel-rejection.md),
ni le début d'une campagne comportementale.

## Mesures mécaniques

Les valeurs suivantes sont calculées sur les octets exacts de `KERNEL.md`, en
UTF-8 sans BOM, avec LF et sans fin de ligne finale.

| Mesure | Valeur |
| --- | ---: |
| Octets UTF-8 | 474 |
| Caractères | 474 |
| Mots séparés par `\s+` | 66 |
| Estimation `ceil(caractères / 4)` | 119 |
| SHA-256 | `e4e23477afceaa290bdfa040a9087ca53fde9a3bd390499671fd46032b56d6b5` |

## Justification bornée

Cette variante conserve le résultat demandé, les contraintes pertinentes, le
travail existant à préserver, la réutilisation, la cohérence transversale et la
vérification. Elle remplace la notion de « causal scope » par « smallest
coherent change » et mentionne explicitement les consommateurs affectés afin de
ne pas confondre petit diff et changement incomplet.

Elle retire du payload always-on les règles de persistance, d'arrêt, de budget
et de communication, ainsi que les inventaires de qualités à préserver. Elle
interdit explicitement de revendiquer une réussite au-delà des preuves.

L'objectif expérimental est une taxe always-on nettement inférieure à celle du
kernel équilibré rejeté. Aucune économie effective ni amélioration
comportementale n'est démontrée par cette définition statique.

## Frontières

- aucune activation ou distribution par adaptateur ;
- aucune modification des points d'entrée racine ;
- aucun protocole comportemental dans ce répertoire ;
- aucune revendication de promotion ou de validation.
