# Architecture et frontières candidates

## Statut

Cette architecture a servi de proposition à la
[décision 0002](../../decisions/0002-llm-agnostic-kernel-architecture.md). Celle-ci
adopte six couches fonctionnelles et une gouvernance externe, sans implémenter ni
activer le kernel expérimental. Le présent document conserve les détails de
frontière issus de la synthèse ; la décision 0002 fait autorité.

## Taxonomie à couche principale unique

| Couche | Contenu candidat | Pourquoi ici | Pourquoi pas ailleurs |
| --- | --- | --- | --- |
| 1. Kernel comportemental | comprendre, ambiguïté matérielle, réutilisation, simplicité correcte, scope causal, réussite/vérification proportionnée, clarté épistémique | invariants pertinents sur presque toute mission et assez courts pour le chargement automatique | aucune séquence de workflow, état, outil ou nom de provider ne doit être permanent |
| 2. Protocole de mission | prévol, recherche/audit, diagnostic, implémentation, publication, destruction, tâche longue, boucles et budgets | activation conditionnelle selon type, impact et irréversibilité | trop détaillé/coûteux pour le kernel ; pas un outil puisqu'il décrit un comportement |
| 3. État récupérable | objectif, scope, état, décisions, preuves, changements, validations, blocages, prochaine action | artefact portable de reprise et source de coordination | pas une mémoire : borné à une mission, explicitement maintenu et supprimable |
| 4. Capacités optionnelles | skills, outils, évaluateurs, hooks, compresseurs, routing | mécanismes activables avec propriétaire, version, test et retrait | ne deviennent ni doctrine ni compatibilité par leur seule existence |
| 5. Adaptateurs | `AGENTS.md`, `CLAUDE.md`, entrée OpenCode, événements, includes, manifests | traduit la source neutre vers une surface de harness | ne doit pas créer de sens propre ; sinon il devient une capacité ou du drift |
| 6. Infrastructure mémoire | capture, consolidation, retrieval, provenance, correction, oubli, export | service de données durable, avec permissions et budgets propres | trop sensible et coûteux pour kernel/état ; indépendante des événements d'un host |

### Périmètre de gouvernance externe

Rejets, quarantaines, limitations, critères de promotion et critères de retrait
contrôlent toutes les couches. Ils ne produisent pas une fonction runtime et ne
constituent donc pas une septième couche. Personas permanentes, claims fixes,
compression non fidèle, injection invisible et artefacts juridiquement
incertains restent rejetés ou en quarantaine sans être rangés dans une couche
fonctionnelle.

Cette attribution reprend les distinctions instruction/enforcement/packaging de
[Caveman](../repositories/01-caveman/behavior-and-delivery.md#what-is-instruction-enforcement-measurement-packaging-or-product),
la frontière ladder/adapters de
[Ponytail](../repositories/03-ponytail/behavior-and-delivery.md#chaîne-dexécution)
et la séparation core/host de
[TencentDB](../repositories/05-tencentdb-agent-memory/repository-map.md#frontières-coreadapters).

## Protocoles de mission : niveau de détail attendu

Le kernel dit **quoi préserver** ; le protocole dit **comment agir dans ce type
de mission**. Exemples de déclencheurs futurs, sans création de mécanisme :

| Protocole | Trigger | Contrôles propres |
| --- | --- | --- |
| Recherche/audit | claim externe ou repository inconnu | snapshot, provenance, faits/inférences, couverture, non-exécution si requise |
| Diagnostic | cause demandée sans autorisation de corriger | reproduction, hypothèses concurrentes, preuve causale, aucune mutation |
| Implémentation | création ou modification autorisée | worktree, impact, conventions, diff causal, tests adaptés |
| Publication | commit/push/PR/release | scope explicite, secrets, licence, provenance, statut CI, consentement externe |
| Destruction | suppression, écrasement, migration irréversible | cible résolue, backup/rollback, confirmation, audit après action |
| Tâche longue | dépasse une session ou forte ramification | budget, checkpoints, état récupérable, stop et reprise |

Ces procédures ne sont pas des skills par défaut. Elles peuvent rester des
documents jusqu'à ce qu'un trigger fiable et un bénéfice mesuré justifient une
capacité.

## Contrat minimal d'état récupérable

### Schéma sémantique

| Champ | Contenu minimal | Interdit |
| --- | --- | --- |
| Objectif | résultat terminal concret | récit de la conversation |
| Périmètre | inclus, exclus, autorité | liste exhaustive du repository |
| État actuel | étape et état des artefacts | répétition des étapes terminées sans effet |
| Décisions prises | choix qui contraignent la suite + motif bref | raisonnement privé ou débat intégral |
| Preuves importantes | références résolubles, résultats ou hashes | copier de gros outputs disponibles ailleurs |
| Modifications réalisées | chemins/objets et effet | diff complet dupliqué |
| Validations exécutées | commande/check, résultat, date/version utile | « testé » sans preuve |
| Blocages | dépendance précise, tentatives utiles, autorité manquante | obstacle vague ou faux blocage |
| Prochaine action | une action exécutable ou décision requise | backlog général |

### Cycle de vie

- **Écrire** lorsqu'une mission doit survivre à une compaction/session, avant un
  handoff, à un blocage réel, ou après une décision difficile à reconstruire.
- **Vivre** dans un artefact repository-owned, textuel, explicitement identifié
  comme temporaire ou durable ; le chemin exact reste une décision différée.
- **Rester compact** par remplacement de l'état courant et liens vers preuves,
  non par append de chaque tool call. Un budget en lignes/octets et un owner sont
  requis avant implémentation.
- **Empêcher la dérive** avec timestamp/commit de référence, critères de fraîcheur,
  champs obligatoires et clôture/suppression quand la mission termine.
- **Reprendre** en lisant objectif, état, validations et prochaine action, puis en
  vérifiant les références contre le workspace avant de leur faire confiance.
- **Rester temporaire** pour notes de travail, hypothèses rejetées, logs et
  prochains gestes. Une décision durable ne migre vers la documentation ou un
  decision record que si elle change le projet au-delà de la mission.

Cette approche adapte l'hypothèse d'externalisation de
[i-have-adhd E37](../repositories/02-i-have-adhd/evidence-ledger.md) sans répéter
l'état à chaque tour, et conserve la leçon preuve/référence de
[TencentDB E-OFFLOAD](../repositories/05-tencentdb-agent-memory/evidence-ledger.md#E-OFFLOAD)
sans installer de mémoire.

## Frontières entre les formes de connaissance

| Objet | Autorité et scope | Durée | Mode d'accès | Exemple de contenu |
| --- | --- | --- | --- | --- |
| Doctrine | règles approuvées du workspace | longue, versionnée | chargement automatique borné | invariants comportementaux |
| État de mission | mission courante seulement | jusqu'à clôture/handoff | lecture ciblée | progression, validations, blocage |
| Mémoire de workspace | faits/événements réutilisables sur ce workspace | durable avec TTL/version | retrieval explicite ou budgété | convention découverte, incident antérieur |
| Mémoire utilisateur | préférences consenties et scoped | durable, corrigeable/oubliable | recall explicite et visible | préférence de format stable |
| Historique brut | trace source non interprétée | rétention définie | résolution de preuve | événement/message/output original |
| Documentation | connaissance intentionnellement publiée | durable et revue | navigation/recherche | guide, architecture, décision |
| Index de recherche | dérivé reconstruisible | jetable/rebuildable | requête | termes, embeddings, mapping refs |

La doctrine prescrit ; l'état coordonne ; la mémoire rappelle ; l'historique
atteste ; la documentation explique ; l'index localise. Aucun résumé mémoire ne
devient doctrine, et aucun historique brut n'est automatiquement une instruction.

## Frontière d'un futur service mémoire neutre

### Responsabilités

1. Capturer des événements explicitement autorisés avec scope et sensibilité.
2. Conserver des preuves brutes locales sous une politique de rétention.
3. Produire des dérivés identifiés comme tels et reconstruisibles autant que
   possible.
4. Rechercher sous scope strict et budget total de recall.
5. Résoudre chaque référence vers sa preuve, si encore retenue.
6. Permettre inspection, correction, contradiction, remplacement et oubli.
7. Exporter données, schéma, provenance et journal d'opérations.
8. Auditer capture, consolidation, recall, correction et purge.

### Invariants

- Aucun événement sans scope structuré `user/workspace/project/agent/session`.
- Aucune abstraction présentée comme fait brut ; producteur, modèle/prompt/version
  et liens `derived-from` restent visibles.
- Tout contenu rappelé est non fiable et sans autorité d'instruction.
- Le budget couvre **toute** l'injection : résultats, profil éventuel, navigation,
  guide et enveloppe ; `0` ne signifie pas « illimité » en production.
- Les preuves brutes sont locales par défaut ; toute sortie vers LLM, embedding
  ou télémétrie distant exige destination, consentement et redaction explicites.
- Correction et oubli propagent un statut vérifiable à indexes, dérivés, backups
  et caches ; une purge incomplète est déclarée.
- Les dérivés et index peuvent être reconstruits ; leur perte ne détruit pas la
  dernière preuve tant que la rétention l'autorise.
- Auto-capture, auto-recall et persona sont désactivés par défaut pendant
  l'expérimentation.

### Interface conceptuelle

```text
capture(event, scope, policy)
consolidate(scope, budget)
retrieve(query, scope, budget)
resolve(reference, scope)
inspect(scope, filters)
correct(memory_id, replacement, evidence)
forget(target, scope)
export(scope, format)
```

Les métadonnées minimales suivent la projection de l'audit TencentDB : IDs
événement/mémoire, scope, rôle/producteur, URI+hash source, dates, type
épistémique, sensibilité, confiance, TTL, version, parent/dérivation, statut
`active/superseded/contradicted/deleted`, budget et raison du recall, journal de
correction/purge
([interface étudiée](../repositories/05-tencentdb-agent-memory/behavior-and-delivery.md#interface-minimale-proposée-comme-objet-détude)).

### Risques et prérequis expérimentaux

Risques : poisoning différé, assistant auto-cité, contamination inter-scope,
profilage, dérive temporelle, hallucination de consolidation, écriture partielle,
ref orpheline, purge incomplète, secrets/PII, exfiltration, coût auxiliaire et
verrouillage de harness. Avant tout prototype : dataset synthétique licencié,
threat model, scopes testables, ledger de coûts complet, baseline sans mémoire,
recall explicite seul, resolver de preuve, correction/oubli E2E et migration de
harness. Aucune base de données n'est choisie.

## Distribution LLM-agnostique

### Comparaison des options

| Critère | A. Canon provider + pointeurs | B. Canon neutre + include/génération | C. Copies générées + hash | D. Bootstrap injecteur |
| --- | --- | --- | --- | --- |
| Codex | excellente si `AGENTS.md` canon | excellente via adapter `AGENTS.md` généré ou canon lu | excellente | possible, mais nouveau runtime |
| Claude Code | include simple si canon est `AGENTS.md` | excellente si `CLAUDE.md` importe le canon | excellente | possible via hook/bootstrap |
| OpenCode | dépend de son support de règle/import | adapter/copie requise selon version | bonne avec fichier découvert | plugin nécessaire |
| Modèle Qwen local via OpenCode ou autre runtime | dépend du host, sémantique neutre | bon si texte matérialisé dans son host | bon, contenu statique inspectable | risque protocole/template/runtime ; Qwen n'est pas un harness |
| Chargement automatique | bon pour provider canon, indirect ailleurs | bon lorsque include existe | bon partout avec fichier reconnu | bon seulement si bootstrap actif |
| Duplication | faible disque, canon provider-shaped | faible avec include ; copies fallback | élevée mais mécanique | faible disque |
| Drift | pointeurs simples, mais canon sémantiquement biaisé | faible si génération/parité | faible si hash bloquant | code/runtime peut dériver |
| Coût tokens | un kernel, hors wrapper | un kernel, hors wrapper | un kernel par session malgré copies disque | kernel + bootstrap/event framing |
| Transparence | haute | haute | très haute, fichiers autonomes | plus faible, injection dynamique |
| Dépendance provider | forte par construction | faible | faible | dépend du runtime bootstrap |
| Complexité | très faible | faible à moyenne | moyenne (génération/check) | forte |
| Publication | simple mais message de neutralité brouillé | claire : canon et adapters explicites | claire si generated marqué | installation et sécurité complexes |
| Adapter absent | aucun comportement ou lecture manuelle | canon reste lisible, pas auto-chargé | fichier non généré : dégradation visible | aucune injection ; panne parfois opaque |

Les faits actuels montrent que Claude sait importer `@AGENTS.md`, tandis que
Codex découvre `AGENTS.md` ; ce bootstrap provisoire fonctionne mais laisse un
nom de provider comme canon
([baseline](../official-harness-baseline.md),
[décision 0001](../../decisions/0001-bootstrap-entrypoints.md)). Les audits CAV,
PON et AKS montrent qu'une fédération de copies manuelles dérive ; leurs fixes
multi-harness justifient une vérification de parité, pas un runtime universel.

### Architecture décidée

La décision 0002 retient **B avec fallback C** :

1. un fichier canonique sémantiquement neutre, chemin à décider ;
2. un adapter mince par harness qui inclut le canon lorsque le host le permet ;
3. une copie générée, marquée et vérifiée par hash lorsqu'il n'existe pas
   d'include fiable ;
4. un contrôle de synchronisation qui compare le contenu sémantique attendu et
   échoue visiblement en développement/publication ;
5. si aucun adapter n'existe, le canon reste lisible et documenté mais aucune
   capacité automatique n'est revendiquée : dégradation propre par absence,
   sans bootstrap caché.

Le futur chemin canonique recommandé est `doctrine/KERNEL.md`, sans le créer
avant promotion. Aucun script ni adaptateur n'est créé à ce stade. L'option D
reste différée : elle ajoute exécution, permissions, lifecycle et supply chain
pour livrer un texte court. L'option A reste le bootstrap actuel, pas la cible
neutre décidée.

## Politique des skills, hooks et capacités

### Test d'admission obligatoire

Toute capacité future doit avoir une fiche versionnée contenant : problème
précis, trigger précis, bénéfice mesurable, coûts contextuel et opérationnel,
propriétaire, version, permissions, méthode de désactivation, test, condition de
suppression et couche principale. Sans champ rempli, elle reste documentation ou
expérience externe.

### Routage par type

| Forme | Justification nécessaire | Ne convient pas si… |
| --- | --- | --- |
| Kernel | règle universelle, compacte, mesurable, sans état/outillage | trigger contextuel ou exception longue |
| Documentation | connaissance consultable, procédure peu fréquente | exécution répétée et mécaniquement vérifiable justifiée |
| Skill | tâche spécialisée, trigger distinct, contexte volumineux utile à la demande | invocation serait quasi universelle |
| Hook | événement fiable et propriété techniquement vérifiable/bloquable | seule l'obéissance sémantique du modèle est visée |
| Outil explicite | effet déterministe ou accès à une ressource sous contrôle utilisateur | mutation invisible ou autorité ambiguë |
| Expérience | bénéfice plausible, preuve/sécurité/portabilité manquante | risques non confinables ou aucune métrique |

Un hook n'« enforce » pas une pensée ou un style ; il peut bloquer une commande,
valider un fichier, journaliser un événement ou injecter du contexte selon les
garanties du host. CAV et PON montrent que les hooks fiables sur l'état restent
provider-specific et peuvent échouer silencieusement
([CAV E041–E044](../repositories/01-caveman/evidence-ledger.md#e041),
[PON E15–E24](../repositories/03-ponytail/evidence-ledger.md#ledger)).

### Budget et promotion

- Plafond strict du payload always-on : 300 tokens estimés par
  `ceil(caractères/4)`, avec une cible souhaitée d'environ 250 ; métadonnées,
  wrappers et adaptateurs sont comptabilisés séparément.
- Métadonnées de capacités : budget agrégé mesuré par harness ; supprimer ou
  raccourcir les descriptions non sélectionnantes.
- Une nouvelle capacité commence **expérimentale, désactivée par défaut**.
- Promotion : trigger precision ≥95 % sur corpus cible, zéro régression critique,
  gain primaire matériel et reproductible, coût session documenté, désactivation
  et suppression testées, propriétaire actif.
- Réexamen à chaque changement majeur de harness/modèle ou au plus à une cadence
  fixée par la future gouvernance ; suppression si trigger rare, bénéfice disparu,
  coût supérieur ou propriétaire absent.
- Nombre de capacités actives : aucune limite arbitraire ; l'enveloppe de contexte
  et la charge de maintenance sont les budgets contraignants.

## Risques architecturaux

- La source « neutre » peut rester biaisée par le premier harness si ses tests ne
  capturent que ce host.
- Une génération par hash peut garantir l'égalité textuelle sans garantir ordre,
  portée ou priorité runtime.
- Le kernel équilibré peut encore être trop long pour certains petits modèles ou
  trop vague pour des tâches risquées.
- L'état récupérable peut devenir une mémoire de fait s'il n'est pas clôturé.
- Une capacité utile peut être promue sur une métrique proxy et provoquer des
  régressions non couvertes.
- Un service mémoire « local » peut toujours exposer des secrets aux processus,
  modèles ou embeddings configurés.

## Alternatives rejetées ou différées

- Union des cinq doctrines : rejetée, contradictions et coût cumulé.
- `AGENTS.md` provider-shaped comme canon permanent : différé au profit d'un
  canon neutre ; conservé seulement comme bootstrap actuel.
- Copies manuelles : rejetées pour drift ; copies générées restent un fallback.
- Bootstrap externe par défaut : différé pour complexité et trust boundary.
- Tout dans des skills : rejeté ; les invariants universels ne doivent pas
  dépendre du routing.
- Tout dans le kernel : rejeté ; protocoles, état et mémoire ont des cycles de
  vie distincts.
- Base vectorielle ou TencentDB comme prérequis : rejeté ; aucun backend choisi.
- Mermaid comme représentation mémoire canonique : rejeté comme universel.

## Décisions formalisées et travail restant

La décision 0002 formalise les six couches, la gouvernance externe, le traitement
expérimental, la proportionnalité, le contrat séparé d'état récupérable, B avec
fallback C, le budget et les capacités différées. Elle ne valide pas l'efficacité
du candidat.

Le travail suivant consiste à construire et tester les adaptateurs dans un
périmètre expérimental : versions fixées, portée, précédence, chargement unique,
hash, comportement sans adaptateur et contexte réellement injecté. Aucune
promotion ne découle automatiquement de ces tests.
