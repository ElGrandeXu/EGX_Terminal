# Frontière de publication V1

## But

La V1 publiée présente un workspace de terminal-agent LLM-agnostique, à racine
neutre, avec ses principes, recherches, décisions et preuves reproductibles. Le
repository canonique public est `ElGrandeXu/EGX_Terminal`. Il contient 36 commits,
zéro tag et zéro release.

## Surface incluse

- `README.md`, `docs/` et le quickstart décrivent le projet et sa gouvernance ;
- `scripts/` et `tests/` fournissent les contrôles locaux actifs ;
- `governance/` contient la politique d'identité publique, les locks et le plan
  de publication ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` portent la
  gouvernance de licences ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les deux
  campagnes rejetées comme archives inactives et immuables.

La racine ne contient ni kernel always-on, adaptateur actif, hook, skill, mémoire,
routing ni injection de doctrine. Les archives ne sont pas des composants
d'exécution de la V1.

## Éléments exclus ou différés

La surface exclut les secrets, credentials, configurations de machine,
transcripts privés, caches, sorties temporaires, modèles, poids et binaires
locaux. Une release et les capacités avancées restent hors périmètre sans
autorisation séparée.

Les bundles de récupération et la capture de l'incident sont des
**`PRIVATE_RECOVERY_ARTIFACT`** hors repository. Le repository de staging
antérieur, son nom de quarantaine, ses runs, sa pull request, ses réglages et son
objet exposé sont également hors de la surface publique. Ce repository reste
privé, non archivé pendant la migration, conservé comme preuve, et ne doit jamais
redevenir public.

## Preuves historiques et archives

Les archives conservent légitimement versions, hashes, mesures de capacité,
protocoles, résultats et endpoints loopback nécessaires à l'audit. Les douze
anciens SHA de la première réécriture restent dans ces preuves et se résolvent
via la [cartographie](../../governance/history-rewrite-map.json).

Les contrôles d'intégrité confirment l'archive `kernel-v1`, l'archive
`kernel-micro-v1` et les dix résultats gelés de Mission 24 octet-identiques. La
recréation du repository n'a modifié aucun fichier expérimental et n'a relancé
aucun benchmark.

## Historique et identité

La première remédiation contrôlée a réécrit 30 commits prépublication. Les quatre
commits suivants ont conservé la même identité canonique. Le 35e commit, issu du
premier squash merge, avait un contenu correct mais GitHub lui avait attribué une
adresse personnelle comme auteur. La politique v2 l'a classé `REVIEW` et le gate
`--fail-on-review` a bloqué la CI comme prévu.

Un force-push ne pouvait pas exclure les références GitHub associées à la pull
request fusionnée. Le dépôt antérieur a donc été placé en quarantaine privée et
le commit a été reconstruit localement avec le même tree, parent, message complet,
sujet, dates, diff, chemins, modes et contenu. Seuls son enveloppe d'identité et
son SHA ont changé. Le 36e commit documente cette décision. Tous les commits du
nouveau repository utilisent une identité GitHub `noreply`, et aucun objet du
repository canonique n'a contenu l'ancienne métadonnée.

Le [rapport d'historique](HISTORY_AUDIT.md), la [remédiation
d'identité](IDENTITY_REMEDIATION.md) et la [décision
0010](../decisions/0010-recreate-public-repository-after-email-exposure.md)
documentent les deux opérations distinctes.

## Contrôles automatisés

`scripts/check_neutral_root.py`, `scripts/check_public_surface.py`,
`scripts/check_licensing.py`, les trois modes de `scripts/check_git_history.py`,
`scripts/check_markdown_links.py`, `scripts/check_github_governance.py`, les 188
tests, `reuse 6.2.0`, actionlint 1.7.12, les parsers JSON et TOML, les locks,
`git diff --check` et `git fsck --full` passent dans la source et dans un clone
indépendant sans hardlinks.

Les recherches d'objets et de refs confirment que l'ancien commit et l'ancienne
identité ne sont pas présents. Le hash agrégé verrouillé de `kernel-v1` reste
`c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0`.

## Recréation et publication

Le nouveau repository canonique a été créé vide et privé, sans initialisation.
Seule la branche `main` nettoyée a été poussée, sans force, tag, release ni pull
request. Les jobs privés `repository / ubuntu`, `repository / windows` et
`licensing / reuse` ont tous réussi avant le changement de visibilité.

Les réglages validés ont été réappliqués : description, dix topics, issues,
projets/wiki/discussions/Pages désactivés, squash-only, suppression des branches
fusionnées, Actions en lecture seule et limitées aux actions épinglées, absence
d'approbation automatique, PVR lorsque disponible, secret scanning, push
protection et alertes de vulnérabilité.

Après passage public, la navigation et le clone anonymes ont retrouvé les 36
commits et passé la suite complète. L'ancien commit et l'ancienne pull request ne
sont pas accessibles dans le repository canonique, et le staging quarantiné
reste inaccessible anonymement.

Le ruleset `main-protection` est actif sur `main` : pull request requise, zéro
approbation obligatoire, conversations résolues, historique linéaire, trois
checks requis, suppression et force-push interdits. Le bypass administrateur est
réservé à la récupération.

## État

**`PUBLIC_V1_READY_FOR_RELEASE_REVIEW`**

Aucun tag ni aucune release n'existe. Le prochain gate est une décision explicite
et séparée sur `v1.0.0` ; ce statut ne l'autorise pas.
