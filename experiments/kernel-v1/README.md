# Kernel v1 expérimental

## Statut

Ce candidat est **expérimental, inactif et non promu**. Il n'est chargé
automatiquement dans EGX_Terminal ni par Codex, ni par Claude Code, ni par
OpenCode. Son existence ne modifie pas le bootstrap actuellement chargé à la
racine. Une validation séparée a confirmé sa découverte dans des fixtures Codex
CLI 0.144.6 jetables ; cela ne constitue ni activation ni promotion.

## Objet de l'expérience

Le répertoire isole un traitement compact destiné à tester si neuf invariants
comportementaux améliorent la correction, le périmètre causal, la vérification et
la communication sans coût permanent disproportionné. Il fige aussi un prototype
de distribution statique, puis isole la validation de chargement Codex de toute
évaluation comportementale inter-harness.

## Prototype de distribution statique

[`tools/sync_adapters.py`](tools/sync_adapters.py) est un générateur expérimental
Python 3 sans dépendance tierce. Dans une cible jetable explicitement fournie, il
matérialise :

- `doctrine/KERNEL.md`, copie exacte de [`KERNEL.md`](KERNEL.md) ;
- `AGENTS.md`, copie exacte du canon pour Codex et OpenCode ;
- `CLAUDE.md`, import minimal `@doctrine/KERNEL.md` ;
- `.egx/doctrine-lock.json`, preuve déterministe de version, stratégie, chemins
  et hashes.

Les opérations disponibles sont `plan`, `write` et `check`. La cible racine du
repository est toujours refusée. Le générateur n'est ni une dépendance runtime,
ni à lui seul une preuve de découverte par un harness. Son contrat, ses tests et
ses limites sont consignés dans le
[rapport de distribution statique](validation/static-distribution.md).

## Probe runtime Codex 0.144.6

[`tools/probe_codex.py`](tools/probe_codex.py) construit six repositories Git
jetables et teste baseline, découverte racine, deux chargements du kernel généré,
scope imbriqué et override. Il impose `--ephemeral`, une sandbox read-only et les
événements JSONL, refuse EGX_Terminal comme cible et ne conserve aucun transcript
brut. Ses tests sans modèle sont dans
[`tests/test_probe_codex.py`](tests/test_probe_codex.py).

La campagne du 2026-07-20 a obtenu six `PASS` sur six tentatives, sans outil,
retry ni mutation. Le protocole, les tokens, les limites et la recommandation
restreinte à Codex CLI 0.144.6 sont consignés dans le
[rapport runtime](validation/codex-runtime-0.144.6.md).

## Readiness OpenCode 1.17.9

Une mission strictement sans inférence a identifié le binaire OpenCode 1.17.9,
sa surface non interactive, ses mécanismes d'isolation connus et les runtimes
locaux disponibles. Un modèle Ollama `qwen3.6:35b` est présent sur disque, mais
aucun serveur local n'était actif et plusieurs propriétés de confinement restent
à valider. La campagne runtime OpenCode est donc **BLOCKED**, sans création de
probe. Les faits, divergences entre documentation actuelle et version installée,
gates réseau et proposition de configuration jetable sont consignés dans le
[rapport de readiness](validation/opencode-readiness-1.17.9.md).

## Smoke runtime Ollama 0.20.2 + Qwen 3.6 35B

Un probe Python standard-library fermé a validé séparément le runtime local
`qwen3.6:35b` avec un contexte effectif de 16 384 tokens. L'unique inférence a
retourné exactement `QWEN_LOCAL_OK`, sans thinking, puis le modèle, le serveur,
ses enfants et les journaux temporaires ont été nettoyés. Ce résultat **PASS**
n'active pas OpenCode et ne valide pas encore son provider. Protocole, identité,
mémoire, métriques, incidents pré-inférence et limites sont consignés dans le
[rapport Ollama/Qwen](validation/ollama-qwen3.6-35b-smoke.md).

## Smoke OpenCode 1.17.9 + Ollama + Qwen

Un probe fermé a ensuite généré le workspace jetable attendu, isolé toutes les
racines connues d'OpenCode, chargé une fois le modèle exact à 16 384 tokens et
lancé un unique `opencode run`. OpenCode a quitté avec le code 1 avant toute
requête modèle ou émission JSONL ; aucune relance n'a été faite. Le résultat est
donc **FAIL** et ne valide ni le provider, ni la découverte d'`AGENTS.md`, ni la
transmission du kernel. Modèle, serveur, processus, port et racine temporaire ont
été intégralement nettoyés. Le protocole et les limites sont consignés dans le
[rapport OpenCode/Qwen](validation/opencode-qwen3.6-smoke-1.17.9.md).

## Diagnostic OpenCode 1.17.9 sans inférence

Le défaut pré-provider a ensuite été identifié précisément : OpenCode 1.17.9
rejetait la clé inline inconnue `subagent_depth`. Le probe corrigé expose
désormais `diagnose`, démarre un faux provider OpenAI-compatible uniquement sur
loopback et inspecte la requête sans conserver son payload. L'unique validation
mock a obtenu une requête, le modèle fictif exact, le kernel exact une fois,
aucun outil et un JSONL final `MOCK_OK`, avec nettoyage complet. Cela valide
l'initialisation et le transport OpenCode, pas Qwen. Détails et limites :
[rapport diagnostique](validation/opencode-preflight-diagnostic-1.17.9.md).

## Pivot Qwen 3.6 27B et reprise OpenCode

Le modèle officiel Ollama `qwen3.6:27b` Q4_K_M est désormais installé sans
remplacer le 35B. Un registre expérimental à deux profils permet aux probes de
sélectionner explicitement l'un ou l'autre modèle tout en conservant le 35B par
défaut. Les 113 tests et le diagnostic mock passent.

Le chargement réel unique du 27B à 16 384 tokens a toutefois laissé seulement
549 MiB de VRAM. Le nouveau gate absolu de 3 Gio a donc arrêté le protocole avant
le lancement d'OpenCode : zéro requête Qwen et zéro retry. Le résultat est
**BLOCKED**, avec nettoyage complet. Détails :
[rapport OpenCode/Qwen 27B](validation/opencode-qwen3.6-27b-smoke-1.17.9.md).

## Réservation VRAM 27B

Une mission séparée a ajouté au seul profil 27B une politique expérimentale de
réservation de 4 Gio par GPU, transmise uniquement au serveur Ollama enfant par
`OLLAMA_GPU_OVERHEAD=4294967296`. Les 122 tests et le diagnostic mock passent.

Le chargement réel unique à 16 384 tokens a déplacé 10 couches sur 65 vers CPU,
mais n'a laissé que 3 683 MiB de VRAM libre. Le gate strict de 4 096 MiB a donc
classé le run **BLOCKED** avant OpenCode : zéro processus OpenCode, zéro requête
Qwen et nettoyage complet. Détails :
[rapport de réservation/offload](validation/opencode-qwen3.6-27b-offload-smoke-1.17.9.md).

## Smoke final 27B avec gate mesuré

La mesure précédente a autorisé un hard gate de 3 072 MiB pour le seul profil
27B. La réservation demandée reste 4 Gio et la cible de confort reste 4 Gio ;
une marge entre 3 et 4 Gio est « acceptable, confort limité ». Cette politique
mesurée ne promet rien pour d'autres machines.

Le run unique a franchi le gate avec 3 550 MiB libres et 55/65 couches GPU, mais
OpenCode a émis une première ligne non JSONL avant toute requête Qwen. Le résultat
est donc **FAIL**, sans retry, puis avec nettoyage complet. Détails :
[rapport final OpenCode/Qwen 27B](validation/opencode-qwen3.6-27b-final-smoke-1.17.9.md).

## Origine conceptuelle

Le texte est une reformulation originale de la
[synthèse des cinq audits](../../docs/research/synthesis/README.md) et de ses
[candidats doctrinaux](../../docs/research/synthesis/doctrine-candidates.md). Il
ne copie ni persona, ni slogan, ni formulation d'un repository audité. La
[décision 0002](../../docs/decisions/0002-llm-agnostic-kernel-architecture.md)
formalise son statut et ses frontières.

## Mesure et intégrité

Les mesures portent uniquement sur les octets exacts de
[`KERNEL.md`](KERNEL.md), encodés en UTF-8 sans BOM, avec fins de ligne LF et sans
fin de ligne finale :

- octets : longueur du tableau d'octets UTF-8 ;
- caractères : nombre de points de code du texte ASCII, identique ici au nombre
  d'octets ;
- mots : segments non vides séparés par un ou plusieurs caractères d'espacement
  (`\s+`) ;
- tokens estimés : `ceil(nombre de caractères / 4)` ;
- intégrité : SHA-256 des mêmes octets.

Cette estimation transparente permet une comparaison statique. Elle n'est le
tokenizer exact d'aucun modèle. Les valeurs calculées et le hash sont enregistrés
dans [`manifest.json`](manifest.json). Métadonnées, wrappers et futurs
adaptateurs devront être mesurés séparément. Le fichier [`.gitattributes`](.gitattributes)
maintient le payload en LF lors des checkouts Git.

## Limites

- Aucun effet comportemental n'a été validé.
- Aucun contexte système complet réellement injecté par un harness n'a été
  capturé ; la validation Codex repose sur des canaris fermés.
- L'initialisation OpenCode, le transport mock et la découverte racine unique du
  kernel sont validés sans inférence ; le premier smoke Qwen reste un **FAIL** et
  n'a pas été retenté.
- Le runtime Ollama/Qwen est validé séparément à 16 384 tokens, mais la marge
  VRAM observée est faible pour le 35B comme pour le 27B ; même la réserve 27B
  de 4 Gio n'a laissé que 3 683 MiB libres. Les deux gates 27B ont bloqué avant
  inférence et le chemin OpenAI-compatible réel reste à tester via OpenCode.
- Le générateur statique existe seulement comme outil expérimental ; aucun
  adaptateur n'est actif dans ce repository.
- Aucun hook, skill, mémoire ou runtime additionnel n'existe ici.
- Les règles peuvent être sous-spécifiées pour une mission risquée ou trop
  présentes pour une tâche triviale.
- Qwen n'est pas un harness ; son comportement dépendra du runtime, du modèle
  précis, de la quantification et du template testés.

## Conditions avant promotion

La promotion exige au minimum des adaptateurs expérimentaux inspectables, une
preuve de chargement unique et de synchronisation, les tests de scope et de
précédence sur versions fixées, la campagne du
[plan de validation](../../docs/research/synthesis/validation-plan.md), le respect
du plafond de 300 tokens estimés pour le payload et une décision explicite
séparée.

## Fichiers racine volontairement inchangés

`AGENTS.md` et `CLAUDE.md` restent inchangés. Aucun `opencode.json`, fichier
d'instruction racine ou réglage utilisateur/global n'est créé. Les tests utilisent
uniquement des répertoires temporaires extérieurs au repository. Le candidat ne
peut donc pas être confondu avec le comportement actif du workspace.
