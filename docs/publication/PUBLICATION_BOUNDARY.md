# Frontière de publication V1

## But

La V1 conserve un workspace de recherche LLM-agnostique à racine neutre, avec
ses principes, décisions, contrôles et artefacts reproductibles dans leurs
limites documentées. Le seul repository canonique est
`ElGrandeXu/EGX_Terminal`.

La phase durable est **`PUBLICATION_RETRY_PREPARATION`**. Le repository est
actuellement privé et non partageable. Une première bascule publique a été
exécutée puis rollbackée ; une seconde tentative unique est conditionnellement
autorisée, mais n'est pas appliquée. La documentation ne permet jamais de
déduire la visibilité ou les protections effectives : elles doivent être relues
sur GitHub.

## Surface canonique incluse

- `README.md`, `docs/` et le quickstart décrivent le projet et sa gouvernance ;
- `scripts/` et `tests/` fournissent les contrôles locaux actifs ;
- `governance/` contient les politiques, registres, locks et le plan GitHub ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` portent
  la gouvernance de licences ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les
  deux campagnes rejetées comme archives inactives et immuables.

Pour le micro-kernel, les artefacts de définition conservés restent auditables,
mais l'agrégat original et les données runtime sources sont irrécouvrables. La
[décision 0014](../decisions/0014-micro-kernel-evidence-erratum.md) documente
cette limite sans modifier le verdict terminal **`REJECT_MICRO`**.

La racine ne contient ni kernel always-on, adaptateur actif, hook, skill,
mémoire, routing ni injection de doctrine. L'incident GitHub est un résultat
auditable de publication, pas la création d'un framework générique de sécurité.

## Éléments privés ou différés

La surface canonique exclut secrets, credentials, configurations de machine,
transcripts privés, caches, sorties temporaires, modèles, poids, binaires
locaux, bundles, mirrors et captures API privées. Les preuves de transition
restent privées et hors repository.

Les réponses GitHub destinées aux preuves sont collectées par allowlist.
`temp_clone_token`, authorization, cookies, tokens, credentials et URL signées
temporaires sont exclus avant écriture ou affichage. Une URL signée devient
`[SIGNED_URL_REDACTED]`; seuls le nom et la présence d'un champ retiré sont
enregistrés. Les hashes sont produits après assainissement et la preuve
assainie devient immuable.

Le champ `temp_clone_token` observé pendant le diagnostic est classé credential
temporaire de clonage. Il n'a été affiché que localement et en privé ; aucune
exposition publique ou persistance Git/Actions n'a été détectée et son ancienne
valeur n'est plus conservée. Son TTL et sa révocation n'étant pas documentés,
le projet n'affirme ni qu'il est actif ni qu'il est expiré. Toute future
collecte l'exclut avant affichage.

## Première transition publique

Le checkpoint `c887949cbc3c6fe8aade34b2675b39545c365905` comptait 42 commits
linéaires, sans PR ouverte, tag, release, package ou fork. L'exposition a duré
de `2026-07-23T08:02:57.4503878Z` à
`2026-07-23T08:34:32.3856142Z`, soit environ 31 minutes et 35 secondes.
L'identité du repository, `main`, le SHA et le contenu sont restés inchangés.
Aucune fuite matérielle n'a été détectée, sans pouvoir exclure une consultation
ou copie par un tiers.

PVR, `main-protection` sans bypass, secret scanning, push protection,
vulnerability alerts, la politique Actions minimale et l'approbation de tous
les contributeurs externes étaient actifs. Les trois checks ont réussi et zéro
alerte secret scanning, package, tag, release ou fork a été observé. Après le
rollback, les contrôles non disponibles sur GitHub Free privé sont redevenus
indisponibles ou inactifs.

Le rollback était imposé par le protocole alors actif après des HTTP 403 sur les
téléchargements REST anonymes des logs. Les mêmes résultats sur
`actions/checkout`, `cli/cli` et `astral-sh/ruff` établissent
`GENERAL_GITHUB_ANONYMOUS_LOG_RESTRICTION` et `PLATFORM_AMBIGUITY`, sans preuve
d'une restriction liée à l'origine privée du run EGX ni d'une vulnérabilité du
repository.

## Seconde tentative conditionnelle

Avant toute seconde bascule, cette PR doit être mergée, le nouveau HEAD audité
en privé, un compte GitHub externe préexistant de Niveau B préparé, le harness
corrigé vérifié et l'absence de nouveau blocker confirmée.

Pendant la bascule, les protections publiques doivent être immédiatement
réappliquées et vérifiées. Un nouveau run doit être créé sur `main` par
`workflow_dispatch`, entièrement après le passage public, puis ses trois jobs
exacts doivent réussir. Le run historique `29951087998` ne doit être ni
réutilisé, ni rerun, ni supprimé. Aucun commit vide ou branche temporaire n'est
autorisé.

Le Niveau A vérifie la surface internet anonyme, y compris les téléchargements
REST de logs comparés à des témoins. Un HTTP 403 généralisé est `INFO` et
`PLATFORM_AMBIGUITY`, pas un blocker absolu si B et C réussissent. Le Niveau B
utilise un compte externe sans collaboration, invitation, équipe ou droit privé
et doit lire les trois jobs et leurs logs ; son échec est critique et impose un
rollback. Le Niveau C propriétaire télécharge et scanne les logs complets,
contrôle les protections et alertes, et ne conserve aucune URL signée.

Après succès des trois niveaux, un rapport peut établir l'état public. Après un
éventuel second rollback, le repository reste privé et non partageable et la
tentative devient une preuve historique. Une troisième tentative exige une
nouvelle ADR.

## Historique, release et état

La remédiation d'identité, la reconstruction content-identical et le checkpoint
de récupération restent documentés par les décisions 0010 à 0013. La release
`v1.0.0` reste un enregistrement historique retiré, non actif dans le repository
recréé. La réservation GitHub de son nom n'est pas contournée.

**État courant : `PUBLICATION_RETRY_PREPARATION`, visibilité privée,
repository non partageable.**

Aucun tag ou release ne peut être créé pendant cette phase ou la tentative
conditionnelle. `v1.0.1` et sa signature SSH restent une mission ultérieure
séparée. Aucun affaiblissement des protections n'est autorisé.
