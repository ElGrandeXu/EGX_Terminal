# Smoke final OpenCode 1.17.9 + Qwen 3.6 27B

## 1. Résultat

- **Date :** 2026-07-21
- **Statut :** **FAIL** avant toute requête Qwen
- **Branche initiale :** `main`
- **HEAD initial :** `63693b6128182233d1fffb8608655bb804909ab3`
- **Sujet initial :** `test: validate Qwen 27B with reserved VRAM`
- **Worktree initial :** propre
- **Profil :** `qwen3.6-27b-q4km`
- **Provider demandé :** `local-ollama`
- **Modèle :** `qwen3.6:27b`, dense, Q4_K_M

Le gate matériel a réussi, mais OpenCode a produit dès la première ligne une
sortie qui n'était pas un événement JSONL valide. Le probe a donc échoué avec
`invalid OpenCode JSONL at line 1` après un seul processus OpenCode et avant
toute requête `/v1/chat/completions`. Conformément au budget, aucune relance,
seconde génération ou correction du probe n'a été faite.

## 2. Décision de marge

Seul `minimum_free_vram_mib` du profil 27B passe de 4 096 à **3 072 MiB**.
La réservation demandée au serveur enfant reste exactement **4 Gio**, soit
`OLLAMA_GPU_OVERHEAD=4294967296`. La cible de confort reste **4 Gio**. Une marge
mesurée entre 3 et 4 Gio est classée **« acceptable, confort limité »**.

Cette décision repose sur cette machine et cette mesure. Elle ne constitue pas
une promesse générale pour d'autres machines, GPU, charges ou versions. Le
contexte 16 384, le parallélisme 1, le split choisi par Ollama, le provider
local, les protections réseau et l'interdiction des outils sont inchangés.

## 3. Prévol et identité

Le prévol a confirmé zéro runtime Ollama/OpenCode, le port 11434 libre et les
versions Python 3.11.9, Ollama 0.20.2 et OpenCode 1.17.9. Les identités sont
restées :

| Élément | Valeur |
| --- | --- |
| Blob 27B | `sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926` |
| Manifest 27B | `sha256:a50eda8ed977ab48a12431878896b27ffd5cef552c17af3317d9623b939a7f1e` |
| Binaire OpenCode | `sha256:65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6` |
| Kernel | `a70b983003abcb59bcb53b3dba5637c6105d85fe3fc47fa5546d668b5d4d1431` |

Le profil 35B et les digests des deux modèles n'ont pas été modifiés.

## 4. Validations avant run

La suite complète a réussi **122 tests sur 122** en 4,740 s. Le plan 27B a
retourné `READY` avec : réserve 4 Gio, gate 3 072 MiB, RAM minimale 16 Gio,
contexte exact 16 384, parallélisme 1, zéro processus, zéro chargement, zéro
requête et zéro retry.

Le diagnostic mock a retourné **PASS** en 3,6 s :

| Contrôle mock | Résultat |
| --- | ---: |
| Requêtes totales / génération | 1 / 1 |
| Occurrences exactes du kernel | 1 |
| Imports Claude | 0 |
| Outils / champ tools / tool choice | 0 / absent / absent |
| Permission / sous-agent / reasoning visible | 0 / 0 / 0 |
| Sortie | `MOCK_OK` |
| Connexion non-loopback | 0 |

Le workspace mock est resté inchangé et son nettoyage a réussi.

## 5. Gel

Après les tests, le plan et le mock, les probes et profils ont été gelés :

| Fichier | SHA-256 |
| --- | --- |
| `tools/probe_ollama.py` | `b81006fc07d786516833c547ed970d4d369e37904592ae2b62a4a15da671d395` |
| `tools/probe_opencode.py` | `c290f482fb9419db6a2ea73eff98db4ddbd41374084bc4d4deeae0cecb8321b4` |
| `model-profiles.json` | `40bd4fdfbcbc9efe42e71d9f329ea1e4731112b181a387d275a5fb533924ddc5` |

Les mêmes hashes ont été recalculés après le run. Aucun de ces fichiers n'a été
modifié après le gel et le run n'a pas été relancé.

## 6. Run unique et budget

La commande autorisée a été exécutée exactement une fois :

```text
python -B experiments/kernel-v1/tools/probe_opencode.py run --profile qwen3.6-27b-q4km --acknowledge-local-inference
```

| Budget | Observé |
| --- | ---: |
| Serveur Ollama | 1 |
| Chargement | 1 |
| Processus OpenCode d'inférence | 1 |
| Requêtes Qwen | 0 |
| Retry | 0 |
| Tool call | 0 requête modèle ; non observable dans le JSONL OpenCode invalide |

Le chargement non génératif a duré **4,469 s**. La durée mur externe de la
commande avec son moniteur a été d'environ **11,9 s** ; la fenêtre échantillonnée
a couvert **10,827 s** avec 57 mesures. Le probe n'a pas émis sa propre durée
totale à cause de l'erreur de parsing.

## 7. Gate, RAM et VRAM

| Moment | RAM disponible | VRAM utilisée | VRAM libre |
| --- | ---: | ---: | ---: |
| Avant chargement | 48,301 Gio | 2 062 MiB | 22 077 MiB |
| Modèle chargé / gate | 41,637 Gio | 20 589 MiB | 3 550 MiB |
| Minimum pendant OpenCode | 41,480 Gio | 20 589 MiB max. | **3 550 MiB** |
| Après l'appel | 42,057 Gio | 20 589 MiB | 3 550 MiB |
| Après nettoyage interne | 48,272 Gio | 2 073 MiB | 22 066 MiB |

Le gate de 3 072 MiB a passé avec une marge minimale observée de **478 MiB**.
La marge reste **546 MiB sous la cible de confort de 4 096 MiB** : elle est donc
« acceptable, confort limité ». La VRAM n'est jamais descendue sous le seuil de
risque de 1 536 MiB ; le risque spécifique demandé n'est pas déclenché.

## 8. Contexte et offload

`/api/ps` a exposé uniquement `qwen3.6:27b`, avec le manifest attendu et un
contexte exact de **16 384**. Le serveur possédé a reçu :

```text
OLLAMA_GPU_OVERHEAD=4294967296
OLLAMA_CONTEXT_LENGTH=16384
OLLAMA_NUM_PARALLEL=1
```

| Allocation chargée | Valeur |
| --- | ---: |
| Taille totale | 24 338 500 544 octets, 22,667 Gio |
| GPU | 17 574 194 176 octets, 16,367 Gio, 72,21 % |
| CPU/RAM calculée | 6 764 306 368 octets, 6,300 Gio, 27,79 % |
| Couches GPU | 55 / 65 |
| Couches CPU | 10 / 65 |

Le moniteur externe a observé au plus 4 % d'utilisation GPU dans les sept
échantillons où le processus OpenCode était présent. Cette mesure brève ne doit
pas être interprétée comme une caractérisation de performance : aucune requête
Qwen n'a atteint le serveur.

## 9. Inférence et sortie

| Critère PASS | Observation |
| --- | --- |
| Exit OpenCode 0 | non exposé après l'échec de parsing ; critère non démontré |
| Une requête modèle | **0**, échec |
| Provider / modèle | `local-ollama` / `qwen3.6:27b` demandés, provider non atteint |
| Réponse exacte | aucune réponse modèle |
| Thinking visible | non mesurable faute de JSONL valide |
| Outil / permission / sous-agent | aucune requête modèle ; événements OpenCode non parsables |
| Seconde génération | 0 |
| Mutation du workspace généré | aucune |
| Nettoyage | complet |

La sortie attendue restait exactement :

```text
Understand the requested outcome, constraints, relevant work, and
```

Aucune sortie Qwen n'a été obtenue. Le statut ne peut donc pas être `PASS`.

## 10. Tokens et vitesse

Les tokens input/output/reasoning, `prompt_eval_count`, `eval_count`, TTFT et
tokens/seconde sont **non mesurés** : le chargement non génératif n'exposait pas
`eval_count`, puis OpenCode a échoué avant la première requête modèle. Il serait
trompeur d'attribuer des métriques d'inférence à ce run.

## 11. Réseau

Le serveur Ollama possédé est resté lié à loopback. Son moniteur a observé trois
connexions loopback et aucune connexion non-loopback. Le moniteur OpenCode était
actif, mais son résumé a été perdu lorsque le parseur JSONL a levé l'erreur ; le
critère réseau OpenCode n'est donc pas démontré par l'artefact final. Aucune
requête n'a atteint Ollama.

## 12. Nettoyage et intégrité

Le probe a demandé le déchargement, confirmé `/api/ps` vide, arrêté le serveur
et tous ses enfants possédés, libéré le port 11434 et supprimé la racine
temporaire, les logs et les fichiers de session. Le model store et le repository
sont restés inchangés pendant le run. Le contrôle externe final a confirmé zéro
processus Ollama/OpenCode et aucun listener 11434.

`AGENTS.md` et `CLAUDE.md` conservent respectivement les hashes
`0205768d593ad1036009a19be137e1cc2cca92670c56238db809a1d921da95e5` et
`336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49`.

## 13. Validations finales

Après la documentation, les 122 tests, le parsing de tous les JSON suivis, la
résolution des liens Markdown locaux, le scan de secrets, `git diff --check` et
l'inspection du diff ont réussi. Les hashes gelés ont été confirmés une dernière
fois. Aucun runtime n'a été relancé.

## 14. Conclusion

La nouvelle marge matérielle est validée sur cette machine : 3 550 MiB libres
ont franchi le hard gate de 3 Gio avec 478 MiB de marge. Le smoke final
OpenCode + Qwen reste toutefois **FAIL**, car OpenCode n'a envoyé aucune requête
Qwen et sa première ligne stdout n'était pas du JSONL valide. Ce run unique ne
valide donc ni la réponse comportementale attendue ni le chemin provider réel.
