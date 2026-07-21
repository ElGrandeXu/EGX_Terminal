# Audit de l'historique Git publiable

## Verdict final

- **Date :** 2026-07-21.
- **Ref publiable :** `refs/heads/main` uniquement.
- **Historique :** **`PASS`**.
- **Identité :** **`PASS`**.
- **Clone propre :** **`PASS`**.
- **Commits de référence avant la première PR protégée :** 34, dont 30 commits
  historiques remédiés et quatre commits de remédiation, gouvernance,
  correction de staging et publication.
- **Merges :** 0.
- **Identités auteur sur ces 34 commits :** 1.
- **Identités committer sur ces 34 commits :** 1.
- **Identités privées :** 0.
- **Politique active :** schéma 2, contributions GitHub `noreply` et committer
  web GitHub borné.

Un audit antérieur a déclenché la remédiation parce que les métadonnées des 30
commits utilisaient une adresse personnelle. Cette adresse n'est jamais affichée
ici. Aucun secret de contenu ou autre bloqueur de publication n'avait été trouvé.

## Identité publique

Les 34 commits qui précèdent la première pull request protégée utilisent
exactement, comme auteur et committer :

```text
Maxime Erard <177521250+ElGrandeXu@users.noreply.github.com>
```

Le schéma 2 de la politique
[`public-commit-identity.json`](../../governance/public-commit-identity.json)
conserve cette identité canonique du mainteneur, dont l'ID `177521250` et le
login `ElGrandeXu` sont inspectables dans l'adresse. Il accepte aussi les auteurs
et committers humains utilisant une adresse GitHub ID-based ou username-only
`noreply`. Une variation du nom d'affichage associée à l'adresse exacte du
mainteneur reste classée comme compte `ElGrandeXu`.

Le committer système exact `GitHub <noreply@github.com>` est accepté uniquement
dans le rôle committer créé par le squash merge web. Il n'est jamais accepté
comme auteur. Une adresse personnelle, une identité invalide, un faux système
ou un bot non déclaré reste `REVIEW` et fait échouer `--fail-on-review`. Plusieurs
identités conformes sont normales et ne constituent plus un finding.

Cette évolution ne réécrit aucun commit. Elle protège la confidentialité et la
provenance inspectable sans imposer une uniformité artificielle des auteurs.

## Réécriture contrôlée

`git-filter-repo` 2.47.0 a réécrit uniquement `refs/heads/main`. La comparaison
ordinale des 30 commits a produit :

| Propriété | Résultat |
| --- | ---: |
| Trees identiques | 30/30 |
| Messages complets identiques | 30/30 |
| Sujets identiques | 30/30 |
| Dates auteur identiques | 30/30 |
| Dates committer identiques | 30/30 |
| Nombres de parents identiques | 30/30 |
| Diffs et chemins modifiés identiques | 30/30 |
| Noms auteur remédiés | 30/30 |
| Emails auteur remédiés | 30/30 |
| Noms committer remédiés | 30/30 |
| Emails committer remédiés | 30/30 |

La [cartographie exhaustive](../../governance/history-rewrite-map.json) contient
30 entrées ordonnées. Une référence active à un ancien SHA a été actualisée.
Douze occurrences dans les archives restent volontairement inchangées et se
résolvent par cette cartographie.

## Contenu historique

Le scan des commits, arbres, blobs, messages et chemins atteignables n'a observé :

- aucun secret ou credential plausible ;
- aucune clé privée PEM ;
- aucun chemin personnel ou transcript privé ;
- aucun fichier `.env` historique ;
- aucun contenu tiers substantiel ou provenance ambiguë ;
- aucun blob supérieur à 512 KiB ;
- aucun pointeur Git LFS ni submodule ;
- aucune signature de commit, merge, note, tag ou ref inattendue.

Les anciens fichiers racine `AGENTS.md` et `CLAUDE.md` restent des éléments sûrs
de l'histoire du bootstrap. Ils ne sont pas présents au `HEAD` et ne remettent
pas en cause la neutralité de la racine active.

## Archives et résultats gelés

Les 46 fichiers sous `experiments/` ont été comparés par SHA-256 avant et après
la réécriture. L'archive `kernel-v1`, l'archive `kernel-micro-v1` et les dix
fichiers gelés de Mission 24 sont octet-identiques. Aucun ancien SHA contenu dans
ces preuves n'a été remplacé et aucun benchmark n'a été relancé.

## Sauvegarde, purge et clone propre

Avant la transformation, un bundle complet a été créé et vérifié hors du
repository. Il est classé **`PRIVATE_RECOVERY_ARTIFACT`**, conserve
volontairement l'ancien historique et ne doit jamais être publié.

Après le commit de remédiation et un premier clone de validation, les éventuelles
refs de sauvegarde, reflogs, objets inatteignables et métadonnées temporaires de
réécriture ont été purgés du repository source. L'ancien HEAD ne s'y résout plus.

Le clone final a été créé avec une copie indépendante sans hardlinks. Son remote
local technique a été supprimé avant les contrôles. Il contient 31 commits, une
branche, zéro tag et l'unique identité attendue. Les contrôles de racine,
surface, licences, historique, tests, JSON, TOML, liens Markdown, archives et
résultats gelés y passent sans dépendance au workspace source. Le clone
temporaire a ensuite été supprimé.

## Contrôle reproductible

Depuis la racine du repository :

```console
python scripts/check_git_history.py
python scripts/check_git_history.py --all-refs
python scripts/check_git_history.py --fail-on-review
```

Le contrôle utilise la politique machine-readable active, n'imprime jamais une
adresse personnelle complète et produit un résultat déterministe. Sur `main`, il
reste strict à la branche publique et aux refs de transport attendues. Sur une
branche de contribution, il inspecte `main + HEAD`, accepte uniquement la
branche courante et son éventuelle ref `origin` identique ou ancêtre, et les
classe `INFO CONTRIBUTION_REF`. Le checkout détaché temporaire d'une pull
request GitHub utilise par défaut un commit de merge synthétique pour tester le
résultat fusionné. Le contrôle ne classe ce seul `HEAD` comme
`EPHEMERAL_GITHUB_PR_MERGE` qu'après concordance stricte des variables Actions,
du payload, du repository, du numéro de PR, du SHA, des deux parents ordonnés et
de l'unique ref `pull/<numéro>/merge`. Son identité et son message générés ne
font pas partie de l'historique publié, mais son arbre, tous ses blobs
atteignables et les deux historiques parents restent intégralement analysés.
Toute identité personnelle dans un parent persistant reste `REVIEW`. Les objets
résiduels locaux font l'objet d'un contrôle séparé pendant la procédure de
purge.

## Limites

Les scanners et comparaisons sont heuristiques et bornés. Ils ne prouvent pas
l'absence absolue de tout secret encodé ou format inconnu et ne remplacent ni
revue humaine ni avis juridique. Le bundle privé conserve intentionnellement
l'ancien historique. Les réglages privés du compte GitHub ne sont pas
vérifiables par API et ne sont pas revendiqués comme contrôlés.
