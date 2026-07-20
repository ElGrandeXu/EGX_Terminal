# Évaluations comportementales du kernel v1

Ce répertoire contient les protocoles et résultats comportementaux du candidat
expérimental. Ces évaluations restent séparées des preuves de distribution et de
transport runtime. Elles n'activent et ne promeuvent aucun kernel.

## Pilote v1

Le [premier pilote](pilot-v1/results.md) compare OpenCode 1.17.9 + Ollama 0.20.2
+ `qwen3.6:27b` sur deux tâches Python réelles, une fois sans instruction projet
et une fois avec le kernel distribué par `sync_adapters.py`.

- protocole pré-enregistré : [protocol.md](pilot-v1/protocol.md) ;
- SHA-256 :
  `25f5d73487446bdbb7fd321720b1945a1c5970649a7eddecc7fa4e93f6ef8c4f` ;
- quatre runs comportementaux, 22 requêtes modèle, aucun retry comportemental ;
- quatre `PASS`, scope causal et préservation intacts ;
- aucun signal de réussite différentiel ; coût agrégé du kernel : +2,61 % de
  tokens totaux et −7,54 % de latence sur seulement deux paires non répétées.

Ce pilote valide surtout l'infrastructure de mesure et démontre qu'elle peut
conserver un résultat nul. Il ne fournit aucune puissance statistique et ne
justifie ni promotion ni rejet.
