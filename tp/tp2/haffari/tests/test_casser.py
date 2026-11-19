"""Activité 1 : casser son API. Cinq requêtes invalides et le code HTTP attendu."""
import pytest

HEADERS = {"X-API-Key": "test-key"}
VALID = {"temperature_c": 60.0, "vibration_mm_s": 2.0, "load_pct": 50.0, "runtime_hours": 5000}

CAS = [
    ("champ manquant", "/v1/predict", {k: v for k, v in VALID.items() if k != "load_pct"}, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 500}, 422),
    ("texte au lieu d'un nombre", "/v1/predict", {**VALID, "temperature_c": "chaud"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "couleur": "rouge"}, 422),
    ("mauvaise route", "/v1/predict_tout", VALID, 404),
]


@pytest.mark.parametrize("nom, route, corps, code", CAS, ids=[c[0] for c in CAS])
def test_requete_invalide(client, nom, route, corps, code):
    assert client.post(route, json=corps, headers=HEADERS).status_code == code