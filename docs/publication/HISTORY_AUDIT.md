# Audit de l'historique Git publiable

## Verdict

- **Date de l'audit :** 2026-07-21.
- **Commit de départ audité :**
  `e88ab8f985b577da3550cfd0c1e5280cc90eb560` (`chore: establish
  file-scoped license governance`).
- **Verdict :** **`REVIEW_REQUIRED`**.
- **Contenu :** aucun bloqueur observé.
- **Identité :** décision explicite de Maxime requise avant publication.

L'historique est techniquement propre selon les contrôles bornés exécutés, mais
les 29 commits antérieurs à cette mission exposent une adresse non-`noreply`.
Elle est masquée ici en `m***@gmail.com`. Elle n'est ni qualifiée de fuite ni
présumée publique : Maxime doit accepter explicitement sa publication, ou décider
ultérieurement d'une mission séparée de réécriture. Aucune réécriture n'a été
effectuée pendant cet audit.

## Périmètre Git

Le mode de publication inspecte `refs/heads/main`. L'inventaire initial contient
exactement cette ref : aucune autre branche locale, branche distante, note, ref
personnalisée, stash ou tag. Le mode `--all-refs` produit donc le même ensemble
atteignable. La publication prévue reste limitée à `main`; un éventuel tag de
release nécessitera une autorisation ultérieure.

Un push normal de `main` transfère ses commits, arbres et blobs atteignables. Les
reflogs sont locaux et ne sont pas publiés. Les objets inatteignables ne sont pas
inclus dans le scan par défaut et ne seraient pas transférés par ce push. Le
contenu du `HEAD`, déjà contrôlé par `check_public_surface.py`, est un sous-ensemble
distinct de l'historique atteignable audité ici.

## Mesures du commit de départ

| Mesure | Valeur |
| --- | ---: |
| Commits atteignables depuis `main` | 29 |
| Commits atteignables depuis toutes les refs | 29 |
| Merges | 0 |
| Objets atteignables | 413 |
| Arbres uniques | 173 |
| Blobs uniques | 211 |
| Taille décompressée cumulée des blobs | 2 621 659 octets |
| Plus gros blob | 96 177 octets |
| Blobs supérieurs à 512 KiB / 1 MiB / 10 MiB | 0 / 0 / 0 |
| Taille initiale approximative de `.git` | 1 244 500 octets |
| Pointeurs Git LFS | 0 |
| Submodules | 0 |

Le plus gros blob est une version historique de
`experiments/kernel-v1/tools/behavioral_pilot.py`. Les dix plus gros blobs vont
de 43 323 à 96 177 octets et appartiennent tous aux outils ou résultats
expérimentaux documentés. Aucun n'est excessif ou injustifié dans ce contexte.

Après enregistrement du commit unique de mission, le même contrôle a mesuré 30
commits, 178 arbres, 220 blobs, 428 objets et 2 709 990 octets décompressés. Les
110 chemins historiques incluent les trois nouveaux fichiers ; `AGENTS.md` et
`CLAUDE.md` restent les deux seuls absents du `HEAD`. Le plus gros blob et les
trois décomptes de seuil restent inchangés. Le commit de mission est identifié
par son sujet exact `chore: audit public git history` et son parent de départ
ci-dessus ; son SHA final est vérifié après le dernier amendement.

## Identités et métadonnées

Une seule identité nominale a été observée pour les auteurs et committers :
`El Grande Xü`. Son adresse masquée est `m***@gmail.com`, classée
`PRIVATE_EMAIL_REVIEW_REQUIRED`. Les décomptes sont donc : un nom d'auteur, une
adresse auteur, un nom de committer et une adresse committer. Aucun trailer
`Co-authored-by`, `Signed-off-by` ou équivalent et aucune signature de commit ne
sont présents.

La configuration Git locale ne définit ni `user.name` ni `user.email`. Le
fallback global utilise le même nom et la même adresse masquée que l'historique.
L'attribution à un compte GitHub attendu ne peut pas être déduite localement et
n'est pas revendiquée. État : **`COMMIT_IDENTITY_REVIEW_REQUIRED`**.

## Chemins et contenus historiques

L'historique de départ contient 107 chemins de fichiers distincts. Deux sont
absents du `HEAD` :

- `AGENTS.md` ;
- `CLAUDE.md`.

Ils appartiennent au bootstrap initial et ont été retirés par le commit de racine
neutre. Leur ancien contenu a été scanné comme tout autre blob : aucun secret,
chemin personnel, transcript, credential ou contenu non publiable n'y a été
observé. Leur présence passée est cohérente avec l'histoire documentée et ne
remet pas en cause la neutralité du `HEAD`.

Le scan de tous les messages et blobs atteignables n'a observé :

- aucun secret ou credential plausible ;
- aucune clé privée PEM ;
- aucun chemin personnel Windows, Unix ou macOS ;
- aucune occurrence du compte local connu dans un contexte machine ;
- aucun fichier `.env`, configuration locale sensible, transcript ou dump ;
- aucun binaire historique, pointeur LFS ou gitlink ;
- aucun blob volumineux au seuil de 512 KiB ;
- aucune URL avec authentification intégrée ;
- aucune ref inattendue ;
- aucun contenu tiers substantiel ou annotation de provenance ambiguë.

L'inventaire des chemins, l'historique des changements et les cinq audits de
repositories documentés ne montrent aucun fichier importé ou asset tiers. Les
noms, URLs, hashes, faits, paraphrases originales et courts extraits attribués
restent distingués d'une copie substantielle. Aucun droit n'est revendiqué sur
un contenu tiers.

## Exceptions légitimes

Les motifs de détection inclus dans les scripts et leurs tests sont des fixtures
intentionnelles construites sans valeur exploitable. Les domaines réservés
`example.com`, `example.net`, `example.org` et `example.invalid`, les hashes,
versions, endpoints loopback et faits de capacité des archives expérimentales
sont également légitimes. Ces cas étroits ne créent aucune exemption générale.

`AGENTS.md` et `CLAUDE.md` sont acceptés uniquement comme anciens fichiers sûrs ;
ils restent interdits à la racine active par la décision de neutralité.

## Contrôle reproductible

Depuis la racine du repository :

```console
python scripts/check_git_history.py
```

Le contrôle utilise Python 3.11 et Git, sans réseau ni écriture dans le
repository. `--all-refs` étend les racines d'atteignabilité, `--fail-on-review`
rend les décisions humaines bloquantes pour l'appelant, `--max-blob-bytes`
change le seuil de 524 288 octets et `--json <path>` écrit un rapport
déterministe hors du repository. Les valeurs détectées et adresses non-`noreply`
sont masquées. Le retour est non nul pour un `BLOCKER`, mais reste nul pour la
présente revue d'identité sauf avec `--fail-on-review`.

La suite construit des repositories Git temporaires et couvre les anciens blobs,
messages, identités, trailers, refs, objets inatteignables, binaires, LFS,
submodules, chemins avec espaces, JSON déterministe et absence de fuite dans les
diagnostics.

## Validation depuis un clone propre

Un clone temporaire sous `%TEMP%` a été créé avec :

```console
git clone --local --no-hardlinks --no-tags --single-branch --branch main
```

L'option `--no-hardlinks` impose une copie réelle des objets. La ref distante
technique créée automatiquement par `clone` n'est pas une ref du repository
source et est retirée avant l'audit final du clone. Dans le clone :

- `check_neutral_root.py`, `check_public_surface.py`, `check_licensing.py` et
  `check_git_history.py` passent ;
- les 74 tests applicables passent ;
- `reuse 6.2.0` confirme 104 fichiers licenciés sur 104 ;
- les 390 liens Markdown locaux sont valides ;
- aucune chaîne ne dépend du chemin du workspace source ;
- aucun fichier non suivi n'est nécessaire.

Le premier checkout a révélé que `core.autocrlf=true` modifiait les octets de
quelques entrées de hash expérimentales. La correction impose `eol=lf` depuis la
racine pour les fichiers Markdown, Python, JSON et `.gitattributes` des
expériences ; aucun fichier d'archive n'a été modifié. Un test dédié verrouille
ce prérequis de clone portable. La validation complète a ensuite produit
**`PASS`**, et le clone temporaire a été intégralement supprimé.

## Limites

Le contrôle est heuristique et borné aux objets atteignables depuis les refs
sélectionnées. Il ne prouve pas l'absence absolue de secret, ne décode pas
arbitrairement les binaires, ne consulte ni reflogs ni objets inatteignables, ne
compare pas le contenu à toutes les sources tierces possibles et ne remplace ni
revue humaine, ni décision de confidentialité, ni avis juridique. Un nouveau
format de credential ou un contenu encodé peut échapper aux motifs connus.

La gate reste **`REVIEW_REQUIRED`** jusqu'à la décision de Maxime sur l'adresse
historique et l'identité de commit future. Il n'existe aucun blocker de contenu,
licence, provenance ou clone propre observé à ce stade.
