# Politique de licences par fichier

## Principe

EGX_Terminal réunit des logiciels, des protocoles expérimentaux et des œuvres
documentaires. Une licence unique traiterait imparfaitement cette nature hybride.
Le repository attribue donc une licence déterminée à chaque fichier couvert :
Apache-2.0 pour les artefacts fonctionnels originaux et CC-BY-4.0 pour les œuvres
documentaires et recherches originales.

Il ne s'agit pas d'une double licence laissant choisir entre Apache-2.0 et
CC-BY-4.0 pour un même fichier. La cartographie de `REUSE.toml` détermine la
licence applicable à chaque chemin.

## Frontière

- `README.md`, les politiques communautaires racine, les templates Markdown
  GitHub et `docs/**` relèvent de CC-BY-4.0.
- `.gitattributes`, `.gitignore`, le workflow GitHub Actions, `scripts/**`,
  `tests/**`, `governance/**`, `licensing/**` et les autres artefacts techniques couverts relèvent
  d'Apache-2.0. Cela inclut la politique d'identité publique et la cartographie
  technique de réécriture.
- `experiments/**` relève entièrement d'Apache-2.0, y compris les README,
  protocoles, fixtures, graders, résultats et payloads. Une expérience forme
  ainsi un bundle fonctionnel réutilisable sous une licence unique.

Les actions distantes sont seulement référencées par repository, release et SHA.
Leur contenu n'est ni copié dans le repository ni relicencié.

Les deux archives expérimentales restent immuables. Leur attribution est
externe dans `REUSE.toml` : aucun en-tête, octet ou retour à la ligne n'a été
ajouté dans `experiments/kernel-v1/` ou `experiments/kernel-micro-v1/`.

Les faits bruts, noms, marques, URLs, commits, hashes, versions, commandes, noms
de modèles et APIs publiques ne deviennent pas des œuvres de Maxime du seul fait
qu'ils sont consignés ici. Les courtes citations attribuées et les références à
des projets tiers ne sont pas relicenciées. La licence CC couvre la sélection,
l'analyse, la synthèse et la rédaction originales, dans la seule mesure des
droits que le donneur de licence peut concéder.

## Sources de vérité

`REUSE.toml` est l'autorité machine-readable pour les fichiers couverts. Les
textes juridiques intégraux sont `LICENSES/Apache-2.0.txt` et
`LICENSES/CC-BY-4.0.txt`. Ils proviennent respectivement de l'Apache Software
Foundation et de Creative Commons.

`licensing/license-lock.json` enregistre leurs URLs canoniques, empreintes
SHA-256, date de récupération, encodage et comparaison avec une seconde source
officielle SPDX. `python scripts/check_licensing.py` vérifie ces empreintes hors
ligne ; il ne télécharge ni ne réécrit aucun fichier.

Le texte Apache est octet-identique au téléchargement ASF. Le texte CC conserve
intégralement le contenu logique du téléchargement Creative Commons ; seule la
ligne vide terminale a été normalisée. Les versions SPDX expriment les mêmes
identifiants mais emploient une mise en forme et des marqueurs de comparaison
différents. `.gitattributes` impose LF aux textes verrouillés afin que leurs
hashes restent stables sur toutes les plateformes.

## Réutiliser et attribuer

Pour un document sous CC BY 4.0, une attribution correcte indique au minimum :

- auteur : Maxime Erard ;
- titre ou chemin du document ;
- source du repository lorsqu'elle est disponible ;
- mention « CC BY 4.0 » avec un lien vers la licence ;
- indication des modifications apportées.

Exemple : « Maxime Erard, `docs/CHARTER.md`, source EGX_Terminal, CC BY 4.0,
modifié ». L'attribution peut être adaptée raisonnablement au support.

Pour un fichier sous Apache-2.0, conserver les avis de copyright et de licence,
fournir une copie de la licence, signaler les fichiers modifiés et respecter les
conditions d'Apache-2.0. Aucun fichier `NOTICE` n'est actuellement requis :
**No NOTICE file required by the current repository contents.**

## Contenus tiers et marques

Un contenu tiers substantiel ne doit être ajouté qu'avec une source, une licence
prouvée, les avis requis et une annotation étroite qui ne revendique pas le
copyright de Maxime. Une provenance incertaine bloque la publication du contenu
concerné. `THIRD_PARTY_NOTICES.md` ou `NOTICE` ne sera créé que si une obligation
réelle le justifie.

Aucune licence du repository n'accorde de permission sur les noms, marques,
logos ou autres droits de tiers. La simple mention d'un projet ne signifie ni
affiliation ni approbation.

## Ajouter ou modifier un fichier

1. Déterminer s'il s'agit d'une œuvre documentaire originale, d'un artefact
   fonctionnel original, de métadonnées factuelles, d'un contenu tiers prouvé ou
   d'une provenance incertaine.
2. Placer le fichier dans la catégorie de chemin la plus étroite de
   `REUSE.toml`. Ne pas créer de chevauchement ni d'expression combinant les deux
   licences des œuvres originales.
3. Pour un contenu tiers substantiel, conserver son titulaire, sa licence, sa
   source et ses obligations dans une annotation spécifique. Ne jamais utiliser
   une règle générale pour écraser cette provenance.
4. Si la provenance reste incertaine, ne pas improviser de licence et traiter le
   fichier comme bloqueur de publication.
5. Exécuter les validations locales et officielles.

Validation locale, déterministe, sans réseau ni dépendance permanente :

```console
python scripts/check_licensing.py
```

Validation supplémentaire avec l'outil officiel :

```console
reuse lint
```

La conformité a été validée le 2026-07-21 avec `reuse 6.2.0` et un résultat
`PASS`. Le contrôle local vérifie la politique particulière de ce repository ;
le linter officiel vérifie REUSE Specification 3.3. Aucun des deux ne remplace
une revue de provenance contextuelle ni un avis juridique.
