# Validation de la distribution statique du kernel v1

## Périmètre exact

Cette validation couvre uniquement la génération déterministe et la vérification
statique d'un workspace jetable. Le prototype est expérimental, inactif et non
promu. Il n'est jamais exécuté sur la racine d'EGX_Terminal.

Aucun modèle, provider, réseau, hook, skill, mémoire, routeur ou mécanisme de
compression n'est utilisé. Aucun binaire Codex, Claude Code ou OpenCode n'est
lancé avec un prompt. La présence ou la version d'un client ne prouve ni la
découverte d'un fichier, ni son injection, ni l'obéissance d'un modèle.

## Environnement local observé

Observation non mutante réalisée le 2026-07-20 sous Windows et PowerShell. Les
chemins absolus locaux sont volontairement omis du rapport public.

| Outil | Résolution locale | Version rapportée | Commandes utilisées | Limite de l'observation |
| --- | --- | --- | --- | --- |
| Python | trouvé | `Python 3.11.9` | `Get-Command python`, `python --version` | prouve seulement qu'un interpréteur répond localement |
| Codex | trouvé | `codex-cli 0.144.6` | `Get-Command codex`, `codex --version` | aucun prompt, chargement ou comportement testé |
| Claude Code | absent du `PATH` | indisponible | `Get-Command claude` | n'exclut pas une installation hors `PATH` |
| OpenCode | trouvé | `1.17.9` | `Get-Command opencode`, `opencode --version` | aucun prompt, chargement ou comportement testé |

## Architecture générée

Le point d'entrée est
[`tools/sync_adapters.py`](../tools/sync_adapters.py), écrit pour Python 3 avec
la seule bibliothèque standard. Il lit [`KERNEL.md`](../KERNEL.md) et vérifie
d'abord son manifeste expérimental. Il ne modifie jamais ces deux sources.

Une cible vide produit exactement :

```text
<target>/
├── .egx/
│   └── doctrine-lock.json
├── doctrine/
│   └── KERNEL.md
├── AGENTS.md
└── CLAUDE.md
```

- `doctrine/KERNEL.md` est identique octet pour octet à la source expérimentale.
- `AGENTS.md` est identique octet pour octet au canon et dessert statiquement
  Codex et OpenCode.
- `CLAUDE.md` contient les 19 octets ASCII `@doctrine/KERNEL.md`.
- Aucun `opencode.json` n'est créé.
- Le générateur n'est pas requis après matérialisation : les quatre sorties sont
  des fichiers ordinaires.

### Encodage et fins de fichier

Le kernel, le canon, `AGENTS.md` et `CLAUDE.md` utilisent UTF-8 sans BOM, des
fins de ligne LF et aucune fin de ligne finale. Le lockfile utilise UTF-8 sans
BOM, LF, et une fin de ligne finale. Le JSON utilise `sort_keys=True`, une
indentation de deux espaces et un ordre de listes fixé.

### Format du lockfile

Le schéma `1` contient :

- `generator.name` et `generator.version` ;
- le statut `experimental` ;
- `canonical.path`, `canonical.source_path` et le SHA-256 canonique ;
- deux entrées `adapters` avec chemins, harnesses, stratégies et SHA-256 ;
- `managed_files`, liste exhaustive des trois fichiers de contenu gérés, avec
  chemin, SHA-256, encodage, fins de ligne et convention de fin de fichier ;
- `lockfile`, qui décrit le chemin et les conventions du fichier de contrôle.

Le lockfile n'inclut pas le hash de ses propres octets, ce qui serait une
définition récursive. `check` recalcule à la place l'intégralité de sa structure
et de ses octets déterministes. Toute entrée gérée supplémentaire, clé manquante,
stratégie modifiée, réorganisation JSON ou convention textuelle divergente fait
échouer la vérification.

## Interface, sécurité et codes de sortie

Depuis la racine du repository :

```console
python experiments/kernel-v1/tools/sync_adapters.py plan --target <path>
python experiments/kernel-v1/tools/sync_adapters.py write --target <path>
python experiments/kernel-v1/tools/sync_adapters.py check --target <path>
```

Codes : `0` succès, `2` usage CLI invalide, `3` refus de sécurité ou de propriété,
`4` échec de vérification, `5` erreur d'entrée/sortie.

Le prototype résout la cible explicitement, refuse la racine réelle, bloque les
sorties qui s'échapperaient de la cible et refuse les fichiers ou répertoires de
sortie symboliques. Un fichier de contenu préexistant n'est considéré comme géré
que si le lockfile attendu en prouve la propriété. Sans cette preuve, `write`
échoue avant toute écriture. Une cible contenant un autre fichier non revendiqué
est également refusée par `plan` et `write` dans cette version étroite. Les
contenus sont remplacés depuis un fichier temporaire du même répertoire ; le
lockfile est écrit en dernier.

`plan` et `check` ne créent ni cible, ni répertoire, ni fichier. Les chemins avec
espaces sont couverts par les tests.

## Commandes et résultats

Suite automatisée :

```console
python -B -m unittest discover -s experiments/kernel-v1/tests -v
```

Résultat : 26 tests réussis, 0 échec. Les workspaces de test sont créés par
`tempfile.TemporaryDirectory` hors du repository puis supprimés.

Les validations manuelles complémentaires utilisent elles aussi un répertoire
temporaire hors du repository : `plan` sans écriture, `write`, `check`, second
`write`, recalcul SHA-256 indépendant, altération de `AGENTS.md`, puis échec
attendu de `check` avec le code `4`.

## Propriétés vérifiées

- conformité préalable de la source au hash et aux métadonnées du manifeste ;
- copie exacte source → canon → `AGENTS.md` ;
- import Claude exact et absence de `opencode.json` ;
- JSON stable entre deux cibles distinctes et second `write` sans réécriture ;
- réparation explicite par `write` d'une dérive dont le lock valide prouve la
  propriété, et refus sans mutation lorsque ce lock est incohérent ;
- recalcul indépendant de tous les hashes de contenu revendiqués ;
- détection des fichiers absents, des trois dérives de contenu, d'un lockfile
  incomplet ou falsifié, d'une revendication supplémentaire, d'un BOM et de CRLF ;
- absence d'écriture par `plan`, `check` et les refus de sécurité ;
- refus d'un `AGENTS.md` ou `CLAUDE.md` préexistant sans preuve de gestion ;
- refus de tout autre fichier préexistant non géré, sans écriture partielle ;
- refus absolu de la racine réelle d'EGX_Terminal ;
- aucune sortie partielle lors des erreurs détectables en prévol.

## Propriétés non vérifiées

- découverte réelle, ordre, scope, précédence ou troncature dans un harness ;
- développement effectif de l'import Claude au premier lancement ou après
  compaction ;
- unicité du chargement OpenCode et comportement depuis un sous-répertoire ;
- contenu exact transmis à un modèle par un client ;
- adhérence, réussite, sécurité, coût token, latence ou effet comportemental ;
- résistance à une coupure machine au milieu des remplacements atomiques ;
- compatibilité avec des versions de Python ou OS autres que l'environnement
  observé.

## Génération statique et chargement réel

La génération statique établit l'identité des octets, les chemins de sortie, les
stratégies déclarées et la détection de drift. Elle ne voit pas les instructions
globales ou imbriquées d'un harness, sa recherche depuis le répertoire de
lancement, ses limites de taille, l'ordre final du contexte ou le traitement par
le modèle. Un hash égal est donc une condition d'intégrité, pas une preuve de
chargement ni de comportement.

## Matrice des expériences futures

| Cellule future | Adaptateur à observer | Contrôles de chargement à réaliser | Modèle |
| --- | --- | --- | --- |
| Codex CLI | copie `AGENTS.md` | découverte racine/sous-répertoire, ordre global/local, occurrence unique, contexte injecté si observable | modèle courant précisément fixé |
| Claude Code | import `CLAUDE.md` | résolution relative, premier consentement éventuel, occurrence unique, reprise/compaction | modèle précisément fixé |
| OpenCode | copie commune `AGENTS.md`, sans `opencode.json` | premier match local, lancement imbriqué, absence de double injection, contexte transmis | grand modèle précisément fixé |
| OpenCode ou autre runtime local | même doctrine statique | responsabilité du runtime, template, contexte, occurrence et coût prefill | Qwen exact, taille et quantification fixées |

Qwen reste un modèle à tester derrière OpenCode ou un autre runtime ; aucune
capacité de découverte ne lui est attribuée.

## Risques résiduels

- Un lockfile copié manuellement pourrait revendiquer à tort la propriété de
  chemins existants ; le prototype prouve une structure attendue, pas l'histoire
  humaine du fichier.
- Les remplacements sont raisonnablement atomiques fichier par fichier, pas sous
  forme d'une transaction multi-fichiers.
- L'égalité textuelle n'empêche ni conflit avec d'autres instructions, ni double
  chargement par une configuration externe.
- L'import Claude minimal dépend toujours du comportement d'une version réelle du
  client.
- Le prototype n'a été exercé localement que sous Windows avec Python 3.11.9.

## Prochaine action

Concevoir une mission séparée de validation de chargement, sans promotion : figer
les versions et configurations visibles, générer uniquement dans des fixtures
jetables, capturer les sources réellement chargées lorsque chaque harness le
permet, tester racine et sous-répertoire avec des canaris non comportementaux, et
prouver l'occurrence unique du hash. Cette mission devra commencer par Codex,
puis Claude Code lorsqu'il sera disponible, puis OpenCode ; les essais Qwen
resteront une cellule modèle/runtime distincte. Elle ne devra encore évaluer ni
l'efficacité comportementale du kernel, ni sa promotion.
