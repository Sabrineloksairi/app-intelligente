# Étude de conception — MaintAI

Groupe : G1 5IA · Aya Haffari · Version : brouillon · Date : 15/11/2026

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) : le responsable de maintenance de l'usine, qui choisit chaque matin les machines à inspecter.

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système : quelles machines inspecter aujourd'hui, à partir des relevés de capteurs.
- Fréquence : chaque matin.
- Coût d'une erreur, et pour qui : une **panne manquée** arrête une ligne de production pendant une journée (coût pour l'usine) ; une **fausse alerte** coûte une heure d'inspection (coût pour l'équipe de maintenance).

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|
| Prédire une panne à partir de 4 mesures de capteurs | ML classique (classification binaire : régression logistique, forêt aléatoire, gradient boosting) | Une règle à seuils (« température > 80 ») ignore les combinaisons de variables et ne se règle pas sur le coût des erreurs. Un réseau de neurones est inutile pour 4 variables et 5 000 lignes. |

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|
| `data/exemple_pannes.csv` (colonnes utiles : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours` ; cible : `failure`) | Relevés synthétiques fournis par le cours (pas de licence particulière indiquée ; usage pédagogique) | 5 000 lignes, 17,6 % de pannes | Non : aucune donnée sur des personnes, uniquement des mesures de machines |

Données utilisées pour ce TP : `data/exemple_pannes.csv` (MaintAI, 5 000 relevés synthétiques) et `data/cantine_repas.csv` (CantineAI, 340 jours d'école synthétiques), tous deux fournis par le cours. Les fichiers CSV ne sont pas versionnés : voir `data/README.md`.

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score : toujours prédire « pas de panne » (classe la plus fréquente). Sur le jeu de test : accuracy 0,824, rappel 0.
- Métrique principale, et pourquoi : le **rappel**, car une panne manquée (une journée d'arrêt) coûte bien plus qu'une fausse alerte (une heure d'inspection). La **précision** sert de garde-fou pour ne pas noyer l'équipe sous les fausses alertes. L'accuracy est écartée : la baseline en a déjà 0,824 sans détecter aucune panne.
- Critères d'acceptation (métrique, nombre, jeu de données, condition) : **rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test** (20 % des données, soit 1 000 relevés, tenus à l'écart, découpage aléatoire stratifié, graine 42), et le modèle doit faire mieux que la baseline sur le rappel.
- Résultat (voir `docs/choix-modele.md`) : régression logistique `class_weight=balanced`, rappel 0,847 et précision 0,527 : critère atteint, avec une marge faible sur la précision.

## 6. Architecture prévue
## 7. Choix technologiques
## 8. Risques, éthique, confidentialité
## 9. Limites et hors périmètre
