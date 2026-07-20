# Audit 03 — DietrichGebert/ponytail

## Identité de l'observation

| Champ | Valeur |
|---|---|
| Repository | `https://github.com/DietrichGebert/ponytail` |
| SHA audité | `16f29800fd2681bdf24f3eb4ccffe38be3baec6b` |
| Observation | 20 juillet 2026 |
| Version déclarée | `4.8.4` |
| Tag/release | `v4.8.4` correspond à un commit antérieur, pas au snapshot |
| Licence | MIT |
| Maturité | jeune, largement distribué, testé statiquement, encore en correction active |

Le snapshot distant n'avait pas dérivé. En revanche, `main`, le tag et npm exposent le même numéro avec des capacités différentes : le paquet npm `4.8.4` ne contient pas les correctifs OpenCode loader/Qwen présents dans le snapshot [E02–E05].

## Ce que c'est

Ponytail est un ensemble portable de six skills, une règle compacte `AGENTS.md`, un builder d'instructions, une machine de modes et des adaptateurs pour de nombreux harnesses. Il cherche moins à raccourcir la prose qu'à changer la décision d'implémentation : éliminer le besoin, réutiliser, employer stdlib ou plateforme native, utiliser une dépendance déjà présente, puis écrire le minimum correct [E06–E09].

Son modèle mental réel est :

```text
comprendre le flux
→ chercher ce qui existe
→ monter la ladder jusqu'au premier rung suffisant
→ préserver exigences et garde-fous
→ laisser un check proportionné au risque
```

La persona « lazy senior » et la sortie très brève encodent ce modèle mental, mais ne sont pas la politique elle-même et leur contribution n'est pas isolée [E52].

## Mécanisme en cinq points

1. `skills/ponytail/SKILL.md` définit persona, ladder, règles, modes et rails [E06–E09].
2. Le builder Node retire le frontmatter, filtre une ligne/un exemple de mode et fournit un fallback [E12–E13].
3. Les adaptateurs injectent ce payload au démarrage, au tour, au sous-agent ou à la demande selon le harness [E17–E31].
4. Un état `off/lite/full/ultra/review` est persisté de façons incompatibles selon le host ; les trois intensités transportent pourtant presque le même texte [E15–E18, E36].
5. Les benchmarks mesurent surtout code évité, sécurité, coût et temps ; plusieurs générations ont corrigé compteur, baseline, contamination et claims [E37–E48].

## Message du repository sans la persona

Avant d'ajouter du code, comprendre la demande et le flux existant, puis préférer dans l'ordre l'absence de solution, la réutilisation, la bibliothèque standard, la plateforme et les dépendances déjà disponibles. N'ajouter que le minimum correct, sans sacrifier sécurité, données, accessibilité, exigences explicites ni validation proportionnée.

C'est principalement une **politique de décision de code**, soutenue par une doctrine et emballée dans un style. Ce n'est pas seulement un style de réponse.

## Forces établies

- La séparation conceptuelle « comportement portable → builder → adaptateurs » est claire et effectivement utilisée par les chemins Node, Pi, MCP et OpenCode [E06, E12, E22, E30].
- Les règles compactes sont strictement synchronisées et les copies OpenClaw sont générées [E10–E11].
- La doctrine ajoute des rails de compréhension et de sécurité au minimalisme ; le prompt one-line de contrôle a supprimé un guard une fois, Ponytail non dans cette petite campagne [E08–E09, E43].
- Le benchmark agentique corrigé retrouve un signal LOC fort sur les tâches à primitive native : −54,22 % recalculé depuis la table publiée [E40–E42].
- Le projet publie ses échecs méthodologiques : compteur LOC, correctness, coûts, contamination et petit modèle négatif [E39, E44, E47].

## Limites principales

- `AGENTS.md` n'est pas le kernel canonique : c'est un fallback compact manuel et la source d'une autre famille de copies [E10].
- Le builder est partagé mais pas universel. Hermes réimplémente la logique et conserve le motif du bug #571 ; Qoder/OpenCode portent aussi de la logique de livraison substantielle [E14, E22, E29, E31].
- Les modes coûtent une machine d'état multi-harness pour seulement 65 caractères de différence entre intensités ; reprise/compaction et commande Claude comportent des incertitudes [E17, E19, E36].
- L'injection par défaut dans tous les sous-agents coûte ~1 300 tokens par worker et peut biaiser les reviewers/readers [E20–E21].
- Le résultat headline ne fournit ni données brutes ni completeness committée ; `n=4` et les tâches favorisent le mécanisme native-first [E40–E46].
- `ponytail-gain` et npm `4.8.4` sont en retard sur `main`, ce qui rend documentation et installation dépendantes de la surface [E05, E34].

## Résultats expérimentaux principaux

| Question | Résultat | Portée |
|---|---|---|
| Réduction agentique de code | −54,22 % recalculé sur 12 moyennes publiées | Haiku 4.5, Claude Code, `n=4`, tâches sélectionnées [E40–E42] |
| Sécurité | 20/20 Ponytail, 19/20 prompt one-line | cinq axes × quatre runs ; Wilson bas 83,9 %, pas « toujours sûr » [E43] |
| Coût | −42 à −75 % rapporté sur Claude ; +26/+39 % sur deux modèles OpenAI reasoning | raw data absente, provider-specific [E46–E47] |
| Petit modèle | aucun gain LOC stable, latence +10–15 % rapportée | Llama 3.2 3B Q4_K_M seulement [E37–E39] |
| Qwen/OpenCode | erreur de messages système corrigée par fusion | compatibilité de protocole, aucune adhérence mesurée [E23–E24] |

Le résultat Llama interdit de présenter la doctrine comme universellement transférable. Il ne prédit pas Qwen ; il motive une instruction plus courte et une expérience dédiée. La correction Qwen n'établit que la possibilité de faire l'appel [E23–E24, E37–E38].

## Projection isolée vers EGX_Terminal

Cette section formule des dispositions candidates, pas une architecture ni une adoption.

1. Le message essentiel est la ladder subordonnée à compréhension, exigences et risque.
2. Le noyau minimal est une politique de décision, non la persona ni le format trois lignes.
3. Une version permanente devrait se limiter à comprendre/réutiliser/stdlib-native/minimum correct et rails ; le détail « one line » devrait rester à la demande [E54].
4. `AGENTS.md` est un fallback dupliqué, pas un bon unique kernel.
5. Le builder Node est une source d'assemblage réelle, mais pas canonique pour Hermes ni les copies compactes.
6. Les adaptateurs réellement minces sont ceux qui ne font que déclarer ou appeler le builder ; Hermes, OpenCode et Qoder portent davantage de sémantique/état.
7. La portabilité de la ladder est sémantique ; événements, schémas JSON, chemins, état et chat templates sont des compatibilités protocolaires.
8. Avec Qwen/OpenCode, fusionner dans l'entrée système existante évite l'erreur observée, sans présumer priorité ni efficacité.
9. L'injection à chaque tour vaut environ 1 300 tokens avant cache ; son coût réel doit être mesuré par provider.
10. Une version neutre condensée est testable pour petits modèles ; la persona et les exemples sont des ablations distinctes.
11. Les sous-agents devraient recevoir la doctrine par capacité d'écriture, pas par regex propriétaire et fail-open.
12. Les modes n'ont pas, au snapshot, une différence sémantique proportionnée à leur complexité.
13. Le marqueur de dette est intéressant comme convention générique ceiling/trigger/upgrade, pas nécessairement sous le nom `ponytail:`.
14. Pour éviter le code golf : priorité explicite correction > exigences > lisibilité > minimalité, test proportionné au risque, et aucune dispense automatique liée au nombre de lignes.
15. Les garde-fous sont bien choisis mais leur couverture expérimentale est étroite.
16. « Un runnable check » est un plancher, jamais un plafond ni un remplacement des conventions du repo.
17. Ne pas reprendre la persona comme autorité, la limite de trois lignes, l'injection universelle, les modes tels quels, le fail-open silencieux ni les claims de gains globaux.
18. Les tests indispensables seraient conformance du kernel entre adaptateurs, schémas live par version, restart/resume/compact, double injection, état concurrent, uninstall, Qwen message shape, ablations multi-modèles et completeness/safety.
19. Les claims solides pour une expérience sont l'effet native-first sur le jeu Haiku, le coût contextuel mesuré et l'échec Llama local.
20. Les gains de coût, de latence, d'adhérence et de sécurité restent provider/model/task-specific.

## Matrice de disposition propre à cet audit

| Element | Adopt | Adapt | Reject | Defer | Evidence |
|---|:---:|:---:|:---:|:---:|---|
| Ladder besoin → réutilisation → stdlib/native/existant → minimum |  | ✓ |  |  | neutraliser, subordonner aux exigences [E07–E08] |
| Compréhension, root cause et callers | ✓ |  |  |  | principe candidat fortement justifié [E08] |
| Persona « lazy senior » |  |  |  | ✓ | contribution non isolée [E52] |
| Format de sortie ≤3 lignes |  |  | ✓ |  | incompatible avec review exhaustive |
| One-line comme rung permanent |  |  | ✓ |  | code-golf et test exemption [E09, E43] |
| Garde-fous trust/data/security/accessibility/hardware |  | ✓ |  |  | élargir et tester [E08, E43] |
| Un check obligatoire |  | ✓ |  |  | plancher à rendre proportionnel au risque [E09] |
| Skill canonique + builder partagé |  | ✓ |  |  | séparation utile, conformance insuffisante [E06, E12–E14] |
| `AGENTS.md` compact |  | ✓ |  |  | fallback utile, duplication manuelle [E10] |
| Modes lite/full/ultra |  |  |  | ✓ | coût complexe, faible delta sémantique [E15–E18, E36] |
| `review` comme état |  |  | ✓ |  | préférer une skill explicite |
| Injection à chaque tour |  |  |  | ✓ | mesurer cache/adhérence par provider [E22, E47] |
| Injection universelle sous-agent |  |  | ✓ |  | coût et biais [E20–E21] |
| Scope par capacité du sous-agent |  | ✓ |  |  | remplacer `agent_type` propriétaire |
| Fusion dans un system message Qwen |  | ✓ |  |  | correctif protocolaire local [E23–E24] |
| Convention ceiling/trigger/upgrade |  | ✓ |  |  | détacher du branding [E33] |
| Review/audit d'over-engineering |  | ✓ |  |  | titre/scope explicites, pas métrique spéculative [E32] |
| Carte `ponytail-gain` |  |  | ✓ |  | chiffres obsolètes [E34] |
| Claim « 100% safe » |  |  | ✓ |  | seulement 20/20 observé [E43] |
| Benchmarks par mécanisme et contre-preuves | ✓ |  |  |  | bonne méthode, raw data à committer [E39–E48] |

Les coches sont des **dispositions analytiques candidates propres à Ponytail**. Elles ne deviennent aucune décision EGX_Terminal.

## Limites et unknowns

- L'adhérence effective de Qwen une fois le protocole corrigé est inconnue [E24].
- La persona, les exemples et la répétition ne sont pas ablatés [E52].
- La restauration exacte des modes Node après resume/compact doit être testée live [E17, E53].
- L'issue Claude #584 et les collisions multi-plugin #595 restent ouvertes au snapshot [E19].
- La validité du chemin Qoder sous-agent n'est pas établie par les docs officielles [E29].
- Prompt caching, reasoning tokens et duplication réelle varient par provider.
- Les scores completeness des douze tâches mises en avant manquent [E45].
- Les données brutes et les versions exactes de plugin utilisées dans certaines campagnes manquent [E46].
- La release qui réconciliera npm et `main` n'existe pas au snapshot [E05].

## Conclusion isolée

La contribution la plus forte de Ponytail est d'avoir transformé un slogan de minimalisme en une politique ordonnée et falsifiable, puis d'avoir documenté plusieurs contre-échecs. Son avantage mesuré vient surtout du choix de primitives natives sur des tâches qui autorisent réellement ce choix, renforcé par des rails de compréhension et de sécurité — pas d'une preuve que « moins de code » gagne partout [E08, E40–E48].

Son coût principal est la livraison active : ~1 300 tokens presque identiques pour trois modes, réinjectés selon le harness et par défaut dans chaque sous-agent, avec état et correctifs propres aux protocoles [E17–E24, E36]. Le noyau sémantique paraît plus portable que l'implémentation des adaptateurs. Aucune adoption n'est décidée avant la synthèse autorisée.

## Navigation

- [repository-map.md](repository-map.md) — inventaire, sources, copies, packages, tests, historique et issues.
- [behavior-and-delivery.md](behavior-and-delivery.md) — doctrine, modes, hooks, sous-agents, harnesses, Qwen et installation.
- [token-economics.md](token-economics.md) — empreinte, petit modèle, benchmarks, recalculs et claims.
- [evidence-ledger.md](evidence-ledger.md) — preuves classées et couverture du template.
