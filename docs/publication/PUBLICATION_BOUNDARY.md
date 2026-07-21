# Frontière de publication V1

## But

La V1 prévue présente un workspace de terminal-agent LLM-agnostique, à racine
neutre, avec ses principes, ses recherches, ses décisions et ses preuves
reproductibles. Ce document décrit une publication future : le repository n'est
pas annoncé comme déjà public ou publié.

## Surface incluse

La composition publique prévue est la suivante :

- `README.md` présente le projet et oriente vers son état, son quickstart et ses
  décisions ;
- `docs/QUICKSTART.md` fournit le parcours local, déterministe et sans runtime ;
- `docs/` porte la charte, l'état, les décisions, les audits, la synthèse et la
  présente frontière ;
- `scripts/` contient des contrôles locaux, déterministes et sans réseau ;
- `tests/` vérifie les contrôles actifs de la distribution ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` rendent la
  gouvernance de licences lisible et machine-readable ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les deux
  campagnes doctrinales rejetées comme preuves historiques inactives ;
- `.gitignore` empêche le suivi accidentel des secrets, configurations locales,
  caches, logs et sorties temporaires plausibles pour ce repository.

La racine neutre ne contient ni kernel always-on ni adaptateur actif. La
documentation décrit des principes et protocoles ; elle ne les active pas. Les
scripts contrôlent la distribution sans fournir de doctrine. Les tests sont des
fixtures et validations, pas des instructions racine. Les archives expérimentales
sont des résultats historiques, pas des composants d'exécution de la V1.

## Éléments exclus ou différés

La surface prévue exclut :

- secrets, credentials, fichiers d'environnement locaux et configurations de
  machine ;
- transcripts ou journaux privés, caches, fichiers temporaires et sorties de
  travail non retenues comme preuve ;
- modèles, poids, données privées et binaires locaux ;
- dépendance obligatoire à un fournisseur, un modèle ou un service réseau ;
- kernel, adaptateur, hook, skill, mémoire, routing ou injection active ;
- packaging, CI nouvelle, remote, release et publication effective.

## Preuves historiques et exceptions documentées

Les deux dossiers sous `experiments/` sont publiables comme archives immuables.
Ils conservent intentionnellement des versions de logiciels et de modèles, des
hashes, des mesures de capacité de la machine d'essai, des protocoles, des
résultats et des endpoints loopback. Ces faits sont nécessaires à l'audit de
l'histoire et ne constituent ni une configuration active ni une dépendance de
la V1.

L'inspection du 2026-07-21 n'y a trouvé aucun chemin personnel, credential réel,
token exploitable, clé privée, adresse RFC 1918 sensible ou transcript brut. Les
adresses loopback, l'adresse d'écoute non spécifiée et l'adresse réservée à la
documentation observées sont des données de test légitimes. Aucun fichier des
archives n'a été modifié pour cette inspection.

Ces éléments historiques forment une exception documentaire à une surface
entièrement générique. Ils ne sont pas des exceptions aux règles bloquantes du
scanner. Aucune exception de taille n'est actuellement déclarée.

## Contrôle automatisé

`scripts/check_public_surface.py` analyse par défaut les fichiers suivis par Git
et contrôle aussi les cinq chemins interdits à la racine. Il détecte notamment
des chemins personnels, le compte local connu dans un contexte machine, des noms
de fichiers sensibles, plusieurs signatures plausibles de secrets, les clés PEM
privées, les adresses RFC 1918, les caches et temporaires suivis, les fichiers de
plus de 512 KiB et les violations de neutralité racine. Les fixtures imbriquées
restent autorisées.

Le contrôle tolère les hashes, versions, commits, exemples fictifs et endpoints
loopback. Son propre code exprime les motifs sous forme de regex et les tests
assemblent les marqueurs sensibles par fragments afin de ne pas déposer de faux
credential complet dans la surface suivie.

Ce contrôle est heuristique. Il ne remplace ni la revue contextuelle, ni la
validation de provenance, ni un audit spécialisé de secrets. Il peut manquer un
format inconnu, une donnée encodée ou un secret dans un binaire ; inversement,
chaque diagnostic doit être classé avant de supprimer une preuve légitime.

`scripts/check_licensing.py` contrôle hors ligne la cartographie par fichier, les
textes de licence verrouillés, les conflits SPDX et l'intégrité des archives. Le
linter officiel `reuse 6.2.0` a également produit `PASS` le 2026-07-21 pour REUSE
Specification 3.3. Ces outils ne remplacent ni la revue de provenance ni un avis
juridique. Aucun contenu tiers substantiel et aucune exception tierce n'ont été
identifiés ; aucun fichier `NOTICE` n'est requis.

## Gate avant remote et premier push

Avant tout ajout de remote ou premier push, il faut au minimum :

1. garder la racine neutre et les deux contrôles locaux au vert ;
2. revoir le diff et l'inventaire suivi, y compris les fichiers volumineux ;
3. valider les JSON, les liens Markdown modifiés et les suites applicables ;
4. confirmer l'intégrité des deux archives et des résultats de Mission 24 ;
5. confirmer l'absence de secret, donnée privée, sortie locale et dépendance de
   machine dans les changements depuis cette inspection ;
6. conserver au vert la gate désormais passée du README public et du quickstart ;
7. conserver au vert `python scripts/check_licensing.py` et `reuse lint` ;
8. obtenir une décision explicite avant la création du remote et le push.

## État

**`READY_FOR_FINAL_PUBLICATION_REVIEW`**

La surface active ne contient aucun bloqueur observé et les contrôles passent.
Les faits historiques et reproductibles conservés dans les archives immuables ne
sont pas des exceptions de licence. La gate du README public, du quickstart et de
la gouvernance de licences est passée. La prochaine gate est la préparation
finale de gouvernance et de publication GitHub. Aucun remote ou push n'est
autorisé par ce statut.
