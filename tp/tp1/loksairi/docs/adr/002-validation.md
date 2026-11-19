# ADR 002 : Validation des relevés et comportement quand le modèle est absent

Date : 19/11/2026 · Auteurs : Sabrine Loksairi

## Contexte
L'API MaintAI reçoit des relevés envoyés par d'autres programmes. Une valeur impossible doit être refusée avant d'atteindre le modèle, sans rejeter une machine réelle en très mauvais état, car c'est justement le cas à signaler. L'API doit aussi réagir clairement si le modèle n'a pas encore été entraîné.

## Décision 1 : les bornes de chaque variable

### Options étudiées
1. **Reprendre le minimum et le maximum des données** : simple, mais une machine un peu plus chaude que celles de l'entraînement serait refusée.
2. **Fixer des bornes physiques** : seules les valeurs impossibles ou manifestement dues à un capteur défaillant sont refusées. Les bornes demandent une justification.

### Décision
Nous retenons les **bornes physiques**.

| Variable | Minimum | Maximum | Justification |
|---|---:|---:|---|
| `temperature_c` | -40 | 150 | Bornes données par l'énoncé : -40 °C couvre un démarrage à froid, et 150 °C correspond à une surchauffe extrême. |
| `vibration_mm_s` | 0 | 100 | Une vitesse efficace ne peut pas être négative. La zone D de la norme ISO 20816-3 commence entre 4,5 et 7,1 mm/s sur support rigide : 100 mm/s laisse donc passer les machines très dégradées. |
| `load_pct` | 0 | 150 | 0 % correspond à une machine à vide. Une surcharge au-delà de 100 % de la capacité nominale est possible ; 150 % sert de limite aux lectures aberrantes. |
| `runtime_hours` | 0 | 200 000 | Un compteur d'heures ne peut pas être négatif. 200 000 h représentent environ 23 ans de fonctionnement continu. Le type `float` accepte les fractions d'heure. |

### Conséquences
- Une valeur hors bornes reçoit un code 422 et n'atteint jamais le modèle.
- Une valeur acceptée peut sortir du domaine d'entraînement, par exemple 150 000 h alors que les données s'arrêtent à 20 000 h. La prédiction est alors une extrapolation à surveiller.
- Les bornes sont générales : elles devront être affinées si l'API sert des machines de types très différents.
- La valeur non standard `NaN` provoque aujourd'hui une erreur 500, car FastAPI ne peut pas la recopier dans sa réponse d'erreur. Elle n'atteint pas le modèle, mais un gestionnaire d'erreur dédié serait nécessaire pour renvoyer un 422.

## Décision 2 : modèle absent

### Options étudiées
1. **Démarrer et répondre 503 sur `/v1/predict`** : `/health` reste disponible et indique `model_loaded: false`, ce qui facilite le diagnostic. En contrepartie, le service paraît démarré alors qu'il ne peut pas prédire.
2. **Refuser de démarrer** : le problème est visible immédiatement au déploiement. En contrepartie, plus aucune route ne répond : on perd `/health`, `/docs` et le message expliquant quoi faire.

### Décision
Nous retenons le **démarrage avec une réponse 503**. Le client comprend que sa requête est correcte, que le service est indisponible, et le message indique la commande à lancer.

### Conséquences
- `/health` doit être surveillé : un code 200 ne suffit pas, il faut vérifier `model_loaded`.
- Après l'entraînement, il faut redémarrer l'API, car le modèle n'est chargé qu'au démarrage.
