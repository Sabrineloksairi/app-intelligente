# ADR 004 : Choix du modèle et du seuil d'alerte de MaintAI

Date : 19/11/2026 · Auteurs : Sabrine Loksairi

## Contexte
L'équipe de maintenance doit inspecter les machines signalées par MaintAI. Une panne manquée arrête une ligne de production, alors qu'une fausse alerte coûte seulement une inspection : le modèle doit donc détecter le plus de pannes possible. Cinq entraînements ont été enregistrés et comparés dans MLflow, sur la même version des données (v1, 5 000 relevés, 1 000 en test).

| Run MLflow | Modèle | C | Seuil | recall | precision | accuracy |
|---|---|---:|---:|---:|---:|---:|
| `python -m maintai.train` | régression logistique | 1.0 | 0.3 | 0.750 | 0.622 | 0.904 |
| `--C 0.01` | régression logistique | 0.01 | 0.3 | 0.691 | 0.653 | 0.908 |
| `--threshold 0.2` | régression logistique | 1.0 | 0.2 | **0.838** | 0.543 | 0.882 |
| `--model forest` | forêt aléatoire | – | 0.3 | 0.728 | 0.562 | 0.886 |
| `--model forest --threshold 0.2` | forêt aléatoire | – | 0.2 | 0.831 | 0.479 | 0.854 |

## Options étudiées
1. **Régression logistique, seuil 0.3** (réglage actuel) : bon équilibre, précision de 0.622, mais un quart des pannes est manqué (recall 0.750).
2. **Régression logistique, seuil 0.2** : le meilleur recall (0.838), avec une précision encore supérieure à 0.5. Le modèle est simple, rapide et explicable.
3. **Forêt aléatoire** : au même seuil, elle fait moins bien que la régression logistique sur les deux métriques (0.728 contre 0.750 de recall au seuil 0.3 ; 0.479 contre 0.543 de précision au seuil 0.2). Elle est aussi plus lourde à enregistrer et à charger.
4. **Régression logistique très régularisée (`C = 0.01`)** : la meilleure précision, mais le plus mauvais recall (0.691). Elle va à l'encontre de la contrainte principale.

## Décision
Nous retenons la **régression logistique avec `C = 1.0` et un seuil d'alerte de 0.2** (option 2), car c'est le run qui manque le moins de pannes : 83,8 % des pannes du jeu de test sont détectées.

- Run MLflow : `4e9de5c730f54326a000f45c90a443ae`
- Version des données : `data_md5 = 73e0b7cb3c6f795c70c3ddf970b99c15` (fichier `data/sensors.csv.dvc`, commit `33f9244` « Données v1 »)

## Conséquences
- **Ce que nous acceptons :** plus de fausses alertes. La précision passe de 0.622 à 0.543 : environ une alerte sur deux est une fausse alerte, ce qui augmente la charge d'inspection.
- Le seuil doit être réglé dans `MAINTAI_THRESHOLD=0.2`, pour que l'API et la commande `maintai-predict` l'appliquent.
- Le seuil a été choisi sur le jeu de test : il faudra le confirmer sur de nouvelles données, idéalement réelles.
- Le run entraîné sur la v2 des données (8 000 relevés) n'est pas comparable directement : son jeu de test est différent. Il faudra refaire la comparaison des cinq réglages sur la v2 avant de changer de version des données.
