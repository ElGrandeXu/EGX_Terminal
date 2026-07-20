# 0002 — Architecture du kernel LLM-agnostique

- **Status:** accepted
- **Date:** 2026-07-20
- **Behavioral activation:** none

## Contexte

Les cinq audits indépendants et leur synthèse ont produit une architecture
candidate, trois traitements de kernel et un plan de validation. Le bootstrap
racine reste actif, mais son nom et son contenu ne doivent pas devenir par défaut
la doctrine stable d'un workspace qui vise Codex CLI, Claude Code, OpenCode et
les modèles transmis par ces harnesses.

Cette décision fixe les frontières et la direction de distribution. Elle ne
prouve pas l'efficacité comportementale du kernel candidat, ne le promeut pas et
ne modifie aucun point d'entrée actuellement chargé.

## Décision

### Six couches fonctionnelles

Chaque mécanisme reçoit une couche fonctionnelle principale :

1. **Kernel comportemental :** invariants courts, neutres et utiles dans presque
   toute mission ; aucun workflow, état, outil ou nom de fournisseur.
2. **Protocoles de mission :** procédures conditionnelles selon le type de tâche,
   son risque et sa réversibilité ; aucun chargement permanent par défaut.
3. **État récupérable :** artefact compact et borné permettant la reprise d'une
   mission ; distinct d'une mémoire utilisateur ou de workspace.
4. **Capacités optionnelles :** outils, évaluateurs, hooks, skills ou autres
   mécanismes activables seulement après justification et décision.
5. **Adaptateurs de harness :** traduction de la source neutre vers la découverte,
   le scope et la précédence propres à chaque harness ; aucune doctrine propre.
6. **Infrastructure mémoire éventuelle :** capture, dérivation, recherche,
   provenance, correction, oubli et export ; service séparé, non requis.

Les rejets, quarantaines, limitations, critères de promotion et critères de
retrait forment un **périmètre de gouvernance externe**. Ils contrôlent les six
couches sans constituer une septième couche fonctionnelle.

### Proportionnalité

La profondeur d'investigation, de communication et de validation dépend du coût
plausible d'une erreur et de la difficulté d'annuler l'action. Les protocoles de
mission pourront préciser des déclencheurs observables ; le kernel ne doit pas
porter leurs checklists.

### État récupérable

Le contrat sémantique décrit dans la synthèse est accepté comme mécanisme séparé
et conditionnel. Il n'est ni injecté intégralement dans le payload always-on, ni
implémenté par cette décision. Son chemin, son budget et son cycle de vie concret
restent à décider avant toute création.

### Kernel expérimental

Le traitement autorisé est le payload original placé dans
[`experiments/kernel-v1/KERNEL.md`](../../experiments/kernel-v1/KERNEL.md). Son
statut est **expérimental, inactif et non promu**. Il reformule les principes de
la synthèse sans reprendre le texte des repositories audités. Il ne remplace ni
ne modifie `AGENTS.md`, et aucun fichier Codex, Claude Code ou OpenCode ne le
charge automatiquement.

### Distribution : B avec fallback C

La direction retenue est :

1. une source sémantique canonique neutre ;
2. un adaptateur mince qui l'inclut quand le harness documente un include fiable ;
3. sinon une copie générée de façon déterministe et vérifiée ;
4. un contrôle de synchronisation visible portant sur contenu, hash, scope et
   risque de double chargement ;
5. aucun bootstrap caché ;
6. en l'absence d'adaptateur, aucune revendication de chargement automatique de
   la source neutre.

Le chemin stable recommandé pour une future revue est `doctrine/KERNEL.md` : il
est fournisseur-neutre, explicite sur sa fonction et extérieur au répertoire
expérimental. Ce chemin n'est pas créé par cette décision.

### Budget

- Le payload always-on a un plafond strict de **300 tokens estimés**.
- La cible souhaitée est d'environ **250 tokens estimés**.
- La méthode comparable et transparente est
  `ceil(nombre de caractères / 4)` ; elle n'est le tokenizer exact d'aucun
  modèle.
- Métadonnées, wrappers et adaptateurs sont mesurés et rapportés séparément du
  payload.

Le candidat v1 mesure 1 013 caractères ASCII et 254 tokens estimés. Les valeurs
et son SHA-256 sont calculés dans son
[`manifest.json`](../../experiments/kernel-v1/manifest.json), pas déduits d'une
estimation éditoriale.

## Éléments de preuve

### Faits documentés

- Codex construit une chaîne depuis `AGENTS.override.md`, `AGENTS.md` et les noms
  de fallback configurés, de la racine du projet vers le répertoire courant ;
  une guidance plus proche apparaît plus tard. Aucun include générique depuis
  `AGENTS.md` n'est documenté dans cette page.
- Claude Code charge `CLAUDE.md`/`CLAUDE.local.md`, permet des imports `@path`
  résolus depuis le fichier importeur et charge les instructions imbriquées selon
  leur portée.
- OpenCode découvre `AGENTS.md`, utilise `CLAUDE.md` comme fallback et accepte des
  fichiers additionnels via `instructions` dans `opencode.json`. Ces instructions
  sont combinées avec `AGENTS.md` ; les références écrites dans `AGENTS.md` ne
  sont pas automatiquement développées.

Sources officielles consultées le **2026-07-20** :

- <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- <https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery>
- <https://code.claude.com/docs/en/memory>
- <https://opencode.ai/docs/rules/>

### Interprétation d'architecture

Claude Code peut recevoir plus tard un adaptateur d'include mince. Codex exige,
en l'absence d'include officiel documenté, une copie générée dans un fichier
découvert. Comme OpenCode découvre aussi `AGENTS.md` et combine ses instructions
configurées avec ce fichier, le même artefact généré pourrait desservir Codex et
OpenCode sans ajouter une seconde injection. Cette topologie reste à vérifier en
runtime avant adoption.

### Inconnues à tester

- contenu exact injecté et ordre effectif avec les versions clientes retenues ;
- comportement de Claude Code au premier import et après compaction ;
- point de départ et sélection du premier fichier local OpenCode dans des
  lancements imbriqués ;
- double chargement OpenCode lorsque `AGENTS.md` et `instructions` désignent une
  sémantique identique ;
- parité sur petits modèles servis par OpenCode. Qwen est un modèle, pas un
  harness, et aucune propriété Qwen n'est affirmée ici.

Le contrat complet est dans
[`adapter-contract.md`](../../experiments/kernel-v1/adapter-contract.md).

## Conséquences

- Les frontières architecturales sont décidées sans activer de comportement.
- Le kernel peut être mesuré, révisé ou supprimé isolément.
- La neutralité réside dans la source sémantique ; les noms et formats de
  fournisseurs restent des adaptateurs remplaçables.
- La génération future ajoute une responsabilité de reproductibilité, de hash et
  de contrôle de drift.
- L'absence d'adaptateur est visible mais signifie que le kernel stable ne sera
  pas chargé automatiquement.
- Le bootstrap actuel demeure la seule instruction repository-owned active ; sa
  migration exige une décision et une mission séparées.

## Capacités différées

Restent hors adoption : mémoire longue durée, auto-recall, compression
sémantique, hooks comportementaux, skills comportementales, routing, personas,
modes de style, patchs de harness, installation et dépendance runtime.

## Garde-fous contre une promotion prématurée

Le candidat ne peut pas être promu tant que tous les points suivants ne sont pas
satisfaits :

1. payload exact, budget et provenance reproductibles ;
2. adaptateurs construits dans un périmètre expérimental, désactivables et sans
   double chargement ;
3. découverte, scope, précédence, contexte injecté et absence d'adaptateur testés
   sur des versions fixées des trois harnesses ;
4. campagne du plan de validation exécutée avec baseline, régressions et coûts
   rapportés par harness et modèle ;
5. seuils de sécurité, réussite, scope et vérification atteints sans claim fondé
   uniquement sur le nombre de tokens ;
6. décision explicite de promotion et plan de migration du bootstrap racine.

## Alternatives rejetées ou différées

- **Canon propre à un fournisseur :** rejeté comme cible stable ; il brouille la
  neutralité sémantique.
- **Copies manuelles :** rejetées ; elles n'offrent pas de preuve de parité.
- **Copie générée partout :** conservée seulement comme fallback lorsque
  l'include n'est pas fiable.
- **Injecteur ou bootstrap caché :** rejeté pour cette architecture ; il ajoute
  runtime, permissions et frontière de confiance.
- **Activation immédiate du candidat :** rejetée ; aucune preuve comportementale
  inter-harness n'existe encore.
- **État récupérable complet dans le kernel :** rejeté ; le coût et le cycle de
  vie sont conditionnels.
- **Septième couche de rejets :** remplacée par une gouvernance externe qui peut
  s'appliquer à chaque couche.

## Déclencheurs de révision

- documentation officielle ou test runtime contredisant le contrat d'adaptateur ;
- impossibilité de garantir un chargement unique et vérifiable ;
- dépassement du plafond ou tokenizer réel révélant un coût disproportionné ;
- régression critique dans la campagne de validation ;
- besoin démontré d'une nouvelle couche fonctionnelle que les six frontières ne
  peuvent pas représenter sans confusion.

## Références internes

- [Synthèse inter-repository](../research/synthesis/README.md)
- [Candidats doctrinaux](../research/synthesis/doctrine-candidates.md)
- [Architecture et frontières](../research/synthesis/architecture-and-boundaries.md)
- [Plan de validation](../research/synthesis/validation-plan.md)
- [Décision du bootstrap](0001-bootstrap-entrypoints.md)
