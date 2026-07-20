# Smoke OpenCode 1.17.9 + Qwen 3.6 27B avec VRAM réservée

## 1. Statut et prévol

- **Date :** 2026-07-21
- **Statut :** **BLOCKED** au gate matériel, avant OpenCode
- **Branche initiale :** `main`
- **HEAD initial :** `232992f355e2143427b2521e1ce0cc65f0c16a3f`
- **Sujet initial :** `test: validate OpenCode with Qwen 27B`
- **Worktree initial :** propre
- **Ollama / OpenCode :** `0.20.2` / `1.17.9`
- **Profil :** `qwen3.6-27b-q4km`
- **Modèle / quantification :** `qwen3.6:27b` / `Q4_K_M`
- **Contexte :** 16 384 tokens
- **Parallélisme :** 1

Le prévol a confirmé zéro processus Ollama ou OpenCode, aucun listener sur
11434, le port disponible, le 27B exact présent avec le digest de blob
`sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926`
et le digest de manifest
`sha256:a50eda8ed977ab48a12431878896b27ffd5cef552c17af3317d9623b939a7f1e`.
Le profil 35B et son model store sont restés inchangés ; son empreinte JSON
canonique demeure
`d237648b45051b9552e0427173ad91b213bb5a3fbeb4f4296cfb6fd61a84c657`.

## 2. Preuve officielle Ollama v0.20.2

La source officielle exacte est
[`envconfig/config.go` au tag v0.20.2](https://github.com/ollama/ollama/blob/v0.20.2/envconfig/config.go).
Elle établit trois faits distincts :

- `GpuOverhead` lit `OLLAMA_GPU_OVERHEAD` avec le parseur `Uint64` ;
- la description publiée dans `AsMap` donne l'unité en octets ;
- le commentaire et la description indiquent une réserve de VRAM par GPU.

La valeur décimale `4294967296` représente donc exactement 4 Gio. Aucun
`num_gpu`, KV cache quantifié, Flash Attention ou Modelfile dérivé n'a été
utilisé.

## 3. Configuration de réservation

Seul le profil expérimental 27B déclare la politique suivante :

```json
{
  "gpu_overhead_bytes": 4294967296,
  "gpu_overhead_gib": 4,
  "minimum_free_vram_mib": 4096,
  "context_length": 16384,
  "num_parallel": 1
}
```

Le probe valide les types, la cohérence des unités et des champs, puis refuse
les valeurs négatives, non entières ou déraisonnables. Il construit un nouvel
environnement pour le seul serveur Ollama possédé. Le processus parent,
l'environnement OpenCode, l'utilisateur et le système ne sont pas modifiés.
L'environnement réellement transmis au serveur contenait :

```text
OLLAMA_GPU_OVERHEAD=4294967296
OLLAMA_CONTEXT_LENGTH=16384
OLLAMA_NUM_PARALLEL=1
```

Le profil historique 35B ne contient aucune de ces nouvelles clés et ne peut pas
hériter d'un éventuel `OLLAMA_GPU_OVERHEAD` parent.

## 4. Commit prévu

La mission est regroupée dans un commit unique portant le sujet demandé :

```text
test: validate Qwen 27B with reserved VRAM
```

Un résultat `BLOCKED` fidèle est autorisé par le protocole.

## 5. Tests et diagnostic mock

La baseline antérieure à l'édition a réussi exactement **113 tests**. Après
l'ajout de la politique et de ses cas de validation, la suite complète a réussi
**122 tests**. Le diagnostic mock final a obtenu `PASS` : une requête mock, un
kernel exact, zéro outil, sortie `MOCK_OK`, aucun accès non-loopback observé et
nettoyage complet.

Les nouveaux contrôles couvrent la lecture et la valeur exacte, le scope du seul
serveur enfant, l'absence de mutation globale, les valeurs invalides, le 35B
inchangé, le plan, le gate fondé sur la mesure réelle, le split de couches et le
nettoyage après erreur.

## 6. Gel

Après les tests et le mock, les fichiers suivants ont été gelés :

| Fichier | SHA-256 |
| --- | --- |
| `tools/probe_ollama.py` | `b81006fc07d786516833c547ed970d4d369e37904592ae2b62a4a15da671d395` |
| `tools/probe_opencode.py` | `766c64bd168f3cbb3944ea175013c457d0971897df8a9de81782e242b37a091d` |
| `model-profiles.json` | `521522a6caa746976a95f6569f72c734afb0cc93f9ed9190c3697624c2b7f394` |

Les mêmes hashes ont été recalculés après le run. Aucun correctif ni retry n'a
été effectué.

## 7. Chargement réel unique

La commande réelle a été exécutée exactement une fois :

```text
python -B experiments/kernel-v1/tools/probe_opencode.py run --profile qwen3.6-27b-q4km --acknowledge-local-inference
```

Un serveur Ollama et un chargement non génératif ont été utilisés. Le chargement
mur a duré **4,406 s** ; sa réponse n'exposait ni `load_duration` natif ni
`eval_count`. Le modèle chargé était uniquement `qwen3.6:27b`, avec le digest de
manifest attendu. Aucun autre modèle n'était chargé.

## 8. Contexte

`/api/ps` a exposé exactement **16 384** tokens. Le serveur enfant avait reçu la
même valeur et le profil OpenCode conservait cette limite. Le contexte n'a été
ni réduit ni augmenté.

## 9. Répartition CPU/GPU

| Mesure chargée | Valeur |
| --- | ---: |
| Taille totale | 24 338 500 544 octets, 22,667 Gio |
| Allocation GPU | 17 574 194 176 octets, 16,367 Gio, 72,21 % |
| Allocation CPU/RAM calculée | 6 764 306 368 octets, 6,300 Gio, 27,79 % |
| Couches GPU | 55 / 65 |
| Couches CPU | 10 / 65 |

Les tailles sont celles de `/api/ps`; elles décrivent l'allocation chargée et ne
doivent pas être confondues avec le seul blob GGUF.

## 10. RAM, VRAM et marge

| Moment | RAM disponible | VRAM utilisée | VRAM libre |
| --- | ---: | ---: | ---: |
| Avant chargement | 48,146 Gio | 1 940 MiB | 22 199 MiB |
| Modèle chargé | 41,663 Gio | 20 456 MiB | **3 683 MiB** |
| Après nettoyage interne | 48,239 Gio | 1 941 MiB | 22 198 MiB |
| Contrôle externe final | environ 48,239 Gio | 1 938 MiB | 22 201 MiB |

La RAM chargée dépassait le minimum de 16 Gio. La VRAM libre réellement
observée était toutefois **413 MiB sous le gate** de 4 096 MiB, soit une marge
de seulement 3,597 Gio. Le gate a donc bloqué avant tout lancement OpenCode.

## 11. Inférence et sortie

| Propriété | Observation |
| --- | --- |
| Provider demandé | `local-ollama` |
| Modèle Ollama | `qwen3.6:27b` |
| Processus OpenCode d'inférence | 0 |
| Requêtes Qwen | 0 |
| Retry | 0 |
| Tool call / permission / sous-agent | 0 |
| Sortie attendue | `Understand the requested outcome, constraints, relevant work, and` |
| Sortie réelle | aucune ; prompt non envoyé |
| Exit OpenCode | non observé ; OpenCode non lancé |

Le critère `OpenCode exit 0` n'est donc pas satisfait. Il ne s'agit pas d'un
échec comportemental de Qwen mais d'un arrêt matériel préalable.

## 12. Tokens et vitesse

`prompt_eval_count`, `prompt_eval_duration`, `eval_count`, `eval_duration`,
tokens/s, tokens input/output/reasoning et durée OpenCode sont non mesurés parce
qu'aucune inférence n'a eu lieu. Le seul temps nouveau est le chargement mur de
4,406 s.

Le 35B historique avait chargé en 4,234 s et généré à 45,934 tokens/s lors d'un
autre canari. Cette vitesse ne peut pas être comparée à un run 27B sans
génération. À contexte identique, le présent 27B réserve davantage à CPU :
16,367 Gio GPU et 6,300 Gio CPU, contre 21,033 Gio GPU et 4,288 Gio CPU pour le
35B historique. Les baselines système diffèrent ; la qualité n'est pas
comparable sur ce seul canari.

## 13. Réseau

Le listener était possédé et lié uniquement à `127.0.0.1:11434`. Le moniteur du
serveur a observé trois connexions loopback et aucune connexion non-loopback.
OpenCode n'ayant pas été lancé, il n'a créé aucune connexion. Après le run,
aucun listener ne subsistait ; seuls des sockets `TIME_WAIT` loopback transitoires
étaient visibles.

## 14. Statut

Le résultat est **BLOCKED** : le réglage officiel a bien modifié l'offload et
augmenté la marge par rapport au premier chargement 27B, mais 3 683 MiB restent
inférieurs au minimum strict de 4 096 MiB. Le protocole interdit tout ajustement
vers 5 ou 6 Gio, second chargement ou retry dans cette mission.

## 15. Nettoyage

Le probe a demandé le déchargement, confirmé `/api/ps` vide, arrêté le serveur et
ses enfants possédés, libéré le port et supprimé la racine temporaire ainsi que
les logs. Le model store et le repository sont restés inchangés pendant le run.
Le contrôle externe final a confirmé zéro processus Ollama/OpenCode et une
mémoire revenue à un état cohérent.

## 16. Fichiers de mission

- `model-profiles.json` : politique expérimentale 27B uniquement ;
- `tools/probe_ollama.py` et `tools/probe_opencode.py` : validation, scope enfant,
  plan, mesures et gate ;
- leurs deux fichiers de tests ;
- le présent rapport, le README, le contrat, le rapport 27B historique et le
  statut projet.

Tous les rapports historiques sont préservés.

## 17. Racine active

`AGENTS.md` et `CLAUDE.md` sont inchangés. Leurs SHA-256 avant et après le run
sont respectivement
`0205768d593ad1036009a19be137e1cc2cca92670c56238db809a1d921da95e5` et
`336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49`.
Aucun `opencode.json` ou réglage Ollama global n'a été créé.

## 18. Git final attendu

La branche reste `main`. Après le commit unique de mission, le worktree doit être
propre. Aucun push ou publication n'est autorisé.

## 19. Recommandation

Ne pas rejouer ce protocole inchangé et ne pas augmenter automatiquement la
réserve. Une mission séparée, sans chargement initial, devrait décider entre un
modèle officiel plus petit et une nouvelle politique CPU/GPU explicitement
autorisée. Le chemin OpenCode + Qwen réel reste non validé.
