"""Configuration du projet : c'est le seul fichier à adapter à votre sujet.

Deux jeux de données sont réglés ici. MaintAI est utilisé par défaut.
Pour CantineAI, dans PowerShell : $env:PROFIL = "cantineai"
Pour revenir à MaintAI : Remove-Item Env:PROFIL
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROFIL = os.environ.get("PROFIL", "maintai")

FEATURES = None              # None = toutes les colonnes sauf la cible ; sinon une liste de noms
TEXT_COLUMN = None           # le nom d'une colonne de texte libre (réclamations…), sinon None
TEST_SIZE = 0.2              # part des données gardée pour le test
SEED = 42                    # graine : mêmes résultats à chaque lancement

if PROFIL == "maintai":
    DATA_PATH = ROOT / "data" / "exemple_pannes.csv"
    TARGET = "failure"
    TASK = "classification"
    MAIN_METRIC = "recall"
    SPLIT = "random"
    TIME_COLUMN = None
    BUSINESS_BASELINE_COLUMN = None     # pas de méthode métier chiffrée pour MaintAI
    MODELS_DIR = ROOT / "models"
elif PROFIL == "cantineai":
    DATA_PATH = ROOT / "data" / "cantine_repas.csv"
    TARGET = "repas_servis"
    TASK = "regression"
    MAIN_METRIC = "mae"
    SPLIT = "chronologique"
    TIME_COLUMN = "date"
    BUSINESS_BASELINE_COLUMN = "repas_semaine_precedente"   # la méthode actuelle du gestionnaire
    MODELS_DIR = ROOT / "models" / "cantineai"
else:
    raise ValueError(f"PROFIL inconnu : « {PROFIL} » (attendu : maintai ou cantineai)")
