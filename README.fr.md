[Français](README.fr.md) · [English](README.md)

# EGX_Terminal

EGX_Terminal est un espace open source de recherche et de gouvernance consacré
aux environnements d’agents dans le terminal. Son objectif est d’étudier des
mécanismes inspectables, sobres en tokens et indépendants d’un modèle, d’un
fournisseur ou d’un harness particulier.

On peut le voir comme un **bureau d’étude ouvert** : le dépôt conserve les
hypothèses, les protocoles, les preuves, les décisions et les résultats
négatifs. Ce n’est pas le produit final, ni un agent universel prêt à installer.

## L’idée de départ

Un agent de terminal peut recevoir des instructions qui orientent sa manière de
travailler : vérifier avant de conclure, préserver le travail existant, limiter
la complexité, ou adapter la vérification au risque. Le projet appelle cet
ensemble de principes une **doctrine comportementale**.

Une doctrine chargée en permanence occupe du contexte et peut modifier le
comportement de l’agent. Une idée plausible ne suffit donc pas : son utilité doit
être démontrée, son coût mesuré et son activation rester explicite.

## La méthode

EGX_Terminal suit une progression volontairement simple :

1. **Hypothèse** — formuler l’effet attendu sans le présenter comme acquis.
2. **Protocole** — définir à l’avance les cas, les mesures, les budgets et la
   règle de décision.
3. **Preuve** — exécuter une expérience isolée et conserver ce qui permet de
   l’inspecter.
4. **Décision** — promouvoir, rejeter ou différer selon les critères annoncés,
   puis conserver aussi les résultats négatifs.

La complexité n’est retenue que si sa valeur est établie selon des critères
explicites.

## Ce que contient la V1

La V1 rassemble :

- la [charte du projet](docs/CHARTER.md) et son
  [statut actuel](docs/STATUS.md) ;
- les audits, la recherche comparative et la synthèse d’architecture ;
- les [décisions](docs/decisions/README.md), avec leurs preuves, conséquences et
  conditions de révision ;
- les protocoles, fixtures, graders et rapports de compatibilité ;
- les [archives expérimentales](experiments/) de deux kernels rejetés ;
- les scripts de vérification locale et leurs tests.

Elle ne contient pas de runtime d’agent universel. La mémoire, les hooks, les
skills, le routage, la compression, les adaptateurs actifs, le packaging, la
distribution de modèles, les intégrations cloud, la télémétrie et la publication
automatique sont différés.

## Une racine neutre

Un clone de la V1 n’active aucun kernel, adaptateur ou payload comportemental à
la racine du dépôt. Les surfaces projet connues de Codex, Claude Code et
OpenCode, recensées dans
[`neutral-root-surfaces.json`](governance/neutral-root-surfaces.json), en sont
absentes.

Les principes restent disponibles dans la documentation, mais leur utilisation
est volontaire : toute capacité ou tout adaptateur futur doit être
**explicitement opt-in**. L’injection cachée d’instructions est hors du
périmètre de la V1.

Cette garantie est bornée aux conventions actives connues du registre actuel ;
elle ne prétend pas couvrir toutes les conventions futures de tous les
harnesses.

## Pourquoi les deux kernels ont été rejetés

Le projet a évalué deux candidats destinés à être chargés en permanence. Aucun
n’a été promu.

| Expérience | Résultat conservé | Verdict |
| --- | --- | --- |
| Kernel équilibré | Sur les cinq paires complètes : 2 victoires primaires pour la baseline, 0 pour le candidat et 3 égalités. Deux faux achèvements ont été relevés côté candidat. Une observation baseline a été perdue après le scoring ; l’overhead de `+19.166 %` ne décrit donc que les cinq paires complètes. | `REJECTED_AS_BALANCED` |
| Micro-kernel | Le rapport historique publie 5 égalités sur 5, une réussite fonctionnelle de 5/5 des deux côtés, aucun faux achèvement et un overhead de `7.850019354305572 %`, supérieur au plafond pré-enregistré de `5 %`. | `REJECT_MICRO` |

Le rejet du micro-kernel demande une précaution importante : le payload, le
protocole, les fixtures, les graders, le manifeste et les hashes consignés des
artefacts conservés restent auditables, mais les données runtime sources et
l’agrégat original sont irrécupérables. Les scores et mesures du rapport sont
donc des affirmations historiques dont la cohérence arithmétique peut être
contrôlée, pas des observations runtime encore vérifiables indépendamment. La
[décision 0014](docs/decisions/0014-micro-kernel-evidence-erratum.md) documente
précisément cette limite sans modifier le verdict terminal `REJECT_MICRO`.

Les conclusions complètes se trouvent dans les décisions sur le
[kernel équilibré](docs/decisions/0003-balanced-kernel-rejection.md), le
[micro-kernel](docs/decisions/0004-micro-kernel-final-evaluation.md) et la
[racine neutre](docs/decisions/0005-ship-v1-with-neutral-root.md).

## Trois questions différentes

Les archives distinguent trois niveaux qui ne doivent pas être confondus :

| Question | Ce qu’elle vérifie | Ce qu’elle ne prouve pas |
| --- | --- | --- |
| **Compatibilité technique** | Le payload peut-il être distribué, découvert ou transporté dans une combinaison mesurée ? | Que toutes les combinaisons de modèles, runtimes et harnesses fonctionnent. |
| **Conformité de sortie** | La réponse respecte-t-elle la forme ou le contrat attendu ? | Que le comportement est meilleur. |
| **Amélioration comportementale** | Le candidat fait-il mieux que la baseline selon les critères pré-enregistrés ? | Rien de plus général que les conditions testées. |

La compatibilité obtenue est classée **SUPPORTED — EXPERIMENTAL** pour les
cellules mesurées. Elle couvre notamment des validations bornées avec Codex CLI
0.144.6, OpenCode 1.17.9 et Ollama 0.20.2. Le transport réel
OpenCode 1.17.9 → Ollama 0.20.2 → `qwen3.6:27b` a été établi, mais un transport
réussi ne démontre ni la conformité formelle de la sortie ni une amélioration
comportementale. Claude Code n’était pas installé et n’a pas été validé.

Le [résumé de compatibilité
runtime](experiments/kernel-v1/validation/runtime-compatibility-summary.md)
présente ces frontières en détail.

## Limites scientifiques connues

- Les expériences portent sur des cellules et des versions précises ; elles ne
  démontrent pas une compatibilité universelle.
- Un modèle servi par un runtime, un runtime et un harness sont des rôles
  distincts. Valider une combinaison ne valide pas toutes les autres.
- Le kernel équilibré a perdu une observation baseline après le scoring. Son
  overhead sur six paires est indisponible.
- Pour le micro-kernel, les données runtime sources et l’agrégat original ne sont
  plus disponibles. Le rapport historique ne permet pas de les reconstruire.
- Les deux rejets classent des payloads précis comme doctrines always-on pour la
  V1. Ils ne démontrent pas que leurs principes sont généralement nuisibles.
- Le registre de neutralité couvre les surfaces actives connues et datées, pas
  d’éventuelles conventions futures.

Ces limites font partie du résultat scientifique ; elles ne sont pas masquées
par les décisions de gouvernance.

## Par où commencer

Le chemin local canonique demande Python 3.11 ou plus récent, un clone Git
complet et REUSE 6.2.0 installé depuis les locks hashés du dépôt. Les contrôles
actifs du projet utilisent uniquement la bibliothèque standard Python ; le
validateur REUSE est une dépendance séparée.

Depuis la racine :

```console
python scripts/check_neutral_root.py
python scripts/check_public_surface.py
python scripts/check_licensing.py
python scripts/check_git_history.py --fail-on-review
python scripts/check_markdown_links.py
python scripts/check_github_governance.py
python -m unittest discover -s tests -v
reuse lint
```

Pour une première visite :

1. suivez le [quickstart détaillé](docs/QUICKSTART.md) ;
2. consultez le [statut actuel](docs/STATUS.md) ;
3. parcourez le [registre des décisions](docs/decisions/README.md) ;
4. inspectez les [archives expérimentales](experiments/) ;
5. lisez la [frontière de publication](docs/publication/PUBLICATION_BOUNDARY.md).

Le quickstart distingue l’audit d’un clone complet de la vérification plus
limitée d’une archive source GitHub. Il explique aussi comment inspecter les
preuves sans relancer de benchmark.

## Statut et licence

Le dépôt canonique est
[`ElGrandeXu/EGX_Terminal`](https://github.com/ElGrandeXu/EGX_Terminal). Sa phase
durable est **`PUBLIC_REPOSITORY_VERIFIED`**. Aucun tag ni aucune release n’est
actif ; la préparation de `v1.0.1` reste une mission ultérieure.

La licence est déterminée fichier par fichier : le code original et les
artefacts fonctionnels sont sous
[Apache-2.0](LICENSES/Apache-2.0.txt), tandis que la documentation et la
recherche originales — dont ce README — sont sous
[CC-BY-4.0](LICENSES/CC-BY-4.0.txt). Consultez le
[résumé de licence](LICENSE), les métadonnées [REUSE](REUSE.toml) et la
[politique détaillée](docs/publication/LICENSING.md).
