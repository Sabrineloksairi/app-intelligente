"""Tests ajoutés par nous (pour aller plus loin) : l'évaluation et le découpage chronologique."""
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

from monprojet import config
from monprojet.data import split
from monprojet.data import load_data
from monprojet.train import build_preprocessing, evaluate


def test_la_baseline_a_un_rappel_nul_sur_maintai():
    """Sur MaintAI, « toujours prédire pas de panne » doit avoir un rappel de 0 et 0,824 d'accuracy."""
    if config.TASK != "classification" or config.DATA_PATH.name != "exemple_pannes.csv":
        pytest.skip("test propre aux données MaintAI")
    X_train, X_test, y_train, y_test = split(load_data())
    model = Pipeline([("preparation", build_preprocessing(X_train)),
                      ("modele", DummyClassifier(strategy="most_frequent"))]).fit(X_train, y_train)
    scores = evaluate(model, X_test, y_test)
    assert scores["recall"] == 0.0
    assert scores["accuracy"] == 0.824


def test_le_decoupage_chronologique_met_le_futur_dans_le_test(monkeypatch):
    """Même si les lignes sont mélangées, le test doit contenir les dates les plus récentes."""
    dates = pd.date_range("2025-01-01", periods=50, freq="D")
    df = pd.DataFrame({"date": dates, "x": range(50), "cible": [i % 2 for i in range(50)]}).sample(frac=1, random_state=0)
    monkeypatch.setattr(config, "TARGET", "cible")
    monkeypatch.setattr(config, "FEATURES", None)
    monkeypatch.setattr(config, "SPLIT", "chronologique")
    monkeypatch.setattr(config, "TIME_COLUMN", "date")
    X_train, X_test, _, _ = split(df)
    assert df.loc[X_train.index, "date"].max() < df.loc[X_test.index, "date"].min()
    assert len(X_test) == round(50 * config.TEST_SIZE)
