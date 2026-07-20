# Résolution OpenCode 1.17.9 + Qwen 3.6 27B

## Verdict

- **Date :** 2026-07-21
- **Statut final :** **BLOCKED** après épuisement du budget de trois démarrages
  Ollama, sans relâcher le critère de réponse exacte
- **OpenCode / Ollama :** `1.17.9` / `0.20.2`
- **Provider / modèle :** `local-ollama` / `qwen3.6:27b` Q4_K_M
- **Contexte / parallélisme :** 16 384 / 1
- **Réservation / gate :** 4 Gio par GPU / 3 072 MiB libres
- **Lancements runtime OpenCode :** 3 sur 6 autorisés
- **Démarrages Ollama :** 3 sur 3 autorisés
- **Requêtes Qwen :** 2 sur 3 autorisées

Le chemin OpenCode vers le provider local est désormais fonctionnel : les deux
dernières tentatives ont atteint exactement une fois `/v1/chat/completions`, et
OpenCode a quitté avec le code 0. Le PASS terminal n'est toutefois pas établi.
Après désactivation effective du thinking, Qwen n'a pas rendu la chaîne exacte
demandée. Un quatrième démarrage Ollama aurait dépassé le budget de mission.

## Résolution classificatoire finale

Le verdict `BLOCKED` ci-dessus reste le résultat historique de cette mission :
son budget était épuisé avant d'obtenir l'égalité stricte exigée. Il n'est pas
réécrit. La résolution de compatibilité du 2026-07-21 interprète cependant les
preuves selon quatre niveaux indépendants :

1. distribution statique : **PASS** ;
2. transport runtime OpenCode → Ollama → `qwen3.6:27b` : **PASS** ;
3. adhérence formelle exacte au canari : **FAIL** ;
4. efficacité comportementale : **NOT TESTED**.

La dernière tentative a réellement utilisé le 27B à 16 384 tokens de contexte,
envoyé une seule requête et reçu une réponse sans reasoning. Les mots exigés y
apparaissent dans le bon ordre, mais sans la ponctuation exacte et avec des mots
supplémentaires. Aucun outil ni réseau non-loopback n'a été utilisé. Ces faits
établissent un échec formel de contrôle de sortie, pas un défaut de découverte,
de provider ou de modèle.

OpenCode + Qwen n'est donc plus `BLOCKED` au niveau projet. La compatibilité est
**SUPPORTED — EXPERIMENTAL**, le projet est non bloqué pour poursuivre, et la
prochaine preuve attendue est comportementale. Aucun kernel n'est promu. La
[synthèse de compatibilité runtime](runtime-compatibility-summary.md) porte le
verdict transversal et explique pourquoi le canari exact ne doit pas servir de
proxy de qualité générale.

## Ledger

| Tentative | Provider atteint | Requête Qwen | Résultat | Cause | Correctif |
|---|---:|---:|---|---|---|
| 1 | non | 0 | FAIL, OpenCode exit 1, première ligne stdout non JSON | valeur 35B figée dans les paramètres Python par défaut alors que le profil actif et la configuration déclaraient le 27B | résolution de `MODEL` au moment de l'appel ; régression commande/configuration |
| 2 | oui | 1 | FAIL, OpenCode exit 0, 64 tokens mais aucun texte final | `think:false` était une option provider inefficace ; le thinking a consommé tout le budget de sortie | remplacement par `reasoningEffort:"none"`, validé comme `reasoning_effort:"none"` contre le mock |
| 3 | oui | 1 | FAIL, OpenCode exit 0, texte non exact | thinking désactivé, mais Qwen omet la ponctuation et dépasse huit mots | aucun correctif spéculatif ni quatrième démarrage ; budget Ollama atteint |

Les trois tentatives diffèrent causalement. Aucune n'a été répétée sans
modification justifiée.

## Incident JSONL initial

Le probe historique décodait les sorties avec `errors="replace"`, puis levait
depuis `parse_jsonl` avant de rendre le résultat d'`invoke_opencode`. Cette
structure perdait les octets concernés, le code de sortie, stderr et le résumé
réseau au niveau public.

La tentative 1 instrumentée a établi les faits suivants pour la première ligne
invalide :

| Propriété | Valeur sanitizée |
|---|---|
| Canal | stdout |
| Flux stdout | 1 541 octets |
| Ligne / offset | ligne 1, offset octet 0 (base zéro) |
| Taille de ligne | 39 octets, fin LF |
| Premiers octets hex | `5b30303a34363a34372e3835305d204552524f522028233130393431293a2066` |
| BOM | absent |
| Encodage | UTF-8 strict valide |
| Fins de ligne du flux | 2 CRLF, 10 LF, 0 CR isolé |
| ANSI | aucune séquence |
| Texte | `[00:46:47.850] ERROR (#10941): failed {` |
| Position JSON | colonne 3, base un |
| JSON valides avant / après | 0 / 2 lignes |
| stderr | vide, 0 octet |
| Exit OpenCode | 1 |
| Requêtes provider | 0 |

La capture binaire est restée en mémoire et dans la racine jetable du probe ;
aucun transcript brut n'est committé. Le présent rapport ne contient que la
version bornée et sanitizée.

## Cause racine de l'incident

### Preuve documentée

- `activate_profile("qwen3.6-27b-q4km")` avait bien construit une configuration
  contenant uniquement `local-ollama/qwen3.6:27b`.
- La commande réellement observée demandait
  `local-ollama/qwen3.6:35b`.
- OpenCode a quitté avec le code 1 avant toute requête provider.
- Le source officiel OpenCode 1.17.9 découpe `--model` en `providerID/modelID` et
  écrit les événements bruts sur stdout en mode `--format json` :
  <https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/cli/cmd/run.ts>.

### Interprétation

Les signatures de `normalized_command`, `opencode_command`,
`invoke_opencode` et `validate_parsed_events` utilisaient `MODEL` comme valeur
par défaut. Python évalue ces valeurs à la définition des fonctions, lorsque le
profil historique 35B est actif. Changer ensuite le profil global ne changeait
donc pas ces valeurs déjà capturées. Le mock passait parce qu'il fournissait
explicitement son provider et son modèle.

### Décision et correctif

Les quatre paramètres deviennent optionnels et résolvent la valeur globale
active au moment de l'appel. Aucun profil, modèle, endpoint ou contrôle réseau
n'est modifié. Le test de régression active le 27B, construit la configuration
et la commande, puis exige l'identité exacte de leurs modèles.

## Capture et parsing des sorties

Le subprocessus OpenCode est désormais lu en mode binaire. Le parseur décode
l'UTF-8 strictement et attache à une erreur JSONL : taille, hexadécimal borné,
BOM, encodage, fins de ligne, ANSI, texte sanitizé, canal, position, lignes JSON
valides avant/après et événements déjà parsés. `invoke_opencode` rend toujours
le code de sortie, les deux canaux, les connexions et le résultat d'arrêt des
processus avant que le chemin supérieur classe l'échec.

Seules trois normalisations bénignes et testées sont permises : ligne vide,
BOM UTF-8 au début du flux et séquences ANSI enveloppant entièrement un objet
JSON. Un warning, un log préfixant du JSON, un fragment multi-ligne, deux objets
concaténés ou un octet UTF-8 invalide restent des erreurs visibles.

## Thinking sur le chemin OpenAI-compatible

### Tentative 2

Après réparation du modèle, OpenCode a atteint le provider une fois et quitté
avec le code 0. Les deux événements JSONL contenaient 2 212 tokens input et 64
tokens output, mais aucun événement texte. La limite de 64 tokens avait été
consommée avant une réponse visible.

Le contrat officiel Ollama 0.20.2 expose `reasoning_effort` dans
`ChatCompletionRequest`; la valeur `none` est convertie en `Think:false` :
<https://github.com/ollama/ollama/blob/v0.20.2/openai/openai.go>.
OpenCode 1.17.9 place les options modèle sous le namespace du SDK provider :
<https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/provider/transform.ts>.

Le champ expérimental `think:false` a donc été remplacé uniquement par l'option
SDK officielle `reasoningEffort:"none"`. Le diagnostic mock a ensuite observé
sur le fil `reasoning_effort:"none"`, avec une requête, un kernel exact, zéro
outil et `MOCK_OK`.

### Tentative 3

La correction a produit un événement texte, `finish_reason:"stop"`, 2 214
tokens input, 14 output et 0 reasoning. Le thinking était donc effectivement
désactivé. La sortie était exactement :

```text
Understand the requested outcome constraints relevant work and observable success condition Ask
```

Elle diffère de la sortie exigée :

```text
Understand the requested outcome, constraints, relevant work, and
```

La ponctuation a été omise et du texte supplémentaire a été généré. Le prompt
n'a pas été modifié. Aucun post-traitement n'a fabriqué un PASS.

## Tests de régression

Quinze tests OpenCode ont été ajoutés. Ils couvrent :

- BOM UTF-8, espaces, lignes vides, CRLF et ANSI enveloppant du JSON ;
- warning textuel, JSON précédé d'un log, JSON fragmenté, objets multiples sur
  lignes séparées et objets concaténés ;
- séparation stdout/stderr, UTF-8 invalide et sortie vide ;
- événements déjà parsés, position et lignes valides après l'incident ;
- conservation du code de sortie, stderr et connexions lors d'un échec parser ;
- résolution tardive du profil 27B dans la commande et dans la validation ;
- transmission mock exacte de `reasoning_effort:"none"`.

Après le dernier correctif : **69 tests ciblés** et **137 tests complets** ont
réussi. Le plan était `READY`; le diagnostic mock était `PASS` avec une requête,
un kernel exact, zéro outil, sortie `MOCK_OK`, exit 0 et nettoyage complet.

## Tokens et performances

| Tentative | Input | Output | Reasoning | Total | Mur OpenCode | Latence Ollama | Débit fin-à-fin | Débit endpoint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | non mesuré | non mesuré | non mesuré | non mesuré | 1,641 s | aucune requête | n/a | n/a |
| 2 | 2 212 | 64 | 0 exposé | 2 276 | 10,578 s | 8,849 s | 6,050 tok/s | 7,232 tok/s |
| 3 | 2 214 | 14 | 0 | 2 228 | 5,781 s | 4,135 s | 2,422 tok/s | 3,385 tok/s |

Le champ reasoning nul de la tentative 2 est celui des événements OpenCode ;
l'absence de texte et l'épuisement exact de 64 tokens établissent néanmoins le
comportement qui a motivé la correction. La tentative 3 démontre directement
la désactivation par ses 14 tokens visibles et zéro reasoning.

## RAM, VRAM et offload

Les trois chargements ont conservé 55 couches GPU sur 65 et 10 couches CPU.
L'allocation est restée 17 574 194 176 octets GPU et 6 764 306 368 octets CPU,
pour 24 338 500 544 octets au total.

| Tentative | RAM disponible au gate | VRAM libre au gate | VRAM libre après appel | Marge au-dessus de 3 072 MiB |
|---|---:|---:|---:|---:|
| 1 | 44 643 991 552 octets | 3 609 MiB | 3 609 MiB | 537 MiB |
| 2 | 44 644 200 448 octets | 3 604 MiB | 3 588 MiB | 516 MiB minimum observé |
| 3 | 44 597 833 728 octets | 3 648 MiB | 3 630 MiB | 558 MiB minimum observé |

Le seuil de risque a toujours été respecté. Après le nettoyage final, 22 167
MiB de VRAM étaient libres et aucun processus de calcul pertinent ne restait.

## Réseau et isolation

- Le provider configuré est exclusivement `local-ollama` sur
  `http://127.0.0.1:11434/v1`.
- Les tentatives 2 et 3 ont observé une seule connexion OpenCode vers
  `127.0.0.1:11434`.
- Les moniteurs OpenCode et Ollama n'ont observé aucune connexion non-loopback.
- Les plugins, skills externes, fetch modèle, mise à jour, télémétrie et outils
  restent désactivés ; les permissions restent wildcard `deny`.
- Aucun provider distant, téléchargement, autre modèle, outil, permission,
  sous-agent ou seconde génération n'a été utilisé.

## Propriétés démontrées

- OpenCode 1.17.9 résout et utilise réellement
  `local-ollama/qwen3.6:27b` après la correction de profil.
- Ollama 0.20.2 sert ce modèle exact à un contexte effectif de 16 384.
- Chaque tentative provider réussie produit exactement une requête Qwen.
- Le diagnostic mock mesure un kernel exact transmis une fois et aucun outil.
- `reasoning_effort:none` traverse OpenCode et le SDK, puis supprime le thinking
  pour la génération réelle.
- Le workspace généré reste inchangé et le nettoyage `finally` fonctionne sur
  les chemins parser, provider et réponse non exacte.

## Limites et blocage restant

Le critère de réponse exacte n'est pas démontré pour cette combinaison fixe de
versions et de modèle. La tentative sans thinking a montré une non-adhérence de
Qwen au comptage de mots et à la ponctuation, sans erreur de transport. Une
nouvelle hypothèse — par exemple un contrôle officiel de génération qui ne
modifie pas le prompt — nécessiterait d'abord un nouveau budget autorisant un
démarrage Ollama et une requête Qwen. Elle ne peut pas être testée dans cette
mission.

Ce statut n'est ni un bug OpenCode nécessitant une mise à jour, ni un blocage
matériel : c'est l'atteinte démontrée du budget maximal de démarrages après trois
causes distinctes, alors que le dernier critère comportemental reste faux.

## Nettoyage et intégrité

Après chaque tentative, le modèle a été déchargé, `/api/ps` est redevenu vide,
le serveur et ses enfants possédés ont été arrêtés, le port 11434 a été libéré et
la racine temporaire supprimée. Les deux model stores et le repository sont
restés inchangés pendant les runs. `AGENTS.md` et `CLAUDE.md` racine n'ont pas
été modifiés.

Les hashes gelés après le dernier correctif et avant la tentative 3 étaient :

| Fichier | SHA-256 |
|---|---|
| `tools/probe_ollama.py` | `b81006fc07d786516833c547ed970d4d369e37904592ae2b62a4a15da671d395` |
| `tools/probe_opencode.py` | `3633febfebcffb6e0f9ff2b6abe71a3dc96569edaf68da613fb7cf9b6782c1d5` |
| `model-profiles.json` | `40bd4fdfbcbc9efe42e71d9f329ea1e4731112b181a387d275a5fb533924ddc5` |

Ils ont été recalculés après la documentation et sont restés identiques. Tous
les rapports historiques restent présents.
