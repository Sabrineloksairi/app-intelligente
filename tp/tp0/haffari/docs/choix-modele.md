# Choix du modèle

Date : 15/11/2026 · Groupe : G1 5IA · Rédigé par Aya Haffari

## Contexte
MaintAI prédit, pour chaque relevé de capteurs, si la machine va tomber en panne (1) ou non (0). Chaque matin, l'équipe de maintenance choisit les machines à inspecter. Une panne manquée arrête une ligne de production pendant une journée ; une fausse alerte coûte une heure d'inspection.

**Métrique principale : le rappel** (la part des vraies pannes qu'on détecte), car le coût d'une panne manquée est bien plus élevé que celui d'une fausse alerte. Elle est complétée par la **précision**, pour ne pas noyer l'équipe sous les fausses alertes (section 5 de l'étude de conception).

## Données et découpage
- Fichier : `data/exemple_pannes.csv`, 5 000 relevés synthétiques, 17,6 % de pannes.
- Variables utilisées : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`. Cible : `failure`.
- Découpage aléatoire, stratifié sur la cible, graine 42 : 4 000 relevés pour l'entraînement, **1 000 pour le test** (dont 176 pannes, soit 17,6 % comme dans l'entraînement).
- Tous les modèles sont entraînés sur les mêmes 4 000 lignes et évalués sur les mêmes 1 000 lignes.

## Résultats sur le jeu de test

Résultats obtenus avec `python -m monprojet.train` (scikit-learn 1.8.0, graine 42), triés par rappel :

| Modèle | Rappel (métrique principale) | Précision | Accuracy | F1 |
|---|---|---|---|---|
| **Régression logistique (class_weight=balanced)** | **0,847** | 0,527 | 0,839 | 0,649 |
| Gradient boosting | 0,574 | 0,697 | 0,881 | 0,629 |
| Régression logistique | 0,574 | 0,737 | 0,889 | 0,645 |
| Forêt aléatoire | 0,557 | 0,705 | 0,881 | 0,622 |
| Baseline (classe la plus fréquente) | 0,000 | 0,000 | 0,824 | 0,000 |

Ce que cela représente sur les 176 pannes du jeu de test :

| Modèle | Pannes détectées | Pannes manquées | Fausses alertes |
|---|---|---|---|
| Régression logistique (balanced) | 149 | 27 | 134 |
| Régression logistique | 101 | 75 | 36 |
| Gradient boosting | 101 | 75 | 44 |
| Forêt aléatoire | 98 | 78 | 41 |
| Baseline | 0 | 176 | 0 |

## Décision
**Modèle retenu : la régression logistique avec `class_weight="balanced"`.**

- **Il bat la baseline** : la baseline a une accuracy de 0,824 mais un rappel de 0, car elle ne détecte aucune panne. Le modèle retenu détecte 149 pannes sur 176 (rappel 0,847).
- **Il a le meilleur rappel**, la métrique qui compte ici : 0,847, contre 0,557 à 0,574 pour les trois autres modèles. Il manque 27 pannes, contre 75 à 78 pour les autres.
- **Le critère d'acceptation est atteint** : rappel ≥ 0,75 (0,847) et précision ≥ 0,50 (0,527) sur le jeu de test.
- **Il a la plus faible accuracy parmi les vrais modèles** (0,839), et c'est normal : il déclenche plus d'alertes (283 alertes contre 137 à 145 pour les autres). On accepte ces fausses alertes (une heure chacune) pour éviter des pannes (une journée chacune). Pour 1 000 relevés, il évite 48 à 51 pannes manquées de plus que les autres, au prix de 90 à 98 fausses alertes de plus.
- Le modèle est un modèle linéaire simple : il est rapide, stable et facile à expliquer à l'équipe de maintenance.

## Limites
- **La marge sur la précision est faible** : 0,527 pour un seuil de 0,50. Avec seulement 176 pannes dans le test, l'incertitude est grande : par rééchantillonnage (bootstrap), l'intervalle à 95 % est d'environ **0,79 à 0,90 pour le rappel** et **0,47 à 0,58 pour la précision**. Le critère sur la précision pourrait donc ne pas tenir sur d'autres données.
- **Le test a servi à choisir le modèle**, en plus de le mesurer : on a gardé le meilleur rappel sur le test. Le score annoncé est donc un peu optimiste. Une validation croisée, ou un troisième jeu mis de côté, donnerait une estimation plus honnête.
- **Données synthétiques** : elles ne disent pas comment le modèle se comporterait sur de vraies machines (capteurs bruités, valeurs manquantes, nouvelles machines, dérive dans le temps).
- **Un seul découpage et une seule graine** : un autre découpage donnerait des chiffres un peu différents.
- **Le seuil de décision n'est pas réglé** : on utilise le seuil par défaut de 0,5. Un seuil choisi à partir du coût réel (panne manquée contre fausse alerte) pourrait améliorer le compromis rappel / précision.
- **Les coûts sont comparés sans chiffres** (une journée contre une heure) : sans le coût réel en dirhams, on ne peut pas dire quel nombre de fausses alertes reste acceptable.
