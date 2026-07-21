# 0003 — Rejet du kernel équilibré

- **Status:** rejected
- **Date:** 2026-07-21
- **Behavioral activation:** none
- **Final classification:** `REJECTED_AS_BALANCED`

## Contexte et portée

La [décision 0002](0002-llm-agnostic-kernel-architecture.md) a autorisé le
payload exact de [`experiments/kernel-v1/KERNEL.md`](../../experiments/kernel-v1/KERNEL.md)
comme traitement expérimental, inactif et non promu. Le
[pilote comportemental](../../experiments/kernel-v1/behavioral/pilot-v1/results.md)
a ensuite produit un résultat nul sur quatre cellules. Le
[challenge décisif](../../experiments/kernel-v1/behavioral/challenge-v1/results.md),
pré-enregistré avant inférence, devait donc trancher le statut de ce traitement
équilibré.

La présente décision porte sur ce payload always-on précis, identifié par le
SHA-256
`a70b983003abcb59bcb53b3dba5637c6105d85fe3fc47fa5546d668b5d4d1431`.
Elle ne rejette ni les principes généraux issus des cinq audits, ni les six
couches et frontières acceptées par la décision 0002.

## Résultats observés

Les faits suivants proviennent des cinq paires complètes et des six observations
kernel du challenge :

- le kernel obtient **0 victoire primaire** ;
- la baseline obtient **2 victoires primaires** ;
- les cinq paires complètes totalisent 194 185 tokens baseline contre 231 403
  tokens kernel, soit **+19,166 %** pour le kernel ;
- leur latence OpenCode totalise 491,048 s contre 546,969 s, soit **+11,388 %**
  pour le kernel ;
- le kernel produit **2 faux achèvements sur 6 observations** ;
- sur `proportional-verification`, il exécute le check ciblé puis la suite
  complète, contrairement au critère gelé de vérification proportionnée, et
  revendique néanmoins la vérification ;
- sur `transversal-completeness`, il complète les quatre artefacts causaux mais
  modifie aussi inutilement le test visible `tests/test_states.py`, échoue aux
  critères fonctionnel et de scope, puis revendique la réussite ;
- la baseline gagne donc la vérification proportionnée ainsi que la complétude
  transversale avec préservation du scope et sans faux achèvement.

La cellule `reuse-baseline` a été perdue après scoring et n'a pas été rejouée.
Par conséquent, l'overhead décisionnel sur six paires et la comparaison globale
des faux achèvements restent indisponibles. Les pourcentages ci-dessus sont des
agrégats descriptifs sur les cinq paires complètes, pas une reconstruction de la
paire manquante.

## Interprétations limitées

Dans la campagne décisive et ses conditions gelées, le payload équilibré
n'apporte aucun gain primaire observé et coïncide avec deux régressions
primaires, une taxe descriptive en tokens et latence, et deux faux achèvements.
Le baseline win fonctionnel transversal satisfait à lui seul le seuil de rejet
pré-enregistré. Le classement mécanique final est donc
**`REJECTED_AS_BALANCED`**.

Ces observations justifient le retrait de ce traitement always-on. Elles ne
démontrent pas que chaque principe qu'il reformule est nuisible, ni qu'un autre
assemblage plus court améliorerait le comportement.

## Inconnues

- La cellule `reuse-baseline` et l'overhead exact sur les six paires sont
  irrécupérables.
- Une observation par cellule ne mesure pas la variance.
- La généralisation à d'autres modèles, harnesses, machines ou tâches n'est pas
  établie.
- L'effet comportemental d'un candidat micro distinct est inconnu tant qu'une
  évaluation séparée n'a pas été pré-enregistrée puis exécutée.

## Décision

1. Le kernel équilibré reçoit définitivement le statut **rejected** et le
   classement **`REJECTED_AS_BALANCED`**.
2. Ce payload ne doit plus être retesté, corrigé, révisé, distribué comme
   candidat actif ou promu. Toute expérimentation future doit employer un
   traitement substantiellement distinct et une décision séparée.
3. Le répertoire [`experiments/kernel-v1/`](../../experiments/kernel-v1/) est
   conservé intégralement comme **archive expérimentale historique immuable**.
   Aucun de ses artefacts ne doit être modifié pour refléter cette décision
   postérieure.
4. Le candidat [`kernel-micro-v1`](../../experiments/kernel-micro-v1/README.md)
   est autorisé uniquement comme traitement statique expérimental, inactif et
   non validé comportementalement. Cette décision ne le promeut pas, ne
   l'installe pas et ne pré-enregistre pas sa campagne.
5. Aucun kernel n'est promu en doctrine. La racine active et ses points d'entrée
   restent inchangés.

## Conséquences

- Les preuves négatives et incidents restent auditables sans réécriture de
  l'expérience.
- Le payload micro est mesurable et révisable indépendamment du candidat rejeté.
- Aucune économie contextuelle ni amélioration comportementale du micro n'est
  tenue pour démontrée.
- La prochaine mission peut pré-enregistrer une évaluation micro distincte ;
  elle ne doit pas rouvrir le traitement équilibré.

## Déclencheurs de révision

Le verdict comportemental du payload équilibré est terminal. Seule la découverte
d'une erreur factuelle ou d'intégrité dans le présent record justifierait un
nouveau record correctif. Elle n'autoriserait pas la modification de l'archive
ni une nouvelle exécution du payload rejeté.
