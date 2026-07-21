# 0005 — Publication de la V1 avec une racine neutre

- **Status:** accepted
- **Date:** 2026-07-21
- **Behavioral activation:** none

## Contexte

Le bootstrap provisoire de la [décision 0001](0001-bootstrap-entrypoints.md)
exposait des instructions racine automatiquement découvertes par Codex et Claude
Code pendant la recherche. Depuis, les cinq audits, la synthèse architecturale et
les deux campagnes doctrinales sont terminés. La V1 doit maintenant préparer sa
distribution publique sans transformer un bootstrap historique ou un candidat
rejeté en politique permanente.

Une racine neutre signifie que le repository cloné n'impose automatiquement
aucun payload comportemental à un harness compatible. Les principes de projet
restent consultables et les protocoles peuvent être choisis volontairement.

## Preuves prises en compte

### Faits observés

- La [décision 0003](0003-balanced-kernel-rejection.md) classe le kernel équilibré
  **`REJECTED_AS_BALANCED`** après zéro victoire primaire observée et deux
  victoires de la baseline sur les cinq paires complètes.
- La [décision 0004](0004-micro-kernel-final-evaluation.md) classe le micro-kernel
  **`REJECT_MICRO`**. La baseline a consommé 229 923 tokens et le micro 247 972,
  soit **7,850019354305572 %** d'overhead, au-dessus du plafond pré-enregistré de
  5 %.
- Les deux décisions interdisent leur promotion comme doctrine V1. La décision
  0004 clôt aussi toute troisième variante et toute nouvelle campagne doctrinale
  pour la V1.
- Avant cette décision, `AGENTS.md` racine contenait le bootstrap commun et
  `CLAUDE.md` ne contenait que son import. `AGENTS.override.md`, `opencode.json` et
  `doctrine/KERNEL.md` étaient absents.

### Interprétation de projet

Les principes documentés restent utiles, mais les expériences ne démontrent pas
qu'un payload always-on améliore suffisamment le comportement pour justifier son
coût. Retirer les points d'entrée automatiques sépare donc les connaissances du
projet de leur activation par un harness et applique les verdicts sans les
réinterpréter.

## Décision

1. La V1 sera publiée avec une racine neutre.
2. Aucun fichier d'instructions automatiquement découvert par Codex, Claude Code,
   OpenCode ou un autre harness n'est livré à la racine. En particulier,
   `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `opencode.json` et
   `doctrine/KERNEL.md` y restent absents.
3. Les principes de conception restent accessibles dans la documentation. Tout
   protocole ou adaptateur futur doit être explicitement opt-in et ne peut pas
   devenir une injection implicite par défaut.
4. Aucune injection cachée n'est autorisée.
5. `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` restent des archives
   expérimentales historiques, immuables et inactives.
6. La question d'une doctrine always-on ne sera pas rouverte pour la V1.
7. Une réouverture ultérieure nécessiterait une nouvelle version, une motivation
   distincte, une décision explicite et de nouvelles preuves. Elle ne modifierait
   ni les verdicts ni l'histoire de la V1.

## Conséquences

- La décision 0001 est superseded : ses deux points d'entrée racine sont retirés
  sans remplacement actif.
- Les six couches et les frontières conceptuelles acceptées par la
  [décision 0002](0002-llm-agnostic-kernel-architecture.md) restent une architecture
  de classement. Aucun kernel ou adaptateur de cette architecture n'est activé.
- Un clone V1 ne reçoit aucune doctrine comportementale repository-owned par
  découverte automatique.
- Utiliser un protocole documenté devient un choix explicite de la mission ou du
  contributeur; l'absence d'adaptateur automatique est intentionnelle.
- Les preuves négatives restent auditables sans modifier les archives.

## Garde-fous

- Un contrôle local, déterministe et sans dépendance externe échoue si l'un des
  cinq chemins interdits réapparaît à la racine.
- Le contrôle cible seulement la racine active; les fixtures et preuves
  historiques imbriquées restent autorisées.
- Toute proposition future d'adaptateur, protocole automatique ou capacité
  avancée exige un besoin démontré, un périmètre opt-in, une décision séparée et
  des critères de retrait.
- Aucun script, configuration ou convention non déclarée ne peut contourner la
  neutralité par injection cachée.

## Éléments explicitement différés

- la réécriture éditoriale complète du README public ;
- le choix de licence ;
- la création du repository GitHub, l'ajout d'un remote et la publication ;
- les adaptateurs opt-in éventuels et leur distribution ;
- la mémoire, les hooks, les skills, le routing, la compression et les autres
  capacités avancées ;
- toute question de doctrine always-on, au minimum jusqu'à une version
  postérieure répondant aux conditions de réouverture ci-dessus.
