# Carte du repository

## Snapshot reproductible

| Champ | Observation |
|---|---|
| Repository | `https://github.com/DietrichGebert/ponytail` |
| Branche par défaut | `main` |
| SHA audité | `16f29800fd2681bdf24f3eb4ccffe38be3baec6b` |
| Commit | 15 juillet 2026, `docs: FAQ entry on using caveman with ponytail (#599)` |
| Version déclarée | `4.8.4` |
| Tag/release correspondant | aucun : `v4.8.4` pointe sur `bc9ee949…`, le 29 juin 2026 |
| Licence | MIT |
| Checkout | historique complet, détaché au SHA, propre, sans submodule |

Le HEAD distant observé est resté celui annoncé dans la mission. Le clone a été placé sous `%TEMP%\EGX_Terminal-audits\ponytail-16f29800`. La divergence release/package est matérielle : les manifests de `main` restent à `4.8.4`, mais le tarball npm signé par son intégrité ne contient pas les correctifs OpenCode des 9–10 juillet [E02–E05].

## Inventaire

Les 156 fichiers suivis ont été inventoriés ; les 150 fichiers textuels ont fait l'objet d'une recherche statique et les 6 binaires d'une inspection de taille/type. Tous les fichiers directement impliqués dans doctrine, injection, état, configuration, installation, packaging, tests et benchmarks ont été lus, ainsi que les diffs historiques ciblés [E01].

| Mesure | Valeur |
|---|---:|
| Fichiers suivis | 156 |
| Texte / binaire | 150 / 6 |
| Taille totale | 1 642 202 octets |
| Markdown | 56 |
| JavaScript/MJS/CJS | 45 |
| JSON | 17 |
| Python | 6 |
| YAML/YML | 9 |
| TOML | 6 |
| PNG/SVG | 11 |

Répertoires dominants par taille : `assets/` (1 074 086 octets), `benchmarks/` (228 751), `tests/` (67 774), `examples/` (36 963), `hooks/` (30 879), `pi-extension/` (25 199). Les fichiers les plus volumineux sont des logos/bannières ; côté code, `benchmarks/agentic/tasks.py` (51 614 octets) et `run.py` (27 148) dominent.

### Arborescence conceptuelle

```text
skills/ponytail/SKILL.md              doctrine complète, source runtime
├─ hooks/ponytail-instructions.js     extraction, modes, fallback
│  ├─ hooks/*                         Claude / Codex / Copilot / Qoder
│  ├─ .opencode/plugins/*             OpenCode
│  ├─ pi-extension/*                  Pi
│  └─ ponytail-mcp/*                  prompt/tool MCP
├─ skills/ponytail-{review,...}/      capacités adjacentes à la demande
└─ .openclaw/skills/*                 copies générées

AGENTS.md                             fallback compact distinct
├─ .agents/.cursor/.cline/.kiro/...   copies exactes contrôlées
├─ gemini-extension.json              contexte instruction-tier
└─ adaptateurs AGENTS génériques

__init__.py + plugin.yaml             runtime Hermes réimplémenté
commands/*.toml + .opencode/command/* commandes dupliquées manuellement
benchmarks/ + examples/               instruments, résultats, sorties éditoriales
tests/ + .github/workflows/           88 tests déclarés, CI, publication
```

## Sources de vérité, copies et dérive

| Surface | Rôle réel | Synchronisation | Risque |
|---|---|---|---|
| `skills/ponytail/SKILL.md` | doctrine complète lue au runtime | canaris avec `AGENTS.md`, tests du filtre | source comportementale principale [E06] |
| `hooks/ponytail-instructions.js` | builder partagé Node | tests unitaires | contient un fallback manuel [E12] |
| `AGENTS.md` | fallback compact et canonical des copies instruction-tier | égalité byte-à-byte normalisée de sept copies | pas généré depuis la skill ; équivalence seulement partielle [E10] |
| `.openclaw/skills/*` | paquet OpenClaw | généré depuis les six skills | dérive bloquée par test [E11] |
| `commands/*.toml` / `.opencode/command/*.md` | commandes par harness | assertions de présence/parsing, pas génération commune | texte et claims peuvent diverger |
| `__init__.py` | adaptateur Hermes | tests propres, pas builder commun | logique métier dupliquée et ancien regex [E14, E31] |
| manifests/version | métadonnées publiques | `check-versions.js` | pas de preuve que release/npm = contenu de `main` [E04–E05] |
| `skills/ponytail-gain` | carte de résultats | aucun lien automatique avec résultats | chiffres obsolètes [E34] |

Les huit règles compactes comparées ont le même SHA-256 normalisé : `a0a2c27dd38daccad59412b8ddaac57344899f38c7451b88d7c8f8aa86821a57`. C'est une synchronisation forte entre copies compactes, mais pas entre cette famille et la doctrine longue.

### Divergences classées

| Divergence | Classe | Effet |
|---|---|---|
| Skill longue vs `AGENTS.md` compact | intentionnelle, manuelle | deux kernels apparents ; seulement neuf canaris communs |
| OpenClaw vs skills | générée | corps alignés, frontmatter adapté |
| Hermes vs builder Node | historique / potentiellement trompeuse | #571 affirme un partage universel qui n'existe pas ; bug latent conservé |
| `ponytail-gain` vs README | obsolète / potentiellement trompeuse | anciens 80–94 % et 47–77 % encore servis à la demande |
| README agentique : 6 safety tasks ; harness courant : 7 | historique | `critic-email` a été ajouté après la campagne publiée |
| completeness disponible vs résultat publié | historique / inconnue | capacité actuelle, aucun score committé pour la campagne mise en avant |
| `4.8.4` main vs tag/npm `4.8.4` | obsolète / packaging | même numéro, capacités différentes |
| Pi/Node refusent `review` par défaut ; Hermes l'accepte | involontaire probable | sémantique de mode divergente |
| Qoder `PreToolUse task|Task` qualifié « subagent » | inconnue | schéma non établi par la documentation Qoder [E29] |

## Packages, installation et publication

Le repository contient un paquet npm public racine, une extension Pi déclarée dans ce paquet, un serveur MCP privé avec dépendances SDK/Zod, des manifests Claude/Codex/Gemini/Qoder/Devin/Hermes/Copilot, un plugin OpenCode et six paquets de skill OpenClaw. Le paquet racine n'a pas de `postinstall` ; il publie règles, hooks, skills, adaptateurs et uninstall [E49].

La CI comporte deux workflows : tests sur Node 22/Python 3.12 avec `pandas` et dépendances MCP, puis publication npm sur tag avec OIDC. Elle n'exécute pas les benchmarks payants. `npm@latest` est installé pendant la publication : l'authentification évite un secret long terme, mais l'outil publié dépend d'une résolution mutable.

La marketplace personnelle `.agents/plugins/marketplace.json` suit `ref: main`, donc une installation ultérieure ne reconstitue pas automatiquement le snapshot. OpenCode peut résoudre le nom npm avec Bun ; le pinning dépend de la configuration/cache du host. Les installations depuis checkout sont réversibles par le host, mais `scripts/uninstall.js` ne nettoie pas tous les états secondaires [E50].

## Tests et CI

Le décompte statique trouve 88 cas `test()` : 62 à la racine, 23 pour Pi, 3 pour MCP. Ils couvrent notamment copies, manifests, filtre de modes, schémas de hooks, Windows, Qoder, OpenCode/Qwen, Hermes, uninstall et instruments de correctness. L'audit n'a exécuté ni code, ni test, ni benchmark upstream conformément à l'isolation demandée [E51].

Les limites visibles des tests sont autant instructives que leur nombre : pas de matrice live multi-harness/multi-version, pas de modèle réel, pas de round-trip release/npm, pas de régression Claude sur le prompt transformé de #584, et le test Hermes ne réutilise pas le corpus de régression du builder Node.

## Benchmarks et artefacts

`benchmarks/` contient trois familles : single-shot Promptfoo, modèle local Ollama, et sessions agentiques Claude Code. Les neuf documents `results/` retracent plusieurs corrections. `examples/` est éditorial ; son ancien `output.json` source n'est pas committé (#415). Les runs agentiques et JSON bruts sont gitignorés, si bien que les tables sont auditables mais non reconstructibles observation par observation [E37–E48].

## Historique pivot

Trente-quatre commits pivots ont été inspectés par message, diff/stat ou contenu ciblé :

| Date | Commit | Pivot |
|---|---|---|
| 2026-06-13 | `321a59c` | benchmark reproductible trois modèles |
| 2026-06-14 | `6d990f8` | première assertion de correction |
| 2026-06-15 | `386f957` | support modèle local |
| 2026-06-15 | `2e6a937` | compteur LOC unfenced |
| 2026-06-16 | `caf138d` | correction gate + robustesse |
| 2026-06-17 | `1b49141` | coût corrigé 42–75 % |
| 2026-06-18 | `b8d6aa7` | benchmark agentique |
| 2026-06-18 | `955fff5` | juge completeness |
| 2026-06-19 | `48cdf05` | retrait du system prompt de baseline |
| 2026-06-22 | `dedc97c` | compréhension et réutilisation |
| 2026-06-21 | `6da37bf` | CVE SDK MCP |
| 2026-06-23 | `763e04d` | garde de versions |
| 2026-06-24 | `17a4660` | publication npm OpenCode/Pi |
| 2026-06-24 | `b9fa564` | injection sous-agents |
| 2026-06-24 | `7d303b7` | publication OIDC |
| 2026-06-26 | `8d154e6` | commentaires exclus du LOC |
| 2026-07-02 | `7e6eca6` | deadlock stdin Windows |
| 2026-07-02 | `40e50d9` | uninstall JSON invalide |
| 2026-07-07 | `4286903` | inclusion uninstall dans npm |
| 2026-07-07 | `988428d` | merge de configuration |
| 2026-07-07 | `bed76c5` | défaut persistant |
| 2026-07-09 | `1715abc` | scope de sous-agent |
| 2026-07-09 | `055a145` | fusion système Qwen |
| 2026-07-09 | `33c00d3` | schéma Codex erroné |
| 2026-07-10 | `3465b1a` | restauration du schéma Codex |
| 2026-07-10 | `2ba0262` | compatibilité PowerShell |
| 2026-07-10 | `65db902` | `review` session-only |
| 2026-07-10 | `0cdd11f` | filtre de modes #571 |
| 2026-07-10 | `b6c0448` | marqueur `ponytail:` resserré |
| 2026-07-09 | `83493b9` | adaptateur Qoder |
| 2026-07-09 | `511ddd4` | export OpenCode corrigé |
| 2026-07-10 | `f12f210` | kill timeout portable |
| 2026-07-10 | `14a0d79` | nudge statusline unique |
| 2026-07-15 | `16f2980` | FAQ Caveman |

Cet historique montre un système jeune mais activement corrigé : gains méthodologiques réels, et surface de compatibilité assez large pour produire des régressions de schéma, Windows, état et packaging.

## Issues et pull requests étudiées

Les 21 références imposées ont toutes été ouvertes et classées : `#126`, `#225`, `#296`, `#308`, `#326`, `#483`, `#505`, `#506`, `#508`, `#522`, `#529`, `#536`, `#553`, `#555`, `#571`, `#572`, `#573`, `#574`, `#576`, `#577`, `#599`.

Des recherches ciblées ont ajouté : `#65`, `#100`, `#121`, `#144`, `#155`, `#169`, `#201`, `#219`, `#231`, `#245`, `#252`, `#301`, `#372`, `#380`, `#415`, `#426`, `#443`, `#502`, `#584`, `#595`, `#596`, `#597`. Soit 43 issues/PR au total, sans compter les commits directs. Les contre-exemples structurants sont : baseline contaminée, métrique LOC erronée, correctness gate incomplète, coûts inversés selon modèle, surcharge sous-agent, schéma Codex cassé puis restauré, commandes Claude non détectées, loader npm non republié et chiffres de gain périmés.

## Documentations officielles consultées

Vérifiées au 20 juillet 2026, sans utiliser la table de compatibilité de Ponytail comme preuve externe :

- Codex : [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skills](https://learn.chatgpt.com/docs/build-skills), [hooks](https://learn.chatgpt.com/docs/hooks), [plugins](https://learn.chatgpt.com/docs/build-plugins).
- Claude Code : [hooks](https://code.claude.com/docs/en/hooks), [subagents](https://code.claude.com/docs/en/sub-agents), [plugins](https://code.claude.com/docs/en/plugins), [skills](https://code.claude.com/docs/en/skills).
- OpenCode : [plugins](https://opencode.ai/docs/plugins/), [skills](https://opencode.ai/docs/skills/), [rules](https://opencode.ai/docs/rules/), [commands](https://opencode.ai/docs/commands/).
- Gemini CLI : [extension reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/reference.md).
- Qoder : [hooks](https://docs.qoder.com/extensions/hooks), [CLI skills](https://docs.qoder.com/en/cli/Skills).
- Pi : [extension API](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md).

Ces seize pages établissent les primitives officielles. Elles ne valident pas à elles seules la manière dont Ponytail les compose [E25–E30].
