# Synthèse de compatibilité runtime du kernel v1

## Statut et portée

- **Date de résolution :** 2026-07-21
- **Compatibilité générale :** **SUPPORTED — EXPERIMENTAL**
- **Statut global :** **non bloqué pour poursuivre**
- **Promotion du kernel :** aucune ; le candidat reste expérimental, inactif et
  en quarantaine
- **Prochaine phase :** évaluation comportementale sur de vraies tâches

Cette synthèse clôt la validation de portabilité runtime. Elle n'annule ni ne
réécrit les verdicts historiques de chaque campagne : elle sépare les niveaux de
preuve afin d'interpréter leur résultat final sans confondre transport, format et
efficacité.

## Matrice des quatre niveaux de preuve

| Niveau | Question mesurée | Résultat | Preuve décisive | Ce que le résultat ne prouve pas |
| --- | --- | --- | --- | --- |
| 1. Distribution statique | Le canon, les adaptateurs, les hashes et la synchronisation sont-ils cohérents ? | **PASS** | Le [prototype statique](static-distribution.md) matérialise et vérifie déterministement le canon, `AGENTS.md`, `CLAUDE.md` et le lockfile dans des cibles jetables. | Découverte par un harness, injection, obéissance ou qualité. |
| 2. Transport runtime | Le fichier est-il découvert et injecté, puis la requête atteint-elle le provider et le modèle attendus ? | **PASS** | Codex découvre la copie générée ; le mock OpenCode observe le kernel exact une fois ; le chemin réel OpenCode 1.17.9 → Ollama 0.20.2 → `qwen3.6:27b` émet une requête unique au modèle exact, à 16 384 tokens de contexte. | Respect exact du format demandé ou effet sur une mission utile. |
| 3. Adhérence formelle | Le modèle respecte-t-il exactement la ponctuation et la limite de huit mots du canari ? | **FAIL** pour `qwen3.6:27b` | La réponse reprend les mots attendus dans le bon ordre, mais omet la ponctuation et ajoute des mots au-delà de la limite. | Incompatibilité du transport ou mauvaise qualité générale. |
| 4. Efficacité comportementale | Le kernel améliore-t-il réellement correction, périmètre, vérification et communication sur des tâches représentatives ? | **NOT TESTED** | Aucune campagne comportementale n'a été exécutée. | Promotion, bénéfice causal ou compatibilité générale de toute version et de tout modèle. |

Les statuts portent sur des périmètres différents. Le `FAIL` du niveau 3 ne
rétrograde donc pas le `PASS` du niveau 2, et le `PASS` de transport ne permet pas
d'anticiper le niveau 4.

## Résultats par cellule

### Codex CLI 0.144.6

La distribution et la découverte sont **PASS**. Les six fixtures du
[rapport Codex](codex-runtime-0.144.6.md) ont réussi sans retry, outil ni
mutation. Deux fixtures indépendantes construites par l'adaptateur ont rendu le
canari kernel exact ; les cas racine, scope imbriqué et override ont également
produit leur sortie attendue. Cette cellule valide la stratégie de copie et la
découverte pour Codex CLI 0.144.6, pas l'efficacité générale du kernel.

### OpenCode 1.17.9 avec provider mock

La distribution et la découverte mock sont **PASS**. Le
[diagnostic OpenCode](opencode-preflight-diagnostic-1.17.9.md) a observé une seule
requête loopback, le modèle mock exact, une occurrence exacte du kernel, zéro
outil et la sortie finale `MOCK_OK`. Cette cellule prouve l'initialisation,
l'injection inspectable et l'unicité dans ce protocole ; elle n'exécute pas Qwen.

### Ollama direct

Le [smoke Ollama direct](ollama-qwen3.6-35b-smoke.md) est **PASS** pour le couple
isolé Ollama 0.20.2 + `qwen3.6:35b`. Le modèle a été chargé à un contexte effectif
de 16 384 tokens et l'unique inférence a rendu `QWEN_LOCAL_OK` exactement. Cette
preuve établit l'aptitude du runtime local dans cette cellule, sans valider
OpenCode, l'injection du kernel ou un usage agentique prolongé.

### OpenCode 1.17.9 + Ollama 0.20.2 + Qwen 3.6 27B

Le transport runtime est **PASS**. Après les correctifs d'intégration documentés
dans le [rapport de résolution](opencode-qwen3.6-27b-resolution.md), OpenCode a
utilisé le provider `local-ollama`, atteint réellement `qwen3.6:27b` Q4_K_M et
quitté avec le code 0. La tentative décisive a envoyé exactement une requête,
avec un contexte de 16 384 tokens, sans reasoning, outil ni connexion
non-loopback.

L'adhérence formelle au canari est **FAIL** : la réponse conserve les mots du
kernel dans le bon ordre, mais ne respecte ni leur ponctuation exacte ni la
limite de huit mots. Il s'agit d'un échec de contrôle de sortie, pas d'un blocage
d'intégration OpenCode, Ollama ou Qwen.

## Faits établis

- le canon, les copies d'adaptateur, les hashes et le lockfile sont
  déterministes et synchronisés dans les cibles jetables ;
- Codex CLI 0.144.6 découvre la copie `AGENTS.md` générée dans les cas mesurés ;
- OpenCode 1.17.9 injecte le kernel exact une fois dans le payload mock observé ;
- OpenCode atteint Ollama par le provider OpenAI-compatible configuré ;
- Ollama sert effectivement `qwen3.6:27b` Q4_K_M à 16 384 tokens de contexte ;
- la tentative réelle décisive envoie une seule requête et OpenCode quitte avec
  le code 0 ;
- `reasoning_effort:none` est transmis et la dernière réponse expose zéro token
  de reasoning ;
- la réponse Qwen reprend les huit mots attendus dans le bon ordre avant de
  continuer ;
- aucun outil, provider distant ni réseau non-loopback n'a été utilisé ;
- les workspaces, processus, modèle chargé, port et racines temporaires ont été
  nettoyés selon les rapports de campagne.

## Pourquoi le canari exact n'est pas un proxy de qualité générale

Le canari reste utile pour détecter découverte, précédence, troncature grossière
et contrôle de sortie. Son égalité stricte mesure toutefois une propriété très
étroite : reproduire une courte chaîne avec sa ponctuation et s'arrêter au
huitième mot.

Il ne mesure ni correction d'un patch, ni diagnostic causal, ni conservation
d'un worktree sale, ni choix d'outils, ni vérification réelle. Il est aussi
sensible au template, au tokenizer, au budget de sortie et aux contrôles du
provider. Une omission de virgules accompagnée des mots corrects dans le bon
ordre peut donc faire échouer légitimement le test formel sans indiquer que le
kernel est absent ou inutile. Inversement, recopier parfaitement huit mots ne
démontre aucun bénéfice sur une mission. Le canari doit rester un contrôle borné,
pas devenir un score de qualité générale.

## Coûts de contexte exploratoires

| Cellule | Entrée observée | Interprétation |
| --- | ---: | --- |
| Codex CLI 0.144.6 | moyenne de **12 191 tokens d'entrée par probe** | 73 148 tokens d'entrée sur six probes, moyenne arrondie à l'unité |
| OpenCode + Qwen 27B | environ **2 214 tokens d'entrée** | 2 212 puis 2 214 tokens sur les deux réponses réelles |

Ces protocoles ne sont pas directement comparables. Ils diffèrent par harness,
modèle, tokenizer, template, contexte système, cache exposé et instrumentation.
Ces valeurs décrivent le contexte complet observé ; elles n'isolent pas le coût
causal du kernel et ne permettent pas de conclure à une efficacité supérieure.

## Performances Qwen observées

Les deux réponses OpenCode + Qwen ont produit un débit fin-à-fin compris entre
**2,422 et 6,050 tokens/s**. La première a consommé 64 tokens sans texte visible
avant la correction du contrôle de thinking ; la seconde a rendu 14 tokens
visibles. Deux réponses courtes, de nature différente, sont insuffisantes pour
juger la latence, la stabilité ou le rendement d'un usage de coding prolongé.

## Limitations

- Les conclusions sont bornées aux versions, modèles, quantifications,
  paramètres, machine et fixtures consignés dans les rapports.
- L'occurrence exacte du kernel a été inspectée sur le mock OpenCode, pas dans le
  payload brut de la requête Qwen réelle.
- Codex n'a pas exposé son modèle exact ni son contexte système complet dans la
  synthèse utilisée.
- Le smoke Ollama direct porte sur le 35B, tandis que la cellule OpenCode réelle
  porte sur le 27B.
- Les canaris fournissent peu de puissance statistique et aucune mesure de
  qualité agentique.
- La marge VRAM et la politique d'offload observées sont propres à l'hôte.
- Claude Code et les autres versions de harnesses ou de modèles ne sont pas
  validés par ces résultats.

## Verdict final

La portabilité runtime est **validée expérimentalement** pour les cellules
mesurées. OpenCode + Qwen n'est plus `BLOCKED` : son transport est **PASS**, son
adhérence exacte au canari est **FAIL**, et son efficacité comportementale est
**NOT TESTED**. La compatibilité générale est donc **SUPPORTED — EXPERIMENTAL**
et le projet est **non bloqué pour poursuivre**.

Ce verdict n'active ni ne promeut le kernel. La prochaine mission proposée,
sans l'exécuter ici, est un pilote comportemental pré-enregistré comparant la
baseline et le kernel dans des fixtures de tâches réelles : correction triviale,
bug avec reproduction, worktree sale et tâche documentaire. Elle doit mesurer
réussite, changements hors scope, vérification réelle, faux achèvement, tokens
et latence selon le
[plan de validation existant](../../../docs/research/synthesis/validation-plan.md).
