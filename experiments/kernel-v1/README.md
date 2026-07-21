# Kernel v1 expérimental

## Statut

Ce candidat est **expérimental, inactif, non promu et rejeté dans sa forme
équilibrée**. Il n'est chargé
automatiquement dans EGX_Terminal ni par Codex, ni par Claude Code, ni par
OpenCode. Son existence ne modifie pas le bootstrap actuellement chargé à la
racine. Une validation séparée a confirmé sa découverte dans des fixtures Codex
CLI 0.144.6 jetables. La portabilité runtime est désormais validée
expérimentalement pour les cellules Codex et OpenCode mesurées, avec une
compatibilité générale **SUPPORTED — EXPERIMENTAL** ; cela ne constitue ni
activation ni promotion. La
[synthèse de compatibilité](validation/runtime-compatibility-summary.md) sépare
distribution, transport, adhérence formelle et efficacité comportementale.

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
à valider. À ce stade historique, la campagne runtime OpenCode était donc
**BLOCKED**, sans création de probe. Les faits, divergences entre documentation
actuelle et version installée, gates réseau et proposition de configuration
jetable sont consignés dans le
[rapport de readiness](validation/opencode-readiness-1.17.9.md). Les campagnes
ultérieures ont levé ce blocage de transport.

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

## Résolution OpenCode/Qwen 27B

La mission de résolution a capturé la ligne invalide en octets et établi qu'elle
était un log d'erreur OpenCode sur stdout, non un JSONL corrompu. Le probe avait
figé `qwen3.6:35b` dans des paramètres Python par défaut alors que le profil actif
et la configuration déclaraient le 27B. La résolution tardive du modèle corrige
ce défaut et les runs suivants ont atteint une fois le provider local avec
OpenCode exit 0.

Une seconde correction remplace l'option inefficace `think:false` par le contrat
OpenAI-compatible officiel `reasoningEffort:"none"`, observé sur le fil mock
comme `reasoning_effort:"none"`. La génération réelle suivante a bien rendu du
texte sans reasoning, mais pas la réponse exacte : elle a omis la ponctuation et
dépassé huit mots. Le [rapport de résolution](validation/opencode-qwen3.6-27b-resolution.md)
conserve le statut historique **BLOCKED** de cette mission après les trois
démarrages Ollama autorisés, avec deux requêtes Qwen et nettoyage complet.

La résolution classificatoire finale ne traite plus cette non-conformité comme
un blocage d'intégration : OpenCode → Ollama → Qwen est **PASS** pour le transport
runtime, tandis que l'adhérence formelle exacte au canari est **FAIL** et
l'efficacité comportementale était encore **NOT TESTED** à cette étape. Le projet est non bloqué pour
poursuivre vers des tâches réelles, sans nouveau canari ni promotion. Détails :
[synthèse de compatibilité runtime](validation/runtime-compatibility-summary.md).

## Premier pilote comportemental OpenCode/Qwen

Le [pilote comportemental v1](behavioral/pilot-v1/results.md) a pré-enregistré
puis exécuté quatre cellules : deux tâches Python, chacune sans instruction
projet puis avec le kernel généré par `sync_adapters.py`. Les quatre cellules ont
obtenu `PASS`, avec correction causale d'une ligne, tests et acceptance réussis,
aucun changement hors scope, travail utilisateur préservé et vérification réelle.

Le pilote totalise quatre runs, 22 requêtes Qwen et zéro retry comportemental.
Le kernel n'a produit aucun delta de réussite sur ces tâches ; son agrégat compte
2,61 % de tokens totaux en plus et 7,54 % de latence en moins. Une seule
observation par cellule et deux tâches simples ne permettent aucune généralisation
statistique. Ce résultat valide l'infrastructure de mesure, pas l'efficacité
générale, et ne promeut ni ne rejette le kernel.

## Challenge comportemental décisif

Le [challenge v1](behavioral/challenge-v1/results.md) a pré-enregistré six
fixtures ciblant les mécanismes exacts du candidat, puis consommé douze cellules
contrebalancées. Onze observations sont disponibles ; `reuse-baseline` a été
perdue après scoring lors d'un refus Windows de nettoyage, consommée et jamais
rejouée.

Sur les cinq paires complètes, le kernel obtient zéro win et la baseline deux.
La baseline vérifie proportionnellement là où le kernel ajoute une suite complète,
et elle complète la modification transversale sans toucher le test visible là où
le kernel le modifie puis déclare la réussite. Ce dernier baseline win fonctionnel
satisfait à lui seul le seuil pré-enregistré : **`REJECTED_AS_BALANCED`**.

L'overhead six-paires est indisponible. Sur les cinq paires complètes, le kernel
utilise descriptivement 19,166 % de tokens et 11,388 % de latence en plus. Un
faux positif du grader sur un import de package local est corrigé et testé, sans
changer la décision. Aucune nouvelle réplication du même kernel équilibré n'est
proposée et aucun fichier racine n'est modifié.

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

- Le premier pilote comportemental était nul, puis le challenge décisif a rejeté
  la forme équilibrée sur deux baseline wins observés. Une cellule baseline est
  indisponible après un incident de nettoyage post-scoring, mais la régression
  fonctionnelle transversale suffit au seuil de rejet.
- Aucun contexte système complet réellement injecté par un harness n'a été
  capturé ; la validation Codex repose sur des canaris fermés.
- L'initialisation OpenCode, le transport mock, la découverte racine unique du
  kernel et le transport provider réel vers le 27B sont validés. La sortie Qwen
  sans thinking n'est pas exacte : **FAIL** d'adhérence formelle, sans invalider
  le **PASS** de transport. L'efficacité comportementale du kernel équilibré est
  désormais classée **REJECTED_AS_BALANCED** dans le harness/model testé.
- Le runtime Ollama/Qwen est validé séparément à 16 384 tokens, mais la marge
  VRAM observée est faible pour le 35B comme pour le 27B ; même la réserve 27B
  de 4 Gio n'a laissé que 3 683 MiB libres lors d'une campagne antérieure. La
  mission de résolution a ensuite maintenu entre 3 588 et 3 648 MiB pendant les
  appels et validé le transport OpenAI-compatible, sans généraliser cette marge.
- Le générateur statique existe seulement comme outil expérimental ; aucun
  adaptateur n'est actif dans ce repository.
- Aucun hook, skill, mémoire ou runtime additionnel n'existe ici.
- Les règles peuvent être sous-spécifiées pour une mission risquée ou trop
  présentes pour une tâche triviale.
- Qwen n'est pas un harness ; son comportement dépendra du runtime, du modèle
  précis, de la quantification et du template testés.

## Statut après décision

La forme équilibrée ne poursuit plus le chemin de promotion et ne doit pas être
répliquée. Une éventuelle suite exige une décision séparée sur un candidat micro
substantiellement distinct ; elle ne réactive pas ce candidat et ne transforme
pas ses preuves de transport en preuve comportementale.

## Fichiers racine volontairement inchangés

`AGENTS.md` et `CLAUDE.md` restent inchangés. Aucun `opencode.json`, fichier
d'instruction racine ou réglage utilisateur/global n'est créé. Les tests utilisent
uniquement des répertoires temporaires extérieurs au repository. Le candidat ne
peut donc pas être confondu avec le comportement actif du workspace.
