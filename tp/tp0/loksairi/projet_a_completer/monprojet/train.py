"""Entraîne chaque modèle candidat, l'évalue sur le jeu de test et les compare.

Usage, depuis la racine du projet : python -m monprojet.train
"""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates

HIGHER_IS_BETTER = {"accuracy": True, "recall": True, "precision": True, "f1": True,
                    "mae": False, "rmse": False, "r2": True}


def build_preprocessing(X: pd.DataFrame) -> ColumnTransformer:
    """Prépare les colonnes : nombres mis à l'échelle, catégories encodées, texte vectorisé. (Fournie.)"""
    text = [config.TEXT_COLUMN] if config.TEXT_COLUMN else []
    numeric = [c for c in X.columns if c not in text and pd.api.types.is_numeric_dtype(X[c])]
    categorical = [c for c in X.columns if c not in text and c not in numeric]
    steps = []
    if numeric:
        steps.append(("nombres", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric))
    if categorical:
        steps.append(("categories", make_pipeline(SimpleImputer(strategy="most_frequent"),
                                                  OneHotEncoder(handle_unknown="ignore")), categorical))
    if text:
        steps.append(("texte", TfidfVectorizer(), config.TEXT_COLUMN))
    return ColumnTransformer(steps, sparse_threshold=0)


def evaluate(model, X_test, y_test) -> dict:
    """Prédit sur le jeu de test et renvoie un dictionnaire {nom de la métrique: valeur}.

    Attendu :
    - classification : "accuracy", "recall", "precision", "f1"
      (average="binary" s'il y a deux classes, "macro" sinon ; zero_division=0) ;
    - régression : "mae", "rmse", "r2" ;
    - des float, arrondis à 3 décimales.

    Pistes : model.predict(X_test) ; les fonctions importées en haut du fichier ; np.sqrt.
    """
    y_pred = model.predict(X_test)

    if config.TASK == "classification":
        average = "binary" if pd.Series(y_test).nunique() == 2 else "macro"
        scores = {
            "accuracy": accuracy_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred, average=average, zero_division=0),
            "precision": precision_score(y_test, y_pred, average=average, zero_division=0),
            "f1": f1_score(y_test, y_pred, average=average, zero_division=0),
        }
    else:
        scores = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
        }
    return {name: round(float(value), 3) for name, value in scores.items()}


def main() -> None:
    """Entraîne chaque candidat, l'évalue, compare, et sauvegarde.

    Plan :
    1. charger les données (load_data) et les découper (split) ;
    2. pour chaque (nom, estimateur) de candidates() :
       model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", estimateur)]),
       l'entraîner sur X_train, y_train, puis l'évaluer avec evaluate() ;
    3. afficher un tableau de comparaison (pd.DataFrame(resultats).T), trié selon config.MAIN_METRIC ;
    4. trouver le meilleur modèle selon config.MAIN_METRIC (HIGHER_IS_BETTER dit dans quel sens) ;
    5. créer config.MODELS_DIR, y sauvegarder le meilleur modèle (joblib.dump) dans model.joblib,
       et écrire metrics.json : {"main_metric": ..., "best": nom du meilleur, "results": {nom: scores}}.
    """
    # 1. Charger et découper
    X_train, X_test, y_train, y_test = split(load_data())

    # 2. Entraîner sur X_train, évaluer sur X_test
    resultats, modeles = {}, {}
    for nom, estimateur in candidates().items():
        model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", estimateur)])
        model.fit(X_train, y_train)
        resultats[nom] = evaluate(model, X_test, y_test)
        modeles[nom] = model

    # 3. Afficher le tableau de comparaison
    metrique = config.MAIN_METRIC
    plus_haut_est_mieux = HIGHER_IS_BETTER[metrique]
    tableau = pd.DataFrame(resultats).T.sort_values(metrique, ascending=not plus_haut_est_mieux)
    print(f"Comparaison sur le jeu de test ({len(X_test)} lignes), triée selon {metrique} :")
    print(tableau.to_string())

    # 4. Trouver le meilleur modèle
    scores = tableau[metrique]
    meilleur = scores.idxmax() if plus_haut_est_mieux else scores.idxmin()
    print(f"\nMeilleur modèle selon {metrique} : {meilleur} ({scores[meilleur]})")

    # 5. Sauvegarder le modèle et les métriques
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(modeles[meilleur], config.MODELS_DIR / "model.joblib")
    metrics = {"main_metric": metrique, "best": meilleur, "results": resultats}
    (config.MODELS_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
