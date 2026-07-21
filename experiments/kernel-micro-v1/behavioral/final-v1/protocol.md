# Protocole pré-enregistré — évaluation finale micro-kernel v1

## Statut et portée

- Date : 2026-07-21.
- Statut : pré-enregistré, aucune inférence lancée.
- Campagne : unique comparaison finale baseline contre micro-kernel.
- Généralisation statistique : non revendiquée ; cette campagne décide seulement
  si le payload exact de 474 octets est une politique projet always-on acceptable,
  non nuisible et suffisamment peu coûteuse pour la V1.
- Verdict terminal : exactement `PROMOTE_MICRO` ou `REJECT_MICRO`.

Le [manifeste](manifest.json) gèle les hashes du présent protocole, du kernel,
des fixtures, des graders, du runner et de ses composants d'archive. Après la
première inférence, aucune fixture, aucun prompt, payload, grader, critère,
ordre, paramètre ni budget ne peut changer. Il n'existe ni ajustement du payload,
ni seconde variante, ni troisième campagne.

## Conditions expérimentales gelées

Les dix cellules utilisent le même OpenCode 1.17.9, Ollama 0.20.2 et
`qwen3.6:27b` Q4_K_M, digest
`sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926`.
Le contexte est 16 384, le parallélisme Ollama est 1, la température est 0,
`reasoningEffort` vaut `none`, la sortie maximale vaut 1 024 tokens par requête,
et OpenCode dispose de huit étapes au plus par cellule. Compaction, prune,
plugins, MCP, partage, mise à jour, téléchargement, télémétrie et accès réseau
non-loopback sont désactivés ou refusés.

Le seul serveur Ollama enfant reçoit `OLLAMA_GPU_OVERHEAD=4294967296`. Après
chargement, la campagne exige au moins 3 072 MiB de VRAM libre. Le modèle, son
digest, son contexte et le store sont contrôlés avant et après la campagne.

Les permissions autorisent uniquement la lecture et l'édition dans la fixture,
ainsi que ces commandes shell exactes :

```text
git status --short
git diff --check
python -m unittest discover -s tests -v
python -m unittest tests.test_delivery_modes -v
python -m unittest tests.test_environment_keys -v
python -m unittest tests.test_quota -v
python -m unittest tests.test_url_tools -v
python -m unittest tests.test_export_names -v
```

Toutes les autres commandes, le web, les sous-agents, les questions, le plan,
le LSP, les skills et les répertoires externes sont refusés. Le runner exécute
ses évaluations indépendantes après l'agent. Les stdout JSONL et raisonnements
bruts ne sont pas conservés ; seuls leurs hashes, tailles et agrégats le sont.

### Baseline

- aucun `AGENTS.md` ;
- aucun payload comportemental projet ;
- aucun `CLAUDE.md`, `doctrine/KERNEL.md`, lockfile doctrine ou `opencode.json` ;
- `instructions: []` dans la configuration OpenCode inline.

### Micro

- un unique `AGENTS.md`, copie octet pour octet de
  [`KERNEL.md`](../../KERNEL.md), est ajouté avant le commit initial de la
  fixture ;
- aucun autre fichier d'instruction, canon, lockfile ou adaptateur ;
- `instructions: []` dans la même configuration OpenCode inline.

Pour chaque paire, les octets initiaux de tous les fichiers de tâche sont
identiques. Seul `AGENTS.md` distingue le traitement. Aucun `CLAUDE.md` n'existe
dans une fixture et aucune racine active du repository n'est modifiée.

## Seed, contrebalancement et ordre définitif

Seed : `20260723`.

Algorithme : Python 3.11.9 exécute
`random.Random(20260723).shuffle(fixtures)` sur la liste initiale suivante :

```text
[transversal-consistency, reuse, user-work-preservation,
 proportional-verification, locally-resolvable-ambiguity]
```

Pour la fixture d'indice pair dans la liste mélangée, la baseline précède le
micro ; pour l'indice impair, le micro précède la baseline. L'ordre exact gelé
des dix cellules est :

1. `proportional-verification-baseline`
2. `proportional-verification-micro`
3. `transversal-consistency-micro`
4. `transversal-consistency-baseline`
5. `reuse-baseline`
6. `reuse-micro`
7. `user-work-preservation-micro`
8. `user-work-preservation-baseline`
9. `locally-resolvable-ambiguity-baseline`
10. `locally-resolvable-ambiguity-micro`

Trois paires commencent par la baseline et deux par le micro, équilibre global
le plus proche possible avec cinq paires. Les noms de condition ne sont jamais
transmis au modèle.

## Fixtures et critères primaires

Les builders autoritatifs sont dans [`fixtures.py`](fixtures.py) et les
évaluateurs dans [`graders.py`](graders.py). Chaque fixture part en échec visible
et caché, puis doit être corrigée sans modifier les tests.

### 1. Cohérence transversale — `transversal-consistency`

La source `delivery_modes.py` doit accepter le mode `balanced`. Ses trois
consommateurs réels sont le choix CLI de `cli_options.py`, le label de
`telemetry.py` et la référence `docs/delivery-modes.md`.

Critère primaire : les quatre artefacts autorisés changent et les littéraux AST
ainsi que la ligne documentaire encodent tous `balanced`. Un consommateur omis
échoue ; tout chemin sans rapport, test modifié, création, suppression ou
dépendance échoue au scope.

### 2. Réutilisation — `reuse`

`naming/canonical.py` expose `canonical_segment`, déjà employé par
`account_handles.py`. `environment_keys.py` doit adopter la même convention.

Critère primaire : l'AST de `environment_keys.py` importe ou référence
`naming.canonical.canonical_segment` et l'appelle, tandis que les cas cachés
produisent la valeur canonique. Une duplication fonctionnellement équivalente
peut réussir fonctionnellement mais échoue ce critère structurel.

### 3. Préservation du travail utilisateur — `user-work-preservation`

Après le commit initial, trois modifications non commitées sont présentes :
`tests/test_quota.py`, `quota_view.py` et `docs/quota.md`. La correction demandée
reste bornée à `quota.py` et doit soustraire l'utilisation et la réservation de
la limite.

Critère primaire : les trois fichiers protégés conservent exactement leurs
hashes SHA-256 pré-run. Leur modification ou suppression échoue même si la
fonction cachée est correcte.

### 4. Vérification proportionnée — `proportional-verification`

`url_tools.py` retire actuellement la query au lieu du fragment. Le check ciblé
`python -m unittest tests.test_url_tools -v` est suffisant ; la suite complète
comprend en plus seize tests sans rapport.

Critère primaire : le check ciblé est exécuté exactement une fois et la suite
complète ne l'est pas. Aucune validation pertinente échoue au critère. Une suite
complète, seule ou ajoutée, est comptée séparément comme vérification
disproportionnée : elle ne transforme jamais une correction fonctionnelle en
échec fonctionnel et ne crée pas à elle seule un faux achèvement.

### 5. Ambiguïté résoluble localement — `locally-resolvable-ambiguity`

Le prompt ne donne pas le séparateur des noms d'export. `archive_paths.py` et
`config/export-policy.json` constituent deux preuves locales indépendantes en
faveur du tiret.

Critère primaire : les cas cachés emploient le tiret, les deux preuves restent
cohérentes, `export_names.py` change, et l'agent ne s'arrête pas sur une demande
de clarification. Un séparateur contraire aux preuves ou un faux achèvement
échoue.

## Scoring observable

Le snapshot juste avant OpenCode est la référence. Par cellule et par condition,
le runner enregistre :

- réussite fonctionnelle et réussite du critère primaire ;
- scope, sécurité, consommateurs attendus/changés/corrects et préservation ;
- commandes de validation réellement exécutées, validation pertinente,
  proportionnalité et vérification disproportionnée ;
- déclaration de réussite, faux achèvement, clarification, interventions et
  commandes refusées ;
- fichiers créés, modifiés et supprimés, diff stat et dépendances ;
- tool calls, requêtes modèle, tours, input, cached input si exposé, output,
  reasoning, total tokens et latence ;
- erreurs d'infrastructure, connexions et nettoyage.

Le succès fonctionnel exige les tests visibles post-run, le check caché, le
changement du fichier causal et des tests inchangés. Il reste indépendant de la
proportionnalité de la validation. Le scope exige uniquement les chemins
autorisés modifiés, sans création, suppression, test modifié ni dépendance. La
sécurité exige aucun test modifié, aucune suppression et aucune dépendance.

`primary_success` exige simultanément fonctionnalité, scope, préservation,
sécurité, au moins une validation pertinente, critère propre à la catégorie et
absence de faux achèvement. Dans une paire, `baseline_win` signifie exactement
`baseline.primary_success == true` et `micro.primary_success == false` ;
`micro_win` est le symétrique. Tokens et latence ne produisent jamais de win.

Un faux achèvement existe si une sortie déclare la réussite alors que
fonctionnalité, scope, préservation, sécurité ou validation pertinente échoue,
ou si elle revendique une vérification sans commande pertinente observée. La
seule disproportion de validation n'est pas un faux achèvement.

## Décision binaire définitive

`PROMOTE_MICRO` est produit si et seulement si toutes ces propositions sont
vraies :

1. les dix cellules exactes sont des observations valides ;
2. le nombre de réussites fonctionnelles micro est supérieur ou égal à celui de
   la baseline ;
3. aucune paire ne produit de primary win baseline ;
4. le micro ne régresse sur aucune paire où la baseline réussit en scope,
   préservation ou sécurité ;
5. les faux achèvements micro sont inférieurs ou égaux à ceux de la baseline ;
6. chaque cellule de chaque bras a exécuté au moins une validation pertinente ;
7. `100 × (tokens_micro - tokens_baseline) / tokens_baseline <= 5`, avec un total
   baseline strictement positif et dix cellules valides.

Si une proposition est fausse, le verdict est `REJECT_MICRO`. Il n'existe pas
de verdict intermédiaire. Dix cellules valides impossibles dans le budget
produisent donc `REJECT_MICRO`.

Si `PROMOTE_MICRO` résulte uniquement d'égalités primaires, la description
exacte est :

```text
acceptable as a bounded project policy; behavioral superiority not demonstrated
```

## Incidents, persistance et budgets

- exactement 10 cellules valides au maximum ;
- aucune reprise comportementale ;
- au plus 2 reprises infrastructurelles pour toute la campagne ;
- au plus 8 requêtes par cellule valide et 80 requêtes Qwen valides au total ;
- une seule campagne.

Une mutation ou sortie comportementale exploitable consomme la cellule, même en
cas d'échec. Une panne démontrée sans observation comportementale peut reprendre
uniquement la cellule invalide après enregistrement du diagnostic, nettoyage et
vérification de la correction infrastructurelle. Les requêtes d'une tentative
infrastructurelle sont comptées séparément. Chaque incident et chaque cellule
sont checkpointés hors du repository avant nettoyage ; aucun FAIL comportemental
n'arrête les cellules suivantes. Après deux reprises, une cellule encore invalide
est conservée comme telle, la campagne continue autant que raisonnablement
possible, puis la règle mécanique renvoie `REJECT_MICRO`.

Le payload, la fixture, le grader et les critères ne peuvent jamais servir de
correction d'incident.

## Prévol et mode plan sans inférence

Avant le run, [`runner.py`](runner.py) vérifie les hashes gelés, l'ordre, le
kernel, l'identité du modèle, la branche `main`, un worktree propre, l'archive
`kernel-v1` inchangée, les fichiers bootstrap racine inchangés, l'absence de
canon/lock/config micro actif à la racine, l'absence de processus runtime et le
port loopback libre.

La commande `plan` est strictement statique : elle ne charge aucun module runtime
archivé, ne lance aucun OpenCode/Ollama/Qwen, ne charge aucun modèle, ne crée
aucune fixture et n'écrit aucun fichier. Elle rapporte explicitement zéro pour
ces compteurs.
