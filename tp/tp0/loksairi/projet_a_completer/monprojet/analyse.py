"""Analyse complémentaire du modèle retenu, sur le jeu de test.

Usage, depuis la racine du projet, après python -m monprojet.train : python -m monprojet.analyse
"""
import joblib
import numpy as np
from sklearn.metrics import confusion_matrix

from monprojet import config
from monprojet.data import load_data, split


def analyse_classification(model, X_test, y_test) -> None:
    """Affiche la matrice de confusion du modèle retenu."""
    vrais_negatifs, fausses_alertes, pannes_manquees, pannes_detectees = confusion_matrix(
        y_test, model.predict(X_test)
    ).ravel()
    print(f"Relevés du jeu de test : {len(y_test)}")
    print(f"Pannes réelles         : {pannes_detectees + pannes_manquees}")
    print(f"Pannes détectées       : {pannes_detectees}")
    print(f"Pannes manquées        : {pannes_manquees}")
    print(f"Fausses alertes        : {fausses_alertes}")
    print(f"Vrais négatifs         : {vrais_negatifs}")


def analyse_regression(model, X_test, y_test) -> None:
    """Compare le modèle à la méthode métier, sur les jours où cette méthode existe."""
    y_reel = y_test.to_numpy()
    y_modele = model.predict(X_test)
    erreur_modele = y_modele - y_reel
    print(f"Jours du jeu de test : {len(y_test)}")
    print(f"MAE du modèle sur tous ces jours : {np.abs(erreur_modele).mean():.1f} repas")

    colonne = config.BUSINESS_BASELINE_COLUMN
    if colonne is None:
        return
    disponible = X_test[colonne].notna().to_numpy()
    erreur_metier = X_test[colonne].to_numpy()[disponible] - y_reel[disponible]
    erreur_comparable = erreur_modele[disponible]
    mae_metier = np.abs(erreur_metier).mean()
    mae_modele = np.abs(erreur_comparable).mean()
    gain = 100 * (mae_metier - mae_modele) / mae_metier

    print(f"\nJours où la méthode métier existe : {disponible.sum()} sur {len(y_test)}")
    print(f"MAE méthode métier ({colonne}) : {mae_metier:.1f} repas")
    print(f"MAE modèle sur les mêmes jours : {mae_modele:.1f} repas")
    print(f"Baisse de la MAE : {gain:.1f} %")
    print(f"Critère (baisse d'au moins 15 %) : {'atteint' if gain >= 15 else 'non atteint'}")
    print("\nSens des erreurs sur ces mêmes jours :")
    print(f"Méthode métier : {(erreur_metier < 0).mean():.1%} de jours en sous-estimation")
    print(f"Modèle         : {(erreur_comparable < 0).mean():.1%} de jours en sous-estimation")
    print(f"Repas préparés en trop, méthode métier : {erreur_metier[erreur_metier > 0].sum():.0f}")
    print(f"Repas préparés en trop, modèle         : {erreur_comparable[erreur_comparable > 0].sum():.0f}")
    print(f"Repas manquants, méthode métier        : {-erreur_metier[erreur_metier < 0].sum():.0f}")
    print(f"Repas manquants, modèle                : {-erreur_comparable[erreur_comparable < 0].sum():.0f}")


def main() -> None:
    _, X_test, _, y_test = split(load_data())
    model = joblib.load(config.MODELS_DIR / "model.joblib")
    if config.TASK == "classification":
        analyse_classification(model, X_test, y_test)
    else:
        analyse_regression(model, X_test, y_test)


if __name__ == "__main__":
    main()
