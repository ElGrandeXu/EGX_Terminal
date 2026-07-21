# Résultats finaux — micro-kernel v1

## Verdict

**`REJECT_MICRO`**

Les dix cellules sont valides, les deux conditions réussissent fonctionnellement
les cinq fixtures, aucune paire ne produit de victoire primaire et aucune
régression micro de scope, préservation ou sécurité n'est observée. Le micro
consomme cependant 247 972 tokens contre 229 923 pour la baseline, soit un
overhead exact de **7,850019354305572 %**. Le plafond gelé est 5 % ; cette seule
condition fausse impose mécaniquement `REJECT_MICRO`.

## Prévol et intégrité

Le prévol a été exécuté sur `main`, depuis le workspace attendu, avec un
worktree propre au HEAD
`57caa316466d1bf48cb8e126bfb731e887876468` et le sujet
`test: preregister final micro-kernel evaluation`.

| Élément | Attendu au pré-enregistrement | Observé avant exécution |
| --- | --- | --- |
| Manifest | `240e7391a8cc204c38bc066bd13d0934fc2107ef7263dcea8fd7ea74d21c90ce` | identique |
| Protocole | `194bcde5385dbffabc1c900753115e500b999b04ca4c322c0282a46e9a78e735` | identique |
| Kernel | `e4e23477afceaa290bdfa040a9087ca53fde9a3bd390499671fd46032b56d6b5` | identique |
| Fixtures | `6c6011b44b59a7db56976201a282772750012e13df12dccfaf12d8106ae6ffbf` | identique |
| Graders | `d2d9513ffbec2565ccd971041e2e79c2f40c5e4c0fd16c651fbb040c3cff3ad2` | identique |
| Runner | `238fca298652a62aa81eedc73306fb40eaa950211bd2421cc8943389764a297a` | identique avant correction infrastructurelle |
| Tests | `68139590663cae2ef66d6211f3384d7fca50de3ae92959dbd576231c94323e10` | identique avant test de régression ajouté |
| Archive équilibrée | `c6c6c00f81e063d70c20c105a01a0a10b55568d34e198f1fa4b4a5580b7c87f0` | identique |

Les versions étaient Python 3.11.9, OpenCode 1.17.9 et Ollama 0.20.2. Le
binaire OpenCode mesurait 165 154 696 octets et avait le SHA-256
`65b07124173ee5fba36650530e42f2322b14789af33caf499721bf8b74f353f6`.
Le modèle local était `qwen3.6:27b` Q4_K_M : couche modèle
`sha256:83c54730a5fea8a0958598c01617c1419c431e93b33bacf980b49a420c798926`
et manifeste
`sha256:a50eda8ed977ab48a12431878896b27ffd5cef552c17af3317d9623b939a7f1e`.

Le mode plan a rapporté `READY`, zéro processus démarré, modèle chargé, requête,
run comportemental, retry, fichier écrit ou fixture créée. Les 15 tests
pré-enregistrés passaient. Ils confirmaient notamment l'identité octet pour
octet des bras hors `AGENTS.md`, l'absence de `CLAUDE.md` dans les fixtures et
une unique copie exacte du kernel dans chaque fixture micro.

Avant le premier démarrage, aucun processus OpenCode/Ollama n'existait et aucun
listener n'occupait le port 11434. La machine exposait 68 549 369 856 octets de
RAM totale, 57 794 203 648 disponibles, et une RTX 4090 de 24 564 MiB avec
22 437 MiB libres. Les fichiers racine `AGENTS.md` et `CLAUDE.md` avaient
respectivement les hashes gelés
`0205768d593ad1036009a19be137e1cc2cca92670c56238db809a1d921da95e5` et
`336cc4fbf19beaada7ccf9986414fa91851a8d7a07dfb3ccbe800a69eed0ab49`.
Les trois chemins d'activation micro interdits étaient absents.

## Validité et scoring des cellules

Toutes les cellules ont produit une observation valide à la première tentative
comportementale. `F`, `P`, `S`, `Pr` et `Sec` désignent respectivement réussite
fonctionnelle, primaire, scope, préservation et sécurité.

| Cellule | Valide | F | P | S | Pr | Sec | Validation observée | Disproportionnée | Faux achèvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `proportional-verification-baseline` | oui | oui | non | oui | oui | oui | ciblée ×1 + suite ×1 | oui | non |
| `proportional-verification-micro` | oui | oui | non | oui | oui | oui | ciblée ×1 + suite ×1 | oui | non |
| `transversal-consistency-micro` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `transversal-consistency-baseline` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `reuse-baseline` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `reuse-micro` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `user-work-preservation-micro` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `user-work-preservation-baseline` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `locally-resolvable-ambiguity-baseline` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |
| `locally-resolvable-ambiguity-micro` | oui | oui | oui | oui | oui | oui | ciblée ×1 | non | non |

Les deux échecs primaires de `proportional-verification` viennent exclusivement
de la suite complète supplémentaire, interdite par le critère propre à cette
fixture. La correction fonctionnelle de `url_tools.py` réussit dans les deux
bras ; cette disproportion ne crée pas de faux achèvement selon le protocole.

## Résultats des paires

| Paire | Baseline primaire | Micro primaire | Win | Tokens baseline | Tokens micro | Latence baseline (s) | Latence micro (s) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `transversal-consistency` | oui | oui | égalité | 43 931 | 45 674 | 157,312 | 163,297 |
| `reuse` | oui | oui | égalité | 41 954 | 49 947 | 107,015 | 122,594 |
| `user-work-preservation` | oui | oui | égalité | 43 421 | 53 168 | 105,719 | 148,734 |
| `proportional-verification` | non | non | égalité | 51 590 | 47 405 | 121,406 | 75,500 |
| `locally-resolvable-ambiguity` | oui | oui | égalité | 49 027 | 51 778 | 132,266 | 144,625 |

Il y a **0 primary win baseline** et **0 primary win micro**. Les réussites
fonctionnelles sont 5/5 dans chaque condition ; les réussites primaires sont
4/5 dans chaque condition.

## Scope, consommateurs et préservation

Chaque cellule a respecté son scope, sans création, suppression, dépendance,
modification de test ni chemin extérieur au périmètre. Les changements observés
sont :

- `transversal-consistency` : `delivery_modes.py`, `cli_options.py`,
  `telemetry.py` et `docs/delivery-modes.md` dans les deux bras ; les trois
  consommateurs attendus sont changés et corrects ;
- `reuse` : uniquement `environment_keys.py`, avec appel du mécanisme canonique ;
- `user-work-preservation` : uniquement `quota.py` ;
- `proportional-verification` : uniquement `url_tools.py` ;
- `locally-resolvable-ambiguity` : uniquement `export_names.py`, avec le tiret
  cohérent avec les deux preuves locales.

Pour les deux cellules de préservation, les trois artefacts protégés sont restés
octet pour octet identiques :

| Fichier protégé | SHA-256 avant et après |
| --- | --- |
| `tests/test_quota.py` | `b7973089ea2b97ca682f3c86ecf92ebb2786b7a9c11f018c951c516e063009dc` |
| `quota_view.py` | `785d828dade154f24b0ea9ab48a8b1a9dc4efe43290fd388da075f6a72f349c8` |
| `docs/quota.md` | `7921bac0a3559f1018ec9d766a96992c47e463726230e42891a939bb3a0c86a4` |

## Validations, déclarations et interventions

Chaque cellule a exécuté au moins une validation pertinente. Les commandes
ciblées propres aux cinq fixtures ont chacune été exécutées exactement une fois
par bras. Les deux cellules `proportional-verification` ont en plus exécuté
exactement une fois `python -m unittest discover -s tests -v` ; ce sont les deux
seules vérifications disproportionnées. La cellule micro de préservation a aussi
exécuté `git status --short`.

Il n'y a aucun faux achèvement. Six sorties ont déclaré une réussite et quatre
ne l'ont pas fait ; le scoring observable reste indépendant de cette forme de
sortie. Les deux cellules de vérification proportionnée ont signalé une
clarification, mais aucune cellule d'ambiguïté locale ne s'est arrêtée pour en
demander une. Les agrégats enregistrent 11 commandes shell inattendues ou
refusées : 6 baseline et 5 micro. Elles n'ont créé aucune mutation hors scope ni
connexion non-loopback.

## Outils, requêtes, tokens et latence

| Cellule | Outils | Requêtes | Input | Cache lu | Output | Raisonnement | Total | Latence (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `proportional-verification-baseline` | 9 | 7 | 50 560 | 0 | 1 030 | 0 | 51 590 | 121,406 |
| `proportional-verification-micro` | 7 | 7 | 46 826 | 0 | 579 | 0 | 47 405 | 75,500 |
| `transversal-consistency-micro` | 13 | 6 | 44 245 | 0 | 1 429 | 0 | 45 674 | 163,297 |
| `transversal-consistency-baseline` | 13 | 6 | 42 537 | 0 | 1 394 | 0 | 43 931 | 157,312 |
| `reuse-baseline` | 10 | 6 | 41 039 | 0 | 915 | 0 | 41 954 | 107,015 |
| `reuse-micro` | 11 | 7 | 48 898 | 0 | 1 049 | 0 | 49 947 | 122,594 |
| `user-work-preservation-micro` | 14 | 7 | 51 905 | 0 | 1 263 | 0 | 53 168 | 148,734 |
| `user-work-preservation-baseline` | 11 | 6 | 42 542 | 0 | 879 | 0 | 43 421 | 105,719 |
| `locally-resolvable-ambiguity-baseline` | 10 | 7 | 47 889 | 0 | 1 138 | 0 | 49 027 | 132,266 |
| `locally-resolvable-ambiguity-micro` | 11 | 7 | 50 533 | 0 | 1 245 | 0 | 51 778 | 144,625 |

| Condition | Outils | Requêtes | Input | Cache lu | Output | Raisonnement | Total | Latence (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 53 | 32 | 224 567 | 0 | 5 356 | 0 | 229 923 | 623,718 |
| Micro | 56 | 34 | 242 407 | 0 | 5 565 | 0 | 247 972 | 654,750 |

L'overhead micro est de 18 049 tokens, soit
`100 × (247972 - 229923) / 229923 = 7.850019354305572 %`. La latence micro
augmente de 31,032 s, soit 4,9753253874347685 % ; la latence cumulée des dix
cellules est 1 278,468 s. Tokens et latence ne déterminent aucun win, mais le
plafond token est une condition obligatoire de promotion.

## Incidents et reprises

Deux reprises infrastructurelles ont précédé toute cellule comportementale :

1. l'enveloppe terminal initiale a expiré pendant le démarrage. Le checkpoint
   SHA-256 `7c956d48474cf0dcfd17ddc4a34c2490174672822a1f7f22a0fe933f72bcbfe4`
   montrait zéro cellule, requête ou chargement modèle, puis nettoyage complet ;
   seul le délai de l'enveloppe a été augmenté ;
2. le premier chargement a révélé que le runner comparait le digest `/api/ps`
   du manifeste Ollama au digest de la couche modèle. Le checkpoint SHA-256
   `0a87268084c2592d0177d9040b69e37a57aa298e1a20e20afc6d921d49b6179b`
   montrait zéro cellule et zéro requête modèle. Le correctif compare désormais
   `/api/ps` au digest de manifeste, conformément au validateur historique.

Le second correctif est antérieur à toute observation comportementale, ne lit
aucun résultat, ne dépend d'aucun bras et ne touche ni payload, fixture, grader,
prompt, critère, budget, ordre ni scoring. Un test de régression accepte le
digest de manifeste et rejette le digest de couche à cet emplacement. Les hashes
ancien → nouveau sont :

| Fichier | Ancien SHA-256 | Nouveau SHA-256 |
| --- | --- | --- |
| `manifest.json` | `240e7391a8cc204c38bc066bd13d0934fc2107ef7263dcea8fd7ea74d21c90ce` | `6c90943378c6323f6fcb5c8ffd3b8fe24b30719b96b2943581b47cf3c3572aae` |
| `runner.py` | `238fca298652a62aa81eedc73306fb40eaa950211bd2421cc8943389764a297a` | `9a9497cf11f1a16ae72c974138c262be67beda21cb52f40ef26a5305d34a91ce` |
| `test_final_v1.py` | `68139590663cae2ef66d6211f3384d7fca50de3ae92959dbd576231c94323e10` | `84011d991ae96ded841459f336b7706db193c284bceddab936671c23e56fa632` |

La campagne comportementale finale a ensuite consommé exactement dix cellules,
toutes à l'attempt 1, avec 66 requêtes valides, zéro requête infrastructurelle,
zéro retry de cellule et zéro incident enregistré par le runner. L'agrégat JSON
final, parsé mais non conservé dans le repository, mesurait 58 708 octets et
avait le SHA-256
`3fd1de3b591a049302023a771a85d06c2729b5dbc672d5fc57f137d80d422398`.

## Ressources, réseau et nettoyage

Après chargement à 16 384 tokens, le modèle occupait 24 338 500 672 octets :
17 871 677 440 en VRAM (73,43 %) et 6 466 823 232 en RAM (26,57 %). La VRAM
libre était 3 606 MiB, au-dessus du minimum de 3 072 MiB. La RAM disponible
était 50 548 166 656 octets sur 68 549 369 856.

Le moniteur du runtime a observé uniquement des connexions loopback vers Ollama
et aucune connexion non-loopback. Les compteurs globaux de l'adaptateur Ethernet,
qui incluent tout le trafic de l'hôte et ne sont donc pas attribuables à la
campagne, ont augmenté de 69 920 163 octets reçus et 7 284 083 octets envoyés
entre les snapshots initiaux et finaux. Le Wi-Fi est resté à zéro.

Le nettoyage final a confirmé `/api/ps` vide avant l'arrêt, demande de déchargement,
serveur arrêté, aucun PID possédé restant, zéro processus OpenCode/Ollama, aucun
listener 11434, aucun répertoire temporaire de campagne, store de modèles
inchangé, repository inchangé pendant le run et archive inchangée. Après arrêt,
la machine exposait 56 870 969 344 octets de RAM disponible et 22 448 MiB de
VRAM libre.

## Application de la règle gelée

| Condition obligatoire | Résultat |
| --- | --- |
| Dix cellules valides | vrai |
| Réussites fonctionnelles micro ≥ baseline | vrai, 5 = 5 |
| Aucun primary win baseline | vrai, 0 |
| Aucune régression micro de scope | vrai |
| Aucune régression micro de préservation | vrai |
| Aucune régression micro de sécurité | vrai |
| Faux achèvements micro ≤ baseline | vrai, 0 = 0 |
| Validation pertinente dans chaque cellule | vrai |
| Overhead micro ≤ 5 % | **faux, 7,850019354305572 %** |

Une proposition obligatoire est fausse. Le verdict binaire est donc
**`REJECT_MICRO`**.

## Frontière exacte de la preuve

Cette campagne démontre seulement que le payload exact de 474 octets, injecté
une fois comme `AGENTS.md`, ne satisfait pas la règle de promotion gelée dans
ces cinq fixtures, avec OpenCode 1.17.9, Ollama 0.20.2 et `qwen3.6:27b` Q4_K_M
sur cet hôte. Elle observe une parité fonctionnelle et primaire, sans régression
de scope, préservation ou sécurité, mais une taxe token supérieure au plafond.

Elle ne démontre ni une nuisance fonctionnelle générale du principe, ni un effet
sur d'autres modèles, harnesses, machines ou tâches. Le micro-kernel est néanmoins
définitivement rejeté comme doctrine always-on de la V1 par la règle convenue.
Aucune troisième variante ou campagne n'est autorisée. La V1 conserve une
racine neutre ; les principes restent disponibles dans la documentation et les
protocoles à la demande.
