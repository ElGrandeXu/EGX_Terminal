# Frontière de publication V1

## But

La V1 prévue présente un workspace de terminal-agent LLM-agnostique, à racine
neutre, avec ses principes, recherches, décisions et preuves reproductibles. Le
repository distant existe désormais en staging privé ; aucune visibilité
publique, aucun tag et aucune release ne sont déclarés.

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
locaux. La définition CI est incluse mais n'a pas encore été exécutée par GitHub.
Remote, release, publication effective et capacités avancées restent hors
périmètre sans autorisation séparée.

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
inspecte l'historique atteignable et exige l'identité publique exacte pour
chaque auteur et committer. Les modes `--all-refs` et `--fail-on-review` passent
localement ; le premier push comptait 32 commits et le correctif ciblé porte ce
total à 33. Le [rapport](HISTORY_AUDIT.md) et la
[remédiation](IDENTITY_REMEDIATION.md) documentent la transformation.

`scripts/check_markdown_links.py` valide hors ligne les liens Markdown suivis.
`scripts/check_github_governance.py` vérifie les fichiers communautaires, la CI,
le lock d'actions et le plan distant. Le workflow a été validé syntaxiquement
avec actionlint 1.7.12 ; sa première exécution GitHub est consignée ci-dessous.

## Staging privé et gate public

Le repository privé `ElGrandeXu/EGX_Terminal` a été créé vide, puis `main` a été
poussé. La première CI a produit :

- `repository / windows` : PASS ;
- `licensing / reuse` : PASS ;
- `repository / ubuntu` : FAIL.

Le défaut Ubuntu provient du tri natif d'objets `Path` dans le calcul agrégé de
l'archive. Windows et Linux n'appliquaient pas le même ordre aux chemins dont la
casse diffère. La correction ciblée dérive le chemin relatif POSIX et applique
explicitement l'ordre canonique insensible à la casse qui préserve le hash
verrouillé.

Le log Windows a révélé un second défaut : `origin/main`, ref locale de transport
créée par le checkout, était classée à tort comme ref publiable inattendue, puis
son code non nul était masqué par la poursuite du bloc PowerShell. La correction
sépare branches/tags/notes publiables, refs de transport `origin` et commit HEAD
audité ; le bloc Windows utilise désormais Bash en mode fail-fast. Le résultat
distant de ces corrections n'est pas anticipé dans ce commit.

Avant toute visibilité publique :

1. conserver la racine neutre, la surface publique et les tests au vert ;
2. exécuter `python scripts/check_git_history.py --fail-on-review` ;
3. conserver `python scripts/check_licensing.py` et `reuse lint` au vert ;
4. vérifier les JSON, TOML, liens Markdown, textes de licence et archives ;
5. confirmer l'intégrité des résultats de Mission 24 ;
6. confirmer zéro secret, donnée privée ou dépendance au workspace source ;
7. valider la gouvernance et le workflow ;
8. obtenir une autorisation explicite séparée avant le changement de visibilité.

## État

**`PRIVATE_REMOTE_STAGING_CI_REMEDIATION`**

Le staging privé est actif. Le passage public reste interdit tant que le nouveau
run ne valide pas les trois checks et que les réglages privés restants ne sont
pas examinés. Ce statut n'autorise ni visibilité publique, ni tag, ni release.
