# Rerun OpenCode 1.17.9 + Ollama 0.20.2 + Qwen 3.6 35B

## Statut et portée

- **Date :** 2026-07-20
- **Statut :** **BLOCKED avant démarrage d'Ollama**
- **Mission :** 14
- **OpenCode demandé :** `1.17.9`
- **Provider demandé :** `local-ollama`
- **Runtime demandé :** Ollama `0.20.2`
- **Modèle demandé :** `qwen3.6:35b`
- **Endpoint demandé :** `http://127.0.0.1:11434/v1`
- **Contexte demandé :** `16 384` tokens
- **Serveurs Ollama démarrés :** zéro
- **Chargements de Qwen :** zéro
- **Processus `opencode run` vers Qwen :** zéro
- **Requêtes de génération Qwen :** zéro
- **Retry :** zéro

Le rerun n'a pas été lancé parce que le prévol GPU obligatoire a échoué. Deux
snapshots ont projeté seulement 443 puis 435 MiB de VRAM résiduelle après le
delta mesuré par la Mission 11, sous le seuil fixe de 512 MiB. Le second snapshot
a aussi confirmé un processus d'application utilisateur avec 3 % d'activité de
calcul GPU. Aucune application utilisateur n'a été fermée et aucun paramètre de
contexte ou de répartition CPU/GPU n'a été modifié.

Ce résultat ne remplace pas le **FAIL** historique de la Mission 12. Il établit
que le probe corrigé par la Mission 13 reste apte au diagnostic mock, mais que
les conditions matérielles de la Mission 14 n'autorisaient pas l'unique
inférence Qwen.

## Filiation avec les Missions 12 et 13

La [Mission 12](opencode-qwen3.6-smoke-1.17.9.md) avait généré et vérifié le
workspace, démarré Ollama et chargé Qwen à 16 384 tokens, puis obtenu une sortie
OpenCode 1 avant toute requête modèle. Son rapport **FAIL** est préservé sans
réécriture.

La [Mission 13](opencode-preflight-diagnostic-1.17.9.md) a prouvé que la clé
inline non supportée `subagent_depth` causait cet échec pré-provider. Elle l'a
retirée, a ajouté un titre fixe empêchant la génération secondaire connue et a
validé le transport vers un mock loopback avec une requête, le kernel exact une
fois, zéro outil et la sortie `MOCK_OK`.

La Mission 14 a rejoué ce diagnostic avec succès avant d'appliquer le gate GPU.
Elle n'a modifié ni la configuration ni les probes après observation du
résultat.

## Prévol Git et versions

Le prévol a confirmé :

- chemin de travail attendu, branche `main` et worktree initial propre ;
- HEAD `332b5b6c2aa3b1e2afc025ae341a0d0ef9fc4fa1` ;
- sujet `fix: repair OpenCode probe initialization` ;
- Python `3.11.9` ;
- OpenCode `1.17.9` ;
- Ollama `0.20.2` ;
- binaire OpenCode de 165 154 696 octets, SHA-256
  `65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6` ;
- aucun processus OpenCode ou Ollama persistant après les commandes de version ;
- port 11434 libre ;
- aucun fichier `opencode.json` créé dans la racine active.

La commande `ollama --version` a brièvement créé son processus client pendant
son exécution et a signalé l'absence de serveur. Un contrôle séquentiel après sa
fin a confirmé zéro processus Ollama/OpenCode et zéro enregistrement sur le port
11434. Cette commande n'a démarré aucun serveur et n'a effectué aucune
inférence.

## Identité locale du modèle

Le mode `plan` a validé le modèle local exact sans démarrer de processus :

| Champ | Observation |
| --- | --- |
| Modèle | `qwen3.6:35b` |
| Digest déclaré attendu | `sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d` |
| Digest calculé du manifest | `sha256:07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522` |
| Kernel SHA-256 | `a70b983003abcb59bcb53b3dba5637c6105d85fe3fc47fa5546d668b5d4d1431` |
| Téléchargement ou installation | aucun |

## Hashes gelés des probes

Après les tests et le diagnostic mock, avant toute décision de lancement, les
hashes suivants ont été gelés :

| Probe | SHA-256 |
| --- | --- |
| [`probe_opencode.py`](../tools/probe_opencode.py) | `1b88471f6ba6442c1cdd1a5b4b09a9e078fe98b9ce1aefd078c9689d551699c0` |
| [`probe_ollama.py`](../tools/probe_ollama.py) | `7095dabe8125bd5e6c438acb355bad0f0f87031cae9e35377f003aa1bf645bf7` |

Leur code n'a pas été modifié pendant la mission. Les mêmes hashes ont été
recalculés après l'abandon contrôlé.

## Budget prévu et budget réel

| Ressource | Maximum autorisé | Réel |
| --- | ---: | ---: |
| Serveur Ollama | 1 | 0 |
| Chargement `qwen3.6:35b` | 1 | 0 |
| Processus OpenCode d'inférence Qwen | 1 | 0 |
| Requête de génération Qwen | 1 | 0 |
| Retry d'inférence | 0 | 0 |
| Tool call | 0 | 0 |
| Provider distant | 0 | 0 |
| Sous-agent | 0 | 0 |

Les commandes de version, le plan statique et le diagnostic mock sont consignés
séparément. Le mock a démarré un serveur HTTP standard-library sur un port
loopback dynamique, lancé un OpenCode isolé et reçu une réponse déterministe ;
il n'a démarré ni Ollama ni Qwen et n'a effectué aucun calcul modèle.

## Tests et plan sans inférence

La commande suivante a réussi avant la décision de run :

```text
python -B -m unittest discover -s experiments/kernel-v1/tests -v
```

Résultat : **109 tests réussis sur 109** en 4,750 s.

Le mode `plan` a retourné `READY` avec : zéro processus démarré, zéro processus
OpenCode d'inférence, zéro serveur, zéro chargement, zéro requête modèle et zéro
retry. Il a confirmé le provider `local-ollama`, l'endpoint loopback, le modèle,
le digest, le contexte 16 384 et la sortie attendue.

## Diagnostic mock préalable

Commande :

```text
python -B experiments/kernel-v1/tools/probe_opencode.py diagnose
```

Résultat : **PASS**.

| Champ | Observation |
| --- | --- |
| Serveur mock | un, `127.0.0.1:<port-dynamique>` |
| Calcul modèle | non |
| Démarrage Ollama | non |
| Requêtes totales / génération | 1 / 1 |
| Route | `POST /v1/chat/completions` |
| Provider / modèle | `mock-openai` / `egx-mock` |
| Kernel exact dans la requête | une occurrence |
| Prompt fermé | une occurrence |
| Outils actifs | zéro ; champs `tools` et `tool_choice` absents |
| Sortie finale | `MOCK_OK` |
| Code OpenCode / événements JSONL | 0 / 3 |
| Tool / permission / thinking visible | non / non / non |
| Connexion non-loopback observée | non |
| Workspace généré modifié | non |
| `sync_adapters.py check` après | réussi |
| Nettoyage | complet |

Le moniteur n'a pas échantillonné la connexion loopback, mais la réception
directe de l'unique requête par le serveur lié littéralement à `127.0.0.1` la
prouve. Aucun payload brut, transcript ou session ID n'a été conservé.

## Gate GPU et RAM

La Mission 11 avait fixé une baseline de 1 076 MiB et un delta modèle de
21 748 MiB. Le probe refuse une baseline supérieure à 1 332 MiB et exige une
marge projetée d'au moins 512 MiB.

| Snapshot | RAM utilisée | RAM disponible | VRAM utilisée | VRAM libre | Dérive baseline | Marge projetée |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Premier prévol | non capturée dans ce snapshot | non capturée | 1 948 MiB | 22 191 MiB | +872 MiB | 443 MiB |
| Décision après mock | 15,650 GiB | 48,192 GiB | 1 956 MiB | 22 183 MiB | +880 MiB | 435 MiB |
| Contrôle final après nettoyage | 15,687 GiB | 48,154 GiB | 1 958 MiB | 22 181 MiB | +882 MiB | 433 MiB |

La RAM disponible restait très supérieure au garde-fou de 4 GiB. La VRAM était
incompatible sur les trois snapshots. `nvidia-smi pmon` a en outre observé
`Hearthstone.exe` à 3 % SM et 0 % mémoire lors des deux contrôles. Il s'agit d'une
application utilisateur : elle n'a pas été arrêtée. Le contexte n'a pas été
réduit, aucun autre modèle n'a été choisi et le split CPU/GPU n'a pas été
modifié.

## Provider, modèle, contexte et sortie Qwen

| Propriété | Demandée | Observée |
| --- | --- | --- |
| Provider | `local-ollama` | non observé, run non lancé |
| Modèle | `qwen3.6:35b` | identité locale statique validée ; non chargé |
| Endpoint | `127.0.0.1:11434` / `/v1` | port libre ; aucun serveur lancé |
| Contexte | 16 384 | non observé au runtime dans cette mission |
| Requêtes de génération | exactement une | zéro, gate préalable bloquant |
| Sortie attendue | `Understand the requested outcome, constraints, relevant work, and` | aucune sortie Qwen |
| Sortie supplémentaire | aucune | aucune |

Le prompt exact était figé dans le probe mais n'a pas été envoyé à Qwen :

```text
Do not use tools or read files. Based only on project instructions already supplied before this message, output only their first eight words.
```

## Outils, permissions, sous-agents et thinking

Pour le diagnostic mock : zéro outil, zéro permission, zéro sous-agent et aucun
événement thinking visible. Pour Qwen, ces propriétés sont **non observées** car
aucune requête réelle n'a été lancée. Aucun `reasoning_content` Qwen n'existe à
mesurer ou à conserver.

## Tokens et performances

Aucune métrique Qwen n'existe : durée OpenCode réelle, time to first token,
input tokens, cached tokens, output tokens, reasoning tokens,
`prompt_eval_count`, `eval_count`, `load_duration`, `prompt_eval_duration`,
`eval_duration` et tokens/seconde sont tous **non mesurés** parce que le serveur,
le modèle et l'inférence n'ont pas démarré.

Le diagnostic mock a duré 3,6 s côté commande. Il ne calcule pas de tokens et ne
constitue pas une mesure de performance modèle.

## Réseau et écritures

Le diagnostic a conservé les protections prévues : provider exclusif, plugins,
auto-update, fetch distant, skills externes et télémétrie désactivés, proxies
enfant neutralisés et `NO_PROXY` limité à loopback. Aucune connexion
non-loopback n'a été observée. Le chemin Qwen n'ayant pas été lancé, aucune
connexion au provider Ollama n'a eu lieu.

Le workspace mock a été produit par
[`sync_adapters.py`](../tools/sync_adapters.py) avec les quatre fichiers attendus.
Le canon, la copie `AGENTS.md` et le lock étaient valides avant l'appel ; le
snapshot était inchangé et le `check` réussissait après. Huit fichiers
temporaires existaient sous la racine jetable avant suppression. La racine
temporaire a été supprimée et le repository était inchangé par le diagnostic.

Le seul fichier repository volontairement créé par la Mission 14 est le présent
rapport. Aucun log brut ou transcript n'est suivi.

## Nettoyage

Le nettoyage a confirmé :

- fin du processus OpenCode mock et disparition de son PID possédé ;
- zéro processus OpenCode ou Ollama après le diagnostic ;
- aucun enfant possédé restant ;
- serveur mock arrêté ;
- racine temporaire et ses huit fichiers supprimés ;
- port 11434 libre ;
- Qwen jamais chargé, donc aucun déchargement nécessaire ;
- aucun serveur Ollama disponible pour `/api/ps`, cohérent avec zéro démarrage ;
- identité, digest du manifest et tailles des blobs locaux concordants entre les
  deux exécutions du plan ; aucune opération susceptible de modifier le model
  store ;
- racine active inchangée par tous les runtimes exécutés ;
- RAM et VRAM non alourdies par Ollama/Qwen, qui n'ont pas démarré.

## Validations finales

Après création du rapport, la suite complète a de nouveau obtenu **109 tests
réussis sur 109**, en 4,726 s. Le plan final a de nouveau retourné `READY` avec
zéro processus, serveur, chargement, requête et retry. Les hashes des probes
étaient identiques aux valeurs gelées, les cinq liens Markdown locaux étaient
résolus, le manifest JSON était valide, `git diff --check` ne signalait aucune
erreur et aucun chemin personnel, secret, transcript ou log brut n'était suivi.

## Propriétés démontrées

- Le code corrigé de Mission 13 passe toujours ses 109 tests.
- OpenCode 1.17.9 accepte la configuration isolée corrigée et atteint le mock
  OpenAI-compatible loopback.
- La copie générée `AGENTS.md` fournit le kernel exact une fois dans la requête
  mock.
- Le diagnostic produit une requête et une sortie exactes sans outil,
  permission, sous-agent, thinking visible, seconde génération ou mutation du
  workspace.
- L'identité statique locale de `qwen3.6:35b` et son digest attendu sont
  présents.
- Le gate matériel arrête le protocole avant tout démarrage ou calcul lorsque la
  marge projetée est inférieure à 512 MiB ou qu'un autre calcul GPU est actif.
- Le budget réel est resté sous tous les plafonds et le nettoyage mock est
  complet.

## Propriétés non démontrées

- compatibilité réelle OpenCode 1.17.9 avec le provider Ollama
  OpenAI-compatible dans ce rerun ;
- résolution effective de `local-ollama/qwen3.6:35b` par OpenCode ;
- chargement effectif à 16 384 tokens dans cette mission ;
- transmission du kernel à Qwen et adhérence de Qwen à sa première phrase ;
- sortie exacte attendue, absence de sortie supplémentaire, tool call,
  permission, sous-agent, thinking ou seconde génération sur le chemin Qwen ;
- tokens, latence, débit et métriques Ollama/OpenCode de la génération ;
- absence exhaustive de paquets au niveau OS au-delà de la surveillance par PID
  et des protections applicatives.

## Conclusion et prochaine étape recommandée

Le rerun est **BLOCKED** avant inférence. Ce statut est un respect du protocole,
pas une incompatibilité observée entre OpenCode et Qwen. Il ne justifie ni
activation, ni promotion, ni conclusion runtime favorable ou défavorable.

Prochaine mission proposée, sans l'exécuter : refaire exactement le même smoke
dans une fenêtre où l'utilisateur a lui-même libéré suffisamment de VRAM et où
aucun autre processus n'exerce de calcul GPU, puis exiger à nouveau au moins
512 MiB de marge projetée avant l'unique lancement. Ne modifier ni le contexte,
ni le split CPU/GPU, ni le modèle, ni le provider pour contourner le gate.
