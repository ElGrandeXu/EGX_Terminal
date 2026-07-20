# Smoke test Ollama 0.20.2 + Qwen 3.6 35B

## Statut et périmètre

- **Date :** 2026-07-20
- **Statut :** **PASS**
- **Runtime :** Ollama `0.20.2`
- **Modèle :** `qwen3.6:35b`
- **Endpoint :** `http://127.0.0.1:11434`
- **Contexte demandé et observé :** `16 384` tokens
- **Appels d'inférence :** un, sans retry
- **OpenCode :** non lancé

Cette mission valide seulement le couple Ollama + modèle local. Elle ne valide
ni le provider OpenCode, ni la découverte du kernel, ni le tool calling dans un
harness agentique.

## Prévol

Le prévol a confirmé `main`, un worktree initialement propre, le commit
`3222253516d5bcbd80ad64403c4f8d902f5e5541` et son sujet
`docs: assess OpenCode runtime readiness`. Python était `3.11.9` et le client
Ollama `0.20.2`. `ollama serve --help` exposait notamment `OLLAMA_HOST`,
`OLLAMA_CONTEXT_LENGTH`, `OLLAMA_KEEP_ALIVE`, `OLLAMA_NO_CLOUD`,
`OLLAMA_NOPRUNE`, `OLLAMA_MAX_LOADED_MODELS` et `OLLAMA_NUM_PARALLEL`.

`nvidia-smi` était disponible et identifiait une NVIDIA GeForce RTX 4090 de
24 564 MiB. Aucun processus Ollama, listener sur le port 11434 ou modèle chargé
n'existait avant l'expérience. Le manifest exact et tous ses quatre blobs
étaient présents localement ; aucune commande de pull, create, copy ou delete
n'a été appelée.

## Documentation officielle consultée

Documentation Ollama actuelle consultée le 2026-07-20 :

- [FAQ](https://docs.ollama.com/faq) : variables serveur, binding loopback par
  défaut, `OLLAMA_NO_CLOUD=1`, préchargement par requête vide et déchargement par
  `keep_alive: 0` ;
- [contexte](https://docs.ollama.com/context-length) : coût mémoire du contexte
  et contrôle de l'allocation/offload ;
- [API show](https://docs.ollama.com/api-reference/show-model-details) : détails,
  capacités, template et `model_info` ;
- [API chat](https://docs.ollama.com/api/chat) : requête non streamée, options,
  `think`, `keep_alive` et métriques ;
- [thinking](https://docs.ollama.com/capabilities/thinking) : `think: false` pour
  les modèles Qwen compatibles ;
- [API ps](https://docs.ollama.com/api/ps) : modèles chargés, taille, VRAM et
  contexte ;
- [usage](https://docs.ollama.com/api/usage) : métriques en nanosecondes.

La documentation est une surface `latest`, pas une preuve de version. Les
contrôles observés ci-dessous ont donc été confirmés séparément avec le binaire
local `0.20.2`.

## Protocole reproductible

[`probe_ollama.py`](../tools/probe_ollama.py) utilise Python 3 et la bibliothèque
standard uniquement. Son interface est fermée : ni modèle ni endpoint ne sont
paramétrables.

```text
python -B experiments/kernel-v1/tools/probe_ollama.py plan
python -B experiments/kernel-v1/tools/probe_ollama.py run --acknowledge-model-load
```

Le serveur enfant recevait `OLLAMA_HOST=127.0.0.1:11434`,
`OLLAMA_NO_CLOUD=1`, `OLLAMA_CONTEXT_LENGTH=16384`,
`OLLAMA_KEEP_ALIVE=2m`, `OLLAMA_MAX_LOADED_MODELS=1`,
`OLLAMA_NUM_PARALLEL=1` et `OLLAMA_NOPRUNE=1`. Les variables proxy n'étaient pas
propagées et `NO_PROXY` était limité à loopback. Le probe a vérifié que le
listener appartenait à ses PID et était lié exactement à `127.0.0.1`.

Tous les appels HTTP construits par le probe sont verrouillés sur le même
endpoint loopback. Le manifest et les blobs locaux sont validés avant démarrage,
ce qui rend un modèle manquant bloquant avant toute requête. Le mode cloud était
désactivé par le mécanisme officiel. Aucun scan réseau ou endpoint distant n'a
été utilisé par le probe.

L'appel smoke utilise `/api/chat`, la primitive native la plus proche de la
sémantique chat-completions prévue pour OpenCode. Elle a été préférée ici à la
compatibilité OpenAI pour fixer `options.num_ctx` par requête et conserver les
métriques natives. Cela ne préjuge pas encore du comportement du provider
OpenAI-compatible d'OpenCode.

## Identité du modèle

| Champ | Observation |
| --- | --- |
| Identifiant | `qwen3.6:35b` |
| Digest déclaré du blob GGUF | `sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d` |
| Digest calculé du manifest | `sha256:07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522` |
| Taille du blob modèle | 23 938 321 664 octets |
| Format / architecture | GGUF / `qwen35moe` |
| Paramètres / quantification | `36.0B` / `Q4_K_M` |
| Contexte maximal annoncé | 262 144 tokens |
| Capacités annoncées | `completion`, `vision`, `tools`, `thinking` |
| Template | 13 caractères ; SHA-256 `b507b9c2f6ca642bffcd06665ea7c91f235fd32daeefdf875a0f938db05fb315` |

Le template intégral et les gros outputs de metadata ne sont pas conservés. Le
digest du blob est celui déclaré par le manifest, dont le nom de blob et la
taille correspondent ; les 23,9 Go n'ont pas été rehachés intégralement.
`/api/ps` a exposé le digest du manifest, pas celui du blob GGUF. Cette
distinction a été vérifiée avant l'inférence finale.

## Chargement et allocation

Une requête `/api/chat` sans message, `stream: false`, `keep_alive: "2m"` et
`options.num_ctx: 16384` a chargé le modèle sans génération. La réponse n'a pas
exposé `load_duration` ni `eval_count`; le temps mur du chargement final était
4,234 s. `/api/ps` a ensuite confirmé :

| Mesure | Valeur |
| --- | ---: |
| Contexte effectif | 16 384 tokens |
| Taille chargée totale | 27 188 902 304 octets, soit 25,322 GiB |
| Part VRAM | 22 584 406 272 octets, soit 21,033 GiB / 83,06 % |
| Part RAM/CPU calculée | 4 604 496 032 octets, soit 4,288 GiB / 16,94 % |

Le contexte maximal annoncé de 262 144 était compatible avec la cible. Le
contexte n'a été ni augmenté ni réduit. La RAM disponible après chargement était
46,492 GiB, très supérieure au garde-fou fixe de 4 GiB.

## Unique smoke call

Configuration : `temperature: 0`, `num_ctx: 16384`, `num_predict: 16`,
`stream: false`, `think: false`, `keep_alive: "2m"`.

| Champ | Résultat |
| --- | --- |
| Message | `Reply with exactly: QWEN_LOCAL_OK` |
| Sortie attendue | `QWEN_LOCAL_OK` |
| Sortie observée | `QWEN_LOCAL_OK` |
| Thinking exposé | non |
| `done` / `done_reason` | `true` / `stop` |
| Tokens prompt / sortie | 21 / 6 |
| Limite de sortie | 16 tokens |

Il n'y a eu qu'un appel avec message sur toute la mission et aucun retry
d'inférence.

## Latence et débit

| Mesure | Valeur |
| --- | ---: |
| Temps mur | 0,359 s |
| `total_duration` | 0,3685358 s |
| `load_duration` de l'appel déjà préchargé | 0,0894954 s |
| `prompt_eval_duration` | 0,1068414 s |
| `eval_duration` | 0,1306210 s |
| Débit de génération recalculé | 45,934421 tokens/s |
| Débit prompt exploratoire recalculé | 196,553022 tokens/s |

Le débit de génération est `6 / (130621000 / 10^9)`. Les durées API sont des
nanosecondes selon la documentation. Le temps mur est un échantillon côté client
et n'est pas supposé identique à la durée interne.

## RAM et VRAM

| Moment | RAM utilisée | RAM disponible | VRAM utilisée | VRAM disponible |
| --- | ---: | ---: | ---: | ---: |
| Avant chargement | 12,407 GiB | 51,435 GiB | 1 076 MiB | 23 063 MiB |
| Après chargement | 17,349 GiB | 46,492 GiB | 23 346 MiB | 793 MiB |
| Après inférence | 17,266 GiB | 46,576 GiB | 23 366 MiB | 773 MiB |
| Après nettoyage | 12,426 GiB | 51,416 GiB | 1 076 MiB | 23 063 MiB |

Le delta échantillonné après chargement est +4,942 GiB de RAM utilisée et
+21,748 GiB de VRAM utilisée. Ces snapshots ne prouvent pas le pic exact. Sous
WDDM, `nvidia-smi` a exposé les PID Ollama mais `[N/A]` pour leur VRAM
individuelle ; la VRAM globale et la répartition `/api/ps` restent disponibles.

La marge VRAM finale pendant l'inférence était seulement 773 MiB. La RAM était
confortable, mais une future campagne ne doit ni augmenter le contexte ni
charger un second modèle en parallèle sans nouvelle validation.

## Incidents pré-inférence et budget réel

Quatre serveurs possédés ont été démarrés au total :

1. arrêt au démarrage, avant chargement, car l'environnement Windows enfant ne
   transmettait pas encore les variables de profil nécessaires ;
2. chargement réussi, puis blocage avant inférence sur la distinction digest du
   manifest / digest du blob ;
3. chargement réussi, puis blocage avant inférence sur `[N/A]` retourné par WDDM ;
4. chargement et smoke test réussis.

Le total réel est donc **quatre démarrages serveur, trois chargements et une
inférence**. Chaque exécution avait son propre plafond d'un démarrage et d'un
chargement. Les trois premiers arrêts ont précédé le budget d'inférence ; aucun
prompt n'a été rejoué.

## Déchargement et nettoyage

Après chaque exécution, y compris les trois arrêts pré-inférence, le bloc
`finally` a traité uniquement les PID du serveur possédé et leurs descendants.
Pour le run final :

- déchargement demandé par `/api/chat` sans message et `keep_alive: 0` ;
- `/api/ps` confirmé vide ;
- serveur possédé arrêté ;
- aucun PID possédé restant ;
- port 11434 libéré ;
- aucun processus Ollama restant lors du contrôle externe post-run ;
- journaux stdout/stderr temporaires supprimés ;
- manifest et blobs requis inchangés ;
- VRAM revenue exactement de 1 076 MiB à 1 076 MiB ;
- RAM revenue d'un état utilisé de 12,407 GiB à 12,426 GiB, variation cohérente
  avec l'activité générale du système.

Aucun blob, manifest ou modèle n'a été supprimé.

## Faits, inférences et inconnues

### Faits

- Ollama `0.20.2` a résolu et chargé le modèle local exact.
- Le digest déclaré attendu, le digest du manifest, les tailles et la présence
  de tous les blobs concordent.
- Le modèle annonce 262 144 tokens et a été chargé à exactement 16 384.
- `/api/ps` montre une répartition 83,06 % GPU / 16,94 % CPU.
- L'unique sortie est exacte, sans thinking, avec `done_reason: stop`.
- Le modèle, le serveur, les enfants, le port et les logs temporaires ont été
  nettoyés.

### Inférences limitées

- Le couple est apte à servir de runtime au prochain smoke probe OpenCode à
  16 384 tokens.
- La faible marge VRAM rend `OLLAMA_MAX_LOADED_MODELS=1` et
  `OLLAMA_NUM_PARALLEL=1` prudents pour la prochaine mission.
- Le chemin natif chat est un indicateur favorable pour le chemin
  OpenAI-compatible, sans constituer sa validation.

### Inconnues et limites

- Aucun packet capture ou sandbox réseau OS n'a mesuré chaque tentative de
  connexion du binaire ; la preuve repose sur `OLLAMA_NO_CLOUD=1`, l'absence de
  proxy enfant, la résolution locale préalable et des URL de probe verrouillées
  sur loopback.
- L'échantillonnage ne capture pas le pic RAM/VRAM exact.
- La VRAM par PID est indisponible sous WDDM dans cette observation.
- Le digest des 23,9 Go n'a pas été recalculé octet par octet.
- Un seul prompt court ne mesure ni stabilité prolongée, ni outils, ni qualité
  agentique, ni compaction.

## Aptitude et configuration recommandée

Le runtime local est **apte au prochain probe OpenCode**, sous réserve de garder
la mission suivante séparée et de ne pas confondre ce résultat avec une
validation du harness.

Configuration serveur recommandée :

```text
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_NO_CLOUD=1
OLLAMA_CONTEXT_LENGTH=16384
OLLAMA_KEEP_ALIVE=2m
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=1
OLLAMA_NOPRUNE=1
```

Pour OpenCode, conserver le provider unique proposé dans le rapport de readiness,
`baseURL: http://127.0.0.1:11434/v1`, modèle et petit modèle fixés à
`local-ollama/qwen3.6:35b`, stockage jetable, permissions deny, plugins et fetchs
désactivés, et confinement loopback-only. Le contexte doit rester fixé côté
serveur : la compatibilité OpenAI Ollama ne fournit pas d'option standard
`num_ctx` par requête.
