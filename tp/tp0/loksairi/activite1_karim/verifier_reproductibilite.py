"""Activité 1 : mesure l'effet de l'absence de graine dans le projet de Karim.

Le notebook de Karim ne définit ni `colonnes` ni `seuil`. Ce script fait donc deux hypothèses :
les trois capteurs sont les variables d'entrée, et le seuil d'alerte vaut 0,5.

Usage : python verifier_reproductibilite.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).resolve().parent / "data" / "capteurs.csv"
COLONNES = ["temperature", "vibration", "charge"]   # hypothèse
CIBLE = "panne"
SEUIL = 0.5                                         # hypothèse
NB_GRAINES = 200

df = pd.read_csv(DATA_PATH)
X, y = df[COLONNES], df[CIBLE]

taux = []
for graine in range(NB_GRAINES):
    X_train, X_test, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=graine)
    model = LogisticRegression().fit(X_train, y_train)
    taux.append((model.predict_proba(X_test)[:, 1] >= SEUIL).mean())
taux = np.array(taux)

print(f"Lignes du fichier : {len(df)} ; lignes de test : {len(X_test)}")
print(f"Pas possible entre deux taux d'alertes : {100 / len(X_test):.1f} point")
print(f"Taux d'alertes sur {NB_GRAINES} graines : minimum {taux.min():.1%}, "
      f"moyenne {taux.mean():.1%}, maximum {taux.max():.1%}")
print(f"14,2 % est-il atteignable avec ce fichier ? {'oui' if (len(X_test) * 0.142).is_integer() else 'non'}")
