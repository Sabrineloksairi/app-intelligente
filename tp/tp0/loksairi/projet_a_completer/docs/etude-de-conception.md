# Étude de conception — MaintAI et CantineAI

Groupe : Sabrine Loksairi, Aya Haffari, Mohamed Amine Farih, Yasser Rais · Version : finale · Date : 27/11/2026

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

## 6. Architecture

Le système construit pendant les TP concerne **MaintAI**. CantineAI reste au stade du prototype d'entraînement du TP0 : il n'a ni API ni interface.

```text
 DONNÉES                     ENTRAÎNEMENT                        MODÈLE
 data/sensors.csv  ───────►  python -m maintai.train  ───────►  models/model.joblib
 (versionné par DVC :        (scikit-learn, graine 42)          models/model_info.json
  reçu sensors.csv.dvc            │                             models/metrics.json
  dans Git, fichier dans          │ enregistre chaque run
  .dvc/cache et le stockage)      ▼
                             MLflow : mlflow.db + mlruns/
                             (paramètres, data_md5, métriques,
                              modèle + versions exactes)
                                                                    │ chargé une fois
                                                                    ▼ au démarrage
                                       API FastAPI — uvicorn, http://localhost:8000
                                       • GET  /health          public
                                       • POST /v1/predict      clé X-API-Key obligatoire
                                       • validation Pydantic (bornes physiques) → 422
                                       • modèle absent → 503 ; clé absente/fausse → 401
                                       • CORS : seulement http://localhost:5500
                                       • secrets lus dans .env (jamais dans Git)
                          ┌────────────────────┼─────────────────────────┐
                          │                    │                         │
         Page web HTML + JS (TP2)    Interface Streamlit (TP3)    Commande maintai-predict (TP4)
         http://localhost:5500       http://localhost:8501        terminal, sans API
         le navigateur appelle       le serveur Python appelle    lit le modèle directement
         l'API → CORS s'applique     l'API (httpx) → pas de CORS  (MAINTAI_MODELS_DIR)
```

| Partie | Où elle tourne | Dossier ou fichier |
|---|---|---|
| Données | Disque local ; versions dans le stockage DVC | `data/sensors.csv`, `data/sensors.csv.dvc` |
| Entraînement | Terminal, `python -m maintai.train` | `maintai/train.py`, `maintai/tracking.py` |
| Suivi des runs | `mlflow ui`, port 5000 | `mlflow.db`, `mlruns/` |
| Modèle | Fichiers locaux | `models/` |
| API | uvicorn, port 8000 | `maintai/api/` |
| Page web | `python -m http.server 5500 -d web` | `web/index.html` |
| Interface Streamlit | `python -m streamlit run ui/app.py`, port 8501 | `ui/app.py`, `maintai/client.py` |
| Commande en ligne | Environnement où le wheel est installé | `maintai/cli.py` |

## 7. Choix technologiques

| Outil | Contrainte à laquelle il répond | Ce qu'on a abandonné |
|---|---|---|
| **scikit-learn** (régression logistique) | Données tabulaires de 5 000 lignes et 4 variables ; modèle rapide, explicable, qui atteint le critère de rappel | Le deep learning, disproportionné pour ce volume ; la forêt aléatoire, moins bonne au même seuil (ADR 004) |
| **Seuil d'alerte à 0,2** | Une panne manquée coûte beaucoup plus cher qu'une fausse alerte | Une partie de la précision : environ une alerte sur deux est fausse |
| **FastAPI + Pydantic** | Un contrat d'entrée validé automatiquement (422) et une documentation `/docs` générée sans effort | Flask, qui demande d'écrire la validation et la documentation à la main |
| **Clé API dans l'en-tête `X-API-Key`** | Réserver l'API aux programmes autorisés, sans exposer la clé dans les URL ni les journaux (ADR 003) | Une authentification par utilisateur (OAuth, jetons), trop lourde pour un prototype |
| **CORS limité au port 5500** | Seule la page prévue peut appeler l'API depuis un navigateur | `*`, qui laisserait n'importe quel site utiliser l'API |
| **`.env` hors de Git** | Ne jamais publier de secret | La simplicité d'une clé écrite dans le code |
| **Streamlit** | Une interface de démonstration en une séance, en Python, sans JavaScript | Une interface personnalisée et légère, adaptée au téléphone d'un technicien |
| **Page HTML + JavaScript** | Montrer ce que voit un vrai client navigateur, y compris CORS | Les graphiques et la rapidité de développement de Streamlit |
| **pyproject.toml + wheel** | Livrer le code à un collègue avec une commande installable, `maintai-predict` | Une image Docker, qui n'était pas au programme et demande plus d'outillage |
| **MLflow** | Comparer les entraînements et retrouver le modèle avec les versions exactes des bibliothèques | Un tableau tenu à la main, sans lien avec le modèle enregistré |
| **DVC** (stockage local) | Versionner les données sans les mettre dans Git, et relier chaque run à sa version (`data_md5`) | Un stockage partagé (S3, Drive) : chaque membre a son propre stockage local |
| **Git, pull requests, tags** | Travailler à quatre sans s'écraser, avec une relecture par un coéquipier pour chaque TP | Le dépôt direct sur `main` |

## 8. Risques, éthique, confidentialité

**Secrets**
- La clé API est lue dans `.env`, ignoré par Git ; seul `.env.example` est commité, avec une fausse valeur. Chaque pull request est vérifiée avant fusion : aucun `.env` dans « Files changed ».
- Une clé publiée par erreur resterait dans l'historique : il faudrait alors la changer, pas seulement supprimer le fichier.
- L'API fonctionne en HTTP sur le poste local. En production, il faudrait du HTTPS, sinon la clé circule en clair.

**Coût d'une erreur, et pour qui**
- **Panne manquée** : une ligne de production arrêtée une journée, pour l'usine. C'est l'erreur que le seuil de 0,2 cherche à réduire : 16 % des pannes restent manquées sur le jeu de test.
- **Fausse alerte** : une heure d'inspection perdue, pour l'équipe de maintenance. Environ une alerte sur deux est fausse : la charge d'inspection doit rester supportable.
- **CantineAI** : un repas manquant prive un élève de déjeuner, un repas en trop est jeté. Le modèle sous-estime plus souvent qu'il ne surestime : une marge de sécurité serait nécessaire avant tout usage réel.

**Données personnelles**
- MaintAI ne traite que des relevés de capteurs de machines, et CantineAI des chiffres agrégés par jour : aucune personne n'est identifiée. Les deux jeux sont synthétiques.
- Si les machines étaient associées à des opérateurs, ou les repas à des élèves, le RGPD et la loi marocaine 09-08 s'appliqueraient : il faudrait alors justifier chaque donnée collectée.

**Place de la décision humaine**
- MaintAI **recommande** une inspection, il ne décide pas. Le responsable de maintenance garde la décision et peut inspecter une machine non signalée.
- La probabilité et le seuil sont affichés, pour que l'utilisateur comprenne le niveau de confiance de l'alerte.

## 9. Limites et hors périmètre

**Ce que le système ne fait pas encore**
- Il n'a été évalué que sur des données synthétiques : ses performances sur de vraies machines restent inconnues.
- Le seuil de 0,2 a été choisi sur le jeu de test : il faudrait le confirmer sur une période de validation séparée.
- Il ne surveille pas la dérive des données et ne se ré-entraîne pas automatiquement.
- Le modèle n'est chargé qu'au démarrage de l'API : après un nouvel entraînement, il faut la redémarrer.
- Une seule clé API est partagée par tous les clients : impossible d'en révoquer un seul.
- Le stockage DVC et MLflow sont locaux à chaque poste : le groupe ne partage pas encore les mêmes données ni les mêmes runs.
- La valeur `NaN` envoyée à l'API provoque une erreur 500 au lieu d'un 422.
- L'API n'est pas déployée sur un serveur : tout tourne sur `localhost`.

**Ce qu'il ne fera pas**
- Il ne commande pas les machines et ne déclenche aucune intervention lui-même.
- Il ne diagnostique pas la cause d'une panne : il estime seulement une probabilité.
- Il ne remplace pas la maintenance préventive planifiée.
- CantineAI ne gère ni les stocks ni les commandes aux fournisseurs : il prévoit seulement un nombre de repas.
