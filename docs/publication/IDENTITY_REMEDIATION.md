# Remédiation de l'identité des commits

## Résultat

Le 2026-07-21, les 30 commits prépublication de `main` ont été réécrits une
seule fois afin de remplacer l'identité personnelle de leurs auteurs et
committers par l'identité publique approuvée :

```text
Maxime Erard <177521250+ElGrandeXu@users.noreply.github.com>
```

L'audit précédent n'avait trouvé aucun secret de contenu, clé privée, chemin
personnel, transcript privé, fichier `.env`, contenu tiers substantiel ou blob
supérieur à 512 KiB. Le seul problème restant était l'exposition d'une adresse
personnelle dans les métadonnées Git. Aucun remote n'existait et aucun push
n'avait eu lieu au moment de la réécriture.

## Méthode et préservation

La réécriture a utilisé `git-filter-repo` 2.47.0 avec un mailmap minimal et
temporaire, limité à `refs/heads/main`. Pour chacun des 30 commits, les arbres,
messages complets, sujets, dates auteur, dates committer, nombres de parents,
diffs, chemins modifiés et modes de fichiers ont été comparés avant et après.
Toutes les comparaisons ont produit `30/30`. Seuls l'identité, les SHA de commit
et, par conséquence, les SHA de parents ont changé.

La cartographie exhaustive, ordonnée du plus ancien au plus récent, se trouve
dans [`governance/history-rewrite-map.json`](../../governance/history-rewrite-map.json).
La politique machine-readable de l'identité future se trouve dans
[`governance/public-commit-identity.json`](../../governance/public-commit-identity.json).

## Références historiques et archives

Une référence active à un ancien commit a été mise à jour. Douze occurrences
d'anciens SHA internes ont été trouvées dans les archives expérimentales. Elles
restent exprimées avec les identifiants pré-réécriture : modifier ces preuves
aurait violé leur immutabilité. La cartographie permet de résoudre leurs
équivalents dans l'historique remédié.

Les 46 fichiers sous `experiments/`, dont les dix fichiers gelés de Mission 24,
sont octet-identiques à leur snapshot préalable. Aucun benchmark ni runtime de
modèle n'a été lancé.

## Sauvegarde et purge

Un bundle Git complet a été créé et vérifié avant la réécriture. Il est classé
**`PRIVATE_RECOVERY_ARTIFACT`**, conservé hors du repository et interdit de
publication. Son rôle exclusif est de permettre une récupération privée de
l'ancien historique en cas d'incident.

Après un premier clone propre validé, les refs de sauvegarde éventuelles, les
reflogs et les anciens objets locaux inatteignables ont été purgés. Les
métadonnées temporaires de l'outil, le mailmap, les inventaires et
l'environnement Python temporaire ont ensuite été supprimés. Le bundle privé
n'a pas été supprimé.

## Limites et règle future

Le bundle privé conserve volontairement l'ancien historique et ne doit jamais
être publié. Les scanners et comparaisons fournissent une assurance bornée ; ils
ne constituent pas une garantie absolue contre toute forme de donnée sensible.
Les réglages privés du compte GitHub ne sont pas vérifiables par cette mission.

Après la première publication, aucune nouvelle réécriture d'historique ne doit
avoir lieu, sauf réponse de sécurité formellement décidée.
