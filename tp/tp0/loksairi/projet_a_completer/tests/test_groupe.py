"""Test ajouté par le groupe (partie « pour aller plus loin » du Lab 2.1)."""
import pytest
from sklearn.pipeline import Pipeline

from monprojet import config
from monprojet.data import load_data, split
from monprojet.models import candidates
from monprojet.train import build_preprocessing, evaluate


@pytest.mark.skipif(config.TASK != "classification", reason="le rappel ne concerne que la classification")
def test_la_baseline_a_un_rappel_nul():
    X_train, X_test, y_train, y_test = split(load_data())
    baseline = next(iter(candidates().values()))
    model = Pipeline([("preparation", build_preprocessing(X_train)), ("modele", baseline)])
    model.fit(X_train, y_train)
    assert evaluate(model, X_test, y_test)["recall"] == 0.0
