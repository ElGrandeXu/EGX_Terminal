# Diagnostic pré-provider OpenCode 1.17.9

## Statut et portée

- **Date :** 2026-07-20
- **Statut :** **PASS** pour l'initialisation et le transport vers un mock local
- **OpenCode :** `1.17.9`
- **Provider mock :** `mock-openai`
- **Modèle fictif demandé :** `egx-mock`
- **Inférence :** aucune
- **Ollama / Qwen :** non démarrés, non chargés, non contactés
- **Exécutions OpenCode :** quatre au total, dont une contre le mock
- **Requêtes mock :** une au total, une de génération
- **Retry :** zéro

Ce diagnostic valide la construction et le transport d'une requête OpenCode vers
un endpoint OpenAI-compatible local déterministe. Il ne valide ni Ollama, ni
Qwen, ni un comportement de modèle.

## 1. Incident initial

La Mission 12 avait lancé le binaire natif avec la commande normalisée suivante,
depuis le workspace généré et avec un environnement enfant allowlisté :

```text
opencode.exe run --pure --dir <temporary-workspace> \
  --model local-ollama/qwen3.6:35b --format json <closed-prompt>
```

OpenCode avait quitté avec le code `1` en 0,641 seconde, avec stdout vide, zéro
événement JSONL et zéro requête provider. Le stderr était présent mais n'avait
pas été conservé. Ollama et Qwen avaient été préchargés correctement puis
nettoyés ; ils n'expliquaient donc pas le défaut pré-provider.

## 2. Cause racine établie

La cause racine est la clé de configuration inline de premier niveau
`subagent_depth`. Elle n'existe pas dans le schéma `ConfigV1.Info` de la version
1.17.9. Le parseur de cette version calcule explicitement les clés de premier
niveau inconnues et lève `InvalidError` avant l'initialisation du provider.

La cause est **prouvée**, et non déduite seulement de la chronologie : une
reproduction native avec la configuration exacte de Mission 12 a rendu le même
code `1`, stdout vide et le diagnostic de schéma précis présenté ci-dessous.

Sources officielles exactes :

- OpenCode tag `v1.17.9`, commit
  [`5c23e88419c4743b9be42cea132f2fb1e6cb63ff`](https://github.com/anomalyco/opencode/commit/5c23e88419c4743b9be42cea132f2fb1e6cb63ff) ;
- rejet des clés inconnues dans
  [`packages/opencode/src/config/parse.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/config/parse.ts) ;
- surface du schéma dans
  [`packages/core/src/v1/config/config.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/core/src/v1/config/config.ts).

## 3. Preuves

Le prévol a confirmé `main`, worktree propre, HEAD
`ddc455b4094b05bb4dedd4381e2608616aeb74ad` et sujet
`test: smoke OpenCode with local Qwen`. OpenCode a répondu `1.17.9`. Son binaire
natif faisait 165 154 696 octets et avait le SHA-256
`65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6`.

Avant et après le diagnostic : aucun processus OpenCode ou Ollama, port 11434
libre et worktree sans mutation runtime. Le mock final a ensuite démontré que la
configuration corrigée est acceptée, que le provider est atteint et que le flux
JSONL arrive à son terme.

## 4. Stderr sanitizé

Le stderr utile de la reproduction native était exactement :

```text
Error: Configuration is invalid at OPENCODE_CONFIG_CONTENT
↳ Unrecognized key: subagent_depth
```

Il ne contenait après sanitisation ni chemin absolu, ni nom utilisateur, ni
secret. L'exécution mock corrigée avait un stderr vide ; cette absence est
enregistrée comme un fait (`stderr_present:false`, valeur sanitizée `null`). Les
deux flux ont été décodés en UTF-8 avec remplacement explicite des octets
invalides. Aucun stderr brut n'a été committé.

## 5. Lanceur PowerShell et binaire natif

PowerShell résout `opencode` vers le lanceur npm `opencode.ps1`. Son contenu
inspecté ne transforme pas les arguments : il appelle le binaire natif et rend
son code de sortie. L'invocation de version via ce lanceur a réussi.

La Mission 12, la reproduction causale et le diagnostic mock ont utilisé
directement `opencode.exe`. La même erreur de configuration est donc présente
sans couche PowerShell : le lanceur n'est pas la cause. Le probe conserve la
résolution préférentielle du binaire natif pour éliminer une couche d'encodage et
de quoting. Un test vérifie cette préférence lorsqu'un lanceur `.ps1` est trouvé.

## 6. Environnement Windows minimal requis

Seules cinq variables parentes Windows sont conservées lorsqu'elles existent :
`PATH`, `SYSTEMROOT`, `WINDIR`, `COMSPEC` et `PATHEXT`. Le run mock réussi prouve
qu'elles suffisent au chemin d'initialisation testé. `USERNAME`, `HOMEDRIVE` et
`HOMEPATH` ne sont pas nécessaires dans ce cas.

`HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, les quatre racines `XDG_*`,
`TMP`, `TEMP`, les caches npm/Bun et `OPENCODE_CONFIG_DIR` pointent tous sous la
même racine temporaire. `OPENCODE_DB=:memory:` est accepté. Les désactivations de
plugins, skills, LSP download, catalogue de modèles et autoupdate sont
maintenues. Les credentials et variables OTLP ne sont pas hérités.

## 7. Configuration effective

La correction retire seulement la clé invalide `subagent_depth`. La
configuration inline acceptée conserve : partage et snapshot désactivés,
compaction automatique et prune désactivés, permissions wildcard `deny`, aucun
MCP, aucun plugin, aucune instruction additionnelle, un seul provider autorisé,
et le même identifiant pour `model`, `small_model` et `--model`.

Le mode `--pure` reste placé après `run` et coexiste avec
`OPENCODE_CONFIG_CONTENT`. La réussite de l'appel prouve cette interaction pour
1.17.9. Le JSON est sérialisé en mémoire et n'est écrit dans aucun
`opencode.json`.

Une seconde correction préventive, établie par la source 1.17.9, ajoute un titre
CLI fixe. Avec le titre par défaut, `SessionPrompt.ensureTitle` peut appeler le
petit modèle avec deux retries configurés. `--title <fixed-title>` évite ce chemin
et rend le plafond d'une requête réellement vérifiable. Source :
[`packages/opencode/src/session/prompt.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/session/prompt.ts).

## 8. Protocole mock

`python -B experiments/kernel-v1/tools/probe_opencode.py diagnose` démarre un
`ThreadingHTTPServer` de la bibliothèque standard, lié littéralement à
`127.0.0.1` sur un port dynamique. Il implémente seulement :

- `GET /v1/models`, pour une éventuelle découverte ;
- `POST /v1/chat/completions`, pour la génération simulée.

Le run observé n'a utilisé que le second endpoint. La réponse est un flux SSE
avec un chunk texte `MOCK_OK`, un chunk final `finish_reason:"stop"` avec usage,
puis `data: [DONE]`. Ce format suit les fixtures officielles du package
`@ai-sdk/openai-compatible` `2.0.41`, tag pointant sur le commit
[`99327b1d7b3d172ed0aae7230ae153f2d32b0ebb`](https://github.com/vercel/ai/commit/99327b1d7b3d172ed0aae7230ae153f2d32b0ebb).

Aucun SDK n'a été installé ou téléchargé. Le serveur ne calcule aucun token et
ne choisit aucune réponse en fonction du prompt.

## 9. Requêtes observées

Une seule requête totale a été reçue :

| Méthode | Route | Génération | Acceptée |
| --- | --- | ---: | ---: |
| `POST` | `/v1/chat/completions` | oui | oui |

Le corps a été décodé, inspecté puis abandonné en mémoire. Aucun payload brut,
header complet ou transcript n'est conservé. Il contenait deux messages, dans
l'ordre `system`, `user`, de 10 016 et 143 caractères. Leurs SHA-256 textuels
étaient respectivement
`e6eccdb9f0f973c02963ee41d60f8e60f67ec9e6307990aff1f4ea387889f795`
et `dbbad163df479010d922e03cfad85fafac502cc37c8b30e4306900152176a578`.

Les options pertinentes étaient `stream:true`, `temperature:0`,
`max_tokens:16` et `stream_options.include_usage:true`. Le prompt fermé attendu
apparaissait exactement une fois.

## 10. Modèle demandé

Le champ `model` reçu valait exactement `egx-mock`, soit le modèle explicitement
déclaré sous le provider exclusif `mock-openai`. Aucun endpoint de découverte et
aucun autre modèle n'ont été demandés.

## 11. Occurrence du kernel

Le probe décode les octets exacts de [`KERNEL.md`](../KERNEL.md) en UTF-8 et
compte cette chaîne exacte dans les contenus textuels de tous les messages. Le
résultat est **une occurrence exacte**. Il ne s'agit donc pas d'une détection
sémantique approximative. L'import `@doctrine/KERNEL.md` de `CLAUDE.md`
n'apparaissait pas dans la requête (`0` occurrence).

## 12. Présence des outils

Le champ `tools` était absent et le nombre d'outils actifs était `0`. Le champ
`tool_choice` était absent. OpenCode n'a émis ni événement d'outil, ni demande de
permission. La source 1.17.9 filtre les outils désactivés par la ruleset avant la
requête ; le wildcard `deny` est donc conservé dans la configuration et dans la
surcharge d'environnement. Source :
[`packages/opencode/src/session/llm/request.ts`](https://github.com/anomalyco/opencode/blob/v1.17.9/packages/opencode/src/session/llm/request.ts).

## 13. Sortie OpenCode

OpenCode a quitté avec le code `0` et produit trois événements JSONL. Le parseur
a extrait exactement `MOCK_OK`. Aucun raisonnement visible, outil ou événement
de permission n'a été détecté. Le JSONL brut et le `sessionID` n'ont pas été
persistés.

## 14. Correction apportée

[`probe_opencode.py`](../tools/probe_opencode.py) a reçu quatre changements
bornés : retrait de `subagent_depth`, titre fixe anti-seconde-requête, capture et
sanitisation du stderr, et sous-commande `diagnose` avec mock/inspection en
mémoire. Les protections de Mission 12 restent actives. Le chemin `run` Qwen
continue d'exiger `--acknowledge-local-inference`.

Les tests vérifient en plus les erreurs de configuration, le binaire natif,
l'environnement minimal, le placement CLI, le mock, JSON/SSE, `MOCK_OK`, le
kernel à zéro/une/deux occurrences, les outils, les requêtes supplémentaires et
le nettoyage.

## 15. Propriétés démontrées

- OpenCode 1.17.9 accepte la configuration inline corrigée avec `--pure`.
- La DB mémoire, les racines temporaires et les locks internes n'empêchent pas
  l'initialisation complète observée.
- Le provider OpenAI-compatible embarqué atteint le seul endpoint loopback.
- Le modèle, les rôles, tailles et hashes de contenus sont inspectables sans
  conserver le payload.
- `AGENTS.md` injecte le kernel exact une fois dans ce cas racine.
- Les permissions wildcard retirent tous les outils de la requête observée.
- Le flux SSE minimal officiel produit un JSONL final `MOCK_OK`.
- Workspace généré, repository, processus, serveur et racine temporaire sont
  nettoyés après succès.

## 16. Propriétés non démontrées

- compatibilité réelle OpenCode + Ollama OpenAI-compatible ;
- chargement, réponse, template, tokens, latence ou comportement de Qwen ;
- adhérence du modèle au kernel ;
- contexte système complet au-delà des résumés mécaniques autorisés ;
- scope imbriqué, précédence ou compaction ;
- absence exhaustive de paquets au niveau OS.

## 17. Limites

Le moniteur par PID n'a échantillonné aucune connexion, probablement en raison
de la brièveté de l'appel. La réception directe par le serveur prouve néanmoins
la connexion loopback. Aucune connexion non-loopback n'a été observée ; les
proxies fermés, l'allowlist, l'absence de credentials et les désactivations
réduisent les autres chemins, sans constituer une règle pare-feu.

Huit fichiers existaient sous la racine jetable avant sa suppression, dont les
quatre fichiers générés du workspace. Cette mesure ne prouve pas l'absence
d'écriture hors des racines connues ; le snapshot du repository et la disparition
de la racine bornent ce qui a été vérifié.

## 18. Aptitude à retenter le smoke Qwen

**GO conditionnel** pour une mission séparée limitée à un unique smoke Qwen. Le
défaut d'initialisation est corrigé, le provider et le transport sont validés
sans inférence, le titre empêche la requête secondaire connue, et le budget d'une
requête est mesurable.

Ce GO n'autorise pas automatiquement une inférence. Le futur prévol doit encore
confirmer les identités OpenCode/Ollama/Qwen, le contexte 16 384, la baseline
mémoire, zéro processus préexistant et le port 11434 libre avant que le probe ne
démarre son serveur Ollama possédé.

## 19. Commande recommandée pour la prochaine mission

Après une autorisation explicite d'inférence locale et le prévol complet :

```text
python -B experiments/kernel-v1/tools/probe_opencode.py run --acknowledge-local-inference
```

La prochaine mission doit arrêter au premier code non nul, à toute requête autre
que l'unique génération attendue, à tout outil/permission, à toute connexion
non-loopback ou à toute mutation de workspace. Elle ne doit effectuer aucun
retry.

## Budget exact de cette mission

1. `opencode --version` via le lanceur PowerShell : version seulement.
2. reproduction native : erreur prouvée, mais affichage local de la preuve
   interrompu par l'encodage console ; nettoyage confirmé.
3. reproduction native identique avec sérialisation ASCII de la preuve : stderr
   capturé et cause établie.
4. validation native contre le mock : `PASS`.

Une seule exécution a contacté le mock. Les trois autres n'avaient aucun serveur
provider disponible et ont produit zéro requête modèle. Aucun retry, provider
distant, démarrage Ollama, chargement Qwen ou calcul de modèle n'a eu lieu.
