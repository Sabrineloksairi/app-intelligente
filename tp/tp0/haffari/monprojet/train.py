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
        average = "binary" if pd.Series(y_test).nunique() <= 2 else "macro"
        scores = {
            "accuracy": accuracy_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred, average=average, zero_division=0),
            "precision": precision_score(y_test, y_pred, average=average, zero_division=0),
            "f1": f1_score(y_test, y_pred, average=average, zero_division=0),
        }
    else:
        scores = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
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
    # 1. Les données, découpées une seule fois : tous les modèles voient le même test.
    df = load_data()
    X_train, X_test, y_train, y_test = split(df)

    # 2. Chaque candidat : préparation + modèle, entraîné sur l'entraînement,
    #    évalué sur le test (jamais vu à l'entraînement).
    results, fitted = {}, {}
    for name, estimator in candidates().items():
        model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", estimator)])
        model.fit(X_train, y_train)
        results[name] = evaluate(model, X_test, y_test)
        fitted[name] = model

    # 3. Le tableau de comparaison, trié selon la métrique principale.
    metric = config.MAIN_METRIC
    higher = HIGHER_IS_BETTER[metric]
    table = pd.DataFrame(results).T.sort_values(metric, ascending=not higher)
    print(f"\nRésultats sur le jeu de test ({len(X_test)} lignes), triés par {metric} :\n")
    print(table.to_string())

    # 4. Le meilleur modèle selon la métrique principale (le sens dépend de la métrique).
    pick = pd.Series({name: scores[metric] for name, scores in results.items()})
    best = pick.idxmax() if higher else pick.idxmin()
    print(f"\nMeilleur modèle selon {metric} : {best}")

    # 5. Sauvegarde du meilleur modèle et des scores.
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted[best], config.MODELS_DIR / "model.joblib")
    summary = {"main_metric": metric, "best": best, "results": results}
    (config.MODELS_DIR / "metrics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Modèle et scores sauvegardés dans {config.MODELS_DIR}")


if __name__ == "__main__":
    main()
