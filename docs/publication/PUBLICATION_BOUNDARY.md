# Frontière de publication V1

## But

La V1 conserve un workspace de recherche LLM-agnostique, à racine neutre, avec
ses principes, décisions, contrôles et artefacts reproductibles dans les limites
documentées. Le seul repository canonique est `ElGrandeXu/EGX_Terminal`. Il
reste privé pendant cette clôture de récupération et ne possède actuellement
aucun Git tag ni aucune release GitHub.

## Surface canonique incluse

- `README.md`, `docs/` et le quickstart décrivent le projet et sa gouvernance ;
- `scripts/` et `tests/` fournissent les contrôles locaux actifs ;
- `governance/` contient les politiques d'identité et de release, le registre
  des surfaces actives, les locks et le plan GitHub ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` portent la
  gouvernance de licences ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les deux
  campagnes rejetées comme archives inactives et immuables.

Pour le micro-kernel, les artefacts de définition conservés — payload,
protocole, fixtures, graders et manifeste — restent auditables. Le rapport
historique conserve les affirmations runtime publiées, mais l'agrégat original
et les données runtime sources sont irrécouvrables ; ces observations ne sont
donc pas entièrement auditables ou reproductibles à partir du record conservé.
La [décision 0014](../decisions/0014-micro-kernel-evidence-erratum.md) documente
cette limite sans modifier le verdict terminal **`REJECT_MICRO`**.

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
PR #2 est ensuite terminée et mergée par squash ; le commit résultant
`c708bc6af88b5e98a08fc801e476d4c16248e701` est son commit de squash merge et
établit le checkpoint historique d'un historique linéaire de 40 commits.

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

La conclusion de gouvernance **`REJECT_MICRO`** associée à la V1 reste
inchangée : aucun fichier expérimental, résultat ou protocole n'est modifié. Les
affirmations runtime publiées restent historiques et ne remplacent pas
l'agrégat et les données runtime sources absents. `v1.0.1` est la prochaine
candidate, mais aucun tag ou release de ce nom n'existe. PR #2 est terminée et
mergée. La prochaine étape est l'audit final de prépublication ; la préparation
séparée de `v1.0.1` et de la signature SSH ne peut commencer qu'ensuite.

## Gouvernance GitHub

La description, la homepage vide et les dix topics définis par la gouvernance
sont appliqués. Les issues sont actives ; projects, wiki, discussions et Pages
sont désactivés. Les merges sont squash-only avec suppression des branches
fusionnées et auto-merge désactivé.

Actions est limité à `actions/checkout@*` et `actions/setup-python@*`, avec
pinning SHA complet, token en lecture seule et approbation de pull request
interdite. Les alertes de vulnérabilité sont actives. Private Vulnerability
Reporting est indisponible tant que le repository reste privé, secret scanning
est désactivé et push protection n'est pas active. Private Vulnerability
Reporting devra être activé et vérifié avant toute publication publique ; aucune
adresse personnelle n'est publiée comme canal de remplacement.

Le ruleset souhaité `main-protection` imposerait pull request, résolution des
conversations, historique linéaire et checks `repository / ubuntu`,
`repository / windows` et `licensing / reuse`, tout en bloquant suppression et
force-push. Il n'est pas appliqué : les rulesets sont indisponibles sur le plan
GitHub Free tant que le repository est privé, et `main` est actuellement non
protégée. Le passage par pull request reste une convention obligatoire du projet,
appliquée procéduralement et non par une protection GitHub active.

Le push direct du commit de clôture est une exception unique de récupération
privée avant activation du ruleset. Il n'autorise aucun push direct futur.

## État

**`PRIVATE_RECOVERY_CLOSED`**

Le commit `c708bc6af88b5e98a08fc801e476d4c16248e701` est le squash-merge commit de
PR #2. À ce checkpoint historique, l'historique linéaire comptait 40 commits.
Le canonique ne possède aucun Git tag ni aucune release. L'audit final de
prépublication est désormais la prochaine étape. Les contrôles distants seront
réévalués avant tout passage public ; ensuite seulement pourront commencer la
préparation séparée de `v1.0.1` et de la signature SSH.
