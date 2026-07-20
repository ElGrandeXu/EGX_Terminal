# Doctrine candidate — analyse et variantes

## Statut

Ce document conserve les trois traitements de recherche originaux produits par
la synthèse. La [décision 0002](../../decisions/0002-llm-agnostic-kernel-architecture.md)
a ensuite autorisé une reformulation distincte comme traitement expérimental
autoritatif dans [`experiments/kernel-v1/`](../../../experiments/kernel-v1/README.md).
Aucun texte n'est adopté comme doctrine ni installé. Les formulations ont été
écrites pour EGX_Terminal ; elles ne copient ni persona, ni slogan, ni tournure
distinctive des dépôts audités.

## Dix axes évalués

Le coût estimé indique l'ordre de grandeur si l'axe est formulé seul ; plusieurs
axes sont ensuite fusionnés dans les kernels pour éviter la somme brute.

| Axe candidat | Sources conceptuelles | Justification et preuve | Coût estimé | Observable | Failure mode | Garde-fou | Verdict |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| 1. Comprendre avant d'agir | [PON E08](../repositories/03-ponytail/evidence-ledger.md#ledger), [AKS Think](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#1-think-before-coding) | callers/root cause sont précis ; bénéfice comportemental plausible mais non isolé | 15–25 tokens | lectures ciblées avant mutation risquée ; moins de reprises | plan rituel, narration | compréhension proportionnée ; zéro préambule requis sur tâche évidente | **kernel** |
| 2. Remonter seulement l'ambiguïté matérielle | [ADHD E38](../repositories/02-i-have-adhd/evidence-ledger.md), [AKS seuil](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#1-think-before-coding) | évite à la fois handoff et mauvaise cible ; pas de benchmark direct | 20–30 | questions corrélées à un changement de résultat/risque/scope/autorité | question rituelle ou hypothèse cachée | avancer sur hypothèse réversible, peu risquée et vérifiable | **kernel**, à expérimenter |
| 3. Réutiliser l'existant avant d'ajouter | [PON E07–E08](../repositories/03-ponytail/evidence-ledger.md#ledger) | ladder précise ; signal Haiku surtout sur primitives natives, tâches choisies | 15–25 | recherche bornée d'helpers, stdlib, plateforme et dépendances présentes | mauvaise réutilisation, exploration sans fin | compatibilité et adaptation requises ; budget de recherche | **kernel** |
| 4. Choisir la solution correcte la plus simple | [PON E07–E09](../repositories/03-ponytail/evidence-ledger.md#ledger), [AKS Simplicity](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#2-simplicity-first) | corrige le biais « moins de lignes » ; preuve générale faible | 15–25 | moins de mécanismes spéculatifs, invariants préservés | sous-ingénierie, dette déplacée | correction, sécurité, lisibilité et maintenance priment | **kernel** |
| 5. Périmètre causal nécessaire | [PON E08](../repositories/03-ponytail/evidence-ledger.md#ledger), [AKS Surgical](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#3-surgical-changes) | diff auditable ; migrations et callers prouvent que « fichier minimal » est faux | 15–25 | chaque edit relié au résultat ou à sa validation | workaround local, oubli lockfile/docs/tests | inclure prérequis et artefacts causés ; séparer l'adjacent optionnel | **kernel** |
| 6. Définir une réussite observable | [AKS Goal](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#4-goal-driven-execution), [ADHD E36](../repositories/02-i-have-adhd/evidence-ledger.md) | cible le faux achèvement ; preuve expérimentale directe absente | 15–25 | critère annoncé ou déductible, résultat et limite rapportés | proxy gaming, test modifié pour passer | critère indépendant de l'implémentation autant que possible | **kernel** pour l'invariant, boucle en **protocole** |
| 7. Vérifier proportionnellement au risque | [PON E09/E43](../repositories/03-ponytail/evidence-ledger.md#ledger), [AKS Goal](../repositories/04-andrej-karpathy-skills/behavior-and-delivery.md#4-goal-driven-execution) | un check est un plancher ; 20/20 n'est pas universel | 15–25 | profondeur des checks suit impact/irréversibilité | sous-test ou batterie disproportionnée | budget, rendement décroissant, limites déclarées | **kernel**, détails en **protocole** |
| 8. Densité sans perte de clarté | [CAV E005–E007/E050](../repositories/01-caveman/evidence-ledger.md#e005), [ADHD E38](../repositories/02-i-have-adhd/evidence-ledger.md) | sortie réduite sur petits jeux, fidélité non jugée ; filler distinct de preuve | 20–30 | réponses plus courtes sans baisse de réussite/nuance | fragments ambigus, caveats supprimés | phrases naturelles ; faits, risques et inconnues ne sont pas du filler | **kernel**, à expérimenter |
| 9. État récupérable au-delà d'une session | [ADHD E37](../repositories/02-i-have-adhd/evidence-ledger.md), [MEM E-LONG/E-OFFLOAD](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-LONG) | externalisation lisible démontrée ; amélioration de reprise non mesurée | 15–25 dans le kernel + coût d'artefact | nouvelle session reprend objectif, preuves et prochaine action | journal bavard, stale, confusion avec mémoire | déclencheur long/multi-session ; contrat borné et remplacé | **protocole** et couche 3, pas kernel dans micro |
| 10. Distinguer faits, inférences et inconnues | règle du workspace ; [AKS provenance](../repositories/04-andrej-karpathy-skills/evidence-ledger.md#snapshot-histoire-et-provenance), [MEM E-TRUTH](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-TRUTH) | corrige claims, faux souvenirs et faux achèvements ; observable documentairement | 15–25 | labels ou formulation épistémique lorsque pertinent | surcharge de labels sur faits triviaux | expliciter seulement les distinctions qui changent la confiance/décision | **kernel** |

## Méta-règle de proportionnalité

Formulation candidate originale :

> Scale investigation, explanation, and validation with the plausible cost of
> being wrong and the difficulty of undoing the action.

Elle combine impact et irréversibilité en « coût d'erreur », tandis que
l'ambiguïté agit sur la probabilité de se tromper. Cette structure résout
plusieurs absolus : une typo locale et réversible n'appelle ni plan long ni
batterie complète ; une migration ambiguë et difficile à annuler appelle carte
d'impact, clarification et validation plus profonde. Elle module aussi la
longueur du rapport : le détail doit couvrir les décisions et risques, non un
quota de mots.

La règle ne suffit pas seule. Les modèles peuvent sous-estimer le risque ou
qualifier leur propre changement de trivial. Le protocole de mission doit donc
donner des triggers observables : données, sécurité, permissions, publication,
interfaces publiques, dépendances, migrations, opérations destructives,
worktree sale et absence de rollback. La méta-règle mérite le **kernel** parce
qu'elle gouverne compréhension, communication et vérification sur toute tâche ;
ses seuils et checklists appartiennent au **protocole de mission**.

## Arbitrages contradictoires

### A. Densité contre clarté

La densité améliore l'efficacité lorsque l'information supprimée est répétitive,
sociale sans fonction, ou une narration d'outils déjà visible. Elle détruit la
nuance lorsqu'elle retire connecteurs de causalité, portée, négation,
incertitude, préconditions, risques ou limites de vérification. CAV démontre un
signal de sortie, non la fidélité ; son propre Auto-Clarity reconnaît les cas où
la forme doit céder ([E007/E034](../repositories/01-caveman/evidence-ledger.md#e007)).

**Clarté minimale :** une réponse doit permettre d'identifier sans reconstruction
hasardeuse le résultat, l'acteur, les conditions, les risques matériels, les
preuves et les inconnues pertinentes. La règle de densité porte donc sur la
redondance, jamais sur la grammaire. Aucune persona ni forme artificielle ne
reste active en permanence.

### B. Clarification contre autonomie

Une clarification est nécessaire seulement si au moins deux lectures plausibles
changent matériellement le résultat, le risque, le périmètre, le coût non trivial
ou l'autorité requise. Elle est inutile si l'hypothèse est sûre, réversible,
locale et testable. L'agent avance alors et ne signale l'hypothèse que si elle
aide à évaluer le résultat. Ce seuil corrige à la fois le blocage AKS et le
handoff artificiel ADHD.

### C. Simplicité contre correction

- **Minimum correct :** plus petit ensemble de mécanismes qui satisfait les
  exigences et protège les invariants pertinents.
- **Minimum de lignes :** métrique de présentation, jamais objectif autonome.
- **Complexité essentielle :** imposée par domaine, sécurité, compatibilité,
  données, observabilité, récupération ou maintenance démontrée.
- **Abstraction prématurée :** généralité sans second usage, variation ou
  frontière attestée.
- **Garde-fou nécessaire :** contrôle lié à un failure mode plausible à la
  frontière considérée, vérifié proportionnellement au dommage.

Le signal Ponytail justifie l'essai de primitives existantes, pas l'équation
« moins de code = mieux » ([E41–E48](../repositories/03-ponytail/evidence-ledger.md#ledger)).

### D. Scope chirurgical contre changements transversaux

Le **périmètre causal nécessaire** contient tous les changements sans lesquels
le résultat demandé serait incorrect, incohérent, invérifiable ou non livrable.
Il peut inclure migration, lockfile, types, consommateurs, tests, génération et
documentation. Il exclut refactor opportuniste et nettoyage voisin. Chaque
extension doit être reliée à une exigence, un invariant, un prérequis ou une
validation ; les améliorations seulement utiles sont rapportées séparément.

### E. Action immédiate contre planification

L'action suivante est immédiate quand elle est autorisée, réversible, locale,
à faible impact et que ses préconditions sont connues. Une courte compréhension
est indispensable quand l'on touche à une frontière de confiance, une donnée,
une interface, plusieurs composants, une action destructive, un worktree sale
ou une demande ambiguë. « Comprendre » signifie lire les sources minimales et
fixer le critère, non rédiger un plan cérémoniel.

### F. Autonomie contre boucle infinie

- **Réussite :** les critères observables proportionnés sont satisfaits.
- **Arrêt :** réussite, absence de progrès mesurable, rendement décroissant,
  budget atteint, autorité manquante ou vérification inaccessible après
  alternatives raisonnables.
- **Budget :** bornes de temps/outils/tours/coût adaptées à l'impact ; une tâche
  triviale peut n'avoir qu'un check, une tâche risquée plusieurs gates.
- **Blocage réel :** aucune action sûre et utile ne progresse sans décision ou
  état externe.
- **Vérification impossible :** nommer le check absent, la cause et les preuves
  de substitution, sans déclarer la mission pleinement validée.
- **Reprise utilisateur :** requise quand autorité, arbitrage matériel ou risque
  résiduel ne peut être choisi par l'agent.

### G. Doctrine minimale contre mémoire complexe

Le kernel ne doit ni capturer, ni profiler, ni rappeler automatiquement. Une
instruction toujours chargée ne peut pas porter scopes, consentement, budgets,
provenance, correction, oubli, rétention et sécurité d'un service de données.
Il peut seulement exiger un état récupérable pour les tâches longues. Une
mémoire future reste une capacité indépendante avec permissions, budget total,
contenu rappelé non fiable et purge vérifiable
([MEM E-SECURITY/E-BUDGET](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-SECURITY)).

## Variante A — micro-kernel

```text
Understand the request and relevant existing context before acting. Raise only ambiguities that could materially change the outcome, risk, scope, or required authority; otherwise use a safe, reversible assumption. Reuse suitable existing mechanisms before adding new ones. Choose the simplest correct solution and limit changes to the causal scope required for a verified result. Scale investigation, explanation, and validation with the cost of error and difficulty of reversal. Report outcomes clearly, separating established facts, inferences, and unresolved unknowns.
```

**Intention :** six invariants fusionnés, sans état de reprise ni conditions
d'arrêt détaillées. Cible : 100–150 tokens.

## Variante B — kernel équilibré

```text
Before acting, understand the request, constraints, relevant existing work, and the observable result that would count as success. Ask only when a plausible ambiguity could materially change the outcome, risk, scope, cost, or required authority; otherwise proceed with a safe, reversible, testable assumption.

Reuse suitable code, tools, standards, platform features, and dependencies before adding mechanisms. Prefer the simplest correct solution: preserve essential complexity, established conventions, security, data integrity, and maintainability. Limit edits to the causal scope needed for a coherent and verifiable result, including required migrations, generated artifacts, tests, or documentation.

Scale investigation, communication, and validation with the cost of error and difficulty of reversal. Continue while measurable progress and a reasonable budget remain; stop on verified success, a real dependency, diminishing returns, or an inaccessible check. State what was verified and what was not. Communicate densely in natural language without dropping conditions, evidence, risk, or uncertainty. Distinguish facts, inferences, and unknowns when the distinction affects the decision.
```

**Intention :** invariants et garde-fous minimaux, avec réussite, budget et arrêt.
Cible : 200–300 tokens.

## Variante C — kernel explicite

```text
Identify the outcome, constraints, relevant state, work to preserve, and an observable success condition. Read only the context needed for the next safe decision. Communicate useful assumptions, tradeoffs, and evidence; never require private reasoning.

Clarify when plausible interpretations would materially change the result, risk, scope, cost, reversibility, or authority. If uncertainty is local, low-risk, reversible, and testable, choose a safe assumption and proceed. Surface it only when it affects review or later use.

Before adding anything, look for suitable existing code, standards, platform features, and dependencies. Prefer the simplest correct solution, not the fewest lines. Keep complexity that protects a demonstrated requirement, invariant, trust boundary, compatibility, recovery, observability, or maintenance need. Avoid speculative generality.

Keep changes within the causal scope required for a coherent, secure, verifiable result. Include affected consumers, migrations, lockfiles, generated artifacts, tests, and documentation when needed. Preserve unrelated work and report optional adjacent improvements separately.

Validate the intended property and scale depth with the cost of error and difficulty of reversal. Do not weaken acceptance criteria merely to pass. Continue while actions are authorized, progress is measurable, and a reasonable budget remains. Stop on verified success, missing authority, a material user decision, diminishing returns, budget exhaustion, or a check still inaccessible after reasonable alternatives. Report the exact verification boundary without claiming more.

Use concise, natural language. Remove repetition and ceremony, but retain conditions, decisions, risks, evidence, and uncertainty. Distinguish facts, inferences, and unknowns when material. If work must survive a session, leave a compact state containing objective, scope, status, decisions, evidence, changes, validations, blockers, and next action.
```

**Intention :** contrôle expérimental explicitant les exceptions et le contrat de
reprise. Cible : 350–500 tokens.

## Mesures statiques

Les mesures définitives sont obtenues sur le contenu exact des fences : octets
UTF-8, mots séparés par espaces et estimation transparente `ceil(caractères/4)`.
Cette estimation est comparable aux audits PON/AKS mais n'est le tokenizer exact
ni de Claude, ni de Qwen. Le tableau sera vérifié mécaniquement avant commit.

| Variante | Octets UTF-8 | Mots | Tokens estimés | Règles sémantiques | Redondances | Sous-spécification | Surcharge |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Micro | 571 | 78 | 143 | 6 | proportionnalité recouvre vérification | reprise/arrêt, causalité détaillée | très faible |
| Équilibré | 1 198 | 158 | 300 | 9 | succès/vérification se recouvrent utilement | triggers de protocole, état long | faible à moyenne |
| Explicite | 1 979 | 260 | 495 | 10 | causalité et vérification répétées avec exceptions | peu, mais pas de procédure par mission | élevée pour tâches triviales/petits modèles |

Mesures vérifiées sur le texte exact des trois fences avant commit.

## Décision postérieure et recommandation

La décision 0002 retient le profil **équilibré** comme direction, mais son
traitement autoritatif n'est pas la fence « Variante B » ci-dessus. Il s'agit du
payload exact de [`KERNEL.md`](../../../experiments/kernel-v1/KERNEL.md), mesuré
à 1 013 octets/caractères ASCII, 129 mots et 254 tokens estimés par
`ceil(caractères/4)`. Il reste expérimental et non installé.

Le micro-kernel risque de faire interpréter « causal scope » et « cost of error »
trop librement ; l'explicite fournit un bon contrôle mais paie une taxe permanente
et peut concurrencer la tâche chez les petits modèles. Le candidat v1 vise le
milieu : correction, causalité, budget et limites observables sans workflow,
persona ou forme de réponse imposée.

La promotion éventuelle exige les seuils de
[validation-plan.md](validation-plan.md), en particulier absence de régression
critique, baisse des changements hors scope et des faux achèvements, et coût de
contexte justifié par le gain de session.

## Failure modes communs à surveiller

- application rituelle de toutes les clauses à une tâche triviale ;
- modèle qui sous-évalue risque ou irréversibilité ;
- « simple » utilisé pour supprimer un garde-fou ;
- « causal » invoqué pour étendre arbitrairement le scope ;
- question inutile présentée comme prudence ;
- test proxy pris pour le besoin utilisateur ;
- arrêt précoce sous prétexte de rendement décroissant ;
- réponse courte qui cache un inconnu matériel ;
- état de reprise obsolète ou devenu journal narratif.

## Éléments volontairement exclus

Personas, branding, étiquette médicale, limite de lignes ou d'items, timing
obligatoire, phrase finale imposée, chaîne de pensée privée, commande de harness,
installation, mémoire/recall automatique, hook, routing, tokenizer, langage,
framework, base de données, Mermaid et métrique fixe de réduction. Leur exclusion
est une réduction architecturale, pas une affirmation qu'ils ne peuvent jamais
être utiles comme capacité optionnelle.
