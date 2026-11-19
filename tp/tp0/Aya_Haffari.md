# TP0 : MaintAI

**Nom :** Aya Haffari · **Groupe :** Sabrine Loksairi, Aya Haffari, Mohamed Amine Farih, Yasser Rais

## Le problème

Prédire une panne de machine à partir de 4 capteurs : température, vibration, charge et heures de fonctionnement. Une panne manquée arrête une ligne de production pendant une journée ; une fausse alerte coûte une heure d'inspection. Le critère d'acceptation est : rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test (20 %, aléatoire stratifié, graine 42).

## Résultats sur le jeu de test (1 000 relevés)

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| baseline (toujours « pas de panne ») | 0.824 | 0.000 | 0.000 |
| forêt aléatoire | 0.881 | 0.557 | 0.705 |
| gradient boosting | 0.881 | 0.574 | 0.697 |
| régression logistique | 0.889 | 0.574 | 0.737 |
| régression logistique équilibrée (`class_weight="balanced"`) | 0.839 | 0.847 | 0.527 |

## Mon choix, et pourquoi

Je retiens la **régression logistique équilibrée**. Elle détecte 149 pannes sur 176, contre 101 pour la régression logistique classique : 48 pannes de plus. Elle donne 98 fausses alertes de plus, mais une panne manquée coûte une journée de production, bien plus qu'une heure d'inspection.

La baseline a une accuracy de 0,824 sans détecter aucune panne : l'accuracy ne suffit donc pas pour juger ce problème, et c'est le rappel qui guide mon choix.

## Le critère est-il atteint ?

**Oui** : rappel 0,847 (≥ 0,75) et précision 0,527 (≥ 0,50), mais la marge sur la précision est faible.

## Le même code sur CantineAI

Sans modifier le code, seulement `config.py` : la régression linéaire donne une MAE de 22,2 repas, contre 70,3 pour la baseline, sur les 68 derniers jours (découpage chronologique).

Le travail complet est dans [`haffari/COMPTE_RENDU.md`](haffari/COMPTE_RENDU.md).

## Ce qui reste flou

Je ne sais pas encore comment choisir un modèle sans utiliser le jeu de test pour la sélection (validation croisée ou jeu de validation), ni comment régler le seuil de décision à partir du coût réel d'une panne manquée.
