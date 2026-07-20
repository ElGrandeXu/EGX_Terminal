# Matrice contradictoire des signaux

## Méthode et légende

La matrice ne compte pas les votes. Elle pondère mécanisme précis, preuve,
observabilité, portabilité, coûts contextuel et opérationnel, risque, capacité
d'évaluation, dépendance à une persona et provenance juridique. Les catégories
de preuve sont : **forte** (code ou mesure reproductible pertinente), **moyenne**
(mécanisme observé ou petit signal indirect), **faible** (claim, interprétation
ou absence d'expérience), **contradictoire** (signal positif et contre-preuve).

Abréviations de source : [CAV](../repositories/01-caveman/README.md),
[ADHD](../repositories/02-i-have-adhd/README.md),
[PON](../repositories/03-ponytail/README.md),
[AKS](../repositories/04-andrej-karpathy-skills/README.md),
[MEM](../repositories/05-tencentdb-agent-memory/README.md). Les coûts sont des
ordres de grandeur issus des audits, jamais des comptes universels de harness.

## Passe 1 — extraction indépendante normalisée

| Origine | Mécanisme central | Bénéfice supposé | Preuve réelle | Coût / harness | Failure modes | Licence / réutilisation | Candidats, rejets, unknowns |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAV | Instruction de densité, escape de clarté, modes et adaptateurs | Moins de sortie visible | Deux petits jeux Claude montrent un signal ; correction et session totale non jugées | Skill ~1 245 tokens, règle ~163, Claude filtré ~728 + ~34/tour ; adapters épais | ambiguïté, fatigue, surcoût court, drift, compression non fidèle | MIT avec notice ; principes reformulables | candidat : densité neutre/clarité ; rejets : persona, 65 % fixe ; unknowns : Qwen, reasoning, fidélité [E005–E034](../repositories/01-caveman/evidence-ledger.md#e005) |
| ADHD | Dix règles d'action, structure et état dans une skill à large trigger | Diminuer friction d'initiation et charge de reprise | Aucun benchmark ; sources médicales ne valident pas le bundle | Skill ~1 299 tokens, frontmatter ~94, rappel always-on ~39 | handoff au user, omission, faux timing, répétition, framing réducteur | MIT avec notice ; principes neutres reformulables | candidats : ownership, delta d'état ; rejets : étiquette médicale, cinq items, timing ; unknowns : bénéfice, invocation, Qwen [E04–E42](../repositories/02-i-have-adhd/evidence-ledger.md) |
| PON | Ladder besoin→réutilisation→stdlib/native/existant→minimum, rails, injection multi-harness | Éviter over-build et code superflu | Signal Haiku −54,22 % LOC sur tâches choisies ; contre-signal Llama et coûts selon modèle | Payload ~1 307 tokens, ~1 307 par sous-agent ; modes quasi identiques | sous-ingénierie, exploration coûteuse, état/adapters fragiles, reviews biaisées | MIT avec notice | candidats : ladder qualifiée, callers/root cause ; rejets : persona/3 lignes/injection universelle ; unknowns : complétude, Qwen, persona [E07–E54](../repositories/03-ponytail/evidence-ledger.md#ledger) |
| AKS | Quatre principes : comprendre, simplifier, scope, objectif vérifié | Moins de reprises, complexité, bruit et faux achèvements | Aucun benchmark sur `main`; micro-éval en PR non généralisable | ~603–674 tokens always-on/on-demand selon surface | questions rituelles, sous-ingénierie, scope trop local, boucle infinie | Pas de `LICENSE` complet/titulaire au snapshot : texte en quarantaine | candidats conceptuels originaux ; rejets : absolus/CoT/branding ; unknowns : efficacité, licence, petits modèles [ledger](../repositories/04-andrej-karpathy-skills/evidence-ledger.md) |
| MEM | L0 brut→L1 atomes→L2 scènes→L3 persona ; offload refs→index→MMD→mutation | Continuité, recall et réduction du contexte principal | Architecture inspectée ; claims benchmark non reproductibles | injections stables + L1 non bornées par défaut, modèles auxiliaires et stockage non comptés | poisoning, fuite de scope, dérive, dual-write, purge irréversible, cache, supply chain | MIT avec notice ; dépendances/datasets à revoir | candidats : preuve/référence, scopes, interface séparée ; quarantaines : auto-persona/recall/Opik ; unknowns : exactitude, coût, purge, Qwen [E-LONG–E-BENCH](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-LONG) |

## Passe 2 — confrontation

### Signaux convergents

| Signal | Convergence | Contre-poids | Conclusion proposée |
| --- | --- | --- | --- |
| Diminuer le superflu | CAV, ADHD, PON et AKS ciblent remplissage ou over-build | moins de mots/lignes n'établit ni correction ni économie | conserver une contrainte de densité/simplicité qualifiée, pas un quota |
| Connaître avant d'éditer | PON exige flux/callers ; AKS explicite hypothèses | préparation peut devenir narration ou blocage | kernel court + seuil matériel ; détail au protocole |
| Réutiliser avant d'ajouter | ladder PON, simplicité AKS | recherche de l'existant peut coûter et réutiliser une mauvaise abstraction | kernel, limité aux options adaptées et compatibles |
| Rendre la réussite visible | AKS goal-driven, ADHD résultat visible, PON check | tests proxies et boucles peuvent tromper | kernel pour le principe ; budgets/arrêt au protocole |
| Externaliser sans tout injecter | état ADHD, progressive disclosure CAV/MEM | état répété ou auto-recall non borné augmente le coût | état de mission séparé ; mémoire optionnelle |
| Adapter les harnesses | tous les dépôts distribués montrent des différences réelles | les adapters accumulent logique et drift | canon neutre + adapters minces + parité vérifiée |

### Signaux complémentaires

- CAV apporte la distinction sortie visible / économie de session ; PON ajoute
  code évité / coût de recherche ; MEM ajoute les coûts des modèles auxiliaires.
  Ensemble, ils imposent un accounting de mission complet, non un chiffre unique
  ([CAV token economics](../repositories/01-caveman/token-economics.md),
  [PON token economics](../repositories/03-ponytail/token-economics.md),
  [MEM token economics](../repositories/05-tencentdb-agent-memory/token-economics.md)).
- ADHD rend explicite l'ownership de l'action et la reprise ; AKS fournit les
  conditions de clarification et d'arrêt ; MEM distingue preuve et dérivé.
- PON rend la simplicité opérationnelle par une ladder ; AKS corrige son risque
  en distinguant simplicité correcte, complexité essentielle et causalité.

### Signaux contradictoires

| Tension | Thèse | Antithèse | Résolution proposée |
| --- | --- | --- | --- |
| Densité / clarté | CAV compresse fortement | CAV Auto-Clarity, AKS et audits exigent hypothèses/preuves | densité sémantique, phrases naturelles, expansion au risque |
| Clarification / autonomie | AKS « demander si incertain » | ADHD action-first et goal loop | question seulement si ambiguïté matérielle ; hypothèse réversible sinon |
| Minimum / correction | PON et AKS chassent le code | rails, safety et contre-preuves coût montrent la dette déplacée | solution correcte la plus simple, pas moins de lignes |
| Scope / transversalité | diff chirurgical | migrations, lockfiles, callers, génération | périmètre causal nécessaire |
| Action / recherche | ADHD réduit la friction | audit et risque exigent lecture préalable | prévol proportionné, puis première action sûre |
| Boucle / arrêt | goal-driven continue jusqu'au succès | tests proxies, budget et autorité peuvent manquer | critères + budget + progrès + conditions d'arrêt |
| Kernel / mémoire | continuité utile | MEM est une infrastructure risquée et coûteuse | kernel demande un état récupérable ; mémoire couche 6 séparée |

### Redondants, stylistiques ou spécifiques

- Redondants : répétitions de « no filler », modes `lite/full/ultra`, descriptions
  dupliquées, copies manuelles et reminders par tour. Conserver un seul invariant
  canonique, pas ses variantes.
- Purement stylistiques : fragments, trois lignes, « wins », ton irrévérencieux,
  phrases bannies, branding. Ils ne disposent pas d'une ablation propre.
- Provider-specific : hooks, commandes, chemins, manifests, messages système,
  plan UIs, statuslines et cache boundaries. Ils appartiennent à la couche 5.
- Infrastructurels : L0–L3, embeddings, Gateway, SQLite/TCVDB, Opik, context
  offload. Ils appartiennent à la couche 6 ou 7, jamais au kernel.
- Non démontrés : bénéfice ADHD, nécessité des personas, exactitude des claims
  fixes, qualité Qwen, économie globale de mémoire.
- Dangereux : compression de doctrine sans validation sémantique, auto-recall
  sans scope/budget, persona automatique, injection invisible, patch postinstall,
  demande de chaîne de pensée privée.
- Inutiles actuellement : Mermaid universel, modes de style persistants,
  statistiques de « tokens sauvés », routing automatique et mémoire utilisateur.

## Matrice de décision des concepts majeurs

Une couche principale est attribuée à chaque ligne. « Pas une autre couche »
explique la frontière architecturale.

| Concept | Origine / problème | Couche principale | Preuve | Portabilité / coût tokens | Risque | Décision proposée | Pourquoi cette couche, pas une autre | Test préalable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Densité de réponse | CAV : sortie bavarde | 1 — Kernel | contradictoire | haute ; ~15–25 tokens candidats | perte de nuance | adapter | invariant de communication, pas mode/outil | qualité, omissions, tokens, préférence par tâche |
| Auto-Clarity | CAV : compression dangereuse | 1 — Kernel | moyenne | haute ; fusionnable avec proportionnalité | auto-classification ratée | adapter | priorité générale de clarté ; triggers détaillés en protocole | ambiguïté, sécurité, petits modèles |
| Réduction de friction | ADHD : difficulté à agir | 1 — Kernel | faible | haute ; ~10–20 tokens | handoff inutile, action prématurée | adapter | ownership/autonomie est invariant ; coaching détaillé ne l'est pas | taux d'achèvement et handoffs |
| État récupérable | ADHD/MEM : reprise | 3 — État récupérable | moyenne | haute ; coût écrit à checkpoints | stale/bavard | adopter conceptuellement | artefact de continuité, ni règle permanente ni mémoire utilisateur | reprise session/harness neufs |
| Limite fixe d'éléments | ADHD : scan de listes | 7 — Rejet | faible | haute ; faible coût | omission du 6e élément | rejeter | préférence de forme arbitraire, aucune capacité nécessaire | aucun avant rejet ; cas exhaustifs comme régression |
| Estimations temporelles | ADHD : perception du temps | 7 — Rejet | faible | haute ; coût variable | fausse précision | rejeter comme défaut | utile seulement sur demande et avec données, donc pas invariant | calibration si une capacité future est demandée |
| Persona Caveman | CAV : mémoriser la densité | 7 — Rejet | non isolée | faible culturellement ; coût élevé | ambiguïté, fatigue, fuite dans artefacts | rejeter | branding/style non nécessaire au mécanisme | ablation seulement si intérêt futur explicite |
| Persona Ponytail | PON : mémoriser le minimalisme | 7 — Rejet | non isolée | faible ; ~1 300 tokens avec doctrine | négligence littérale, biais review | rejeter | branding non nécessaire à la ladder | ablation neutre/persona |
| Réutilisation / stdlib / native / existant | PON : over-build | 1 — Kernel | moyenne, étroite | haute ; ~15–25 tokens | mauvais composant, exploration coûteuse | adapter | politique générale de choix ; détails/version au protocole | tâches où dépendance est et n'est pas légitime |
| Simplicité | PON/AKS : complexité accidentelle | 1 — Kernel | moyenne-faible | haute ; ~10–15 tokens | sous-ingénierie | adapter | invariant si qualifié par correction | contraintes cachées, sécurité, maintenance |
| Scope chirurgical | PON/AKS : diff bruyant | 1 — Kernel | plausible | haute ; ~15–20 tokens | patch local incohérent | adapter | responsabilité permanente ; cartographie d'impact en protocole | worktree sale, migration, code généré |
| Ambiguïté matérielle | AKS : mauvaise interprétation | 1 — Kernel | plausible | haute ; ~20–30 tokens | questions rituelles ou hypothèse cachée | expérimenter | seuil compact général ; cas et autorité au protocole | demandes ambiguës/headless, utilité des questions |
| Goal-driven execution | AKS : faux achèvement | 2 — Protocole | faible | haute ; corps potentiellement coûteux | boucle, proxy gaming | adapter | boucle dépend du type de mission, budget et preuve | tâches avec/sans tests, opérations risquées |
| Vérification proportionnée | AKS/PON : succès non prouvé | 1 — Kernel | moyenne conceptuelle | haute ; ~15–25 tokens | sous-test ou sur-test | expérimenter | invariant de niveau ; sélection des checks au protocole | risque croissant, faux achèvement, coût |
| Progressive disclosure | CAV/ADHD/PON/MEM : contexte inutile | 2 — Protocole | forte sur mécanisme, faible sur rendement | haute ; réduit coût si triggers précis | miss de contexte, trigger trop large | adopter conceptuellement | politique de chargement conditionnelle, pas comportement de chaque réponse | découverte, sélection, coût, réussite |
| Externalisation des preuves | MEM : gros résultats | 3 — État récupérable | forte sur stockage, faible sur retrieval | haute ; économies conditionnelles | ref cassée, preuve purgée | expérimenter | l'index/référence relève de l'état ; moteur de recherche serait couche 6 | détail rare, resolve, purge, migration |
| Mermaid | MEM : index navigable | 4 — Capacité optionnelle | faible | moyenne ; coût variable | format imposé, instabilité | différer | visualiseur possible, non invariant ni mémoire en soi | Mermaid vs liste/arbre sur tâches réelles |
| Mémoire L0→L3 | MEM : continuité longue | 6 — Infrastructure mémoire | forte sur présence, faible sur qualité | faible à moyenne ; coût élevé/non borné | dérive, poisoning, non-déterminisme | expérimenter seulement après prérequis | pipeline de données séparé, jamais règle comportementale | provenance, fidélité, coût total, crash/rebuild |
| Persona automatique | MEM : profil global | 7 — Quarantaine | faible | faible ; injection persistante | profilage, essentialisation, hallucination | quarantaine | risque de données/autorité ; aucune nécessité kernel | ablation sans persona, consentement, correction/purge |
| Auto-recall | MEM : rappel sans action | 7 — Quarantaine | mécanisme fort, bénéfice faible | moyenne ; caps désactivés par défaut | fuite de scope, poisoning, cache | quarantaine | mutation automatique non sûre ; recall explicite peut être couche 4/6 | scopes adversariaux, précision, budget |
| Recall budgété | MEM : contexte rappelé trop grand | 6 — Infrastructure mémoire | moyenne | haute conceptuellement ; budget explicite | budget partiel ou mauvais tokenizer | adopter comme invariant de service | contrôle interne au service, pas règle de réponse | enveloppe totale, tokenizer réel, bénéfice marginal |
| Mémoire locale | MEM : contrôle/inspection | 6 — Infrastructure mémoire | forte sur mécanisme | haute ; coût disque/opérations | secrets locaux, processus voisins | expérimenter | propriété de stockage du service | permissions, chiffrement éventuel, export/purge |
| Adaptateurs provider-specific | tous : discovery divergente | 5 — Adaptateurs | forte | inhérente ; coût faible si minces | drift/version | adopter conceptuellement | seule couche autorisée à nommer le harness | matrice de versions, parité sémantique |
| Hooks d'enforcement | CAV/PON/AKS PR/MEM : activation/contrôle | 4 — Capacité optionnelle | moyenne sur état, faible sur comportement | faible portabilité ; coût/exécution | mutation, silence, supply chain | différer | mécanisme activable avec permissions, non doctrine ni adapter pur | besoin précis, fail modes, uninstall, sécurité |
| Compression automatique | CAV/MEM : réduire contexte/fichiers | 7 — Quarantaine | faible/contradictoire | variable ; modèles auxiliaires | perte de sens, exfiltration, sur-suppression | quarantaine | mutation risquée sans invariants ; pas capacité générale actuelle | corpus adversarial, diff sémantique, rollback |
| Action suivante obligatoire | ADHD : initiation | 7 — Rejet | faible | haute ; sortie ajoutée | synthetic handoff | rejeter | format universel nuisible à l'autonomie | cas de coaching seulement si capacité future |
| Reporting factuel d'erreur | ADHD/AKS : bruit et faux causes | 1 — Kernel | plausible | haute ; coût neutre | certitude excessive | adapter | partie de faits/inférences/inconnues | diagnostics avec causes incertaines |
| État répété à chaque tour | ADHD : visibilité | 7 — Rejet | faible | haute ; coût récurrent | stale, duplication | rejeter | l'état canonique est couche 3, pas prose automatique | comparer delta/pointer au replay complet |
| Modes de style persistants | CAV/PON : intensité | 4 — Capacité optionnelle | faible | faible portabilité ; coût état/injection | drift et complexité | différer | préférence utilisateur optionnelle seulement | bénéfice marginal par mode et uninstall |
| Marqueur de dette ceiling/trigger/upgrade | PON : compromis réversible | 2 — Protocole | moyenne conceptuelle | haute si neutre ; coût faible | dette oubliée | adapter | convention de changement, pas règle toujours active | recherche, ownership, suppression à l'échéance |
| Chaîne de pensée exposée | AKS formulation : justification | 7 — Rejet | aucune nécessité | non portable/politique ; coût élevé | fuite de raisonnement, verbosité | rejeter | seules décisions observables sont requises | vérifier qualité avec synthèse externe courte |

## Claims transversaux et niveau de confiance

| Claim synthétique | Statut | Base et limite |
| --- | --- | --- |
| Un kernel plus court est probablement préférable | hypothèse moyenne | écarts 163/1 245 CAV et 656/1 307 PON, sans efficacité marginale directe [CAV E016](../repositories/01-caveman/evidence-ledger.md#e016), [PON E35–E36](../repositories/03-ponytail/evidence-ledger.md#ledger) |
| La proportionnalité peut remplacer plusieurs absolus | hypothèse à forte cohérence | résout les contre-exemples des cinq audits ; aucune ablation dédiée |
| Native-first peut réduire le code quand une primitive adaptée existe | signal moyen | −54,22 % Haiku sur tâches sélectionnées ; complétude/raw data manquantes [PON E40–E46](../repositories/03-ponytail/evidence-ledger.md#ledger) |
| Une persona est nécessaire à l'adhérence | non démontré | aucune ablation sémantiquement contrôlée [CAV E050](../repositories/01-caveman/evidence-ledger.md#e050), [PON E52](../repositories/03-ponytail/evidence-ledger.md#ledger) |
| La mémoire réduit le coût total | non démontré | modèles auxiliaires, recall et corrections exclus des claims [MEM E-BENCH](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-BENCH) |
| Une source neutre réduit le drift | inférence forte | duplications et bugs d'adapters observés dans CAV, PON et AKS |
| L'état récupérable améliore la reprise | hypothèse moyenne | mécanisme plausible, pas de test cross-session comparatif dans les audits |

## Équité de représentation

Les cinq audits ont chacun fourni au moins un mécanisme candidat, une
contre-preuve, un coût et une limite juridique/portabilité. Leur poids final
diffère volontairement selon la preuve : aucun chiffre Caveman, Ponytail ou
TencentDB n'est élevé au rang de vérité générale ; l'absence de benchmark ADHD
et AKS est conservée comme absence, non compensée par leur popularité ou leur
autorité de marque.
