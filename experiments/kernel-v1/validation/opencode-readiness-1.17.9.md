# Readiness OpenCode 1.17.9 et runtimes locaux

## 1. Objectif et périmètre

- **Date d'observation et de consultation :** 2026-07-20.
- **Client ciblé :** OpenCode `1.17.9` exactement.
- **Objet :** déterminer si une future campagne de découverte du kernel peut
  utiliser OpenCode avec un modèle local, dans des fixtures jetables, sans
  configuration utilisateur, session persistante, outil mutateur ou provider
  distant involontaire.
- **Résultat de readiness :** **BLOCKED** pour une campagne runtime immédiate.
- **Motifs principaux :** aucun serveur local ne répond actuellement ; le seul
  candidat Qwen identifié n'est pas chargé ; son contexte effectif n'est pas
  établi ; et la configuration OpenCode seule ne constitue pas une barrière
  réseau suffisante.

Cette mission n'a exécuté ni `opencode run`, ni TUI, ni prompt, ni embedding. Elle
n'a installé, démarré, arrêté, chargé ou téléchargé aucun composant. Elle ne
valide donc encore ni la découverte runtime OpenCode, ni le couple OpenCode +
Qwen, ni l'effet comportemental du kernel.

Les étiquettes employées sont :

- **Documenté :** documentation officielle actuelle ;
- **Confirmé 1.17.9 :** aide locale ou source du tag installé ;
- **Observé localement :** commande ou état local non mutant ;
- **Inféré :** conséquence raisonnable qui reste à vérifier ;
- **Inconnu :** aucune preuve suffisante ;
- **À tester :** gate d'une future mission runtime.

## 2. Version et identité du binaire

PowerShell résout `opencode` vers le lanceur normalisé
`<NPM_GLOBAL>/opencode.ps1`. Ce lanceur appelle le binaire
`<NPM_GLOBAL>/node_modules/opencode-ai/bin/opencode.exe`.

| Élément | Observation locale |
| --- | --- |
| `opencode --version` | `1.17.9`, code `0` |
| Lanceur PowerShell | SHA-256 `7dc7f9e963b88bbfb7a529a82d1922adf642d386f096fc250e891e374884ee8e` |
| Binaire cible | 165 154 696 octets |
| SHA-256 du binaire cible | `65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6` |
| Release officielle | tag immuable `v1.17.9`, commit `5c23e88419c4743b9be42cea132f2fb1e6cb63ff` |

Les chemins réels contenaient un nom utilisateur ; ils ne sont ni reproduits ni
committés. Le hash local identifie les octets observés, mais il n'a pas été
comparé à une somme publiée de l'asset Windows.

## 3. Documentation officielle consultée

Sources primaires consultées le 2026-07-20 :

- documentation actuelle :
  [CLI](https://opencode.ai/docs/cli/),
  [configuration](https://opencode.ai/docs/config/),
  [règles](https://opencode.ai/docs/rules/),
  [permissions](https://opencode.ai/docs/permissions/),
  [outils](https://opencode.ai/docs/tools/),
  [plugins](https://opencode.ai/docs/plugins/),
  [modèles](https://opencode.ai/docs/models/) et
  [providers](https://opencode.ai/docs/providers/) ;
- release :
  [`v1.17.9`](https://github.com/anomalyco/opencode/releases/tag/v1.17.9) et
  [commit de release](https://github.com/anomalyco/opencode/commit/5c23e88419c4743b9be42cea132f2fb1e6cb63ff) ;
- source exacte `v1.17.9` :
  [`session/instruction.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/session/instruction.ts),
  [`cli/cmd/run.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/cli/cmd/run.ts),
  [`config/config.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/config/config.ts),
  [`config/paths.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/config/paths.ts),
  [`provider/provider.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/provider/provider.ts),
  [`plugin/index.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/plugin/index.ts),
  [`effect/runtime-flags.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/effect/runtime-flags.ts),
  [`core/global.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/global.ts),
  [`core/flag/flag.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/flag/flag.ts),
  [`core/database/database.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/database/database.ts),
  [`core/models-dev.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/models-dev.ts),
  [`core/npm.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/npm.ts),
  [`installation/index.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/installation/index.ts) et
  [`core/observability/otlp.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/observability/otlp.ts) ;
- runtimes locaux : documentation officielle OpenCode pour
  [llama.cpp](https://opencode.ai/docs/providers/#llama-cpp),
  [LM Studio](https://opencode.ai/docs/providers/#lm-studio) et
  [Ollama](https://opencode.ai/docs/providers/#ollama), documentation Ollama de
  [compatibilité OpenAI](https://docs.ollama.com/api/openai-compatibility), fiche
  officielle [`qwen3.6:35b`](https://ollama.com/library/qwen3.6:35b), et
  documentation LM Studio des
  [endpoints OpenAI compatibles](https://lmstudio.ai/docs/developer/openai-compat).

La documentation `latest` est datée du jour, mais n'est pas assimilée au tag.
Par exemple, elle décrit `--auto`, absent de l'aide locale `run` 1.17.9, qui
expose à la place `--dangerously-skip-permissions`.

## 4. Matrice documentation / version installée

| Sujet | Documentation actuelle | Preuve 1.17.9 installée ou tag | Statut |
| --- | --- | --- | --- |
| Exécution non interactive | `opencode run [message..]` | aide locale et `run.ts` concordants | **Confirmé 1.17.9** |
| Modèle explicite | `--model provider/model` | aide locale et parseur `run.ts` | **Confirmé 1.17.9** |
| Sortie structurée | `--format json`, événements bruts | aide locale et émission JSONL dans `run.ts` | **Confirmé 1.17.9** |
| Reprise | `--continue`, `--session`, `--fork` | aide locale et sélection de session dans `run.ts` | **Confirmé 1.17.9** |
| Nouvelle session | implicite sans option de reprise | `run.ts` crée une session ; aucun flag `--ephemeral` | **Confirmé 1.17.9** |
| Plugins externes | `--pure` | aide locale ; le tag omet `cfg.plugin_origins` si `pure` | **Confirmé 1.17.9** |
| Plugins intégrés | variable `OPENCODE_DISABLE_DEFAULT_PLUGINS` | lue dans `runtime-flags.ts` | **Confirmé 1.17.9** |
| Permissions | `allow`, `ask`, `deny`, wildcard `*` | configuration et source du tag ; defaults permissifs | **Confirmé 1.17.9** |
| Auto-approbation | docs : `--auto` | absent de l'aide locale ; `--dangerously-skip-permissions` existe | **Divergence** |
| Provider allowlist | `enabled_providers` | filtre final dans `provider.ts` | **Confirmé 1.17.9** |
| Catalogue distant | `OPENCODE_DISABLE_MODELS_FETCH` | bloque le fetch `models.dev` dans `models-dev.ts` | **Confirmé 1.17.9** |
| Mise à jour | `autoupdate:false` et `OPENCODE_DISABLE_AUTOUPDATE` | variable présente dans le tag ; chemins réseau d'update identifiés | **Confirmé 1.17.9**, enforcement à tester |
| Configuration | sources fusionnées, non remplacées | ordre et fusion présents dans `config.ts` | **Confirmé 1.17.9** |
| Data/cache/config/state | chemins XDG | `global.ts` construit les quatre chemins depuis `xdg-basedir` | **Confirmé par source**, non exposé par l'aide |
| Session en mémoire | non documenté | `OPENCODE_DB=:memory:` accepté dans `database.ts` | **Confirmé par source**, à tester |
| Télémétrie | aucun flag général documenté | export OTLP seulement si `OTEL_EXPORTER_OTLP_ENDPOINT` est défini | **Confirmé par source limitée** |
| Provider local OpenAI-compatible | exemples Ollama, LM Studio, llama.cpp | package intégré `@ai-sdk/openai-compatible` dans `provider.ts` | **Confirmé 1.17.9** |

## 5. Fonctionnement connu de la découverte d'instructions

### Documenté actuellement

- OpenCode remonte depuis le répertoire courant pour chercher les règles projet.
- `AGENTS.md` gagne sur `CLAUDE.md` comme fallback local.
- Le global OpenCode est `~/.config/opencode/AGENTS.md`; le fallback Claude
  global est `~/.claude/CLAUDE.md` sauf désactivation.
- Le premier match gagne dans chaque catégorie.
- `opencode.json.instructions` accepte chemins et globs, y compris des URL ; ces
  fichiers sont combinés avec le fichier découvert.
- Une référence écrite dans `AGENTS.md` n'est pas développée automatiquement.

### Confirmé dans le tag `v1.17.9`

`session/instruction.ts` fixe l'ordre projet `AGENTS.md`, `CLAUDE.md`, puis
`CONTEXT.md` déprécié. Le premier type ayant un match interrompt la recherche.
Le global OpenCode précède le fallback Claude global. Les fichiers
`instructions` locaux sont ajoutés ; les URL configurées peuvent être récupérées
avec un timeout de cinq secondes.

Le tag contient aussi un comportement plus précis que la page de règles : quand
un fichier est lu par l'agent, `resolve()` remonte depuis ce fichier vers la
racine du projet et peut joindre un fichier d'instruction imbriqué non déjà
chargé, une fois par message. Ce chargement dynamique n'est pas encore confirmé
par canari et ne doit pas être confondu avec le premier fichier système trouvé au
lancement.

### À tester

- point de départ exact dans une fixture Git et arrêt à la worktree ;
- `AGENTS.md` racine, fallback `CLAUDE.md`, et précédence quand les deux existent ;
- lancement depuis un sous-répertoire ;
- chargement dynamique d'une instruction imbriquée après lecture d'un fichier ;
- combinaison et ordre effectif de `instructions` avec `AGENTS.md` ;
- occurrence unique du kernel généré, contexte exact et éventuelle troncature.

## 6. Surface CLI non interactive

Les seules commandes OpenCode exécutées pendant cette mission sont des aides ou
la version :

```text
opencode --version
opencode --help
opencode run --help
opencode models --help
opencode debug --help
opencode debug paths --help
opencode session --help
opencode providers --help
opencode agent --help
opencode mcp --help
opencode serve --help
opencode export --help
opencode plugin --help
```

Toutes ont retourné `0`. Les éléments pertinents de `run` sont :

- message positionnel optionnel `message..`, tableau vide par défaut ;
- `--command <command>`, qui réinterprète le message comme arguments, à exclure
  du protocole fermé ;
- `--model provider/model` ;
- `--format default|json`, défaut `default` ;
- `--dir <directory>` ;
- `--continue`, `--session`, `--fork` pour la reprise ;
- `--share` pour le partage ;
- `--attach` pour joindre un serveur ;
- `--interactive`, désactivé par défaut, et `--demo`, à exclure ;
- `--dangerously-skip-permissions`, à proscrire.

Le JSON est du JSONL d'événements horodatés, avec `sessionID`, événements de
texte, raisonnement, étapes, outils et erreurs. Le futur parseur devra refuser
tout événement d'outil ou de permission, conserver seulement résultat normalisé,
métriques, code de sortie et verdict, puis abandonner le flux brut.

`opencode models` n'a pas été exécuté : la source 1.17.9 montre qu'il initialise
les providers et peut rafraîchir `models.dev`; il n'est donc pas requis pour un
prévol sans réseau. `opencode debug config` et `opencode debug paths` n'ont pas
été exécutés, car ils auraient chargé ou révélé l'état global actuel.

## 7. Stratégie d'isolation

La future mission doit créer un unique `TemporaryDirectory` contenant :

```text
<temp>/
├── fixture/            # repository Git jetable et working directory
├── home/               # home logique jetable et fallbacks globaux
├── config/             # OPENCODE_CONFIG_DIR
├── xdg-config/
├── xdg-data/
├── xdg-cache/
├── xdg-state/
├── npm-cache/
└── tmp/
```

Le processus enfant doit recevoir avant son démarrage :

| Variable | Valeur future |
| --- | --- |
| `HOME`, `USERPROFILE` | `<temp>/home` |
| `XDG_CONFIG_HOME` | `<temp>/xdg-config` |
| `XDG_DATA_HOME` | `<temp>/xdg-data` |
| `XDG_CACHE_HOME` | `<temp>/xdg-cache` |
| `XDG_STATE_HOME` | `<temp>/xdg-state` |
| `TEMP`, `TMP` | `<temp>/tmp` |
| `OPENCODE_CONFIG_DIR` | `<temp>/config` |
| `OPENCODE_DB` | `:memory:` |
| `NPM_CONFIG_CACHE` | `<temp>/npm-cache` |
| `NPM_CONFIG_OFFLINE` | `true` |

`global.ts` calcule data, cache, config et state au chargement du module : les
variables XDG doivent donc être positionnées dans l'environnement enfant avant
l'exécution. `OPENCODE_CONFIG_DIR` seul ne déplace ni data, ni cache, ni state.

Le processus doit recevoir un environnement construit par allowlist, pas une
copie aveugle de l'environnement parent : omettre credentials de providers,
tokens, variables cloud, proxies et variables OTLP. `HOME` et `USERPROFILE`
doivent tous deux pointer vers le home enfant avant le chargement du client,
notamment pour isoler les fallbacks Claude. Aucun `auth.json` ni secret global
ne sera lu ou copié. La fixture Git, la configuration, le home logique et toutes
les sorties appartiendront au même répertoire temporaire, supprimé après
snapshot final.

Limite : le tag crée des répertoires et logs au démarrage, et son chargeur de
configuration peut préparer `@opencode-ai/plugin` via npm dans chaque répertoire
de config, même si aucun plugin externe n'est ensuite chargé. `--pure` ne prouve
pas l'absence de cette préparation. `NPM_CONFIG_OFFLINE` et l'isolation XDG
bornent la tentative, mais seule une barrière d'egress et un snapshot des écritures
peuvent établir le résultat.

## 8. Stratégie de permissions et outils

Le futur enfant doit cumuler :

- `--pure` ;
- `OPENCODE_DISABLE_DEFAULT_PLUGINS=1` ;
- `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` ;
- `OPENCODE_DISABLE_LSP_DOWNLOAD=1` ;
- `permission: { "*": "deny" }` dans la configuration inline ;
- `OPENCODE_PERMISSION={"*":"deny"}` comme dernière surcharge connue du tag ;
- `subagent_depth: 0`, `mcp: {}` et `snapshot: false` ;
- absence de `--dangerously-skip-permissions` ;
- arrêt de campagne au premier événement tool/permission ou à la première
  mutation de fixture.

Les permissions gouvernent les outils proposés au modèle, pas les écritures
internes du client (DB, logs, cache, préparation npm). Un snapshot avant/après de
la fixture et de toutes les racines temporaires reste nécessaire. Il ne prouve
pas à lui seul l'absence d'écriture ailleurs ; une surveillance de processus ou
un sandbox OS doit compléter la mesure.

## 9. Stratégie anti-provider-distant

La défense en profondeur future est :

1. aucune authentification copiée et environnement sans clé de provider ;
2. `enabled_providers: ["local-ollama"]` ;
3. un seul provider configuré, avec `baseURL` littéral
   `http://127.0.0.1:11434/v1` ;
4. `model` et `small_model` fixés au même identifiant local ;
5. répétition de `--model local-ollama/qwen3.6:35b` sur la ligne de commande ;
6. `OPENCODE_DISABLE_MODELS_FETCH=1` ;
7. `share: "disabled"`, `mcp: {}`, aucune URL dans `instructions` ;
8. variables proxy supprimées et `NO_PROXY=127.0.0.1,localhost` ;
9. contrôle d'egress au niveau du processus : loopback seulement, toute autre
   destination refusée et journalisée.

L'allowlist provider est bien appliquée dans `provider.ts`, mais elle n'est pas
une sandbox réseau : l'update, le catalogue, un chargement de dépendance, une
configuration managée ou un plugin sont des chemins distincts. La campagne ne
sera donc `GO` qu'avec une barrière externe qui autorise uniquement le loopback.

## 10. Télémétrie et mise à jour

### Mise à jour

La documentation indique que les mises à jour automatiques sont actives au
démarrage et fournit deux mécanismes : `autoupdate: false` et
`OPENCODE_DISABLE_AUTOUPDATE=1`. Les deux doivent être appliqués. La source
1.17.9 contient des accès aux registries et à GitHub pour déterminer la dernière
version ; l'egress loopback-only doit rendre toute régression observable et
inoffensive.

### Télémétrie

Aucun flag général « no telemetry » n'est documenté. Le pipeline OTLP inspecté
dans `core/observability/otlp.ts` ne crée logger ou exporter que lorsque
`OTEL_EXPORTER_OTLP_ENDPOINT` existe. Le futur environnement doit supprimer :

```text
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS
OTEL_RESOURCE_ATTRIBUTES
```

Cela confirme l'absence d'export OTLP configuré dans le chemin inspecté, pas
l'absence exhaustive de toute communication. Le blocage réseau externe reste la
preuve décisive.

## 11. Runtimes locaux détectés

| Runtime | Commande | Processus | Endpoint interrogé | Résultat |
| --- | --- | --- | --- | --- |
| Ollama | trouvé ; client `0.20.2` | aucun avant/après | `ollama list` a tenté uniquement `127.0.0.1:11434` | connexion refusée, code `1` |
| LM Studio / `lms` | absent du `PATH` | aucun processus ciblé | aucun | non détecté |
| vLLM | absent du `PATH` | aucun processus ciblé | aucun | non détecté |
| SGLang | absent du `PATH` | aucun processus ciblé | aucun | non détecté |
| llama.cpp `llama-server` | absent du `PATH` | aucun processus ciblé | aucun | non détecté |

Il n'y a eu aucun scan de ports. Aucun service n'a été lancé. Le refus de
connexion prouve seulement qu'aucun serveur Ollama n'écoutait sur l'endpoint
officiel au moment de l'observation.

## 12. Candidats Qwen détectés

La recherche a été limitée aux manifests dont le chemin contient `qwen`; aucun
inventaire des autres modèles personnels n'est publié.

| Propriété | Observation locale non inférentielle |
| --- | --- |
| Identifiant | `qwen3.6:35b` |
| Runtime | Ollama |
| Installation | manifest présent ; blob modèle présent |
| Chargement actuel | non chargé, déduit de l'absence de processus Ollama |
| Format / famille | GGUF / `qwen35moe` |
| Type / quantification | `36.0B` / `Q4_K_M` |
| Taille déclarée et réelle du blob | 23 938 321 664 octets |
| Digest du blob | `sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d` |
| Endpoint futur | `http://127.0.0.1:11434/v1` |
| API | OpenAI-compatible ; Ollama expose aussi son API native |
| Contexte | **inconnu** dans les métadonnées consultées |

Le digest du manifest/config et la taille du blob ont été lus ; le hash du blob
de 23,9 Go n'a pas été recalculé. La fiche Ollama officielle concorde sur 24 GB,
36B et `Q4_K_M`. Le contexte effectif, le template, le support d'outils avec
OpenCode, la mémoire nécessaire et la vitesse restent à établir.

## 13. Candidat recommandé pour le premier test

Le seul candidat admissible identifié est `qwen3.6:35b` via Ollama. Il est
recommandé **conditionnellement** pour un unique smoke test OpenCode + Qwen,
après démarrage externe et explicitement autorisé d'Ollama, vérification de
`/api/tags` ou `/v1/models`, fixation du contexte et activation d'un confinement
loopback-only.

Les niveaux de preuve devront rester séparés :

1. **Harness OpenCode :** un modèle local quelconque peut confirmer la
   découverte, la structure JSONL et les garde-fous du client.
2. **OpenCode + Qwen :** `qwen3.6:35b` doit répondre via le provider local exact,
   sans prouver l'effet du kernel.
3. **Kernel + Qwen :** une campagne comportementale avec baseline et seuils est
   une mission ultérieure distincte.

## 14. Configuration éphémère future, sans secret

Illustration seulement, non écrite ni exécutée pendant cette mission :

```json
{
  "autoupdate": false,
  "share": "disabled",
  "snapshot": false,
  "subagent_depth": 0,
  "compaction": {
    "auto": false,
    "prune": false
  },
  "permission": {
    "*": "deny"
  },
  "mcp": {},
  "plugin": [],
  "instructions": [],
  "enabled_providers": ["local-ollama"],
  "model": "local-ollama/qwen3.6:35b",
  "small_model": "local-ollama/qwen3.6:35b",
  "provider": {
    "local-ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama loopback",
      "options": {
        "baseURL": "http://127.0.0.1:11434/v1"
      },
      "models": {
        "qwen3.6:35b": {
          "name": "Qwen3.6 35B Q4_K_M local",
          "limit": {
            "context": "<VERIFIED_CONTEXT_TOKENS>",
            "output": "<PRESET_OUTPUT_CEILING>"
          }
        }
      }
    }
  }
}
```

Les placeholders doivent être remplacés par des entiers vérifiés avant parsing
par OpenCode. La valeur JSON peut être fournie via `OPENCODE_CONFIG_CONTENT` ;
aucun `opencode.json` n'est nécessaire dans EGX_Terminal ou dans le home global.

Pour une campagne limitée à `AGENTS.md`, définir
`OPENCODE_DISABLE_CLAUDE_CODE=1`. Un test séparé du fallback projet
`CLAUDE.md` exige un home enfant jetable et la réactivation contrôlée du prompt
Claude ; il ne doit jamais exposer le home réel.

## 15. Commandes futures proposées mais non exécutées

Prévol local sans inférence, seulement après détection d'un processus Ollama :

```text
GET http://127.0.0.1:11434/api/tags
GET http://127.0.0.1:11434/v1/models
```

Commande normalisée d'un futur appel unique :

```text
opencode run --pure --dir <temp>/fixture \
  --model local-ollama/qwen3.6:35b \
  --format json "<closed-canary-prompt>"
```

Interdits dans ce protocole : `--command`, `--continue`, `--session`, `--fork`,
`--share`, `--attach`, `--interactive`, `--demo`,
`--dangerously-skip-permissions`, `models --refresh`, toute URL d'instruction et
toute commande de gestion de modèle.

Avant le premier prompt, une future mission peut exécuter `opencode debug paths`
et `opencode debug config` **uniquement dans l'environnement enfant entièrement
isolé**, puis vérifier que toutes les valeurs publiées sont temporaires et que le
provider/modèle résolus sont exacts. Ces commandes n'ont pas été exécutées ici.

## 16. Nombre maximal d'appels recommandé

- **Gate initial :** un seul appel smoke OpenCode + Qwen.
- **Campagne de découverte si le smoke passe :** maximum six appels réussis,
  sept tentatives totales, un seul retry d'infrastructure.
- **Arrêt immédiat :** baseline invalide, provider/modèle inattendu, sortie non
  parsable, outil/permission, mutation, egress non-loopback, reprise de session ou
  code non nul.

Les six cellules maximales sont : baseline, `AGENTS.md`, fallback `CLAUDE.md`,
précédence des deux, lancement imbriqué, et combinaison `instructions` sans
duplication. Une campagne comportementale n'est pas incluse.

## 17. Critères GO / BLOCKED pour la mission runtime

### GO

Tous les critères suivants sont requis :

- OpenCode et son SHA-256 correspondent à ce rapport ;
- un processus Ollama préexistant répond uniquement sur loopback ;
- `qwen3.6:35b` est listé, son digest/quantification/contexte sont enregistrés ;
- le provider et les deux modèles configurés valent exactement le candidat local ;
- config, data, cache, state, DB, temp, npm et working directory sont jetables ;
- aucune auth ou configuration globale n'est lue ou copiée ;
- plugins externes et intégrés sont désactivés ; permissions `deny` résolues ;
- update, partage, catalogue distant, LSP download et OTLP sont désactivés ;
- une barrière vérifiée refuse toute connexion non-loopback ;
- le harness préenregistre budget, cas, sorties attendues et critères d'arrêt.

### BLOCKED actuel

- aucun serveur Ollama actif ;
- modèle Qwen installé mais non chargé ;
- contexte effectif inconnu ;
- absence de preuve runtime de l'isolation XDG/DB/config ;
- absence de barrière d'egress validée ;
- préparation npm automatique possible dans les répertoires de config ;
- aucune preuve d'unicité ou de précédence OpenCode par canari.

## 18. Risques résiduels

- Les sources de configuration sont fusionnées. Une configuration managée peut
  avoir une priorité supérieure à l'inline ; elle n'a pas été inspectée.
- Les permissions ne bornent pas les écritures internes d'OpenCode.
- `--pure` ne désactive pas les plugins intégrés et ne prouve pas l'absence de
  préparation npm ; les variables supplémentaires sont nécessaires.
- `enabled_providers` filtre la disponibilité finale, mais le code initialise
  auparavant certains mécanismes de providers ; seule la barrière réseau interdit
  matériellement un egress.
- `OPENCODE_DB=:memory:` est une interface source non documentée, susceptible de
  changer ; elle doit être validée sur chaque version.
- Le JSONL expose un `sessionID`; session en mémoire ne signifie pas absence de
  tous logs ou artefacts.
- Le candidat de 23,9 Go peut être lent ou dépasser les ressources disponibles.
- Le contexte, le template et les appels d'outils de `qwen3.6:35b` ne sont pas
  établis.
- Une réponse canari prouve une transmission dans un cas, pas le contexte système
  complet ni l'adhérence générale.

## 19. Faits, inférences et inconnues

### Faits

- OpenCode `1.17.9` et son binaire exact sont identifiés.
- `run --format json --model provider/model --dir <path>` existe.
- aucune option éphémère native n'est exposée ; `run` crée une session.
- `OPENCODE_DB=:memory:` existe dans la source 1.17.9.
- les quatre racines XDG pilotent les chemins connus de config/data/cache/state.
- les permissions par défaut sont permissives ; wildcard `deny` est disponible.
- Ollama `0.20.2` est installé, mais son endpoint était inactif.
- `qwen3.6:35b` Q4_K_M est présent sur disque et non chargé.

### Inférences

- XDG temporaire + DB mémoire + suppression du répertoire devraient éliminer la
  reprise entre processus dans le protocole prévu.
- allowlist provider + modèle CLI réduisent fortement le fallback distant.
- un blocage d'egress loopback-only transforme les chemins réseau inconnus en
  échecs observables plutôt qu'en fuite distante.

### Inconnues / à tester

- ensemble exact des fichiers ouverts et écrits par `run` sur Windows ;
- comportement réel de la DB mémoire et nettoyage après crash ;
- effet de configurations managées éventuelles ;
- absence de téléchargement npm en mode pure/offline ;
- provider et modèle réellement utilisés dans les événements ;
- comportement imbriqué, ordre, occurrence et troncature des instructions ;
- contexte, template, débit, mémoire et tool-calling du Qwen local.

## 20. Analyse token concise de la campagne Codex

À partir du rapport [`codex-runtime-0.144.6.md`](codex-runtime-0.144.6.md) :

| Mesure, six appels | Total | Moyenne par appel |
| --- | ---: | ---: |
| Input | 73 148 | 12 191,33 |
| Cached input, sous-ensemble de l'input | 53 760 | 8 960,00 |
| Input non caché calculé | 19 388 | 3 231,33 |
| Output | 309 | 51,50 |
| Input + output | 73 457 | 12 242,83 |

La part cachée est `53 760 / 73 148 = 73,49 %` de l'input. Les **73 148 tokens
d'entrée ne sont pas le coût du kernel** : ils couvrent le contexte complet du
client, ses instructions, métadonnées et prompts.

Les prompts des cas baseline et kernel utilisent le même texte fermé. Les inputs
kernel dépassent exploratoirement la baseline de `219` et `213` tokens, moyenne
`216`. Ce delta n'est pas une attribution causale : une seule baseline, chemins
et fixtures différents, sérialisation du contexte, métadonnées dynamiques,
tokenizer réel, cache et contexte global non capturé restent des facteurs de
confusion. Les outputs diffèrent aussi (`95` baseline contre `68` et `69`) et ne
doivent pas être interprétés comme une économie du kernel.

## 21. Prochaine mission recommandée

Réaliser une mission autonome de **préparation du probe OpenCode 1.17.9**, sans
commencer l'évaluation comportementale :

1. obtenir l'autorisation de rendre Ollama disponible sans que le probe le
   démarre ;
2. vérifier non inférentiellement le candidat, son contexte et son endpoint ;
3. implémenter un harness jetable avec environnement allowlisté, DB mémoire,
   snapshots et egress loopback-only ;
4. tester d'abord les chemins/configurations sans prompt ;
5. n'ouvrir ensuite qu'un smoke call, puis au maximum la campagne de découverte
   préenregistrée.

Le probe OpenCode n'est volontairement pas créé dans cette mission.

## 22. Gate runtime levé séparément

Le [smoke test Ollama 0.20.2 + Qwen 3.6 35B](ollama-qwen3.6-35b-smoke.md),
réalisé le 2026-07-20 dans une mission autonome, a levé le gate runtime local :
le modèle exact a été chargé à 16 384 tokens, l'unique réponse attendue a été
obtenue, puis modèle, serveur et enfants ont été nettoyés. La campagne OpenCode
reste non exécutée ; ses autres gates d'isolation, de provider, de stockage et
de découverte demeurent applicables.
