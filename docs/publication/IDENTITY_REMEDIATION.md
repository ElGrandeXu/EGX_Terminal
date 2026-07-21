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

Les 34 premiers commits du nouvel historique conservent l'identité canonique du
mainteneur. Le passage ultérieur de la politique au schéma 2 ne modifie aucun de
ces commits et ne réalise aucune nouvelle réécriture de cette séquence.

## Incident public distinct et recréation

Le premier squash merge public avait produit un 35e commit dont le tree, le
parent, le message, les dates et le contenu étaient corrects, mais dont GitHub
avait associé l'auteur à une adresse personnelle. La politique v2 a correctement
classé cette identité `REVIEW` et bloqué les jobs Ubuntu et Windows. L'adresse
n'est jamais reproduite dans cette documentation.

Un simple force-push ne pouvait pas garantir la disparition de l'objet à travers
les références GitHub de la pull request fusionnée. Le repository public a donc
été rendu privé immédiatement, validé inaccessible sans credentials, puis
renommé en quarantaine. Son nom privé n'est pas publié ici. Il conserve
volontairement le commit, la pull request, les runs et les réglages comme preuve
et ne doit jamais redevenir public.

Le 35e commit a été reconstruit avec `git commit-tree`. Son tree, son parent, son
message complet, son sujet, ses dates auteur et committer, son diff binaire, ses
chemins, ses modes et son contenu sont identiques. Son auteur est `ElGrandeXu`,
son committer est `Maxime Erard`, et les deux utilisent l'adresse GitHub ID-based
`noreply` approuvée. Le remplacement canonique est
`0a7e689142aec791467d200d6e6d3f733bad1e6b`.

Le repository canonique a été recréé vide et privé, puis a reçu uniquement la
branche `main` nettoyée. Le commit de cette documentation porte l'historique à
36 commits. Aucun objet du nouveau repository n'a contenu l'ancienne métadonnée,
et aucun contenu fonctionnel n'a changé.

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

Un bundle Git complet a été créé et vérifié avant la première réécriture. Il est classé
**`PRIVATE_RECOVERY_ARTIFACT`**, conservé hors du repository et interdit de
publication. Son rôle exclusif est de permettre une récupération privée de
l'ancien historique en cas d'incident.

Avant la seconde reconstruction, une nouvelle capture privée a enregistré le
bundle complet du staging quarantiné, un snapshot du tree, le diff, les modes et
OID, les chemins, le message, le sujet et leurs hashes. Elle reste elle aussi
hors repository et interdite de publication.

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
avoir lieu, sauf réponse de sécurité formellement décidée. La
[décision 0010](../decisions/0010-recreate-public-repository-after-email-exposure.md)
est cette réponse : elle recrée une surface publique sans importer l'objet
exposé, plutôt que de force-push l'ancien repository.

La politique active vise désormais la confidentialité des emails publics et une
provenance GitHub inspectable, pas l'uniformité artificielle de tous les auteurs.
Elle accepte les contributeurs humains avec une adresse GitHub ID-based ou
username-only `noreply`, et accepte l'identité exacte
`GitHub <noreply@github.com>` uniquement comme committer d'un merge web. Les
contributions externes restent attribuées à leur propre compte GitHub. Une
adresse personnelle, une identité invalide ou une automatisation non déclarée
reste soumise à `REVIEW`; aucun bot futur n'est autorisé sans règle explicite.

L'ancienne adresse privée demeure absente de l'historique canonique. Le réglage
GitHub de confidentialité des emails n'est pas exposé par l'API disponible et
reste consigné comme `EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`. Toute future
opération web exige néanmoins ce réglage ; aucune adresse personnelle n'est une
valeur de repli acceptable.
