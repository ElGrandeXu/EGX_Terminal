# Smoke test OpenCode 1.17.9 + Ollama 0.20.2 + Qwen 3.6 35B

## Statut et portée

- **Date :** 2026-07-20
- **Statut :** **FAIL**
- **OpenCode :** `1.17.9`
- **Runtime local :** Ollama `0.20.2`
- **Modèle demandé :** `qwen3.6:35b`
- **Contexte demandé et chargé :** `16 384` tokens
- **Processus `opencode run` :** un
- **Requêtes OpenCode observées vers le modèle :** zéro
- **Retry :** zéro

Le test a échoué avant l'appel modèle : OpenCode a quitté avec le code `1` en
0,641 s, sans événement JSONL et sans requête `/v1/chat/completions` observée.
La sortie fermée n'a donc pas été produite. Le plafond d'un lancement
d'inférence a interdit toute relance.

Ce résultat valide plusieurs mécanismes préparatoires et de nettoyage, mais ne
valide ni le provider OpenCode, ni la découverte d'`AGENTS.md`, ni la réception
du kernel par Qwen.

## Objectif limité

La mission devait vérifier en un seul smoke run la génération du workspace,
l'isolation d'OpenCode, le provider Ollama loopback, le modèle résolu, la
découverte du kernel, l'absence d'outil et la disparition de tout état. Elle ne
testait ni baseline, ni scope imbriqué, ni précédence, ni tâche de code, ni gain
comportemental.

## Prévol

Le prévol a confirmé :

- répertoire attendu, branche `main` et worktree initial propre ;
- HEAD `28ba0c86502a080805d2adf5b3ed9e7e4ca090a2`, sujet
  `test: validate local Qwen runtime` ;
- Python `3.11.9`, OpenCode `1.17.9` et Ollama `0.20.2` ;
- binaire OpenCode de 165 154 696 octets, SHA-256
  `65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6` ;
- lanceur OpenCode SHA-256
  `7dc7f9e963b88bbfb7a529a82d1922adf642d386f096fc250e891e374884ee8e` ;
- modèle local GGUF `qwen3.6:35b`, architecture `qwen35moe`, 36,0 B,
  quantification `Q4_K_M` ;
- digest déclaré du blob modèle
  `sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d` ;
- digest calculé du manifest
  `sha256:07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522` ;
- tous les blobs requis présents, sans téléchargement ni rehash des 23,9 Go ;
- aucun processus Ollama ou OpenCode persistant, port 11434 libre et aucun
  calcul GPU actif ;
- GPU NVIDIA GeForce RTX 4090, 24 564 MiB, usage initial 1 069 MiB, soit
  7 MiB sous la baseline de Mission 11 ; marge projetée après le delta de
  21 748 MiB : 1 322 MiB, supérieure au seuil de 512 MiB.

Les processus très courts utilisés par les commandes de version ne sont pas des
processus d'inférence. Le contrôle séquentiel effectué après leur terminaison a
confirmé l'absence de processus préexistant.

## Probe et protocole

[`probe_opencode.py`](../tools/probe_opencode.py) utilise Python 3 et uniquement
la bibliothèque standard. Il importe les modules locaux
[`sync_adapters.py`](../tools/sync_adapters.py) et
[`probe_ollama.py`](../tools/probe_ollama.py) pour réutiliser respectivement la
génération statique et l'identité, le serveur, le chargement, les mesures, le
déchargement et l'arrêt Ollama.

```text
python -B experiments/kernel-v1/tools/probe_opencode.py plan
python -B experiments/kernel-v1/tools/probe_opencode.py run --acknowledge-local-inference
```

Le mode `plan` a retourné `READY` avec zéro processus, zéro serveur, zéro
chargement et zéro requête. Le mode `run` impose un budget d'un processus
`opencode run`, d'une requête modèle et de zéro retry. Le nettoyage Ollama et
OpenCode est exécuté dans les chemins `finally`.

## Workspace jetable

Le probe a exécuté les opérations logiques `sync_adapters.py write` puis
`sync_adapters.py check` dans un `TemporaryDirectory`. L'état vérifié avant
OpenCode contenait seulement :

```text
workspace/
├── .egx/doctrine-lock.json
├── doctrine/KERNEL.md
├── AGENTS.md
└── CLAUDE.md
```

Le canon et `AGENTS.md` étaient identiques octet pour octet au candidat, SHA-256
`a70b983003abcb59bcb53b3dba5637c6105d85fe3fc47fa5546d668b5d4d1431`.
`CLAUDE.md` contenait exactement `@doctrine/KERNEL.md`, le lockfile avait le
schéma 1, aucun `opencode.json` ni fichier non géré n'existait. Le snapshot et le
`check` après OpenCode étaient inchangés et réussis.

## Isolation OpenCode

Une racine temporaire unique contenait workspace, home, config, data, state,
cache, temp, caches npm/Bun et stockage de session. L'environnement enfant était
construit par allowlist et fixait dans cette racine :

- `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA` ;
- les quatre racines `XDG_*` ;
- `TMP`, `TEMP`, caches npm et Bun ;
- `OPENCODE_CONFIG_DIR` ;
- `OPENCODE_DB=:memory:`.

Aucune authentification ni configuration globale n'a été copiée. La
configuration inline fixait `autoupdate:false`, partage et snapshot désactivés,
compaction désactivée, `subagent_depth:0`, `mcp:{}`, `plugin:[]`,
`instructions:[]` et `permission:{"*":"deny"}`. Les variables 1.17.9
désactivaient plugins par défaut, skills externes, téléchargement LSP, fetch de
modèles, auto-update et fallback Claude. Les endpoints OTLP étaient absents et
le SDK OTLP désactivé.

Les proxies HTTP, HTTPS et ALL de l'enfant pointaient vers un endpoint loopback
inactif ; `NO_PROXY` valait seulement `localhost,127.0.0.1`. Cette défense ne
constitue pas une sandbox réseau OS.

## Provider et modèle

La configuration ne déclarait que `local-ollama`, avec le package intégré
`@ai-sdk/openai-compatible`, `baseURL` fixé à
`http://127.0.0.1:11434/v1`, et une allowlist contenant ce seul provider.
`model`, `small_model` et la CLI demandaient tous
`local-ollama/qwen3.6:35b`. Le contexte déclaré était 16 384 et la sortie bornée
à 64 tokens. Aucune clé, même factice, n'était fournie.

Ollama a chargé une fois `qwen3.6:35b`. `/api/ps` a confirmé le contexte exact,
le digest de manifest attendu, 27 188 902 304 octets chargés, dont
22 584 406 272 en VRAM et 4 604 496 032 côté CPU/RAM.

**Limite essentielle :** cet état prouve le préchargement du modèle possédé par
le probe. Comme OpenCode n'a émis aucune requête, il ne prouve pas que le
provider ou le modèle ont été effectivement résolus par OpenCode.

## Unique appel OpenCode

Commande normalisée :

```text
opencode.exe run --pure --dir <temporary-workspace> \
  --model local-ollama/qwen3.6:35b --format json <closed-prompt>
```

Prompt exact :

```text
Do not use tools or read files. Based only on project instructions already supplied before this message, output only their first eight words.
```

| Champ | Résultat |
| --- | --- |
| Sortie attendue | `Understand the requested outcome, constraints, relevant work, and` |
| Sortie observée | chaîne vide |
| Correspondance exacte | non |
| Code de sortie OpenCode | `1` |
| Durée murale | 0,641 s |
| Événements JSONL | 0 |
| Stderr | présent, non conservé |
| Requêtes `/v1/chat/completions` | 0 |
| Retry | 0 |

Le flux stderr brut n'a pas été persisté, conformément au protocole. La version
du probe exécutée enregistrait seulement sa présence ; la cause précise de la
sortie 1 est donc inconnue. Le probe a ensuite été renforcé pour classifier une
future erreur sans conserver son contenu, mais aucune seconde exécution n'a été
faite.

## Outils, permissions et instructions

Aucun événement d'outil, de permission, de raisonnement ou de sous-agent n'a été
observé. Cette absence est triviale ici : aucun événement JSONL et aucune
requête modèle n'ont été produits. Elle ne démontre pas encore le comportement
des permissions face à une réponse du modèle.

Le fichier `AGENTS.md` attendu existait et était intact dans le répertoire de
lancement. En revanche, l'absence d'appel modèle empêche de conclure qu'OpenCode
l'a découvert ou injecté. Qwen n'a pas reçu le kernel dans ce run.

## Tokens, latence et débit

OpenCode n'a exposé aucune métrique de tokens. `prompt_eval_count`, `eval_count`,
durée d'évaluation et vitesse sont donc inconnus. Le préchargement sans
génération a duré 4,265 s et n'a exposé ni `load_duration` ni `eval_count`.
Aucun débit d'inférence ne peut être calculé honnêtement.

## RAM et VRAM

| Moment | RAM utilisée | RAM disponible | VRAM utilisée | VRAM disponible |
| --- | ---: | ---: | ---: | ---: |
| Avant chargement | 12,558 GiB | 51,284 GiB | 1 069 MiB | 23 070 MiB |
| Modèle chargé | 17,395 GiB | 46,447 GiB | 23 339 MiB | 800 MiB |
| Après tentative OpenCode | non capturé dans ce chemin d'erreur | non capturé | non capturé | non capturé |
| Après nettoyage | 12,572 GiB | 51,270 GiB | 1 069 MiB | 23 070 MiB |

Le delta chargé est de 4,837 GiB de RAM utilisée et 21 748 MiB de VRAM. Le
snapshot après tentative manquait dans le chemin d'erreur exécuté ; le probe a
été corrigé après le run pour le capturer lors d'une future erreur, sans
relancer cette mission.

## Connexions observées

Le moniteur a suivi le PID OpenCode possédé et ses descendants avec des
échantillons `Get-NetTCPConnection`. Il n'a observé ni connexion loopback ni
connexion non-loopback pendant les 0,641 s du processus. Les logs Ollama n'ont
contenu aucune route `/v1/chat/completions`.

Cette surveillance n'est pas une packet capture, ni une règle de blocage du
pare-feu. Sa cadence et la brièveté du processus peuvent manquer une tentative
très courte. Les proxies enfants, l'allowlist et les désactivations applicatives
complétaient la mesure, mais l'absence observée ne constitue pas une preuve
exhaustive d'absence de paquet.

## Écritures temporaires

Treize fichiers existaient sous la racine jetable avant suppression : les
quatre fichiers générés du workspace, deux `.gitignore` internes OpenCode, un log
OpenCode, deux logs Ollama et quatre fichiers de deux locks OpenCode
(`heartbeat` et `meta.json`). Aucun fichier de base de données ou transcript brut
n'a été observé. Les noms de session et le contenu des logs n'ont pas été
conservés.

Toutes ces écritures étaient sous le `TemporaryDirectory`. Aucune écriture du
run n'a touché la racine active.

## Nettoyage

Le bloc de nettoyage puis le contrôle externe ont confirmé :

- modèle explicitement déchargé et `/api/ps` vide ;
- serveur Ollama possédé arrêté ;
- processus OpenCode possédé et descendants disparus ;
- aucun processus Ollama ou OpenCode restant ;
- port 11434 libéré ;
- racine temporaire et logs supprimés ;
- model store inchangé ;
- VRAM revenue exactement de 1 069 à 1 069 MiB ;
- RAM revenue de 12,558 à 12,572 GiB, variation cohérente avec l'activité
  générale ;
- repository inchangé pendant le run.

Aucun modèle n'a été supprimé.

## Faits, inférences et inconnues

### Faits

- `sync_adapters.py write` et `check` ont produit et validé le workspace exact.
- L'environnement OpenCode connu était entièrement dirigé vers la racine
  temporaire et la DB demandée était en mémoire.
- Ollama a chargé une fois le modèle exact à 16 384 tokens sur loopback.
- Un seul processus `opencode run` a été lancé, sans retry.
- OpenCode a quitté avec le code 1, sans JSONL et sans requête modèle observée.
- Aucun tool call, événement de permission, egress non-loopback ou changement de
  workspace n'a été observé.
- Modèle, serveur, enfants, port et racine temporaire ont été nettoyés.

### Inférences limitées

- La sortie très rapide avant toute route Ollama est compatible avec un échec
  d'initialisation locale d'OpenCode, de configuration ou de provider. Les
  preuves conservées ne permettent pas de choisir entre ces causes.
- L'absence de fichier DB et la suppression des racines rendent une reprise de
  session improbable, sans prouver toutes les écritures possibles hors des
  chemins inspectés.

### Inconnues

- cause exacte du code 1 ;
- provider et modèle résolus par OpenCode ;
- découverte et ordre d'`AGENTS.md` ;
- présence effective du kernel dans le prompt envoyé au modèle ;
- comportement des permissions et outils lors d'une génération ;
- tokens, vitesse et métriques Ollama d'une requête OpenCode ;
- absence exhaustive d'egress au niveau paquet.

## Conclusion et décision recommandée

Le smoke est **FAIL** pour la combinaison exacte OpenCode `1.17.9` + Ollama
`0.20.2` + `qwen3.6:35b` à 16 384 tokens. Il ne justifie ni activation, ni
promotion, ni déclaration de compatibilité runtime OpenCode.

La stratégie de copie générée commune dans `AGENTS.md` reste un candidat
d'adaptateur cohérent statiquement, mais son statut runtime OpenCode demeure
**non validé**. Ne pas ajouter `opencode.json`, ne pas promouvoir le kernel et ne
pas commencer baseline, scope ou précédence.

## Prochaine expérience proposée

Mener une mission diagnostique **sans inférence** sur OpenCode 1.17.9 : recréer
le même environnement temporaire, valider la configuration résolue et
l'initialisation du provider avec les commandes debug locales autorisées, puis
capturer uniquement une catégorie d'erreur expurgée et les écritures/connexions.
Une nouvelle autorisation distincte devra être obtenue avant tout second
`opencode run` ou appel modèle.
