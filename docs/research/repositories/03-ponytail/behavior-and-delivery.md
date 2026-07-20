# Comportement et livraison

## Doctrine et politique de décision

Ponytail est d'abord une politique de sélection de solution. Sa persona de « lazy senior developer » sert de moyen mnémotechnique ; son style bref sert de sortie ; la ladder et ses garde-fous gouvernent la décision. Confondre ces couches rend impossible de savoir laquelle produit un gain [E06–E09, E52].

| Couche | Contenu | Valeur possible | Risque |
|---|---|---|---|
| Branding/persona | paresse, ancienneté, ton irrévérencieux | mémorisation, cohérence narrative | modèle littéral : négligence, contradiction de besoin |
| Style | code d'abord, explication ≤3 lignes | réduit la prose | masque hypothèses, findings ou limites |
| Politique | ladder du besoin au minimum correct | force alternatives moins coûteuses | exploration excessive ou refus d'une exigence légitime |
| Garde-fous | compréhension, callers, sécurité, données, accessibilité, matériel, check | empêche que « moins » devienne « fragile » | couverture concise et jugement délégué au modèle |
| Mécanisme | builder, modes, hooks, état, adaptateurs | répétition active, portabilité | contexte, duplication, bugs inter-harness |
| Mesure | LOC, sécurité, coût, temps | rend la thèse falsifiable | tâches et providers étroits, données brutes absentes |

### Anatomie de la ladder

| Rung | Preuve avant application | Bénéfice | Risque et coût d'exploration | Placement candidat |
|---|---|---|---|---|
| Besoin réel / YAGNI | l'exigence est spéculative ou déjà satisfaite | zéro code | contester une demande explicite ; faible coût | permanent, subordonné à l'utilisateur |
| Réutilisation interne | recherche des helpers, types, patterns et callers | cohérence, moins de duplication | recherche longue, réutilisation d'une mauvaise abstraction | codebase-aware, permanent |
| Standard library | API disponible dans la version cible | moins de supply chain | sémantique/ergonomie insuffisante | permanent avec vérification de compatibilité |
| Plateforme native | feature accessible et compatible | code et maintenance évités | couverture UX/accessibilité/browser imparfaite | permanent, mais domaine-specific |
| Dépendance installée | dépendance présente, maintenue et adaptée | pas de nouvelle dépendance | lock-in ou usage excessif d'une grosse API | permanent |
| Une ligne | lisible, correcte aux bords, testable | diff minimal | code golf, classification « trivial » erronée | à la demande, jamais objectif autonome |
| Minimum nouveau | les rungs précédents échouent | limite le scope | sous-conception, dette cachée | permanent avec rails |

Le coût d'exploration n'est pas nul : rechercher l'existant et tous les callers peut augmenter lectures, tool calls et reasoning avant de réduire l'output. L'issue #121 observe précisément ce déplacement sur Cursor [E48]. La valeur attendue est donc du code et de la maintenance évités, pas nécessairement des tokens de session.

### Règles transversales

- **YAGNI, deletion, boring, minimal diff.** Bon filtre contre scope spéculatif, insuffisant pour juger correction ou évolutivité.
- **Root cause et callers.** Correctif important ajouté après des contre-exemples ; il empêche un petit patch local de déplacer le bug [E08].
- **Compréhension avant simplification.** Réduit le code-golf aveugle, mais accroît le coût de lecture.
- **Sécurité et trust boundaries.** La doctrine nomme les axes essentiels ; la campagne n'en prouve que cinq avec `n=4` [E43].
- **Accessibilité et matériel.** Garde-fous présents mais peu testés dans les résultats committés.
- **Un check exécutable.** Plancher utile pour une petite fonction, pas substitut aux tests existants, aux tests de régression ou à l'analyse de risque. La dispense des one-liners est particulièrement fragile parce que le modèle juge lui-même la trivialité [E09].
- **`ponytail:`.** Rend un compromis explicite et réversible, mais lie le code produit à une marque et peut normaliser une dette non suivie [E33].

La persona n'est pas démontrée comme nécessaire. Le bras « YAGNI + one-liner » est plus court, mais retire aussi la réutilisation, la compréhension, les exemples et les rails ; son comportement erratique ne constitue donc pas une ablation de persona [E52]. Une expérience pertinente comparerait des règles sémantiquement identiques : persona longue, formulation neutre longue, formulation neutre condensée, puis ablations rung par rung.

## Chaîne d'exécution

```text
skills/ponytail/SKILL.md
        │
        ├── retrait frontmatter
        ├── sélection ligne de mode + exemple
        └── fallback condensé si lecture impossible
                │
                ├── activate / mode-tracker / subagent hooks
                ├── OpenCode system.transform
                ├── Pi before_agent_start
                └── MCP prompt/tool
                         │
                      harness → modèle

AGENTS.md → copies instruction-tier → harness → modèle
Hermes __init__.py → réimplémentation Python → modèle
```

Le builder partagé est une vraie source d'assemblage pour Node, pas la source canonique universelle. Il dépend du texte de la skill, contient un fallback manuel et n'est pas utilisé par Hermes. Les adaptateurs peuvent donc être minces seulement lorsqu'ils délèguent réellement à ce builder [E10–E14].

### Runtime et erreurs

Le builder normalise un mode inconnu vers `full`; une lecture de skill échouée utilise silencieusement le fallback. La configuration invalide ou illisible retourne silencieusement `full`. Cette stratégie fail-open maintient l'activation, mais une installation partielle ou un état corrompu devient peu observable [E12, E16].

Les hooks manifest ont un timeout de cinq secondes ; les trackers qui lisent stdin s'auto-terminent après une seconde. Le chemin POSIX invoque directement `node`, tandis que le chemin PowerShell vérifie sa présence : « reste silencieux sans Node » n'est donc pas identique sur toutes les plateformes. Les corrections Windows couvrent variables PowerShell, stdin qui ne se ferme pas, BOM, `CLAUDE_CONFIG_DIR`, suppression de `exec` et kill de groupes [E51].

## Modes et machine d'état

| Mode | Sémantique | Persistance Node | Activation | Contenu effectif |
|---|---|---|---|---|
| `off` | aucune injection | défaut possible ; flag supprimé | commande ou config/env | zéro |
| `lite` | construire, signaler une alternative | défaut + état live | commande/env/config | doctrine quasi complète, ligne/exemple lite |
| `full` | ladder enforce, défaut | défaut + état live | startup ou commande | doctrine quasi complète, ligne/exemple full |
| `ultra` | couper plus agressivement | défaut + état live | commande/env/config | doctrine quasi complète, ligne/exemple ultra |
| `review` | pointeur vers skill de review | session-only attendu | `/ponytail-review` | banner/pointeur dans Node ; corps review dans Hermes |

```text
env > config > full
       │ SessionStart startup/resume/clear/compact
       ▼
  off ─┬─ lite ─ full ─ ultra
       │        commande live
       └──────── review (session-only attendu)

prochain SessionStart → relit le défaut, pas nécessairement le mode live
```

Le défaut est portable comme intention, pas l'état :

- Claude utilise le répertoire de configuration ; Codex/Copilot des data dirs de plugin ; Qoder `~/.qoder` [E18].
- OpenCode utilise XDG/`~/.config/opencode/.ponytail-active`, persistant entre sessions [E22].
- Pi écrit une entrée custom dans le transcript et restaure la dernière [E30].
- Hermes conserve `_current_mode` dans le processus et accepte encore `review` dans la configuration [E31].

Le hook Node réécrit l'état depuis le défaut sur chaque `SessionStart`, y compris `resume` et `compact`; il ne restaure donc pas explicitement le choix live. C'est un risque de perte de mode dérivé du code, à vérifier en intégration [E17, E53]. La commande skill Claude est elle-même contestée par #584 [E19]. Les modes ajoutent ainsi une sémantique très faible — une ligne et un exemple changent — pour une machine d'état devenue substantielle [E36].

## Sous-agents

Claude/Codex ont besoin d'une surface séparée parce que le contexte du parent n'est pas hérité automatiquement [E27]. Ponytail choisit pourtant l'injection universelle par défaut : chaque worker reçoit environ 1 300 tokens ; le matcher optionnel est un regex sur `agent_type`, fail-open [E20–E21].

| Type de sous-agent | Bénéfice probable | Coût/risque | Scope candidat |
|---|---|---|---|
| implémentation/refactor | élevé | faible si rails adaptés | opt-in par capacité « écrit du code » |
| debug/root cause | moyen-élevé | peut pousser trop tôt vers petit diff | version neutre sans style court |
| review sécurité/correction | faible ou négatif | limite de trois lignes et biais deletion | exclure |
| recherche/read-only | faible | contexte et attention sans code à réduire | exclure |
| plan/architecture | incertain | YAGNI utile, one-line nocif | doctrine courte dédiée |

Un `agent_type` propriétaire au harness n'est pas un concept portable. Le principe portable serait une capacité déclarée — écrit du code, review exhaustive, recherche — traduite par chaque adaptateur. Le défaut le plus prudent est opt-in pour les agents d'implémentation ; fail-open privilégie aujourd'hui l'adhérence au détriment du coût et de la pureté des reviewers.

## Skills adjacentes

Toutes sont découvertes par frontmatter et chargées à la demande dans un harness de skills ; leurs descriptions restent toutefois dans le budget de découverte [E26, E35].

| Skill | Objet/trigger | Dépendance | Coût statique estimé | Risque principal |
|---|---|---|---:|---|
| `ponytail-review` | diff, suppression d'over-engineering | ladder centrale implicite | ~607 tokens | scope exclut bugs/sécurité/perf ; `net -N` spéculatif [E32] |
| `ponytail-audit` | même analyse, repo entier | forte | ~423 | scan large et estimation lignes/deps non instrumentée |
| `ponytail-debt` | collecte `ponytail:` | convention centrale | ~437 | commentaires de marque ; grep non natif Windows [E33] |
| `ponytail-gain` | comparer la réalisation au benchmark | données benchmark | ~469 | carte obsolète [E34] |
| `ponytail-help` | modes/install/update | surfaces de livraison | ~715 | claims « active every session » et commandes divergents |

Review/audit annoncent leurs exclusions, ce qui est honnête mais facile à rater si l'utilisateur dit seulement « review ». Une version portable devrait nommer le résultat « audit d'over-engineering » dans le titre de sortie et interdire toute présentation comme review complète. Les économies `net` devraient être mesurées depuis un patch proposé ou marquées estimation.

## Portabilité par harness

Niveaux : **instruction-tier** = texte statique toujours en contexte ; **skill-tier** = métadonnées visibles, corps à la demande ; **plugin/hook-tier** = injection et état actifs.

| Harness | Entry point | Injection event | Content | State | Scope / subagents | Enforcement | Evidence |
|---|---|---|---|---|---|---|---|
| Codex CLI/desktop | manifest, skills, hooks | `SessionStart`, `UserPromptSubmit`, `SubagentStart` | builder complet | `PLUGIN_DATA/.ponytail-active` | parent + tous sous-agents par défaut | plugin/hook + skill | [E18, E20, E26] |
| Claude Code | marketplace, skill, mêmes hooks | startup/resume/clear/compact, prompts, subagents | builder complet | config dir Claude | parent + subagents | plugin/hook + skill | [E17, E19, E27] |
| OpenCode | npm/local `.mjs` | `experimental.chat.system.transform` chaque tour | builder fusionné au dernier system | XDG global OpenCode | session globale ; propagation propre non établie | plugin + skills + AGENTS | [E22–E25] |
| Qwen via OpenCode | même plugin | même transform | une seule entrée système | idem | idem | compatibilité protocole seulement | [E23–E24] |
| Gemini CLI | `gemini-extension.json` | chargement `contextFileName` | `AGENTS.md` compact | aucun mode live | portée du fichier de contexte | instruction + skills/commands | [E28] |
| Pi | paquet npm/extension | `session_start`, `before_agent_start` | builder complet | transcript custom | session Pi ; sous-agent non démontré | plugin + skills | [E30] |
| Qoder | AGENTS/rule/manifest + template hooks | `UserPromptSubmit`, `PreToolUse task|Task` | compact et/ou builder | `~/.qoder` | sous-agent revendiqué via outil Task | instruction/skill/plugin annoncé | [E29] |
| Hermes | `plugin.yaml`, `__init__.py` | `pre_llm_call`, gateway dispatch | builder Python | variable process | partagé par processus | plugin + skills | [E14, E31] |
| fallback générique | `AGENTS.md` ou copie | découverte de règles du host | compact | aucun | projet/global selon host | instruction-tier | [E10] |

Les adaptateurs secondaires (Cursor, Windsurf, Cline, Kiro, Copilot instructions, `.agents`, OpenClaw, Devin, Swival, Zed, etc.) ont été cartographiés. Leur contenu committé est vérifiable ; leurs claims de découverte/installation restent author claims lorsqu'aucune documentation officielle n'a été approfondie. Cette réserve est préférable à transformer une table de compatibilité mainteneur en vérité sur vingt harnesses.

## OpenCode et Qwen

### Flux réel

1. OpenCode charge le module depuis npm ou checkout ; le hook `config` ajoute six commandes et le chemin des skills.
2. `command.execute.before` reconnaît seulement la commande Ponytail, valide le mode et écrit l'état ; le commentaire précise que le changement vaut au message suivant.
3. À chaque `experimental.chat.system.transform`, le plugin relit le mode et reconstruit environ 1 300 tokens.
4. Si une entrée système existe, le payload est concaténé à la dernière ; sinon il est poussé comme première entrée.
5. Les erreurs de lecture reviennent au défaut ; les erreurs d'enregistrement config sont largement silencieuses ; l'écriture d'état peut remonter une erreur [E22–E23].

Le commit `055a145…` répond à une erreur 400 rapportée pour `Qwen35-397B-A17B-FP8`. Il réduit le nombre de messages système, mais ne change ni la taille, ni la persona, ni la politique. C'est donc un correctif de compatibilité de protocole, pas une preuve d'efficacité comportementale [E23–E24].

La concaténation au dernier system prompt a quatre inconnues : priorité textuelle effective, collision avec les instructions du harness, cache exact du provider, et comportement quand plusieurs entrées système ont déjà des rôles distincts. Le suffixe stable peut être cacheable si tout le préfixe reste stable, mais le plugin l'assemble à chaque tour et aucun benchmark de cache OpenCode/Qwen n'est committé.

Le risque de livraison est plus concret : le paquet npm `4.8.4` ne contient pas ce correctif ni le correctif d'export #301, alors que le checkout `main` les contient sous le même numéro [E05]. Une évaluation Qwen doit donc épingler à la fois SHA du plugin, version OpenCode, modèle, provider et template de chat.

## Installation, réversibilité et supply chain

| Surface | Écriture principale | Dépendances | Rollback observé |
|---|---|---|---|
| Claude | marketplace/plugin, config/data, éventuelle statusline | Node dans shell non interactif | host uninstall + script partiel |
| Codex | plugin + approbation hooks, `PLUGIN_DATA` | Node | `codex plugin remove`; état data non nettoyé par script |
| OpenCode | cache npm/Bun ou checkout, état XDG | Bun/npm resolution, Node pour builder CJS | retirer plugin ; état persiste |
| Gemini | répertoire extension | découverte native | désinstaller extension ; pas d'état live |
| Pi | paquet npm + transcript | runtime Pi/Node | `pi uninstall`; entrées transcript restent |
| Qoder | copies projet/config utilisateur et chemin absolu remplacé manuellement | Node | supprimer hooks/règles/skill et état manuellement |
| Hermes | plugin Python, état process | runtime Hermes/Python | désactiver plugin/restart |
| règles statiques | fichier projet/global | aucune | supprimer le fichier copié |

Il n'y a ni `postinstall`, ni réseau post-installation propre à Ponytail [E49]. Les risques viennent du host : résolution npm/Bun, marketplace `main` mutable, dépendance MCP à installer, commandes d'update `latest`, approbation de hooks et copies à chemins locaux. L'uninstall est partiel et son parsing de statusline par `&&|;` n'est pas un parseur de shell [E50].

## Principes candidats, pas décisions

- Une politique neutre « comprendre → réutiliser → stdlib/native/existant → minimum correct » est plus portable que la persona.
- Le kernel doit préserver exigences explicites, conventions du repo, sécurité et profondeur de test proportionnelle au risque.
- Les adaptateurs devraient transporter un objet sémantique versionné, avec tests de conformance, plutôt que recopier le texte et la machine d'état.
- L'injection répétée devrait être réservée aux contextes qui écrivent du code ; skill-tier/instruction-tier suffit ailleurs.
- Toute expérience multi-modèle doit distinguer compatibilité du protocole, adhérence à la politique, qualité, coût de raisonnement et code évité.

Ces éléments restent des **Candidate principles**. Aucune adoption EGX_Terminal n'est décidée dans cet audit isolé.
