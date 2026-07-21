# 0006 — Adopter des licences Apache et CC par fichier

- **Status:** accepted
- **Date:** 2026-07-21
- **Copyright holder:** Maxime Erard
- **Initial year:** 2026

## Contexte

La V1 contient à la fois du code et des artefacts fonctionnels, de la recherche
et de la documentation, ainsi que deux archives expérimentales immuables. Maxime
a choisi Apache-2.0 pour les œuvres fonctionnelles originales et CC-BY-4.0 pour
les œuvres documentaires originales. La politique doit être exhaustive,
compréhensible et vérifiable sans modifier les archives.

L'audit de provenance a classé les fichiers suivis comme œuvres originales de
Maxime, métadonnées ou références factuelles, ou fichiers exemptés par REUSE.
Les audits contiennent des noms, URLs, SHA, versions, faits techniques,
paraphrases originales et courtes citations attribuées ; aucun contenu tiers
substantiel copié n'a été identifié. Aucune provenance ne reste incertaine.

## Options étudiées

### Apache-2.0 partout

Simple à cartographier, mais moins adaptée à l'attribution et à la réutilisation
des documents et travaux de recherche.

### Apache-2.0 et CC-BY-4.0 par catégorie

Adapte la licence à la nature de chaque œuvre tout en conservant une frontière
déterministe et automatisable.

### Deux licences au choix pour chaque fichier

Permettrait au réutilisateur de choisir pour chaque œuvre, mais effacerait la
frontière voulue entre documents et artefacts fonctionnels. Cette option est
rejetée.

## Décision

Le repository adopte une gouvernance de licences multiples par fichier, et non
une double licence au choix :

| Catégorie | Chemins | Licence |
| --- | --- | --- |
| Documentation et recherche originales | `README.md`, `docs/**` | `CC-BY-4.0` |
| Artefacts fonctionnels et techniques originaux | `.gitattributes`, `.gitignore`, `scripts/**`, `tests/**`, `licensing/**` | `Apache-2.0` |
| Bundles expérimentaux complets | `experiments/**`, README et payloads inclus | `Apache-2.0` |

`REUSE.toml`, conforme au schéma version 1 de REUSE 3.3, est l'autorité
machine-readable. `LICENSE` résume la frontière et `LICENSES/` contient les deux
textes officiels. `licensing/license-lock.json` verrouille leurs sources et
hashes.

## Archives et provenance

L'attribution des archives est exclusivement externe. Aucun fichier sous
`experiments/kernel-v1/` ou `experiments/kernel-micro-v1/` n'est modifié. Le hash
agrégé de `kernel-v1` reste
`c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0`,
et les résultats gelés de Mission 24 restent octet-identiques.

Les faits, noms de tiers, marques, URLs, versions, hashes, commandes et courtes
citations attribuées ne sont pas revendiqués comme créations de Maxime. Tout
futur contenu tiers substantiel conservera sa licence, son titulaire, sa source
et ses avis ; toute provenance incertaine sera un bloqueur de publication.

## Raisons et conséquences

La sophistication n'a de valeur ici que parce qu'elle est explicite,
automatisée, exhaustive et proportionnée à la nature hybride du repository. La
frontière rend les expériences réutilisables comme ensembles fonctionnels sans
fragmenter leur licence, tout en donnant aux documents une règle d'attribution
adaptée.

Le coût est la maintenance de `REUSE.toml`, des textes verrouillés, du contrôle
local et des annotations tierces éventuelles. Une modification de structure doit
préserver la couverture exhaustive et l'absence de chevauchement involontaire.

No NOTICE file required by the current repository contents.

## Garde-fous

- `scripts/check_licensing.py` vérifie hors ligne la cartographie, les hashes, les
  conflits SPDX, les archives et la frontière attendue avec Python 3.11 standard
  library uniquement.
- Le linter officiel `reuse 6.2.0` a produit `PASS` le 2026-07-21 pour REUSE
  Specification 3.3.
- Le contrôle local ne remplace ni le linter officiel, ni une revue contextuelle
  de provenance, ni un avis juridique.
- Aucun `NOTICE`, texte de licence ou exception tierce ne peut être ajouté sans
  obligation documentée.

## Modification future

Toute nouvelle catégorie ou licence exige une nouvelle décision ou une révision
explicite de celle-ci, le texte de licence officiel et son lock, une annotation
étroite, des tests du contrôle local et un `reuse lint` réussi. Un nouveau fichier
doit être classé avant intégration ; s'il contient du contenu tiers ou possède
une provenance ambiguë, la règle générale ne doit jamais écraser cette situation.
