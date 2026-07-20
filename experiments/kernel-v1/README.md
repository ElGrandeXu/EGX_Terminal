# Kernel v1 expérimental

## Statut

Ce candidat est **expérimental, inactif et non promu**. Il n'est chargé
automatiquement ni par Codex, ni par Claude Code, ni par OpenCode. Son existence
ne modifie pas le bootstrap actuellement chargé à la racine.

## Objet de l'expérience

Le répertoire isole un traitement compact destiné à tester si neuf invariants
comportementaux améliorent la correction, le périmètre causal, la vérification et
la communication sans coût permanent disproportionné. Il permet de figer le
payload avant la future construction expérimentale des adaptateurs et avant tout
test inter-harness.

## Origine conceptuelle

Le texte est une reformulation originale de la
[synthèse des cinq audits](../../docs/research/synthesis/README.md) et de ses
[candidats doctrinaux](../../docs/research/synthesis/doctrine-candidates.md). Il
ne copie ni persona, ni slogan, ni formulation d'un repository audité. La
[décision 0002](../../docs/decisions/0002-llm-agnostic-kernel-architecture.md)
formalise son statut et ses frontières.

## Mesure et intégrité

Les mesures portent uniquement sur les octets exacts de
[`KERNEL.md`](KERNEL.md), encodés en UTF-8 sans BOM, avec fins de ligne LF et sans
fin de ligne finale :

- octets : longueur du tableau d'octets UTF-8 ;
- caractères : nombre de points de code du texte ASCII, identique ici au nombre
  d'octets ;
- mots : segments non vides séparés par un ou plusieurs caractères d'espacement
  (`\s+`) ;
- tokens estimés : `ceil(nombre de caractères / 4)` ;
- intégrité : SHA-256 des mêmes octets.

Cette estimation transparente permet une comparaison statique. Elle n'est le
tokenizer exact d'aucun modèle. Les valeurs calculées et le hash sont enregistrés
dans [`manifest.json`](manifest.json). Métadonnées, wrappers et futurs
adaptateurs devront être mesurés séparément. Le fichier [`.gitattributes`](.gitattributes)
maintient le payload en LF lors des checkouts Git.

## Limites

- Aucun effet comportemental n'a été validé.
- Aucun contexte réellement injecté par un harness n'a été capturé.
- Aucun adaptateur, générateur, hook, skill, mémoire ou runtime n'existe ici.
- Les règles peuvent être sous-spécifiées pour une mission risquée ou trop
  présentes pour une tâche triviale.
- Qwen n'est pas un harness ; son comportement dépendra du runtime, du modèle
  précis, de la quantification et du template testés.

## Conditions avant promotion

La promotion exige au minimum des adaptateurs expérimentaux inspectables, une
preuve de chargement unique et de synchronisation, les tests de scope et de
précédence sur versions fixées, la campagne du
[plan de validation](../../docs/research/synthesis/validation-plan.md), le respect
du plafond de 300 tokens estimés pour le payload et une décision explicite
séparée.

## Fichiers racine volontairement inchangés

`AGENTS.md` et `CLAUDE.md` restent inchangés. Aucun `opencode.json`, fichier
d'instruction racine ou réglage utilisateur/global n'est créé. Le candidat ne
peut donc pas être confondu avec le comportement actif du workspace.
