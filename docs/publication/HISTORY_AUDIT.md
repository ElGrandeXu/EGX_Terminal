# Audit de l'historique Git canonique

## Verdict final

- **Date :** 2026-07-21.
- **Ref canonique :** `refs/heads/main` uniquement.
- **Historique :** **`PASS`**, linéaire, 38 commits.
- **Identité :** **`PASS`**, uniquement des identités acceptées.
- **Tags Git :** 0 localement et à distance.
- **Releases GitHub :** 0.
- **Pull requests GitHub :** 0.
- **Visibilité :** privée.
- **Preuves expérimentales modifiées :** 0.

Le premier audit prépublication avait remédié 30 commits. Un incident distinct a
ensuite concerné l'identité auteur sélectionnée par GitHub pour un squash merge.
Le scanner a détecté l'adresse personnelle sans l'afficher et a fait échouer le
gate `--fail-on-review`. Aucun secret de contenu ni autre bloqueur fonctionnel
n'a été trouvé.

## Reconstruction bornée

Le commit concerné a été reconstruit à l'identité GitHub ID-based `noreply`
approuvée. La comparaison a confirmé l'identité du tree, du parent, du message
complet, du sujet, des dates auteur et committer, du diff binaire, des chemins,
des modes et du contenu. Seule l'enveloppe d'identité, et donc le SHA du commit,
a changé.

Le repository canonique a été recréé vide et privé, puis alimenté uniquement par
la branche `main` propre. L'objet affecté, l'ancienne pull request et ses refs
n'ont pas été importés. Aucun force-push n'a été utilisé.

## Politique d'identité

Les 38 commits utilisent des identités acceptées par
[`public-commit-identity.json`](../../governance/public-commit-identity.json).
La politique accepte le mainteneur et les contributeurs humains utilisant une
adresse GitHub ID-based ou username-only `noreply`. L'identité système GitHub
exacte est bornée au rôle committer d'un merge web. Une adresse personnelle, une
identité invalide, un faux système ou un bot non déclaré reste `REVIEW`.

Les diagnostics masquent les adresses. L'adresse exposée lors de l'incident
n'apparaît ni dans l'historique canonique ni dans cette documentation.

## Refs et release historique

La seule branche persistante finale est `main`. Les refs locales et distantes
obsolètes du chantier ont été retirées après vérification de leur sauvegarde et
de leur intégration. Le clone canonique ne contient aucun Git tag.

`v1.0.0` est un enregistrement historique retiré pendant la remédiation, et non
une release active. Ses anciens objets sont absents du canonique et conservés
uniquement dans des bundles privés vérifiés. Le checker valide la cohérence du
record historique sans lire, reconstruire ou simuler les objets absents. Toute
réapparition de la ref retirée est rejetée.

`v1.0.1` est la prochaine candidate, mais aucun tag, objet tag ou release de ce
nom n'existe. La politique SSH reste `KEY_SELECTION_REQUIRED` sans identité
active.

## Preuves privées et suppression distante

Les deux repositories temporaires ont été capturés séparément dans des mirrors,
bundles complets, métadonnées privées et synthèses hors repository. Chaque bundle
passe `git bundle verify`, chaque mirror passe `git fsck --full`, et le manifeste
SHA-256 complet passe après régénération.

Après ces validations, les deux repositories ont été supprimés. Les lectures API
authentifiées et les URLs renvoient `404`, et la liste du compte ne contient plus
que le canonique pour ce projet. Les bundles et le manifeste privés sont
conservés ; leurs chemins et contenus ne sont pas publiés ici.

## Contenu historique et intégrité

Le scan des commits, arbres, blobs, messages et chemins atteignables n'observe ni
secret plausible, clé privée PEM, chemin personnel, transcript privé, fichier
`.env` historique, contenu tiers substantiel, pointeur Git LFS, submodule, note,
tag ou ref inattendue.

Les fichiers sous `experiments/kernel-v1/` et
`experiments/kernel-micro-v1/` sont inchangés. Le hash agrégé verrouillé de
`kernel-v1` reste
`c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0`,
et les dix fichiers gelés de Mission 24 restent octet-identiques.

## Contrôle reproductible

Depuis un clone Git complet :

```console
python scripts/check_git_history.py
python scripts/check_git_history.py --all-refs
python scripts/check_git_history.py --fail-on-review
```

Une archive source sans `.git` ne peut pas prouver l'historique, les refs ou les
objets absents. Elle utilise uniquement les validations content-only et ne doit
simuler aucune preuve Git.

## Limites

Les scanners et comparaisons sont heuristiques et bornés. Ils ne remplacent ni
revue humaine ni avis juridique. Les artefacts privés conservent volontairement
l'ancien historique. Le réglage de confidentialité des emails GitHub n'est pas
vérifiable par l'API disponible :
`EMAIL_PRIVACY_SETTING_NOT_API_VERIFIABLE`.
