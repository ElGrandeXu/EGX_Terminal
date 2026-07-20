# Contrat des adaptateurs du kernel v1

## Statut et portée

Ce document décrit le contrat sémantique des adaptateurs **expérimentaux**. Le
prototype de génération statique l'implémente uniquement dans une cible jetable ;
il ne charge pas le candidat et ne change pas les fichiers racine. Les sources
officielles ont été consultées le **2026-07-20**.

Les étiquettes de preuve sont :

- **Documenté :** affirmation explicite de la documentation officielle citée ;
- **Inféré :** choix d'architecture dérivé des faits documentés ;
- **À tester :** comportement non établi par la documentation seule.

## Source neutre et identité sémantique

Dans le repository, la seule source du candidat reste [`KERNEL.md`](KERNEL.md).
Elle n'est pas un point d'entrée stable. Le prototype la copie octet pour octet
vers `doctrine/KERNEL.md` dans une cible jetable seulement. Après une éventuelle
promotion, ce chemin reste le canon stable recommandé ; aucune promotion ni
création de ce chemin à la racine réelle n'a lieu ici.

Un adaptateur distribue exactement un payload identifié par version et SHA-256.
Il ne devient jamais la source sémantique. Un wrapper, une métadonnée ou une
syntaxe d'include est comptabilisé séparément du payload always-on.

## Matérialisation statique expérimentale

[`tools/sync_adapters.py`](tools/sync_adapters.py) expose trois opérations :

- `plan` calcule les créations et modifications sans écrire ;
- `write` matérialise les quatre sorties attendues dans une cible explicite ;
- `check` vérifie sans écrire la source, le canon, les adaptateurs et le lockfile.

`AGENTS.md` est la copie exacte commune à Codex et OpenCode. Aucun
`opencode.json` n'est créé, afin de ne pas combiner cette copie avec une seconde
surface `instructions`. `CLAUDE.md` contient exactement
`@doctrine/KERNEL.md`, sans fin de ligne finale. Le kernel, sa copie et l'import
sont en UTF-8 sans BOM, LF, sans fin de ligne finale. Le JSON est trié, indenté
sur deux espaces et terminé par LF.

Le lockfile `.egx/doctrine-lock.json` revendique exhaustivement les trois fichiers
de contenu gérés et leurs hashes. Il s'identifie séparément comme artefact de
contrôle : un hash de ses propres octets serait récursif. Son intégrité est donc
vérifiée par régénération déterministe exacte. Il ne contient ni timestamp, ni
chemin absolu, ni donnée de machine.

## Responsabilités autorisées

Un adaptateur peut uniquement :

- occuper un chemin officiellement découvert par son harness ;
- inclure la source neutre par un mécanisme officiellement documenté et fiable ;
- à défaut, matérialiser une copie déterministe octet pour octet ;
- ajouter le minimum de syntaxe indispensable au chargement ;
- déclarer harness, versions testées, scope, précédence et source/hash attendus ;
- exposer un contrôle de synchronisation lisible et un moyen de désactivation ;
- échouer visiblement pendant génération ou vérification si la parité manque.

## Responsabilités interdites

Un adaptateur ne doit pas :

- ajouter, retirer, reformuler ou réordonner la doctrine ;
- masquer une injection, patcher un harness ou modifier un réglage utilisateur ;
- installer une dépendance, exécuter un hook ou amorcer un runtime ;
- charger une mémoire, une persona, une skill ou une capacité optionnelle ;
- prétendre résoudre les conflits par la seule égalité de hash ;
- utiliser un fichier propre à un fournisseur comme source canonique ;
- charger le même payload par plusieurs surfaces sans preuve d'unicité.

## Stratégie de livraison

1. Préférer un include direct seulement lorsque sa résolution, son moment de
   chargement et sa portée sont officiellement documentés.
2. Sinon générer une copie déterministe depuis la source neutre.
3. Vérifier séparément : octets du payload, wrapper, source/hash déclarés, ordre,
   scope, nombre de chargements et contexte effectivement injecté.
4. Un écart doit échouer de façon visible ; aucune réparation silencieuse.
5. L'absence d'adaptateur signifie que la source neutre n'est pas chargée
   automatiquement. Les autres instructions déjà présentes peuvent rester
   actives ; aucune capacité du kernel ne doit alors être revendiquée.
6. Une sortie préexistante n'est écrasable que si un lockfile structurellement
   exact prouve qu'elle appartient à cette génération ; sinon l'écriture échoue
   avant toute mutation.

## Précédence, scope et instructions imbriquées

La précédence syntaxique du harness n'assure pas qu'un modèle résoudra deux
instructions contradictoires de manière déterministe. Chaque adaptateur futur
doit donc inventorier les sources globales, projet, locales et imbriquées,
capturer leur ordre lorsque le harness le permet, puis tester un conflit canari
sans modifier les réglages globaux de l'utilisateur.

Une instruction imbriquée ne doit pas redéfinir le kernel. Elle peut préciser un
contexte local dans une couche adaptée, à condition de ne pas dupliquer le
payload always-on. Un hash prouve l'identité des octets, pas la portée, la
priorité, la troncature ou l'adhérence du modèle.

## Matrice des harnesses

| Harness | Fichiers et recherche automatiques | Include vers une source neutre | Adaptateur futur recommandé | Risques et absence | Statut |
| --- | --- | --- | --- | --- | --- |
| Codex CLI | Global : premier fichier non vide entre `AGENTS.override.md` et `AGENTS.md` dans `CODEX_HOME`. Projet : de la racine vers le répertoire courant, au plus un fichier par niveau, ordre `AGENTS.override.md`, `AGENTS.md`, puis fallbacks configurés. Les fichiers sont concaténés racine d'abord ; le plus proche apparaît plus tard. La recherche s'arrête au répertoire courant. | Aucun include générique n'est documenté pour `AGENTS.md`. Les noms fallback sont de la configuration et ne constituent pas un include repository-owned. | **Fallback C :** copie générée dans l'adaptateur `AGENTS.md`, avec hash visible hors payload. | Global, overrides et fichiers sur le chemin de lancement peuvent contredire le payload ; limite de taille et répertoire de lancement affectent la chaîne. Sans adaptateur reconnu, le canon neutre n'est pas chargé. | Recherche/précédence : **documenté**. Absence d'include et copie : **inféré**. Découverte, scope et override : **validés par canaris sur 0.144.6** ; contexte complet toujours inconnu. |
| Claude Code | Projet : `./CLAUDE.md` ou `./.claude/CLAUDE.md`, plus `CLAUDE.local.md` et `.claude/rules/**/*.md`. Les fichiers au-dessus du répertoire courant chargent au lancement ; ceux des sous-répertoires et les règles path-scoped chargent à la lecture correspondante. Les `CLAUDE.md` découverts sont concaténés du plus général au plus proche. | `@path` est développé au lancement, relatif au fichier importeur, récursif jusqu'à quatre sauts. | **B :** `CLAUDE.md` mince important la future source neutre. | Les conflits concaténés peuvent être suivis arbitrairement ; imports externes soumis au flux d'approbation documenté ; les fichiers imbriqués sont chargés à la demande. Sans `CLAUDE.md` adaptateur, le canon neutre n'est pas chargé. | Recherche/include : **documenté**. Wrapper exact et comportement premier import/compaction : **à tester**. |
| OpenCode | Projet : recherche locale ascendante de `AGENTS.md`, avec `CLAUDE.md` comme fallback ; global : `~/.config/opencode/AGENTS.md`, puis fallback Claude global. Le premier match gagne dans chaque catégorie. | `opencode.json` accepte `instructions` avec chemins/globs et combine ces fichiers avec `AGENTS.md`. Les références textuelles dans `AGENTS.md` ne sont pas développées automatiquement. | **Fallback C partagé :** consommer la copie `AGENTS.md` générée pour Codex. Ne pas ajouter simultanément `instructions` vers le même canon tant que l'unicité n'est pas prouvée. | `AGENTS.md` + `instructions` peut doubler ou contredire la sémantique. Le détail du premier match lors de lancements imbriqués doit être vérifié. Sans fichier découvert/configuré, le canon neutre n'est pas chargé. | Fichiers/config/combinaison : **documenté**. Adaptateur partagé : **inféré**. Parcours imbriqué et double chargement : **à tester**. |

### Sources officielles

- Codex : <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Codex, configuration de découverte :
  <https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery>
- Claude Code : <https://code.claude.com/docs/en/memory>
- OpenCode : <https://opencode.ai/docs/rules/>

Le [rapport runtime Codex CLI 0.144.6](validation/codex-runtime-0.144.6.md)
consigne six cas jetables réussis. Il confirme la stratégie de copie pour cette
version seulement, sans capturer le contexte système complet ni autoriser une
promotion.

## Profils runtime expérimentaux

[`model-profiles.json`](model-profiles.json) sépare désormais l'identité du
modèle des probes Ollama et OpenCode. Il contient uniquement les deux profils
mesurés `qwen3.6-35b-q4km` et `qwen3.6-27b-q4km`, avec digests, architecture,
paramètres, quantification, taille, contextes et endpoint loopback. Cette couche
est une donnée de test expérimentale : elle n'ajoute aucun provider, routage,
modèle actif ou règle comportementale au repository.

Les probes gardent le 35B comme défaut historique et acceptent une sélection
explicite par `--profile`. L'identité locale et les blobs sont vérifiés avant
tout démarrage. Le [rapport 27B](validation/opencode-qwen3.6-27b-smoke-1.17.9.md)
consigne le premier usage du registre et son arrêt matériel avant inférence.

Le seul profil 27B porte désormais une politique d'allocation expérimentale
explicite : contexte 16 384, parallélisme 1, réserve de 4 Gio par GPU et gate de
4 096 MiB de VRAM réellement libre. La réserve est injectée uniquement dans
l'environnement du serveur Ollama enfant ; elle n'est ni un réglage global, ni
une règle d'adaptateur comportemental. Le
[rapport d'offload](validation/opencode-qwen3.6-27b-offload-smoke-1.17.9.md)
consigne son résultat `BLOCKED` avant OpenCode.

## Risque de double chargement

Le cas le plus net est OpenCode : sa documentation dit que `instructions` est
combiné avec `AGENTS.md`. Si `AGENTS.md` matérialise déjà le kernel pour Codex,
un `opencode.json` pointant vers le canon le chargerait vraisemblablement deux
fois. C'est une **inférence** à confirmer en capturant le contexte runtime. Pour
Claude Code, `AGENTS.md` n'est pas découvert au runtime ; un unique import depuis
`CLAUDE.md` évite donc la duplication documentée. Pour Codex, la sélection d'au
plus un fichier par niveau n'empêche pas les conflits avec les niveaux globaux ou
imbriqués.

## Recommandation pour le futur canon stable

Recommander `doctrine/KERNEL.md` après promotion :

- `doctrine/` exprime une autorité stable sans nommer de fournisseur ;
- le chemin est distinct de `experiments/`, donc une promotion nécessite un acte
  visible plutôt qu'un simple changement de statut ;
- aucun des trois harnesses ne le découvre automatiquement par ce seul nom ;
- Claude Code pourra l'inclure directement ; Codex et OpenCode pourront recevoir
  une copie générée commune dans `AGENTS.md` ;
- la source, les copies et leurs wrappers pourront être mesurés séparément.

Cette recommandation ne vaut ni création du chemin, ni validation runtime, ni
autorisation de migrer le bootstrap actuel.

## Tests exigés avant branchement

- fixer OS, version du client, répertoire de lancement et configuration visible ;
- confirmer la liste et l'ordre des sources chargées ;
- comparer le payload injecté au SHA-256 attendu et compter les occurrences ;
- tester racine, sous-répertoire, override/fallback et adaptateur absent ;
- injecter des canaris non dangereux pour révéler précédence et contradiction ;
- mesurer séparément payload, wrappers et métadonnées ;
- répéter avec un nouveau processus et après compaction/reprise lorsque pertinent ;
- pour un modèle local, enregistrer runtime, modèle Qwen exact, quantification et
  template sans attribuer au modèle la découverte effectuée par OpenCode.
