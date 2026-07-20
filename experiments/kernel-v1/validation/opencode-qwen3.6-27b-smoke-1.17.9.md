# Smoke OpenCode 1.17.9 + Ollama 0.20.2 + Qwen 3.6 27B

> **Note de suivi — 2026-07-21 :** une mission séparée a testé la politique
> autorisée `OLLAMA_GPU_OVERHEAD=4294967296`. Le chargement unique a laissé
> 3 683 MiB de VRAM libre, sous le nouveau gate de 4 096 MiB ; OpenCode n'a pas
> été lancé. Voir le
> [rapport d'offload](opencode-qwen3.6-27b-offload-smoke-1.17.9.md).

## Statut et portée

- **Date :** 2026-07-20
- **Mission :** 15
- **Statut :** **BLOCKED après chargement, avant inférence OpenCode**
- **Provider demandé :** `local-ollama`
- **Modèle chargé :** `qwen3.6:27b`
- **Contexte demandé et observé :** `16 384` tokens
- **Serveurs Ollama réels :** un pour le run, plus un serveur distinct pour le pull
- **Chargements réels :** un
- **Processus OpenCode vers Qwen :** zéro
- **Requêtes de génération Qwen :** zéro
- **Retry :** zéro

Le gate de confort a interrompu le protocole parce que le chargement laissait
seulement 549 MiB de VRAM, sous le minimum absolu de 3 Gio. Le modèle a été
déchargé et tous les processus ont été nettoyés. La compatibilité réelle
OpenCode + Qwen reste donc inconnue ; le résultat ne doit pas être interprété
comme un échec du provider ou du modèle à répondre.

## Raison du pivot 35B vers 27B

La Mission 14 avait projeté seulement 435 MiB de marge pour le 35B et s'était
arrêtée avant lancement. Le 27B dense a été choisi comme candidat principal pour
réduire la taille chargée et viser au moins 4 Gio de marge, avec un minimum
absolu de 3 Gio. Cette hypothèse de confort n'a pas été confirmée sur la machine :
le 27B est plus petit, mais son allocation à 16 384 tokens remplit encore presque
entièrement la RTX 4090.

## Prévol

Le prévol a confirmé :

- branche `main`, worktree initial propre ;
- HEAD `94815799fc491d6c37ba824a69134811f59ff6b2` ;
- sujet `test: confirm OpenCode with local Qwen` ;
- Python `3.11.9`, OpenCode `1.17.9`, Ollama `0.20.2` ;
- zéro processus Ollama/OpenCode et port 11434 libre ;
- environ 1 400,117 Gio libres sur le volume du model store, au-dessus du seuil
  obligatoire de 22 Gio ;
- modèle `qwen3.6:35b` présent avant téléchargement ;
- modèle `qwen3.6:27b` absent avant téléchargement.

Le binaire OpenCode verrouillé faisait 165 154 696 octets, SHA-256
`65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6`.

## Téléchargement officiel et identité

Source exclusive : [fiche officielle Ollama `qwen3.6:27b`](https://ollama.com/library/qwen3.6:27b).
Une seule invocation initiale a été exécutée :

```text
ollama pull qwen3.6:27b
```

Elle a réussi en 188,9 s. Aucune reprise n'a été nécessaire. Ollama a annoncé la
vérification SHA-256, l'écriture du manifest puis `success`. Aucun modèle n'était
chargé avant ou après le pull. Aucun mirror, namespace alternatif, autre
quantification, téléchargement Hugging Face ou mise à jour d'Ollama n'a été
utilisé.

| Champ | Observation locale après pull |
| --- | --- |
| Tag | `qwen3.6:27b` |
| Digest du manifest | `sha256:a50eda8ed977ab48a12431878896b27ffd5cef552c17af3317d9623b939a7f1e` |
| Digest de la couche modèle | `sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926` |
| Taille de la couche modèle | 17 420 420 832 octets, soit 16,224 Gio |
| Taille déclarée de toutes les entrées | 17 420 432 739 octets |
| Format / architecture | GGUF / `qwen35`, dense |
| Paramètres totaux / actifs | 27,8 B / 27,8 B |
| Quantification | `Q4_K_M` |
| Contexte natif annoncé | 262 144 tokens |
| Licence | Apache 2.0, blob de 11 357 octets |
| Capacités annoncées | `completion`, `vision`, `tools`, `thinking` |

Le manifest contient quatre entrées. Tous les blobs requis existaient et leurs
tailles correspondaient. Le gros blob n'a pas été rehaché séparément par le
probe ; l'absence de corruption signalée repose sur la vérification SHA-256 du
pull officiel, la concordance manifest/nom/taille et l'ouverture réussie par
Ollama.

## Conservation du 35B

`qwen3.6:35b` est resté présent et n'a été ni lancé, ni retéléchargé, ni modifié.
Avant et après le pull, son manifest conservait :

- SHA-256 `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522` ;
- mtime UTC `2026-06-04T21:15:34.0617344Z` ;
- couche modèle
  `sha256:f5ee307a2982106a6eb82b62b2c00b575c9072145a759ae4660378acda8dcf2d` ;
- taille 23 938 321 664 octets.

## Profils de modèles

[`model-profiles.json`](../model-profiles.json) centralise deux profils
déterministes :

| Profil | Modèle | Architecture | Paramètres | Taille | Contexte de test |
| --- | --- | --- | --- | ---: | ---: |
| `qwen3.6-35b-q4km` | `qwen3.6:35b` | `qwen35moe`, MoE | 36,0 B / 3,0 B actifs | 23 938 321 664 | 16 384 |
| `qwen3.6-27b-q4km` | `qwen3.6:27b` | `qwen35`, dense | 27,8 B / 27,8 B actifs | 17 420 420 832 | 16 384 |

Les faits historiques 35B de taille, digest, architecture, quantification et
contexte sont inchangés. Le nom officiel Qwen
[`Qwen3.6-35B-A3B`](https://github.com/QwenLM/Qwen3.5) fournit le nombre de
paramètres actifs. Les deux profils restent `experimental` et pointent vers
`http://127.0.0.1:11434`.

[`probe_ollama.py`](../tools/probe_ollama.py) et
[`probe_opencode.py`](../tools/probe_opencode.py) acceptent `--profile`. Sans
option, le profil 35B historique reste le défaut pour préserver les commandes
existantes. Le code n'est pas dupliqué par modèle. Le probe OpenCode applique le
gate absolu du 27B après chargement et surveille séparément les connexions de
ses arbres Ollama et OpenCode.

## Validations statiques et mock

Le registre JSON a été parsé et les deux profils ont passé les contrôles de
schéma, endpoint, digests, architecture, paramètres, quantification, licence,
taille et contexte. La suite complète finale a réussi : **113 tests sur 113**.

Les plans 27B de chaque probe ont quitté avec le code 0 sans processus, serveur,
chargement ou requête. Le plan OpenCode a retourné `READY`, le provider
`local-ollama`, le modèle et les deux digests exacts, le contexte 16 384 et la
sortie attendue.

Le diagnostic mock final a obtenu **PASS** en 3,4 s :

| Propriété | Résultat |
| --- | --- |
| Requêtes mock totales / génération | 1 / 1 |
| Kernel exact | une occurrence |
| Import `@doctrine/KERNEL.md` | zéro occurrence |
| Outils / `tool_choice` | zéro / absent |
| Sortie JSONL | `MOCK_OK` |
| Code OpenCode / événements | 0 / 3 |
| Tool call / permission / thinking visible | non / non / non |
| Connexion non-loopback | non observée |
| Workspace généré / check adaptateurs | inchangé / réussi |
| Nettoyage | complet |

Un premier mock intermédiaire avait également produit une requête et `PASS` ;
le mock final a été rejoué après le dernier durcissement sans inférence de la
surveillance réseau. Ces deux exécutions n'ont démarré ni Ollama ni Qwen.

## Gel avant run

| Fichier gelé | SHA-256 |
| --- | --- |
| [`probe_ollama.py`](../tools/probe_ollama.py) | `d66773e48ce87300adbb620eb92ca8a02dee0623d1548ed92457d375925b29a3` |
| [`probe_opencode.py`](../tools/probe_opencode.py) | `ffdb862aa52714f2d0128ea9ad6ba4c2098e10c6aa690e831a4674d9861c77bf` |
| [`model-profiles.json`](../model-profiles.json) | `b9600a46922d926639c4e717d747ead1b4cc4730bd20a72c09044f355c3cab05` |

Les trois hashes étaient identiques après le run. Aucun de ces fichiers n'a été
modifié après le lancement réel.

## Chargement réel et gate de confort

Commande unique :

```text
python -B experiments/kernel-v1/tools/probe_opencode.py run --profile qwen3.6-27b-q4km --acknowledge-local-inference
```

Le probe a démarré un serveur Ollama 0.20.2 possédé avec
`OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_NO_CLOUD=1`, contexte 16 384,
`OLLAMA_MAX_LOADED_MODELS=1` et `OLLAMA_NUM_PARALLEL=1`. Le chargement sans
message a duré 4,421 s et n'a produit aucun token. `/api/ps` a confirmé :

| Mesure | Valeur |
| --- | ---: |
| Modèle effectif | `qwen3.6:27b` |
| Digest runtime du manifest | `a50eda8ed977ab48a12431878896b27ffd5cef552c17af3317d9623b939a7f1e` |
| Contexte effectif | 16 384 |
| Taille chargée totale | 23 533 728 704 octets, 21,917 Gio |
| VRAM | 20 647 610 368 octets, 19,230 Gio, 87,74 % |
| RAM/CPU calculée | 2 886 118 336 octets, 2,688 Gio, 12,26 % |

| Moment | RAM utilisée | RAM disponible | VRAM utilisée | VRAM libre |
| --- | ---: | ---: | ---: | ---: |
| Avant chargement | 15,621 Gio | 48,221 Gio | 1 967 MiB | 22 172 MiB |
| Après chargement | 19,273 Gio | 44,569 Gio | 23 590 MiB | **549 MiB** |
| Après nettoyage | 15,583 Gio | 48,259 Gio | 1 970 MiB | 22 169 MiB |
| Contrôle externe final | non recalculée | 48,275 Gio environ | 1 965 MiB | 22 174 MiB |

La RAM restait largement au-dessus de 4 Gio. La marge VRAM de 549 MiB, soit
0,536 Gio, était sous le minimum de 3 072 MiB et la cible de 4 096 MiB. Le probe
a donc classé **BLOCKED**, sans modifier le contexte ou le split et sans lancer
OpenCode.

## Inférence, provider, sortie et performances

Le prompt fermé était prêt mais n'a pas été envoyé :

```text
Do not use tools or read files. Based only on project instructions already supplied before this message, output only their first eight words.
```

| Propriété | Observation réelle |
| --- | --- |
| Provider demandé | `local-ollama` |
| Provider effectif OpenCode | non observé ; OpenCode non lancé |
| Modèle effectif Ollama | `qwen3.6:27b` |
| Processus OpenCode d'inférence | 0 |
| Requêtes `/v1/chat/completions` | 0 |
| Sortie attendue | `Understand the requested outcome, constraints, relevant work, and` |
| Sortie réelle | aucune |
| Tool call / permission / sous-agent | aucun processus susceptible d'en émettre |
| Thinking visible / seconde génération | aucun calcul modèle |

La commande de run a duré environ 9,9 s au total et a signalé un statut non nul
associé au `BLOCKED`. `time to first token`, tokens input/output/reasoning,
`prompt_eval_count`, `eval_count`, `prompt_eval_duration`, `eval_duration` et
tokens/s sont non mesurés, car aucune inférence n'a eu lieu. La réponse de
préchargement n'exposait ni `load_duration` natif ni `eval_count`; seul le temps
mur de 4,421 s est disponible.

## Réseau et écritures

Pendant le pull autorisé, des connexions loopback vers 11434 et non-loopback
HTTPS/443 ont été observées. Aucun override de registry ou mirror n'était défini ;
le manifest final est sous `registry.ollama.ai/library/qwen3.6/27b`. Les noms ou
IP distants détaillés n'ont pas été conservés.

Après installation, Ollama fonctionnait avec le cloud désactivé. La surveillance
continue du chargement a observé uniquement trois connexions loopback et aucune
connexion non-loopback. OpenCode n'a créé aucune connexion réelle, puisqu'il n'a
pas été lancé.

Le workspace jetable contenait les quatre sorties attendues. Il est resté
inchangé, son check d'adaptateurs a réussi, puis sa racine temporaire et les logs
Ollama ont été supprimés. Aucun transcript, raisonnement, JSONL brut ou log brut
n'est conservé.

## Budget réel et nettoyage

| Ressource du run | Maximum | Réel |
| --- | ---: | ---: |
| Serveur Ollama | 1 | 1 |
| Chargement réel | 1 | 1 |
| Processus OpenCode d'inférence | 1 | 0 |
| Requête Qwen | 1 | 0 |
| Retry | 0 | 0 |
| Tool call | 0 | 0 |
| Provider distant après installation | 0 | 0 observé |
| Sous-agent | 0 | 0 |

Après le blocage : déchargement demandé, `/api/ps` confirmé vide avant arrêt,
serveur et enfants possédés arrêtés, port libéré, racine temporaire supprimée,
model store inchangé par le run et repository inchangé par le runtime. Un
contrôle externe a confirmé zéro processus Ollama/OpenCode, zéro listener 11434,
27B installé conservé et 35B conservé.

## Propriétés démontrées

- Le modèle officiel 27B exact est installé avec ses quatre blobs cohérents.
- Le 35B historique est conservé et inchangé.
- Les probes sélectionnent de façon déterministe les profils 35B et 27B sans
  duplication complète.
- Le plan 27B, les 113 tests et le diagnostic mock final réussissent.
- Qwen 27B se charge à exactement 16 384 tokens sous Ollama 0.20.2.
- Le gate mesure la marge après chargement et bloque avant toute inférence sous
  3 Gio.
- Le budget réel, le gel, le confinement observé et le nettoyage sont respectés.

## Propriétés encore inconnues

- résolution effective de `local-ollama/qwen3.6:27b` par OpenCode ;
- transmission du kernel à Qwen et adhérence au prompt ;
- sortie exacte, absence de thinking et comportement OpenCode sur le chemin Qwen ;
- tokens, latence et débit d'une génération réelle ;
- stabilité avec une marge conforme ;
- absence exhaustive de connexions au-delà de l'échantillonnage par PID.

## Comparaison limitée avec le 35B

À 16 384 tokens, le 27B a réduit la taille chargée de 3,404 Gio, la part VRAM de
1,804 Gio et la part CPU de 1,600 Gio par rapport aux mesures finales 35B de la
Mission 11. Cette réduction n'a pas produit la marge attendue : le 35B avait
laissé 793 MiB après chargement dans une baseline à 1 076 MiB, tandis que le 27B
n'en a laissé que 549 MiB avec une baseline à 1 967 MiB. Les baselines système
diffèrent ; cette comparaison ne permet donc pas d'attribuer toute la différence
au modèle.

## Conclusion et prochaine mission proposée

Le résultat fidèle est **BLOCKED**, sans inférence. Un rerun inchangé n'est pas
justifié : même le 27B dense à 16 384 tokens ne satisfait pas le gate matériel.
La prochaine mission devrait, sans lancer de modèle, décider entre un candidat
officiel plus petit et une politique explicitement autorisée de répartition
CPU/GPU conservant le contexte 16 384, puis définir un nouveau protocole et un
nouveau budget. Elle ne doit pas revenir automatiquement au 35B ni réduire le
contexte sans décision séparée.
