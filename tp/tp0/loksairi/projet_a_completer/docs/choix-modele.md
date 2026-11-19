# Choix du modèle

Date : 19/11/2026 · Groupe : Sabrine Loksairi, Aya Haffari, Mohamed Amine Farih, Yasser Rais

Tous les chiffres viennent de `python -m monprojet.train` et `python -m monprojet.analyse`, avec la graine 42.

# Partie 1 : MaintAI

## Contexte
Chaque matin, l'équipe de maintenance choisit les machines à inspecter à partir de relevés de capteurs. La métrique principale est le **rappel**, car une panne manquée arrête une ligne pendant une journée, alors qu'une fausse alerte coûte une heure d'inspection.

## Données et découpage
- Fichier : `data/exemple_pannes.csv`, 5 000 relevés, 17,6 % de pannes, aucune valeur manquante.
- Colonnes utilisées : `temperature_c`, `vibration_mm_s`, `load_pct`, `runtime_hours`.
- Découpage aléatoire et stratifié : 4 000 relevés d'entraînement, 1 000 relevés de test (176 pannes).

## Résultats sur le jeu de test

| Modèle | Rappel (métrique principale) | Précision | F1 | Accuracy |
|---|---:|---:|---:|---:|
| Baseline (classe la plus fréquente) | 0,000 | 0,000 | 0,000 | 0,824 |
| Forêt aléatoire | 0,557 | 0,705 | 0,622 | 0,881 |
| Gradient boosting | 0,574 | 0,697 | 0,629 | 0,881 |
| Régression logistique | 0,574 | 0,737 | 0,645 | 0,889 |
| **Régression logistique équilibrée** | **0,847** | **0,527** | **0,649** | **0,839** |

## Décision
**Modèle retenu : la régression logistique équilibrée** (`class_weight="balanced"`).

- Il détecte 149 pannes sur 176 et en manque 27. Il produit 134 fausses alertes.
- Il dépasse la baseline de 0,847 point de rappel, puisque celle-ci ne détecte aucune panne.
- Le rappel gagne 0,273 point par rapport à la régression logistique classique, contre une perte de 0,210 point de précision. Ce compromis est cohérent avec le coût des erreurs.
- **Critère d'acceptation atteint** : rappel 0,847 ≥ 0,75 et précision 0,527 ≥ 0,50 sur le jeu de test.

## Limites
- La précision dépasse le seuil de peu : son intervalle de confiance à 95 % va d'environ 0,47 à 0,59. Le rappel est plus solide, entre environ 0,79 et 0,90.
- Le modèle déclenche 283 alertes pour 1 000 relevés : il faut vérifier que l'équipe peut absorber cette charge.
- Les données sont synthétiques. Les performances sur de vraies machines restent à mesurer.
- Le fichier n'identifie pas les machines : on ne peut pas vérifier qu'une même machine n'apparaît pas à la fois en entraînement et en test.
- Le meilleur modèle a été choisi sur le jeu de test parmi cinq candidats, ce qui rend son score légèrement optimiste.

# Partie 2 : CantineAI

## Contexte
Chaque jour à 10 h, le gestionnaire commande les repas du lendemain. La métrique principale est la **MAE**, exprimée en repas : elle se lit directement et suit le nombre de repas jetés ou manquants.

## Données et découpage
- Fichier : `data/cantine_repas.csv`, 340 jours d'école, aucune cible manquante.
- Colonnes utilisées : toutes sauf `date` et la cible `repas_servis`.
- `repas_semaine_precedente` est vide pour 60 jours, après les vacances. Le prétraitement remplace ces valeurs par la médiane de l'entraînement.
- Découpage chronologique : 272 jours d'entraînement (09/09/2024 au 24/02/2026), 68 jours de test (25/02/2026 au 19/06/2026).

## Résultats sur le jeu de test

| Modèle | MAE en repas (métrique principale) | RMSE | R² |
|---|---:|---:|---:|
| Baseline (moyenne) | 70,271 | 88,416 | -0,151 |
| Gradient boosting | 39,015 | 51,049 | 0,616 |
| Forêt aléatoire | 31,825 | 41,647 | 0,745 |
| **Régression linéaire** | **22,239** | **28,170** | **0,883** |

Comparaison avec la méthode actuelle du gestionnaire, sur les 58 jours de test où le chiffre de la semaine précédente existe :

| Sur 58 jours | Méthode actuelle | Régression linéaire | Évolution |
|---|---:|---:|---:|
| MAE | 79,0 repas | 23,3 repas | -70,4 % |
| Repas préparés en trop | 2 285 | 409 | -82,1 % |
| Repas manquants | 2 295 | 945 | -58,8 % |
| Matière première perdue (15 DH par repas) | 34 275 DH | 6 135 DH | -28 140 DH |
| Jours en sous-estimation | 55,2 % | 65,5 % | +10,3 points |

## Décision
**Modèle retenu : la régression linéaire.**

- Sa MAE est 68,4 % plus basse que celle de la baseline moyenne.
- **Critère d'acceptation atteint** : sa MAE est 70,4 % plus basse que celle de la méthode actuelle, pour un objectif d'au moins 15 %.

## Limites
- Le modèle sous-estime plus souvent qu'il ne surestime, avec un écart moyen de -9,2 repas par jour. Or un repas manquant prive un élève de déjeuner : une marge de sécurité serait à régler sur une période de validation, pas sur ce jeu de test.
- La MAE traite de la même façon un repas en trop et un repas manquant, alors que leurs coûts diffèrent.
- Le test couvre une seule fin d'année scolaire, avec 10 jours d'examens, 2 veilles de vacances et 4 sorties scolaires.
- Les données sont synthétiques, et le découpage unique ne mesure pas la stabilité des résultats dans le temps.
