# Frontière de publication V1

## But

La V1 conserve un workspace de recherche LLM-agnostique, à racine neutre, avec
ses principes, décisions et preuves reproductibles. Le seul repository canonique
est `ElGrandeXu/EGX_Terminal`. Il reste privé pendant cette clôture de
récupération et ne possède actuellement aucun Git tag ni aucune release GitHub.

## Surface canonique incluse

- `README.md`, `docs/` et le quickstart décrivent le projet et sa gouvernance ;
- `scripts/` et `tests/` fournissent les contrôles locaux actifs ;
- `governance/` contient les politiques d'identité et de release, le registre
  des surfaces actives, les locks et le plan GitHub ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` portent la
  gouvernance de licences ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les deux
  campagnes rejetées comme archives inactives et immuables.

La racine ne contient ni kernel always-on, adaptateur actif, hook, skill,
mémoire, routing ni injection de doctrine. Les archives ne sont pas des
composants d'exécution de la V1.

## Éléments privés ou différés

La surface canonique exclut les secrets, credentials, configurations de machine,
transcripts privés, caches, sorties temporaires, modèles, poids et binaires
locaux. Elle exclut également les bundles, mirrors, captures API et manifestes
de l'incident. Ces preuves restent privées, hors repository, et ne constituent
pas une preuve publiquement vérifiable.

Les repositories temporaires de récupération ont été supprimés après sauvegarde
locale complète et vérifiée. Leurs noms privés, chemins locaux, objets et
anciennes refs ne sont pas publiés dans le canonique.

## Historique et identité

La première remédiation contrôlée avait réécrit 30 commits prépublication à
l'identité GitHub `noreply` approuvée. Lors d'un premier squash merge ultérieur,
GitHub a produit un commit fonctionnellement correct avec une adresse auteur
personnelle. La politique d'identité a détecté l'incident immédiatement.

Le repository affecté a été rendu privé et remplacé. Le commit fonctionnel a été
reconstruit à l'identité `noreply` avec le même tree, parent, message complet,
sujet, dates et diff. L'objet affecté et les refs de l'ancienne pull request
n'ont pas été importés. Le 38e commit clôt cette récupération sans force-push.

Le [rapport d'historique](HISTORY_AUDIT.md), la [remédiation
d'identité](IDENTITY_REMEDIATION.md) et les décisions [0010](../decisions/0010-recreate-public-repository-after-email-exposure.md)
et [0012](../decisions/0012-close-canonical-recovery-after-immutable-tag-reservation.md)
documentent les opérations distinctes.

## Release historique retirée

`v1.0.0` n'est pas une release active ou téléchargeable dans le repository
recréé. C'est un enregistrement historique retiré pendant la remédiation de
confidentialité. Son ancienne cible, son ancien objet tag et son ancienne release
sont conservés uniquement dans des preuves privées vérifiées. La réservation
GitHub liée aux releases immuables interdit de réutiliser ce nom dans le
repository recréé ; aucun contournement n'est poursuivi.

Les conclusions expérimentales associées à V1 restent valables : aucun fichier
expérimental, résultat ou protocole n'est modifié. `v1.0.1` est la prochaine
candidate, mais aucun tag ou release de ce nom n'existe. PR 2 reste une étape
ultérieure séparée.

## Gouvernance GitHub

La description, la homepage vide et les dix topics définis par la gouvernance
sont appliqués. Les issues sont actives ; projects, wiki, discussions et Pages
sont désactivés. Les merges sont squash-only avec suppression des branches
fusionnées et auto-merge désactivé.

Actions est limité à `actions/checkout@*` et `actions/setup-python@*`, avec
pinning SHA complet, token en lecture seule et approbation de pull request
interdite. Private Vulnerability Reporting, secret scanning, push protection et
alertes de vulnérabilité sont actifs.

Après le premier passage vert des trois checks privés, le ruleset
`main-protection` impose pull request, résolution des conversations, historique
linéaire et checks `repository / ubuntu`, `repository / windows` et
`licensing / reuse`, tout en bloquant suppression et force-push.

Le push direct du commit de clôture est une exception unique de récupération
privée avant activation du ruleset. Il n'autorise aucun push direct futur.

## État

**`PRIVATE_RECOVERY_CLOSED`**

Le canonique possède 38 commits propres, aucun Git tag, aucune release et aucune
pull request. Il est prêt pour PR 2, sans que celle-ci soit commencée par cette
mission.
