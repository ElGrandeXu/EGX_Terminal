# Validation runtime Codex CLI 0.144.6

## Statut, date et périmètre

- **Date :** 2026-07-20
- **Environnement :** Windows, PowerShell, Python 3.11.9
- **Harness :** `codex-cli 0.144.6` exactement
- **Statut du kernel :** expérimental, inactif et non promu
- **Résultat :** six cas `PASS`, six appels réussis sur six tentatives, aucun retry

Cette expérience valide seulement la découverte et la précédence des instructions
projet par Codex CLI 0.144.6 dans des repositories Git jetables. Elle observe
aussi le chargement du `AGENTS.md` produit octet pour octet par l'adaptateur
statique. Elle n'évalue ni l'obéissance générale au kernel, ni la qualité du code,
ni les économies nettes de tokens, ni un autre harness ou modèle.

## Prévol et protocole

Le prévol a confirmé la branche `main`, un worktree propre, le commit
`0b29504b1116435ecbd5a447fe40d93c1234e45d` et son sujet
`feat: prototype deterministic doctrine adapters`. `python --version` a retourné
`Python 3.11.9`; `codex --version` a retourné `codex-cli 0.144.6`.

L'aide locale de `codex exec` expose officiellement `--ephemeral`,
`--sandbox read-only`, `--cd`, `--json` et `--output-schema`. Le probe utilise
`--json` pour obtenir des événements JSONL structurés, ainsi que la commande
normalisée suivante :

```text
codex exec --ephemeral --ignore-user-config --ignore-rules --sandbox read-only --cd <fixture-cwd> --json --color never <closed-prompt>
```

[`probe_codex.py`](../tools/probe_codex.py) vérifie le kernel et son manifeste
avant chaque appel. Il réutilise `sync_adapters.py write` pour les deux fixtures
kernel et `sync_adapters.py check` après chacun de ces appels. Chaque cas reçoit
son propre `TemporaryDirectory`, initialisé comme repository Git après création
de la fixture. Un snapshot de contenu est comparé avant et après l'appel.

Le parseur ne conserve que la sortie finale normalisée, la présence d'un outil,
le code de sortie, les métriques et le verdict. Les événements bruts restent en
mémoire le temps du parsing puis sont abandonnés. Aucun transcript, prompt
système, raisonnement ou canari brut n'est écrit dans le repository.

### Plafond appliqué

- maximum six appels Codex réussis ;
- maximum sept tentatives totales ;
- au plus un retry, uniquement sur exception locale d'infrastructure ;
- arrêt sur baseline invalide, outil ou approbation, mutation, ou blocage runtime.

Observation : la campagne a utilisé **six tentatives**, obtenu **six appels
réussis** et utilisé **zéro retry**. Une première invocation locale du probe
s'était arrêtée avant tout processus Codex et avant tout appel modèle, car Python
ne résolvait pas le lanceur Windows sous son nom nu. La résolution a été corrigée
avec `shutil.which`, puis couverte par test. Cette invocation pré-Codex ne compte
donc ni comme appel ni comme tentative modèle.

## Résultats des six cas

Les canaris uniques ont été générés en mémoire. Le tableau emploie des libellés
neutres à leur place. Pour la baseline, le contenu exact a été volontairement
écarté après avoir établi qu'il était non vide et différent du préfixe kernel ;
cela évite de persister une éventuelle instruction utilisateur globale.

| Cas | Objectif et fixture | Sortie attendue | Sortie observée conservée | Code | Outil | Workspace | Verdict |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| 0 — baseline | Repository Git vide, sans `AGENTS.md`, `CLAUDE.md` ni doctrine | réponse concise autre que le préfixe kernel | réponse non vide, différente du préfixe, contenu écarté | 0 | non | inchangé | **PASS** |
| 1 — racine | Un `AGENTS.md` racine avec canari unique | `<ROOT_DISCOVERY_CANARY>` | `<ROOT_DISCOVERY_CANARY>` | 0 | non | inchangé | **PASS** |
| 2 — kernel A | Workspace produit par `sync_adapters.py write` | `Understand the requested outcome, constraints, relevant work, and` | `Understand the requested outcome, constraints, relevant work, and` | 0 | non | inchangé; check statique OK | **PASS** |
| 3 — kernel B | Nouvelle fixture indépendante produite par le générateur | `Understand the requested outcome, constraints, relevant work, and` | `Understand the requested outcome, constraints, relevant work, and` | 0 | non | inchangé; check statique OK | **PASS** |
| 4 — scope imbriqué | `AGENTS.md` racine et `child/AGENTS.md`, lancement depuis `child` | `<CHILD_CANARY>` | `<CHILD_CANARY>` | 0 | non | inchangé | **PASS** |
| 5 — override | `AGENTS.md` et `AGENTS.override.md` au même niveau | `<OVERRIDE_CANARY>` | `<OVERRIDE_CANARY>` | 0 | non | inchangé | **PASS** |

Une sortie approchante n'aurait pas été acceptée. Les cinq attentes exactes ont
été comparées par égalité stricte ; la baseline a seulement le critère négatif
préenregistré décrit ci-dessus.

## Comptabilité des tokens

Les événements `turn.completed` ont exposé `input_tokens`,
`cached_input_tokens` et `output_tokens` pour les six appels. Le total rapporté
par le probe vaut `input_tokens + output_tokens`; les tokens cachés sont une
sous-catégorie de l'entrée et ne sont pas additionnés une seconde fois.

| Cas | Input | Cached input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| 0 — baseline | 12 076 | 8 960 | 95 | 12 171 |
| 1 — racine | 12 146 | 8 960 | 25 | 12 171 |
| 2 — kernel A | 12 295 | 8 960 | 68 | 12 363 |
| 3 — kernel B | 12 289 | 8 960 | 69 | 12 358 |
| 4 — scope imbriqué | 12 192 | 8 960 | 26 | 12 218 |
| 5 — override | 12 150 | 8 960 | 26 | 12 176 |
| **Campagne** | **73 148** | **53 760** | **309** | **73 457** |

Ces mesures décrivent le contexte complet traité par les appels. Elles
n'isolent pas le coût causal du kernel et ne démontrent aucune économie nette.

## Nettoyage et non-modification

- Les six résultats portent `fixture_cleaned: true`.
- Les snapshots avant/après sont égaux pour les six workspaces jetables.
- Les checks statiques post-appel des cas 2 et 3 ont réussi.
- Le snapshot d'EGX_Terminal avant/après la campagne runtime est identique.
- `--ephemeral` et `--sandbox read-only` sont présents dans chaque invocation.
- Aucun événement de tool call ou d'approbation n'a été observé.

Le flag éphémère est confirmé au niveau de l'interface officielle et de chaque
commande. Par règle de confidentialité, l'expérience n'a pas inspecté les
répertoires globaux de sessions pour tenter une seconde preuve. L'absence de
tool call signifie également que cette campagne n'a pas provoqué une tentative
d'écriture afin de tester activement l'enforcement de la sandbox.

## Faits, inférences et inconnues

### Faits expérimentaux

- La baseline jetable ne contenait aucun fichier d'instruction projet et n'a pas
  reproduit les huit premiers mots du kernel.
- Un `AGENTS.md` racine a transmis son canari exact.
- Deux processus indépendants ont retourné exactement les huit premiers mots du
  `AGENTS.md` réellement généré.
- Depuis un sous-répertoire, le canari du fichier le plus proche a gagné sur le
  canari racine.
- Au même niveau, le canari de `AGENTS.override.md` a gagné sur celui
  d'`AGENTS.md`.
- Aucun outil n'a été observé et aucun contenu de fixture n'a changé.

### Inférences limitées

- Pour Codex CLI 0.144.6 dans ce protocole, la copie générée dans `AGENTS.md` est
  un adaptateur de découverte fonctionnel.
- Les résultats des cas 4 et 5 sont cohérents avec la précédence documentée du
  scope le plus proche et de l'override.
- La répétition du cas kernel réduit le risque d'un résultat isolé, sans établir
  une probabilité générale de succès.

### Inconnues maintenues

- Une éventuelle instruction globale utilisateur reste un facteur externe non
  inspecté. `--ignore-user-config` désactive la configuration utilisateur, mais
  l'expérience ne lit aucun fichier global d'instructions.
- Le modèle exact choisi par le client n'a pas été fixé avec `--model` et n'est
  pas exposé dans la synthèse JSONL utilisée ; les conclusions portent sur le
  harness et sa configuration d'invocation, pas sur un modèle nommé.
- Le contexte système complet, le nombre d'occurrences internes du payload, les
  limites de taille, la compaction et la reprise ne sont pas observés.
- L'enforcement actif de la sandbox face à une écriture n'est pas testé, puisque
  tout tool call invalidait le cas.

## Limites méthodologiques

Les réponses sont des canaris comportementaux minuscules. Elles constituent une
preuve expérimentale de transmission et de précédence dans ces cas, pas une
capture du contexte injecté. La baseline fournit un contrôle négatif du préfixe
kernel, pas une preuve d'absence de toute instruction externe. Deux répétitions
kernel ne mesurent ni taux d'adhérence ni stabilité statistique. Les tokens du
contexte complet ne permettent pas d'attribuer un coût net au seul payload.

Cette expérience ne démontre pas :

- l'obéissance générale au kernel ou son effet sur la qualité du code ;
- un gain de sécurité, de latence ou de tokens ;
- la portabilité vers Claude Code, OpenCode ou Qwen ;
- le comportement d'une autre version de Codex CLI ;
- la promotion ou l'activation du candidat.

## Conclusion et décision recommandée

Pour **Codex CLI 0.144.6 uniquement**, conserver la stratégie **fallback C** :
une copie déterministe octet pour octet du canon dans `AGENTS.md`, vérifiée par
hash et lockfile. Cette stratégie a franchi le contrôle runtime de découverte,
de scope et de précédence prévu ici. Elle ne doit pas encore être activée à la
racine ni présentée comme doctrine stable.

Avant promotion, il reste au minimum à :

1. valider séparément les adaptateurs Claude Code et OpenCode sur versions fixes ;
2. vérifier unicité, limites de taille et conflits avec les surfaces globales ;
3. exécuter la campagne comportementale avec baselines et seuils préenregistrés ;
4. mesurer coûts du payload, wrappers et contexte complet sans confondre tokens
   et valeur ;
5. prendre une décision explicite de promotion et préparer la migration du
   bootstrap racine.

La prochaine expérience recommandée est une mission autonome de découverte
runtime de l'adaptateur Claude Code sur une version fixée, uniquement si elle
offre des garanties officielles équivalentes de session jetable et de sandbox
read-only. Elle ne doit pas être commencée dans cette mission.
