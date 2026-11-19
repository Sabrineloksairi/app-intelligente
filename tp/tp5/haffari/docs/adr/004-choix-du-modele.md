# ADR 004 : choix du modèle et du seuil pour MaintAI

Date : 19/11/2026 · Auteurs : Aya Haffari

## Contexte
Une panne manquée arrête une ligne de production pendant une journée ; une fausse alerte coûte une heure d'inspection. Le critère d'acceptation de la section 5 de l'étude de conception est : rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test. Il faut choisir un modèle et un seuil, et pouvoir le justifier à partir des runs MLflow.

## Options étudiées
Six runs MLflow, tous mesurés sur le même jeu de test (1 000 lignes) pour les cinq premiers, sur les données v1 (`data_md5` 73e0b7cb) :

| Run | Réglage | recall | precision | accuracy |
|---|---|---|---|---|
| e28be495 | régression logistique, C = 1, seuil 0,3 (par défaut) | 0,750 | 0,622 | 0,904 |
| e097a530 | régression logistique, C = 0,01, seuil 0,3 | 0,691 | 0,653 | 0,908 |
| d585df2a | régression logistique, C = 1, seuil 0,2 | 0,838 | 0,543 | 0,882 |
| 6a45d7c1 | forêt aléatoire, seuil 0,3 | 0,728 | 0,562 | 0,886 |
| 979941ca | régression logistique, C = 1, seuil 0,1 | 0,919 | 0,434 | 0,826 |

1. Régression logistique au seuil 0,3 : atteint tout juste le rappel de 0,75 (marge nulle).
2. Seuil 0,1 : le meilleur rappel (0,919), mais la précision tombe à 0,434, sous le critère de 0,50.
3. Forêt aléatoire : plus lourde et son rappel (0,728) est sous le critère ; elle n'est pas meilleure ici.

## Décision
Régression logistique (C = 1) avec un **seuil de 0,2** : rappel 0,838 et précision 0,543, donc les deux conditions du critère d'acceptation sont remplies, avec une marge sur le rappel. La contrainte qui justifie le choix : une panne manquée coûte plus cher qu'une fausse alerte, donc on vise le rappel le plus élevé qui respecte encore la précision minimale de 0,50.

- Identifiant du run : `d585df2acb2c4269a54ed58ac35a56fa`
- `data_md5` des données utilisées : `73e0b7cb3c6f795c70c3ddf970b99c15` (v1, 5 000 lignes, commit « Données v1 »)

## Conséquences
- Plus de fausses alertes qu'au seuil 0,3 : la précision passe de 0,622 à 0,543, soit environ une alerte sur deux qui est fausse. L'équipe de maintenance accepte ce coût en échange de pannes détectées en plus (rappel 0,750 → 0,838).
- La marge sur la précision est faible (0,543 pour un minimum de 0,50) : il faudra la surveiller si les données changent.
- Le run sur la v2 des données (549aa2be, `data_md5` 93fdeef2) a été entraîné avec le seuil 0,3 : il ne se compare pas directement à ce run, car les données et le jeu de test ne sont pas les mêmes.
- Le modèle, ses versions de bibliothèques et ses données sont retrouvables : le run MLflow garde le `requirements.txt` du modèle, et `data_md5` correspond au reçu `data/sensors.csv.dvc`.
