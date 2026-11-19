# Applications intelligentes — Dépôt du groupe

Dépôt de groupe du module **Développement et déploiement d'applications intelligentes** (EMSI).

## Membres du groupe

| Membre | Dossier personnel dans chaque TP |
|---|---|
| Sabrine Loksairi | `loksairi/` |
| Aya Haffari | `haffari/` |
| Mohamed Amine Farih | `farih/` |
| Yasser Rais | `rais/` |

## Organisation du dépôt

```text
app-intelligente/
├── README.md
├── .gitignore
├── projet/                       ← travail commun du projet
└── tp/
    ├── COMPTE_RENDU_MODELE.md    ← modèle à copier si le TP n'en fournit pas
    ├── tp0/
    │   ├── loksairi/
    │   ├── haffari/
    │   ├── farih/
    │   └── rais/
    ├── tp1/   (mêmes dossiers)
    ├── tp2/   (mêmes dossiers)
    ├── tp3/   (mêmes dossiers)
    └── tp4/   (mêmes dossiers)
```

## Règles de dépôt

1. À partir du TP1, chaque TP est rendu sur **une branche commune** (`tp1`, `tp2`, etc.), par **une pull request relue par un membre du groupe**, puis avec **un tag** (`tp1`, `tp2`, etc.).
2. Chaque membre dépose son travail **uniquement dans son dossier**. Exemple pour Aya et le TP3 : `tp/tp3/haffari/`.
3. Chaque dossier de TP contient **le code du TP et son compte rendu**.
4. Les captures d'écran vont dans un sous-dossier `captures/`.
5. Ne jamais déposer de `.env`, de mot de passe, de clé d'API, d'environnement virtuel (`.venv/`), de données (`data/*.csv`) ni de modèle (`models/`).

## Déposer son travail (PowerShell)

### Première fois seulement

Accepter d'abord l'invitation GitHub reçue par e-mail, puis :

```powershell
git config --global user.name "Prénom Nom"
git config --global user.email "email-du-compte-github@exemple.com"

cd $HOME\Documents
git clone https://github.com/Sabrineloksairi/app-intelligente.git
cd app-intelligente
```

### À chaque TP

L'exemple ci-dessous correspond à Aya pour le TP3. Remplacer `tp3` et `haffari` par le bon TP et le bon dossier.

```powershell
cd $HOME\Documents\app-intelligente

# 1. Se placer sur la branche du TP
git switch main
git pull
git fetch origin
git switch tp3                    # si la branche existe déjà
# git switch -c tp3               # seulement si elle n'existe pas encore

# 2. Copier son travail dans son dossier (ou le faire depuis l'explorateur)
Copy-Item -Recurse "C:\chemin\vers\mon_tp3\*" "tp\tp3\haffari\"

# 3. Enregistrer uniquement son dossier
git add tp/tp3/haffari
git status                        # .env, .venv, models et les CSV ne doivent pas apparaître
git commit -m "TP3 - Haffari : code et compte rendu"

# 4. Envoyer sur GitHub
git push -u origin tp3
```

Si `git push` affiche `rejected` ou `fetch first`, un autre membre vient de déposer :

```powershell
git pull --rebase origin tp3
git push -u origin tp3
```

### Rendre le TP

Quand les quatre membres ont déposé leur travail sur la branche :

1. Sur GitHub, un membre ouvre **une pull request** de `tp3` vers `main`.
2. Un autre membre lance les tests, relit les changements, écrit au moins un commentaire et clique sur **Approve**.
3. La pull request est fusionnée avec **Create a merge commit**.
4. Un seul membre crée le tag :

```powershell
git switch main
git pull
git tag tp3
git push --tags
```

### Problèmes fréquents

| Message ou situation | Solution |
|---|---|
| `rejected` ou `fetch first` au moment du push | Lancer `git pull --rebase origin <branche>`, puis `git push`. |
| `ModuleNotFoundError` | Activer le `.venv` du dossier du TP dans ce terminal. |
| `Permission denied` ou `403` | L'invitation au dépôt n'a pas été acceptée, ou le compte connecté n'est pas le bon. |
