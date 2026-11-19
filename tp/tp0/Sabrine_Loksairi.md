# TP0 : MaintAI

**Nom :** Sabrine Loksairi · **Groupe :** Sabrine Loksairi, Aya Haffari, Mohamed Amine Farih, Yasser Rais

## Le problème

Prédire une panne à partir de 4 capteurs : température, vibration, charge et heures de fonctionnement. Une panne manquée arrête une ligne pendant une journée, alors qu'une fausse alerte coûte une heure d'inspection.

## Résultats sur le jeu de test

| Modèle | Accuracy | Rappel | Précision |
|---|---:|---:|---:|
| baseline | 0.824 | 0.000 | 0.000 |
| forêt aléatoire | 0.881 | 0.557 | 0.705 |
| gradient boosting | 0.881 | 0.574 | 0.697 |
| régression logistique | 0.889 | 0.574 | 0.737 |
| régression logistique équilibrée | 0.839 | 0.847 | 0.527 |

## Mon choix, et pourquoi

Je retiens la **régression logistique équilibrée** (`class_weight="balanced"`).

- Elle a le meilleur rappel : elle détecte 149 pannes sur 176.
- Elle produit plus de fausses alertes (134), mais une fausse alerte coûte beaucoup moins cher qu'une panne manquée.
- La baseline a une bonne accuracy (0,824) sans détecter aucune panne : l'accuracy ne suffit donc pas ici.

## Le critère (rappel >= 0,75) est-il atteint ?

**Oui avec le modèle retenu** : son rappel est de 0,847. La régression logistique classique ne l'atteint pas, avec un rappel de 0,574. Sa précision de 0,527 reste proche de l'objectif de 0,50 que nous nous étions fixé.

Le travail complet est dans [`loksairi/COMPTE_RENDU.md`](loksairi/COMPTE_RENDU.md).

## Ce qui reste flou

À compléter par Sabrine.
