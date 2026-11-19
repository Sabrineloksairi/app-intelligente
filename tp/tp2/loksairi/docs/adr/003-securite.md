# ADR 003 : Transmission de la clé API et origines autorisées

Date : 19/11/2026 · Auteurs : Sabrine Loksairi

## Contexte
L'API MaintAI ne doit répondre qu'aux programmes autorisés, et la clé ne doit jamais apparaître dans le code ni dans Git. Une page web servie sur `http://localhost:5500` doit pouvoir appeler l'API, contrairement à une page servie depuis une autre origine.

## Décision 1 : où transmettre la clé

### Options étudiées
1. **En-tête `X-API-Key`** : la clé reste séparée des données métier et n'apparaît pas dans l'adresse. Le client doit ajouter un en-tête à chaque appel.
2. **URL** : l'appel est simple à écrire, mais la clé serait enregistrée dans les journaux du serveur et l'historique du navigateur.
3. **Corps JSON** : la clé n'apparaît pas dans l'URL, mais elle se mélange au relevé, change le contrat de `SensorReading` et ne fonctionne pas pour une requête `GET`.

### Décision
Nous transmettons la clé dans l'**en-tête `X-API-Key`**. Choisir l'URL ferait perdre la confidentialité de la clé. Choisir le corps ferait perdre la séparation entre l'authentification et les données.

### Conséquences
- Toutes les routes `/v1` passent par `require_api_key`, tandis que `/health` reste public.
- La clé est lue depuis `.env`, ignoré par Git. Seul `.env.example` est commité, avec une fausse valeur.
- En production, l'API devra être servie en HTTPS, car HTTP transmet l'en-tête en clair.
- Tous les clients partagent une seule clé : il n'est pas possible d'en révoquer un seul sans changer la clé de tous.

## Décision 2 : quelles origines autoriser

### Options étudiées
1. **Liste explicite d'origines** : seules les pages prévues peuvent appeler l'API depuis un navigateur. Chaque nouvelle origine doit être ajoutée à la configuration.
2. **Toutes les origines (`*`)** : aucune configuration n'est nécessaire, mais n'importe quel site pourrait envoyer des requêtes à l'API depuis le navigateur d'un utilisateur.

### Décision
Nous utilisons une **liste explicite**, configurée dans `MAINTAI_CORS_ORIGINS` du fichier `.env` : `http://localhost:5500` et `http://127.0.0.1:5500`. Choisir `*` ferait perdre le contrôle des sites autorisés à utiliser l'API depuis un navigateur.

### Conséquences
- Une page servie sur le port 5501 est bloquée par le navigateur.
- Une nouvelle origine n'est prise en compte qu'après le redémarrage d'uvicorn.
- CORS ne remplace pas l'authentification : `curl.exe` et les autres programmes ne sont pas concernés par cette règle. La clé API reste donc indispensable.
