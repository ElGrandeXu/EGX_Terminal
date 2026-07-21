# Audit de l'historique Git publiable

## Verdict final

- **Date :** 2026-07-21.
- **Ref publiable :** `refs/heads/main` uniquement.
- **Historique :** **`PASS`**.
- **Identité :** **`PASS`**.
- **Clone propre et clone anonyme :** **`PASS`**.
- **Commits avant la décision de remédiation publique :** 35.
- **Commits finaux :** 36.
- **Merges dans l'historique canonique :** 0.
- **Tags et releases :** 0.
- **Identités privées :** 0.
- **Politique active :** schéma 2, contributions GitHub `noreply` et committer
  web GitHub borné.

Le premier audit prépublication avait remédié 30 commits. Un incident distinct a
ensuite concerné l'identité d'auteur choisie par GitHub pour le premier squash
merge public. Le scanner a détecté cette adresse personnelle sans l'afficher et
a fait échouer `--fail-on-review`. Aucun secret de contenu ni autre bloqueur
fonctionnel n'a été trouvé.

## Identité publique finale

Les 34 premiers commits utilisent l'identité canonique du mainteneur. Le 35e
commit reconstruit utilise `ElGrandeXu` comme auteur et `Maxime Erard` comme
committer. Le 36e commit de documentation utilise l'identité canonique. Toutes
ces identités emploient l'adresse GitHub ID-based `noreply` approuvée :

```text
177521250+ElGrandeXu@users.noreply.github.com
```

La politique
[`public-commit-identity.json`](../../governance/public-commit-identity.json)
accepte aussi les auteurs et committers humains utilisant une adresse GitHub
ID-based ou username-only `noreply`. Le committer système exact
`GitHub <noreply@github.com>` est borné au rôle committer d'un merge web. Une
adresse personnelle, une identité invalide, un faux système ou un bot non
déclaré reste `REVIEW` et fait échouer `--fail-on-review`.

## Première réécriture contrôlée

`git-filter-repo` 2.47.0 avait réécrit uniquement `refs/heads/main`. La
comparaison ordinale des 30 commits avait produit :

| Propriété | Résultat |
| --- | ---: |
| Trees identiques | 30/30 |
| Messages complets identiques | 30/30 |
| Sujets identiques | 30/30 |
| Dates auteur identiques | 30/30 |
| Dates committer identiques | 30/30 |
| Nombres de parents identiques | 30/30 |
| Diffs et chemins modifiés identiques | 30/30 |
| Noms et emails auteur remédiés | 30/30 |
| Noms et emails committer remédiés | 30/30 |

La [cartographie exhaustive](../../governance/history-rewrite-map.json) reste
inchangée. Douze occurrences dans les archives expérimentales restent
volontairement exprimées avec les SHA historiques afin de préserver les preuves.

## Incident du premier squash merge

Avant toute mutation distante, le dépôt public avait 35 commits, aucun tag,
aucune release et aucun fork observé. Son `main`, le tree, le parent et le message
du commit concerné correspondaient aux valeurs gelées. Le tree était également
identique au tip de la branche de contribution.

La mise en privé a précédé toute autre mutation distante. La page du dépôt, le
commit, la pull request fusionnée et le clone ont ensuite été testés sans
credentials : les trois URLs ont répondu `404` et le clone a échoué. Le dépôt a
été renommé sous un nom de quarantaine non publié ici ; il reste privé, non
supprimé et conserve ses runs, sa pull request, ses réglages et son historique.

Le nom canonique a été recréé dans un nouveau repository privé. Aucun objet n'a
été transféré depuis la quarantaine : seule la branche locale nettoyée a été
poussée.

## Reconstruction du 35e commit

Le commit de remplacement `0a7e689142aec791467d200d6e6d3f733bad1e6b` a été
créé avec `git commit-tree` à partir du tree et du parent gelés, du message exact
et des dates ISO originales.

| Propriété | Résultat |
| --- | ---: |
| Tree | identique, 1/1 |
| Parent | identique, 1/1 |
| Message complet et sujet | identiques, 1/1 |
| Dates auteur et committer | identiques, 1/1 |
| Diff binaire et contenu | identiques, 1/1 |
| Chemins, modes et OID de blobs | identiques, 1/1 |
| Identité auteur | remplacée par `noreply` |
| Identité committer | remplacée par `noreply` |

Le SHA a nécessairement changé. Aucune propriété fonctionnelle n'a changé et les
trois commits de la branche de contribution n'ont pas été réécrits
individuellement.

## Contenu historique et intégrité

Le scan des commits, arbres, blobs, messages et chemins atteignables n'observe ni
secret plausible, clé privée PEM, chemin personnel, transcript privé, fichier
`.env` historique, contenu tiers substantiel, blob supérieur à 512 KiB, pointeur
Git LFS, submodule, note, tag ou ref inattendue.

Les 46 fichiers sous `experiments/` sont inchangés. L'archive `kernel-v1`,
l'archive `kernel-micro-v1` et les dix fichiers gelés de Mission 24 sont
octet-identiques. Le hash agrégé verrouillé de `kernel-v1` reste
`c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0`.

## Sauvegarde, purge et clones

Avant reconstruction, un bundle complet vérifié, un tar du tree, le diff, les
modes/OID, les chemins, le message, le sujet et leurs hashes ont été capturés
hors repository comme **`PRIVATE_RECOVERY_ARTIFACT`**. Les bundles privés
antérieurs restent eux aussi hors repository.

Après déplacement de `main`, la branche de contribution et toutes les refs de
transport ont été supprimées, les reflogs expirés et les objets inatteignables
collectés. L'ancien SHA n'est plus résoluble localement et l'empreinte de
l'ancienne adresse ne correspond à aucun objet restant.

Un clone indépendant sans hardlinks, puis un clone HTTPS anonyme, contiennent 36
commits, une branche et zéro tag. Les contrôles de racine, surface, licences,
historique, gouvernance, liens, tests, JSON, TOML, locks, actionlint, REUSE, Git et
intégrité gelée y passent.

## Contrôle reproductible

Depuis la racine du repository :

```console
python scripts/check_git_history.py
python scripts/check_git_history.py --all-refs
python scripts/check_git_history.py --fail-on-review
```

Le contrôle n'imprime jamais une adresse personnelle complète. Il reste strict
sur `main`, borne les branches de contribution et valide le checkout détaché
d'une pull request seulement après concordance du contexte Actions et de ses
deux parents. Toute identité personnelle dans un parent persistant reste
`REVIEW`.

## Limites

Les scanners et comparaisons sont heuristiques et bornés. Ils ne remplacent ni
revue humaine ni avis juridique. Les artefacts privés conservent volontairement
l'ancien historique. Le réglage de confidentialité des emails GitHub n'est pas
vérifiable par l'API disponible :
`EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`.
