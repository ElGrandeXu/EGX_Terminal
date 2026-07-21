# Frontière de publication V1

## But

La V1 publiée présente un workspace de terminal-agent LLM-agnostique, à racine
neutre, avec ses principes, recherches, décisions et preuves reproductibles. Le
repository public est `ElGrandeXu/EGX_Terminal`. Aucun tag et aucune release ne
sont déclarés.

## Surface incluse

- `README.md`, `docs/` et le quickstart décrivent le projet et sa gouvernance ;
- `scripts/` et `tests/` fournissent les contrôles locaux actifs ;
- `governance/` contient la politique d'identité publique et la cartographie
  technique de la réécriture prépublication ;
- `REUSE.toml`, `LICENSE`, `LICENSES/` et `licensing/license-lock.json` portent la
  gouvernance de licences ;
- `experiments/kernel-v1/` et `experiments/kernel-micro-v1/` conservent les deux
  campagnes rejetées comme archives inactives et immuables.

La racine ne contient ni kernel always-on, adaptateur actif, hook, skill, mémoire,
routing ni injection de doctrine. Les archives ne sont pas des composants
d'exécution de la V1.

## Éléments exclus ou différés

La surface exclut les secrets, credentials, configurations de machine,
transcripts privés, caches, sorties temporaires, modèles, poids et binaires
locaux. La définition CI est incluse et exécutée par GitHub. Une release et les
capacités avancées restent hors périmètre sans autorisation séparée.

Le bundle de récupération de l'identité est un
**`PRIVATE_RECOVERY_ARTIFACT`** hors repository. Il contient l'ancien historique,
est interdit de publication et n'appartient jamais à la surface publique.

## Preuves historiques et archives

Les archives conservent légitimement versions, hashes, mesures de capacité,
protocoles, résultats et endpoints loopback nécessaires à l'audit. Aucun fichier
d'archive n'a été modifié pendant la remédiation d'identité. Douze anciens SHA
internes restent dans ces preuves et se résolvent via la
[cartographie](../../governance/history-rewrite-map.json).

Les contrôles d'intégrité confirment l'archive `kernel-v1`, l'archive
`kernel-micro-v1` et les dix résultats gelés de Mission 24 octet-identiques. Ces
faits historiques sont des exceptions documentaires, pas des exceptions de
licence ni de sécurité.

## Contrôles automatisés

`scripts/check_neutral_root.py` vérifie les cinq chemins doctrinaux interdits.
`scripts/check_public_surface.py` inspecte la surface suivie. Le contrôle reste
heuristique et ne remplace pas une revue contextuelle spécialisée.

`scripts/check_licensing.py` vérifie la cartographie, les textes verrouillés et
l'intégrité des archives. `reuse 6.2.0` vérifie REUSE Specification 3.3. Aucun
contenu tiers substantiel ni exception tierce n'a été identifié.

`scripts/check_git_history.py` lit la politique
[`public-commit-identity.json`](../../governance/public-commit-identity.json),
inspecte l'historique atteignable et applique le schéma 2 selon le rôle auteur,
committer ou trailer. Les contributeurs humains GitHub `noreply` sont acceptés ;
le committer web exact de GitHub est borné au rôle committer ; les adresses
personnelles et automatisations non déclarées restent `REVIEW`. Les 34 commits
antérieurs à la première pull request protégée conservent l'identité canonique du
mainteneur, sans réécriture supplémentaire. Les trois modes passent depuis une
branche de contribution et la classent `INFO CONTRIBUTION_REF`, sans en faire
une racine publique permanente. Le [rapport](HISTORY_AUDIT.md) et la
[remédiation](IDENTITY_REMEDIATION.md) documentent la transformation initiale et
la politique active.

`scripts/check_markdown_links.py` valide hors ligne les liens Markdown suivis.
`scripts/check_github_governance.py` vérifie les fichiers communautaires, la CI,
le lock d'actions et le plan distant. Le workflow a été validé syntaxiquement
avec actionlint 1.7.12 ; sa première exécution GitHub est consignée ci-dessous.

## Staging privé et publication

Le repository privé `ElGrandeXu/EGX_Terminal` a été créé vide, puis `main` a été
poussé. Le premier run a révélé un tri d'archive dépendant de la plateforme, une
classification incorrecte de `origin/main` et l'absence de fail-fast sous
PowerShell. La correction conserve le hash verrouillé, distingue les refs de
transport et exécute Windows sous Bash.

Le commit correctif a été amendé une seule fois pour construire la fixture
`AUTHENTICATED_URL` uniquement dans le repository temporaire du test. L'unique
force-push a utilisé la lease explicite attendue. Le run amendé a passé
`repository / ubuntu`, `repository / windows` et `licensing / reuse`, y compris
Windows sous Bash `-e -o pipefail` et le contrôle historique avec les refs
Actions. Les deux anciens runs de staging échoués ont ensuite été supprimés ; le
run vert a été conservé.

Les réglages distants documentés ont été appliqués avant le changement de
visibilité. Après autorisation explicite, le repository est devenu public. PVR,
secret scanning, push protection et alertes de vulnérabilité sont actifs. Un
clone HTTPS anonyme sans credentials a retrouvé 33 commits, la seule identité
autorisée, les hashes gelés, zéro ancien SHA amendé et zéro URL authentifiée
dans les blobs publiés. Tous les contrôles et tests y ont passé, puis le clone
temporaire a été supprimé.

La seconde CI publique sur le 34e commit a passé `repository / ubuntu`,
`repository / windows` et `licensing / reuse`. Le ruleset `main-protection` est
actif : il exige la pull request, la résolution des conversations, l'historique
linéaire et les trois checks, et interdit suppression et force-push de `main`.
La correction d'état et de politique est livrée par le premier workflow de pull
request réellement protégé, sans bypass administrateur.

## État

**`PUBLIC_V1_READY_FOR_RELEASE_REVIEW`**

La visibilité publique, les protections de sécurité et le ruleset sont actifs.
Aucun tag ni aucune release n'existe. Le prochain gate est une décision explicite
et séparée sur `v1.0.0` ; ce statut ne l'autorise pas.
