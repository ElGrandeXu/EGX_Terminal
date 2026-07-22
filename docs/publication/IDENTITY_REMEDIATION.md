# Remédiation de l'identité des commits

## Première remédiation prépublication

Le 2026-07-21, 30 commits prépublication de `main` ont été réécrits une seule
fois afin de remplacer une identité personnelle par l'identité publique
approuvée :

```text
Maxime Erard <177521250+ElGrandeXu@users.noreply.github.com>
```

La réécriture a utilisé `git-filter-repo` 2.47.0 avec un mailmap temporaire
limité à `main`. Les trees, messages, sujets, dates, nombres de parents, diffs,
chemins et modes ont été comparés avant et après. Seuls les champs d'identité et,
par conséquence, les SHA de commits et de parents ont changé. La cartographie
exhaustive reste dans
[`governance/history-rewrite-map.json`](../../governance/history-rewrite-map.json).

## Incident de squash merge distinct

Le premier squash merge GitHub de la consolidation avait un contenu et une
topologie corrects, mais son auteur utilisait une adresse personnelle. La
politique d'identité a classé ce commit `REVIEW` immédiatement et les checks
d'historique ont échoué comme prévu. L'adresse n'est reproduite nulle part dans
le repository ou dans ce compte rendu.

Le repository affecté a été rendu privé avant toute autre mutation. Un simple
force-push n'aurait pas garanti l'exclusion de l'objet à travers les refs GitHub
de la pull request ; aucun force-push n'a donc été utilisé. Un nouveau repository
canonique privé a été créé avec uniquement l'historique propre.

Le commit fonctionnel a été reconstruit avec `git commit-tree` à l'identité
GitHub ID-based `noreply`. Son tree, parent, message complet, sujet, dates auteur
et committer, diff, chemins, modes et contenu sont identiques. L'ancien objet,
l'ancienne pull request et ses refs n'ont pas été importés.

## Preuves privées et suppression des surfaces temporaires

Les objets historiques nécessaires à l'incident ont été conservés hors
repository dans des preuves privées. Avant la suppression des deux repositories
temporaires, chacun a fait l'objet :

- d'une capture privée des métadonnées et réglages accessibles ;
- d'un clone mirror indépendant ;
- d'un bundle complet de toutes les refs accessibles ;
- de `git bundle verify` et `git fsck --full` ; et
- d'une vérification SHA-256 intégrale par manifeste.

Les captures texte et JSON masquent les adresses électroniques. Les bundles
restent néanmoins des artefacts probatoires susceptibles de contenir des
métadonnées historiques privées ; ils ne doivent jamais être publiés.

Après ces vérifications, les repositories temporaires ont été supprimés. Leurs
noms privés, chemins locaux et objets ne font pas partie du canonique. Les
preuves locales, bundles et manifeste ont été conservés.

## Clôture canonique

La consolidation reconstruite a été validée techniquement, mais la
réutilisation du nom `v1.0.0` est bloquée par la réservation GitHub des releases
immuables. La [décision 0012](../decisions/0012-close-canonical-recovery-after-immutable-tag-reservation.md)
abandonne donc sa republication.

Le repository canonique actuel a 38 commits propres, aucun Git tag, aucune
release et aucune pull request. `v1.0.0` reste un enregistrement historique
retiré dont les objets ne sont présents que dans les preuves privées vérifiées.
`v1.0.1` est la prochaine candidate, sans tag ni release créée. PR 2 reste une
étape ultérieure.

Le commit de clôture est poussé directement sur `main` par fast-forward non-force
comme exception unique de récupération privée, avant activation finale du
ruleset. Cette exception n'autorise aucun push direct futur.

## Intégrité expérimentale et règle future

Aucun fichier sous `experiments/kernel-v1/` ou
`experiments/kernel-micro-v1/` n'est modifié. Les dix fichiers gelés listés sous
`frozen_files` par le manifeste Mission 24 restent octet-identiques et aucun
benchmark ou runtime de modèle n'est relancé. Cette intégrité des archives
conservées ne démontre ni la complétude de la preuve runtime, ni la conservation
de l'agrégat original et de ses données sources ; voir la
[décision 0014](../decisions/0014-micro-kernel-evidence-erratum.md).

La politique active accepte les contributeurs humains avec une adresse GitHub
ID-based ou username-only `noreply`, ainsi que l'identité GitHub web exacte
uniquement comme committer. Une adresse personnelle, une identité invalide ou
une automatisation non déclarée reste soumise à `REVIEW`. Les diagnostics
masquent les adresses et aucune adresse personnelle n'est une valeur de repli.
