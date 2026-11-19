# Compte rendu TP0 — Séance 3 : étude de conception, projet reproductible, entraîner et comparer des modèles (MaintAI)

**Nom :** Aya Haffari · **Groupe :** G1 5IA · **Date :** 15/11/2026

## 1. Activité 1 — Pourquoi personne d'autre n'obtient 14,2 %

Karim affirme : « ça marche chez moi, on obtient 14,2 % d'alertes ». En ouvrant `analyse.ipynb`, voici ce qui empêche quelqu'un d'autre de retrouver ce chiffre. Lancé de haut en bas sur une autre machine, le notebook s'arrête dès la cellule 2.

| # | Problème | Où (cellules numérotées dès 0, le titre est la cellule 0) | Pourquoi ça empêche de retrouver 14,2 % |
|---|---|---|---|
| 1 | Chemin écrit en dur : `C:/Users/Karim/Desktop/PFE/donnees_capteurs.csv` | cellule 2 | Ce dossier n'existe que chez Karim (`FileNotFoundError`). Le fichier fourni s'appelle d'ailleurs `data/capteurs.csv` : ce n'est pas le même nom. |
| 2 | Cellules exécutées dans le désordre : numéros d'exécution 3, 1, 6, 4, 5, 7 | toutes | Le notebook garde des variables en mémoire : il fonctionne chez Karim à cause de l'ordre dans lequel il a cliqué. De haut en bas, `X_train` est utilisé (cellule 4) avant d'être défini (cellule 5). |
| 3 | Variables jamais définies : `colonnes` et `seuil` | cellules 3 et 6 | Elles ne sont définies dans aucune cellule : elles n'existaient sans doute que dans la mémoire de la session de Karim. Le **seuil** détermine directement la part d'alertes, donc le 14,2 %. |
| 4 | Pas de graine : `train_test_split(..., test_size=0.2)` sans `random_state` | cellule 5 | Le jeu de test change à chaque lancement, donc le pourcentage d'alertes change aussi. |
| 5 | Pas de `requirements.txt` ni de versions de bibliothèques ; `seaborn` est importé mais ne sert à rien | cellule 1 | Une autre version de scikit-learn peut donner d'autres résultats ; l'autre personne ne sait pas quoi installer. |
| 6 | Aucun test, aucune consigne claire : le README dit seulement « lancez toutes les cellules » | README | Personne ne peut vérifier que le résultat est le bon. |

Remède : un environnement virtuel avec `requirements.txt` aux versions épinglées (`==`), les chemins construits dans `config.py`, une graine fixe (`SEED = 42`), des scripts lancés avec `python -m`, et des tests `pytest`. C'est exactement la structure du projet à compléter.

## 2. Activité 2 — Créer l'environnement et lancer le squelette

Commandes : `python -m venv .venv`, activation, `pip install -r requirements.txt`, `python -m pytest`.

Avant d'écrire le code, `python -m pytest` donne : **7 failed, 1 passed** (le seul test qui passe est `test_split_chronologique_teste_sur_le_futur` : comme `SPLIT = "random"`, il ne vérifie rien et se termine tout de suite). C'est normal : rien n'est encore écrit.

**Question 6 — `python monprojet/train.py` : que se passe-t-il, et pourquoi ?**
Python s'arrête avec `ModuleNotFoundError: No module named 'monprojet'`. Quand on lance un fichier directement, Python ajoute à son chemin de recherche le dossier du fichier (`monprojet/`) et non la racine du projet : l'instruction `from monprojet import config` ne trouve donc pas le paquet. Il faut lancer depuis la racine avec `python -m monprojet.train`. Là, l'erreur devient celle qu'on attend avant d'avoir écrit le code : `NotImplementedError: main() n'est pas encore écrite`.

**Quelles fonctions faut-il écrire, et dans quels fichiers ?**

| Fichier | Fonctions à écrire |
|---|---|
| `monprojet/data.py` | `load_data()`, `split()` |
| `monprojet/models.py` | `candidates()` |
| `monprojet/train.py` | `evaluate()`, `main()` |

Sont déjà fournies : `feature_columns()` (dans `data.py`), `build_preprocessing()` et `HIGHER_IS_BETTER` (dans `train.py`), et tout `config.py`.

## 3. Activité 3 — Sections 4 et 5 de l'étude de conception

Les sections 4 et 5 sont écrites dans `docs/etude-de-conception.md`. En résumé :

- **Section 4 — Données** : `data/exemple_pannes.csv`, 5 000 relevés synthétiques fournis par le cours, 17,6 % de pannes, pas de données personnelles.
- **Section 5 — Baseline** : toujours prédire « pas de panne » (accuracy 0,824, rappel 0).
- **Section 5 — Métrique** : le **rappel** (une panne manquée arrête une ligne une journée ; une fausse alerte coûte une heure), avec la précision comme garde-fou.
- **Section 5 — Critère d'acceptation** : rappel ≥ 0,75 et précision ≥ 0,50 sur le jeu de test (20 %, 1 000 relevés, tenus à l'écart).

**Traduction en réglages de `config.py`**

| Réglage | Valeur |
|---|---|
| `DATA_PATH` | `data/exemple_pannes.csv` |
| `TARGET` | `"failure"` |
| `TASK` | `"classification"` |
| `MAIN_METRIC` | `"recall"` |
| `SPLIT` (et `TIME_COLUMN`) | `"random"` (`TIME_COLUMN = None`) |
| `TEXT_COLUMN` | `None` |

**Vérification des critères (auto-vérification, à faire confirmer par le groupe voisin)**

| Pour chaque critère | Oui | Non |
|---|---|---|
| Une métrique est nommée (rappel, précision) | ✔ | |
| Un nombre à atteindre (0,75 et 0,50) | ✔ | |
| Le jeu de données sur lequel on mesure (jeu de test, 20 %) | ✔ | |
| La condition (seuils minimaux, mesurés sur le test tenu à l'écart ; et mieux que la baseline) | ✔ | |

## 4. Étude de cas — MaintAI et CantineAI (sections 1 à 5)

| Section | MaintAI | CantineAI |
|---|---|---|
| **1. Utilisateur principal** | Le responsable de maintenance de l'usine. | Le gestionnaire de la cantine du lycée. |
| **2. Décision et fréquence** | Quelles machines inspecter aujourd'hui. Chaque matin. | Combien de repas commander à la cuisine pour le lendemain. Chaque jour d'école (lundi au vendredi), à 10 h. |
| **2. Coût d'une erreur** | **Panne manquée** : une ligne de production arrêtée pendant une journée (coût pour l'usine). **Fausse alerte** : une heure d'inspection (coût pour l'équipe de maintenance). | **Trop de repas** : repas jetés, environ 15 DH de matière première perdus par repas, et du gaspillage alimentaire (coût pour la cantine). **Pas assez de repas** : des élèves sans déjeuner ou un sandwich de remplacement acheté en urgence, et des plaintes des parents (coût pour les élèves, les parents et le gestionnaire). |
| **3. Approche** | **ML classique** (classification binaire). Pourquoi pas plus simple : une règle à seuils (« température > 80 ») ignore les combinaisons de variables et ne se règle pas sur le coût des erreurs. Pourquoi pas plus complexe : un réseau de neurones est inutile pour 4 variables. | **ML classique** (régression, série temporelle). Pourquoi pas plus simple : reprendre le chiffre de la semaine précédente ignore les examens (394 repas en moyenne les jours d'examens contre 513 les autres jours), les sorties scolaires (421) et les veilles de vacances (440). Pourquoi pas plus complexe : avec 340 jours seulement, le deep learning n'a pas assez de données ; un LLM n'a pas de raison d'être ici. |
| **4. Données** | `data/exemple_pannes.csv` : 5 000 relevés de capteurs synthétiques (température, vibration, charge, heures de fonctionnement), 17,6 % de pannes. Source : cours (pas de licence indiquée, usage pédagogique). Aucune donnée personnelle. | `data/cantine_repas.csv` : 340 jours d'école de septembre 2024 à juin 2026, une ligne par jour, synthétiques (générés pour le cours). Source : cours (pas de licence indiquée, usage pédagogique). Aucune donnée personnelle : ce sont des totaux par jour. |
| **5. Baseline** | Toujours prédire « pas de panne » (classe la plus fréquente). Accuracy **0,824**, rappel **0**. | Le chiffre du même jour de la semaine précédente (colonne `repas_semaine_precedente`, c'est ce que fait le gestionnaire aujourd'hui). Sur les 58 jours du test où elle existe : MAE **79,0 repas**. |
| **5. Métrique principale** | Le **rappel**, parce qu'une panne manquée coûte bien plus qu'une fausse alerte. Avec la **précision** comme garde-fou contre les fausses alertes. | La **MAE en repas** : elle est exprimée dans l'unité du problème, et les deux erreurs (trop ou pas assez) coûtent à peu près autant, donc on les compte toutes les deux. |
| **5. Critère d'acceptation** | Rappel ≥ 0,75 **et** précision ≥ 0,50 sur le jeu de test (20 %, soit 1 000 relevés, tenus à l'écart). | MAE au moins 20 % sous la baseline (soit ≤ 63 repas), sur les 68 derniers jours d'école (découpage chronologique), mesurée sur les jours où la baseline existe. |

**Traduction en réglages de `config.py`**

| Réglage | MaintAI | CantineAI |
|---|---|---|
| `DATA_PATH` | `data/exemple_pannes.csv` | `data/cantine_repas.csv` |
| `TARGET` | `"failure"` | `"repas_servis"` |
| `TASK` | `"classification"` | `"regression"` |
| `MAIN_METRIC` | `"recall"` | `"mae"` |
| `SPLIT` | `"random"` | `"chronologique"` |
| `TIME_COLUMN` | `None` | `"date"` |

**MaintAI : un modèle qui ne prédit jamais de panne aurait quelle accuracy ? Pourquoi cette métrique ne convient-elle pas ?**
Il aurait une accuracy de **0,824** (82,4 % des relevés du test sont sans panne), sans détecter une seule panne : son rappel est de 0. L'accuracy compte toutes les erreurs de la même façon, alors qu'ici une panne manquée coûte une journée d'arrêt et une fausse alerte une heure. Avec 17,6 % de pannes, un modèle inutile paraît donc très bon.

**CantineAI : pourquoi ne faut-il pas tirer les jours de test au hasard ?**
Parce qu'on doit mesurer le modèle comme il sera utilisé : prévoir le futur à partir du passé. Un tirage au hasard met des jours du futur dans l'entraînement, et les jours voisins se ressemblent (le nombre d'inscrits augmente de 620 à 697 sur la période). Pire, la variable `repas_semaine_precedente` d'un jour de test est la cible d'un jour qui peut être dans l'entraînement : le modèle « connaît » déjà la réponse. Le score est alors trop optimiste. Avec la régression linéaire : MAE moyenne d'environ **19 repas** avec 20 tirages au hasard, contre **22 repas** en découpage chronologique, qui est la mesure honnête.

## 5. Lab 2.1 — Résultats sur MaintAI

**Tests.** `python -m pytest` : **10 passed** (les 8 tests fournis + 2 tests ajoutés, voir plus bas).

**Choix de conception**

- `load_data()` lit le CSV, lève une `ValueError` claire si la cible est absente, et retire les lignes sans cible.
- `split()` : découpage aléatoire stratifié (20 %, graine 42), ou chronologique (tri par date, les plus récents en test).
- `candidates()` : la baseline en premier, puis quatre modèles (régression logistique, régression logistique avec `class_weight="balanced"`, forêt aléatoire, gradient boosting). Pour une régression : baseline « moyenne », régression linéaire, forêt aléatoire, gradient boosting.
- `evaluate()` : accuracy, rappel, précision, F1 (ou MAE, RMSE, R²), arrondis à 3 décimales.
- `main()` : mêmes données et même test pour tous les modèles, tableau trié selon la métrique principale, sauvegarde du meilleur modèle (`models/model.joblib`) et des scores (`models/metrics.json`).
- Aucun chemin ni nom de colonne n'est écrit en dur hors de `config.py`.

**`python -m monprojet.train`**

```
Résultats sur le jeu de test (1000 lignes), triés par recall :

                                               accuracy  recall  precision     f1
Régression logistique (class_weight=balanced)     0.839   0.847      0.527  0.649
Gradient boosting                                 0.881   0.574      0.697  0.629
Régression logistique                             0.889   0.574      0.737  0.645
Forêt aléatoire                                   0.881   0.557      0.705  0.622
Baseline (classe la plus fréquente)               0.824   0.000      0.000  0.000

Meilleur modèle selon recall : Régression logistique (class_weight=balanced)
```

**Vérification demandée :** la baseline obtient bien une accuracy de **0,824** et un rappel de **0**.

**Modèle retenu :** la régression logistique avec `class_weight="balanced"`. Rappel 0,847 (149 pannes détectées sur 176), précision 0,527. **Le critère d'acceptation est atteint** (rappel ≥ 0,75 et précision ≥ 0,50), avec une marge faible sur la précision. Le détail et les limites sont dans `docs/choix-modele.md`.

**Pour aller plus loin (fait) :**
- Le modèle avec `class_weight="balanced"` fait passer le rappel de 0,574 à 0,847 : il détecte 48 pannes de plus sur 176, au prix de 98 fausses alertes de plus.
- Deux tests ajoutés dans `tests/test_evaluate.py` : la baseline a un rappel de 0 (et 0,824 d'accuracy) sur MaintAI ; le découpage chronologique met bien les dates les plus récentes dans le test, même si les lignes sont mélangées.

**Le même code sur CantineAI.** J'ai d'abord travaillé avec une version de `cantine_repas.csv` reconstruite à partir du PDF ; j'ai ensuite relancé avec le fichier CSV fourni par le cours (340 lignes, 11 colonnes) : les valeurs sont identiques et les résultats ci-dessous sont les mêmes. Sans toucher au code, seulement avec les réglages de `config.py` ci-dessus : **9 passed, 1 skipped** (le test de la baseline pour la classification est ignoré en régression), et `python -m monprojet.train` donne :

```
Résultats sur le jeu de test (68 lignes), triés par mae :

                        mae    rmse     r2
Régression linéaire  22.239  28.170  0.883
Forêt aléatoire      31.825  41.647  0.745
Gradient boosting    39.015  51.049  0.616
Baseline (moyenne)   70.271  88.416 -0.151
```

Test : du 25/02/2026 au 19/06/2026 ; entraînement : du 09/09/2024 au 24/02/2026. Sur les 58 jours où la baseline « semaine précédente » existe, le modèle a une MAE de 23,3 repas contre 79,0 pour la baseline : environ 70 % de moins, donc le critère de 20 % est largement atteint. Le modèle linéaire gagne sur le gradient boosting parce qu'il n'y a que 272 jours d'entraînement.

## 6. Ticket de sortie — Séance 3

**1. Quelle est la baseline de votre projet, et son score ?**
Pour MaintAI : toujours prédire « pas de panne » (la classe la plus fréquente). Accuracy 0,824 et rappel 0 sur le jeu de test.

**2. Pourquoi évaluer tous les modèles sur le même jeu de test ?**
Pour que la comparaison soit juste : si chaque modèle était mesuré sur des données différentes, on ne saurait pas si un score est meilleur parce que le modèle est meilleur ou parce que son test était plus facile. Ce jeu doit aussi n'avoir jamais été vu à l'entraînement, et le découpage utilise la même graine.

**3. Dans quel cas l'accuracy peut-elle tromper ?**
Quand les classes sont déséquilibrées. Avec 17,6 % de pannes, « jamais de panne » a 82,4 % d'accuracy mais ne détecte aucune panne. Elle trompe aussi quand les deux types d'erreur n'ont pas le même coût, ce qui est le cas ici.

**4. Qu'est-ce qui reste flou pour vous ?**
Comment choisir un modèle sans utiliser le jeu de test pour la sélection (validation croisée ou jeu de validation), et comment régler le seuil de décision à partir du coût réel d'une panne manquée.

## 7. Dépôt GitHub

- Dépôt du groupe : https://github.com/Sabrineloksairi/app-intelligente, dossier `tp/tp0/haffari/`. Mon rapport court est dans `tp/tp0/Aya_Haffari.md`.
- Dépôt direct sur `main`, sans pull request ni tag : c'est la consigne de Sabrine Loksairi pour le TP0, comme pour son propre dossier.
- Aucun CSV, `.env`, `.venv` ni dossier `models/` n'est déposé ; `data/README.md` indique où placer les deux fichiers de données fournis par le cours.
