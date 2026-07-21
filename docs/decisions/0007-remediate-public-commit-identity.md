# 0007 — Remédier l'identité publique des commits

- **Status:** Accepted
- **Date:** 2026-07-21

## Contexte

L'audit prépublication de `main` a confirmé un historique linéaire de 30 commits,
sans secret de contenu, clé privée, chemin personnel, transcript privé, fichier
`.env`, contenu tiers substantiel, gros blob, remote ou push. Il a aussi identifié
une adresse personnelle unique dans les métadonnées auteur et committer de tous
les commits.

## Problème

Publier `main` aurait publié cette adresse personnelle avec chaque commit. La
politique choisie exige une identité publique stable, attribuable au compte
GitHub prévu et indépendante de l'adresse personnelle.

## Alternatives considérées

1. **Accepter l'exposition.** Rejeté, car la décision explicite est de ne pas
   publier l'adresse personnelle.
2. **Ajouter seulement une `.mailmap`.** Rejeté, car une mailmap modifie
   l'affichage mais laisse les métadonnées originales dans les objets publiés.
3. **Réécrire avant publication.** Retenu, car aucun collaborateur distant,
   remote ou push n'existe encore et que la préservation peut être démontrée.

## Décision

Réécrire une seule fois les 30 commits prépublication afin que leurs auteurs et
committers utilisent exactement :

```text
Maxime Erard <177521250+ElGrandeXu@users.noreply.github.com>
```

Le login GitHub associé est `ElGrandeXu` et l'identifiant numérique est
`177521250`. La politique machine-readable est
[`governance/public-commit-identity.json`](../../governance/public-commit-identity.json).

## Méthode et sauvegarde

La transformation utilise `git-filter-repo` 2.47.0, un mailmap minimal temporaire
et la seule ref `refs/heads/main`. Un bundle complet, vérifié et privé est créé
hors repository avant toute réécriture. Il est interdit de publication et n'est
pas supprimé par cette décision.

## Préservation et cartographie

Les arbres, contenus, messages, dates, ordre, arités, structure des parents,
diffs, chemins et modes des 30 commits sont préservés. Les archives
expérimentales restent octet-identiques. La cartographie exhaustive des anciens
vers les nouveaux SHA est conservée dans
[`governance/history-rewrite-map.json`](../../governance/history-rewrite-map.json).

## Conséquences

- Tous les anciens SHA de commit changent.
- Aucune collaboration distante n'est perturbée, puisqu'aucun push n'existait.
- Les archives restent inchangées ; leurs anciens SHA internes se résolvent via
  la cartographie.
- Un unique commit post-réécriture documente la remédiation et installe les
  garde-fous.
- La configuration Git locale impose l'identité publique sans modifier la
  configuration globale.

## Garde-fous futurs

Le contrôle historique lit la politique publique et exige le nom, l'adresse
ID-based `noreply`, le login et l'identifiant GitHub exacts pour chaque auteur et
committer. `--fail-on-review` rend toute autre identité bloquante. Après
publication, une autre réécriture est interdite sauf réponse de sécurité
formellement décidée. Le bundle privé ne doit jamais être publié.
