# Étude de conception — MaintAI et CantineAI

Groupe : Sabrine Loksairi, Aya Haffari, Mohamed Amine Farih, Yasser Rais · Version : sections 1 à 5 finales · Date : 19/11/2026

## 1. Contexte et utilisateurs

| | MaintAI | CantineAI |
|---|---|---|
| Utilisateur principal | Responsable de l'équipe de maintenance de l'usine | Gestionnaire de la cantine du lycée |

## 2. Problème et décision

| | MaintAI | CantineAI |
|---|---|---|
| Décision prise avec le système | Choisir les machines à inspecter | Fixer le nombre de repas à commander pour le lendemain |
| Fréquence | Chaque matin | Chaque jour d'école, à 10 h |
| Coût d'une sous-estimation | Panne manquée : une ligne de production arrêtée pendant une journée, pour l'usine | Repas manquant : un élève sans déjeuner ou un sandwich acheté en urgence, et des plaintes des parents |
| Coût d'une surestimation | Fausse alerte : une heure d'inspection perdue, pour l'équipe de maintenance | Repas en trop : environ 15 DH de matière première perdus pour la cantine, et du gaspillage |

## 3. Approche par sous-problème

| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| MaintAI : prédire une panne (oui ou non) | ML supervisé, classification sur données tabulaires | Une règle à seuil fixe sur un capteur prend mal en compte la combinaison des quatre mesures. Le DL et les LLM ne se justifient pas pour 5 000 lignes et 4 variables numériques. |
| CantineAI : prévoir un nombre de repas | ML supervisé, régression sur série temporelle | La règle actuelle, reprendre le chiffre de la semaine précédente, ignore le menu, les examens, les sorties et les vacances. Le DL ne se justifie pas pour 340 lignes. |

## 4. Données

| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/exemple_pannes.csv` (MaintAI) | Données synthétiques fournies pour le cours ; licence non précisée | 5 000 lignes ; 4 variables d'entrée et la cible `failure` ; 17,6 % de pannes | Non : relevés de capteurs de machines |
| `data/cantine_repas.csv` (CantineAI) | Données synthétiques générées pour le cours ; licence non précisée | 340 jours d'école, du 09/09/2024 au 19/06/2026 ; 9 variables d'entrée, la date et la cible `repas_servis` | Non : chiffres agrégés par jour, aucun élève identifié |

## 5. Métriques, baseline et critères d'acceptation

### MaintAI
- **Baseline et son score :** toujours prédire « pas de panne » : accuracy 0,824, rappel 0.
- **Métrique principale :** le rappel, car une panne manquée coûte beaucoup plus cher qu'une fausse alerte.
- **Critère d'acceptation :** rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test (20 % des données, découpage aléatoire stratifié, graine 42).

### CantineAI
- **Baseline et son score :** dans le code, prédire la moyenne d'entraînement : MAE 70,3 repas. Baseline métier : reprendre les repas servis le même jour de la semaine précédente : MAE 79,0 repas sur les 58 jours de test où cette valeur existe.
- **Métrique principale :** la MAE en repas, car elle se lit directement et suit le nombre de repas jetés ou manquants.
- **Critère d'acceptation :** MAE au moins 15 % plus basse que la baseline métier, sur les jours où celle-ci existe parmi les 68 derniers jours d'école (20 % des données, découpage chronologique).

### Réglages de `config.py`

| Réglage | MaintAI | CantineAI |
|---|---|---|
| `DATA_PATH` | `data/exemple_pannes.csv` | `data/cantine_repas.csv` |
| `TARGET` | `failure` | `repas_servis` |
| `TASK` | `classification` | `regression` |
| `MAIN_METRIC` | `recall` | `mae` |
| `SPLIT` | `random` | `chronologique` |
| `TIME_COLUMN` | `None` | `date` |
| `TEXT_COLUMN` | `None` | `None` |

## 6. Architecture prévue
À compléter lors des prochaines séances.

## 7. Choix technologiques
À compléter lors des prochaines séances.

## 8. Risques, éthique, confidentialité
À compléter lors des prochaines séances.

## 9. Limites et hors périmètre
À compléter lors des prochaines séances.
