"""Les modèles à comparer.

À vous d'écrire candidates(). Les tests de tests/test_models.py disent ce qui est attendu.
"""
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression

from monprojet import config


def candidates() -> dict:
    """Renvoie un dictionnaire {nom: modèle scikit-learn non entraîné}.

    Attendu :
    - le PREMIER modèle est la baseline : le modèle le plus simple possible
      (DummyClassifier pour une classification, DummyRegressor pour une régression) ;
    - au moins trois vrais modèles ensuite, adaptés à config.TASK ;
    - random_state=config.SEED pour les modèles qui ont du hasard.

    Pistes : sklearn.dummy, sklearn.linear_model, sklearn.ensemble, sklearn.neighbors, sklearn.tree.
    """
    seed = config.SEED
    if config.TASK == "classification":
        return {
            "Baseline (classe la plus fréquente)": DummyClassifier(strategy="most_frequent"),
            "Régression logistique": LogisticRegression(max_iter=1000, random_state=seed),
            "Régression logistique (class_weight=balanced)": LogisticRegression(
                max_iter=1000, class_weight="balanced", random_state=seed),
            "Forêt aléatoire": RandomForestClassifier(n_estimators=200, random_state=seed),
            "Gradient boosting": HistGradientBoostingClassifier(random_state=seed),
        }
    return {
        "Baseline (moyenne)": DummyRegressor(strategy="mean"),
        "Régression linéaire": LinearRegression(),
        "Forêt aléatoire": RandomForestRegressor(n_estimators=200, random_state=seed),
        "Gradient boosting": HistGradientBoostingRegressor(random_state=seed),
    }
