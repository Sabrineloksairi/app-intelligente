# ADR 002 : Validation des relevés et modèle absent

Date : 15/11/2026 · Auteurs : Aya Haffari

## Contexte
L'API MaintAI reçoit des relevés de capteurs envoyés par d'autres programmes, que nous ne contrôlons pas. Une valeur impossible (500 °C) ne doit jamais atteindre le modèle, et l'API doit rester claire quand le modèle n'a pas été entraîné.

## Options étudiées
1. Bornes physiques dans le schéma Pydantic (`Field(ge=..., le=...)`) : le refus est automatique (422), documenté dans `/docs`, et écrit une seule fois. Inconvénient : il faut choisir des bornes réalistes.
2. Bornes copiées sur les données (minimum et maximum de `sensors.csv`) : simple à calculer, mais une machine réelle un peu plus chaude que les données d'entraînement serait refusée à tort.
3. Aucun contrôle à l'entrée : le modèle recevrait n'importe quoi et renverrait une probabilité sans sens, sans que personne ne s'en aperçoive.

## Décision
Bornes physiques dans le schéma Pydantic :

| Variable | Minimum | Maximum | Justification |
|---|---|---|---|
| `temperature_c` | -40 | 150 | Plage d'un moteur industriel : du froid extrême d'un entrepôt à la surchauffe avant destruction de l'isolation. |
| `vibration_mm_s` | 0 | 50 | Une vitesse de vibration n'est jamais négative ; au-delà d'environ 11 mm/s la machine est en zone dangereuse, 50 laisse une marge pour un capteur déréglé sans accepter l'absurde. |
| `load_pct` | 0 | 120 | Pourcentage de la charge nominale : une surcharge temporaire jusqu'à 120 % est possible. |
| `runtime_hours` | 0 | 100000 | Environ 11 ans de marche continue, au-delà de la durée de vie d'une machine. |

Modèle absent : l'API démarre quand même et répond **503** à `/v1/predict`, avec un message qui dit quoi faire (entraîner le modèle, puis relancer). `/health` indique `model_loaded: false`.

## Conséquences
- Un relevé invalide est refusé avant le modèle (422), avec un message précis, et les bornes sont visibles dans `/docs`.
- Si une machine dépasse une borne dans la réalité (par exemple 130 % de charge), les relevés seront refusés : il faudra revoir les bornes avec un technicien.
- Pour le modèle absent, répondre 503 garde l'API en vie : `/health` et `/docs` fonctionnent, et un tableau de bord peut afficher « service indisponible ». Ce qu'on perd : l'erreur n'apparaît qu'à la première requête, pas au démarrage. Refuser de démarrer serait plus visible pour l'équipe, mais couperait aussi `/health` et la documentation, et un orchestrateur relancerait l'API en boucle.
- À surveiller : le nombre de 422 reçus (des bornes trop strictes ou un capteur défectueux) et la présence du modèle au déploiement.
