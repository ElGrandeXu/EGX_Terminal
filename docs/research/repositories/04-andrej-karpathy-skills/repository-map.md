# Carte du repository

## Méthode et décomptes

Le snapshot épinglé est `2c606141936f1eeef17fa3043a72095b4765b9c2` sur `main`, vérifié le 2026-07-20. Le clone contient l'historique complet accessible et n'a pas été exécuté. Les fichiers ont été lus intégralement ; les objets Git, branches, tags, releases et PR ont été énumérés ; les patches et conversations sémantiquement pertinents ont été inspectés.

| Objet | Décompte exact | Précision |
|---|---:|---|
| Fichiers suivis au snapshot | 9 | 9 textuels, 0 binaire |
| Commits | 30 | tous refs distants ; 28 joignables depuis `main` |
| Branches distantes réelles | 5 | hors référence symbolique `origin/HEAD` |
| Tags | 0 | aucun tag Git |
| Releases GitHub | 0 | aucune release |
| Issues accessibles | 0 | 0 ouverte, 0 fermée ; fonctionnalité Issues désactivée au moment de l'audit |
| Pull requests | 147 | 96 ouvertes, 12 fusionnées, 39 fermées sans fusion |
| Drafts parmi les PR | 2 | #155 ouverte ; #107 fermée sans fusion |

Les numéros absents de la suite des PR ne prouvent pas l'existence d'issues : des PR citent notamment #10, #12, #22, #23, #32 et #46, mais les endpoints correspondants répondent `404`. Leur contenu est donc inconnu, pas « inspecté ». La page du repository et son API indiquent actuellement `has_issues: false`.

## Arborescence et rôle de chaque fichier

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .cursor/rules/
│   └── karpathy-guidelines.mdc
├── skills/karpathy-guidelines/
│   └── SKILL.md
├── CLAUDE.md
├── CURSOR.md
├── EXAMPLES.md
├── README.md
└── README.zh.md
```

| Fichier | Octets | Lignes | Rôle au snapshot |
|---|---:|---:|---|
| `.claude-plugin/marketplace.json` | 787 | 29 | Catalogue Claude local : identité de marketplace et entrée du plugin. Ce n'est pas le payload comportemental. |
| `.claude-plugin/plugin.json` | 401 | 11 | Manifeste Claude ; déclare notamment le répertoire `skills`. |
| `.cursor/rules/karpathy-guidelines.mdc` | 2 708 | 70 | Copie comportementale Cursor, avec `alwaysApply: true`. |
| `CLAUDE.md` | 2 422 | 65 | Copie comportementale destinée à être placée à la racine d'un projet Claude Code. |
| `CURSOR.md` | 1 983 | 28 | Documentation d'installation Cursor ; n'est pas une règle runtime. |
| `EXAMPLES.md` | 15 360 | 522 | Exemples rédigés après le noyau ; aucune référence runtime ne le charge. |
| `README.md` | 6 369 | 171 | Présentation, installation, provenance revendiquée, développement et indicateurs proposés. |
| `README.zh.md` | 6 213 | 171 | Traduction chinoise du README, documentation seulement. |
| `skills/karpathy-guidelines/SKILL.md` | 2 585 | 67 | Skill Claude avec frontmatter de découverte puis payload chargé à la demande. |

Les 9 fichiers sont du texte UTF-8 ou ASCII sans octet NUL. Le dépôt ne contient ni code applicatif, ni tests, ni CI, ni hook, ni benchmark sur `main`.

## Histoire exhaustive et commits pivots

| Commit | Date | Fait observé |
|---|---|---|
| `8462496` | 2026-01-27 | Création de `CLAUDE.md` et README ; les quatre principes existent déjà ; co-signé Claude Opus 4.5. |
| `c488bed` | 2026-01-27 | Ajoute des commandes d'installation avec la faute `andrej-karpthy-skills`. |
| `0b53cbc` | 2026-01-27 | Ajoute la variante skill sous `.claude/skills` ; co-signé Opus 4.5. |
| `bf5837f` | 2026-01-27 | Corrige le lien X `1886192184808149383` en `2015883857489522876` ; co-signé Opus 4.5. |
| `b4c9b0f` | 2026-01-27 | Fusion de la PR #1. |
| `24eb5e2` | 2026-01-27 | Développe README, indicateurs, tradeoffs et mention MIT ; co-signé Opus 4.5. |
| `6c8ac84` | 2026-01-27 | Fusion de la PR #2. |
| `64723a4` | 2026-01-28 | Déplace le skill vers `skills/` et ajoute l'installation `npx skills`; PR #3. |
| `84512da` | 2026-01-28 | Fusion de la PR #3. |
| `4f6e050` | 2026-01-29 | Ajoute `EXAMPLES.md`; ultérieurement fusionné par #7. |
| `82467fa` | 2026-01-30 | Premier manifeste plugin et commande `claude plugins add`, chemins/forme incorrects ; co-signé Opus 4.5. |
| `c692832` | 2026-01-31 | Fusion de la PR #13. |
| `adc91eb` | 2026-01-31 | Ramène les URLs de `jiayuan7` vers `forrestchang`; co-signé Claude Haiku 4.5. |
| `a4f0aa3` | 2026-01-31 | Fusion de la PR #15. |
| `579a5e3` | 2026-01-31 | Déplace le manifeste dans `.claude-plugin`; co-signé Opus 4.5. |
| `c67b1ad` | 2026-02-01 | Fusion de la PR #17. |
| `6077083` | 2026-02-01 | Fusion de la PR #7 et de ses exemples. |
| `b26f4c3` | 2026-01-31 | Corrige le chemin du skill et modifie l'installation ; co-signé Opus 4.5. |
| `3cf049f` | 2026-01-31 | Ajoute la marketplace et passe à une installation en deux étapes ; co-signé Opus 4.5. |
| `68b67a5` | 2026-01-31 | Corrige encore le schéma du manifeste et le répertoire du skill ; co-signé Opus 4.5. |
| `aa4467f` | 2026-02-16 | Fusion de la PR #18 et des trois corrections précédentes. |
| `0c78745` | 2026-04-13 | Commit de branche : option Multica. |
| `884ffab` | 2026-04-14 | Commit de branche : lien Multica en tête. |
| `fb8fdb0` | 2026-04-14 | Fusion squash de #51 : lien Multica. |
| `9ec6bef` | 2026-04-16 | Ajuste le README. |
| `331a3ac` | 2026-04-16 | Ajoute des liens projet/réseaux sociaux. |
| `c9a44ae` | 2026-04-16 | Ajuste de nouveau ces liens. |
| `fcd5d36` | 2026-04-19 | Fusion de #93 : traduction chinoise. |
| `fb7a22c` | 2026-04-18 | Fusion de #92 : support Cursor. |
| `2c60614` | 2026-04-20 | Fusion de #95 : synchronise la traduction avec Cursor. |

Dix commits portent un trailer Claude : neuf `Claude Opus 4.5` et un `Claude Haiku 4.5`. Un trailer documente une co-rédaction déclarée, pas la proportion exacte de texte produite par le modèle.

Les pivots sémantiques sont la création (`8462496`), la correction de provenance (#1), l'expansion doctrinale (#2), le packaging skill (#3), les exemples (#7), la séquence de quatre PR pour le plugin (#13, #15, #17, #18), puis Cursor (#92/#95). Le reste modifie promotion, liens ou traduction.

## Branches, tags et releases

| Branche distante | Tête | Relation utile |
|---|---|---|
| `main` | `2c606141936f1eeef17fa3043a72095b4765b9c2` | Snapshot audité. |
| `add-multica-link` | `0c78745f4bc956c603423aefab7e63b223d8f295` | Ancienne branche de #51. |
| `add-multica-link-top` | `884ffab4797a7d2b53d09142734aee3c1c849f0a` | Ancienne branche de #51. |
| `docs/expand-readme-content` | `24eb5e2bb2fa934914dcc215ddf8d5b8b2140267` | Branche de #2. |
| `forrestchang/fix-readme-links` | `adc91eb4f4d64dcfd12a9fc2a9531870e0744986` | Branche de #15. |

Il n'existe aucun tag et aucune release GitHub au 2026-07-20. Le repository a été créé sous une identité historique `forrestchang`, a momentanément reçu des URLs `jiayuan7`, puis est aujourd'hui possédé par `multica-ai`. Le snapshot continue à utiliser des URLs `forrestchang` qui redirigent ; la date exacte du transfert n'est pas établie.

## Inventaire des pull requests

Toutes les 147 PR ont été énumérées avec leur état, fichiers modifiés, compte de commits, commentaires, reviews et checks ; les patches et discussions affectant sens, distribution, compatibilité, évaluation, licence ou provenance ont été lus. Aucun check n'était attaché aux PR prioritaires inspectées et `main` ne contient pas de workflow CI.

- Fusionnées (12) : #1, #2, #3, #7, #13, #15, #17, #18, #51, #92, #93, #95.
- Fermées sans fusion (39) : #8, #19, #24, #26, #27, #37, #41, #47, #49, #50, #85, #88, #91, #94, #106, #107, #108, #111, #112, #115, #116, #125, #128, #132, #134, #135, #137, #145, #146, #147, #148, #151, #160, #165, #171, #173, #178, #182, #183.
- Ouvertes (96) : #25, #28, #29, #30, #33, #35, #38, #39, #43, #44, #54, #55, #57, #62, #63, #64, #66, #68, #78, #82, #83, #84, #86, #87, #89, #90, #96, #97, #98, #99, #100, #101, #102, #103, #104, #105, #109, #110, #113, #114, #117, #118, #119, #120, #121, #122, #123, #124, #126, #127, #129, #130, #131, #133, #136, #138, #139, #140, #141, #142, #143, #144, #149, #150, #152, #153, #154, #155, #156, #157, #158, #159, #161, #162, #163, #164, #166, #167, #168, #169, #170, #172, #174, #175, #176, #177, #179, #180, #181, #184, #185, #186, #187, #188, #189, #190.

### PR qui changent l'interprétation

| PR | État au 2026-07-20 | Portée et conclusion d'audit |
|---|---|---|
| [#1](https://github.com/multica-ai/andrej-karpathy-skills/pull/1) | Fusionnée | Corrige la publication X de vibe coding vers les notes de coding ; changement de provenance matériel. |
| [#2](https://github.com/multica-ai/andrej-karpathy-skills/pull/2) | Fusionnée | Développe les règles, indicateurs et compromis ; texte co-rédigé avec Opus 4.5. |
| [#3](https://github.com/multica-ai/andrej-karpathy-skills/pull/3) | Fusionnée | Rend le skill installable via l'écosystème `skills`; ne démontre pas son effet. |
| [#7](https://github.com/multica-ai/andrej-karpathy-skills/pull/7) | Fusionnée | Ajoute 522 lignes d'exemples documentaires non chargées par le runtime. |
| [#13](https://github.com/multica-ai/andrej-karpathy-skills/pull/13), [#15](https://github.com/multica-ai/andrej-karpathy-skills/pull/15), [#17](https://github.com/multica-ai/andrej-karpathy-skills/pull/17), [#18](https://github.com/multica-ai/andrej-karpathy-skills/pull/18) | Fusionnées | Quatre étapes nécessaires pour réparer commande, propriétaire, emplacement, marketplace, chemin et schéma Claude. |
| [#25](https://github.com/multica-ai/andrej-karpathy-skills/pull/25) | Ouverte | Revendique 84→96 de découvrabilité ; fournit un PNG binaire de 68 558 octets (blob `f11a9d7…`) et un JSON de 136 octets, sans protocole reproductible. |
| [#26](https://github.com/multica-ai/andrej-karpathy-skills/pull/26), [#27](https://github.com/multica-ai/andrej-karpathy-skills/pull/27) | Fermées sans fusion | Principes additionnels sécurité/docs ; ne font pas partie du snapshot. #27 a été retirée par son auteur. |
| [#28](https://github.com/multica-ai/andrej-karpathy-skills/pull/28) | Ouverte | Regroupe principes additionnels et nouveaux packagings ; proposition, pas `main`. |
| [#38](https://github.com/multica-ai/andrej-karpathy-skills/pull/38) | Ouverte | Adaptateur GitHub Copilot ; questions non résolues sur chargement et écrasement. |
| [#41](https://github.com/multica-ai/andrej-karpathy-skills/pull/41) | Fermée sans fusion | Corrige `claude plugins` vers la forme CLI actuelle singulière et ajoute des tests statiques. |
| [#44](https://github.com/multica-ai/andrej-karpathy-skills/pull/44) | Ouverte | Ajoute une règle de complétude vérifiée ; utile conceptuellement, mais universalise lint/typecheck/build. |
| [#47](https://github.com/multica-ai/andrej-karpathy-skills/pull/47) | Fermée sans fusion | Propose un vrai `LICENSE` MIT ; absent de `main`. |
| [#54](https://github.com/multica-ai/andrej-karpathy-skills/pull/54) | Ouverte | Ajoute environ 220 lignes de hooks JS « d'enforcement » ; heuristiques fail-open, exécutables, non évaluées. |
| [#55](https://github.com/multica-ai/andrej-karpathy-skills/pull/55) | Ouverte | CI/stale automation ; absente du snapshot. |
| [#84](https://github.com/multica-ai/andrej-karpathy-skills/pull/84), [#98](https://github.com/multica-ai/andrej-karpathy-skills/pull/98) | Ouvertes | Réparent/documentent `npx skills`; ne changent pas le comportement de `main`. |
| [#88](https://github.com/multica-ai/andrej-karpathy-skills/pull/88) | Fermée sans fusion | Développe les exemples et leur chargement supposé ; pas de preuve runtime. |
| [#92](https://github.com/multica-ai/andrej-karpathy-skills/pull/92), [#95](https://github.com/multica-ai/andrej-karpathy-skills/pull/95) | Fusionnées | Ajoutent la règle Cursor always-on puis la traduction. |
| [#96](https://github.com/multica-ai/andrej-karpathy-skills/pull/96) | Ouverte | Plugin OpenCode JS, installation npm depuis Git non épinglé et injection intégrale automatique au premier message. Intrusif et fondé sur un hook non documenté actuellement. |
| [#97](https://github.com/multica-ai/andrej-karpathy-skills/pull/97) | Ouverte | Adaptateur Codex valide dans son idée (`AGENTS.md` + `.agents/skills`) mais ajoute 1 257 lignes et plusieurs copies. |
| [#136](https://github.com/multica-ai/andrej-karpathy-skills/pull/136) | Ouverte | Signale que le champ `skills` du manifeste ajoute au scan par défaut et peut dupliquer l'enregistrement. |
| [#141](https://github.com/multica-ai/andrej-karpathy-skills/pull/141) | Ouverte | Propose de rapprocher le texte de la source ; confirme implicitement que `main` est une adaptation. |
| [#156](https://github.com/multica-ai/andrej-karpathy-skills/pull/156) | Ouverte | Nouveau `LICENSE` MIT, avec titulaire proposé mais non confirmé. |
| [#168](https://github.com/multica-ai/andrej-karpathy-skills/pull/168), [#169](https://github.com/multica-ai/andrej-karpathy-skills/pull/169) | Ouvertes | Garde-fous simplicité/sécurité et fallback non interactif ; montrent des limites des formulations absolues. |
| [#183](https://github.com/multica-ai/andrej-karpathy-skills/pull/183) | Fermée sans fusion | Proposait vérification sans tests et déclaration honnête ; absent de `main`. |
| [#186](https://github.com/multica-ai/andrej-karpathy-skills/pull/186) | Ouverte | Benchmark expérimental étroit, 3 tâches et 30 appels par dataset ; réécrit aussi fortement le contenu. |
| [#188](https://github.com/multica-ai/andrej-karpathy-skills/pull/188) | Ouverte | Propose des auto-checks supplémentaires. |
| [#189](https://github.com/multica-ai/andrej-karpathy-skills/pull/189) | Ouverte | Corrige les URLs vers le propriétaire actuel et note que les anciennes redirigent encore. |

## Matrice de statut des idées

| Élément | Snapshot | Historique seulement | PR ouverte | Fermé/rejeté | Revendiqué non démontré |
|---|:---:|:---:|:---:|:---:|:---:|
| Quatre principes | oui | — | reformulations | — | efficacité |
| Exemples | oui | — | extensions | — | chargement runtime |
| Plugin Claude | oui | anciens manifests cassés | réparations supplémentaires | correction CLI #41 | installation exacte selon version |
| Cursor `alwaysApply` | oui | — | — | — | efficacité |
| Licence MIT complète | non | — | #156 | #47/#107 | propriétaire |
| Support Codex | non | — | #97 et variantes | certaines variantes | efficacité/maintenance |
| Support OpenCode | non | — | #66/#96 et variantes | — | hook #96, efficacité Qwen |
| Hooks d'enforcement | non | — | #54 | — | enforcement réel |
| Discoverability 84→96 | non | — | #25 | — | protocole/données |
| Benchmark comportemental | non | — | #186 | — | généralisation au snapshot |

## Source canonique et duplications

Il n'existe pas de source canonique déclarée ni de mécanisme de génération. Le README demande aux contributeurs de maintenir synchronisés `CLAUDE.md`, `SKILL.md` et la règle Cursor, ce qui reconnaît la duplication sans la résoudre.

Après retrait du frontmatter et des titres, `CLAUDE.md` et la règle Cursor partagent le même cœur de 2 395 caractères ; `SKILL.md` conserve une introduction de provenance et omet le footer de critères observables. Un diff `CLAUDE.md`/`SKILL.md` compte 8 lignes ajoutées et 6 retirées ; `CLAUDE.md`/Cursor, 6 ajoutées et 1 retirée. La source historique est `CLAUDE.md`, mais « première copie » n'équivaut pas à « canonique maintenue ». La duplication disque n'entraîne une duplication de contexte que si plusieurs surfaces sont chargées dans une même session.
