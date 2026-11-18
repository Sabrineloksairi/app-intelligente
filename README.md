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
    ├── COMPTE_RENDU_MODELE.md    ← modèle à copier pour chaque TP
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

1. Chaque membre dépose son travail **uniquement dans son dossier**. Exemple pour Aya et le TP1 : `tp/tp1/haffari/`.
2. Chaque dossier de TP contient **le code du TP et son compte rendu** (`COMPTE_RENDU.md` ou `COMPTE_RENDU.pdf`).
3. Les captures d'écran vont dans un sous-dossier `captures/`.
4. Ne jamais déposer de mot de passe, de clé d'API, de fichier `.env` ni d'environnement virtuel (`venv/`, `.venv/`).
5. GitHub refuse les fichiers de plus de 100 Mo : pour un gros modèle ou jeu de données, mettre un lien dans le compte rendu.

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

### À chaque dépôt

L'exemple ci-dessous correspond à Aya pour le TP1. Remplacer `tp1` et `haffari` par le bon TP et le bon dossier.

```powershell
cd $HOME\Documents\app-intelligente

# 1. Récupérer le travail des autres
git pull --rebase origin main

# 2. Copier ses fichiers dans son dossier (ou le faire depuis l'explorateur)
Copy-Item -Recurse "C:\chemin\vers\mon_tp1\*" "tp\tp1\haffari\"

# Si le TP copié contenait son propre dépôt Git, retirer ce dossier caché de la copie
Remove-Item -Recurse -Force "tp\tp1\haffari\.git" -ErrorAction SilentlyContinue

# 3. Enregistrer uniquement son dossier
git add tp/tp1/haffari
git status
git commit -m "TP1 - Haffari : code et compte rendu"

# 4. Envoyer sur GitHub
git pull --rebase origin main
git push origin main
```

### Problèmes fréquents

| Message ou situation | Solution |
|---|---|
| `rejected` ou `fetch first` au moment du push | Un autre membre vient de déposer : relancer `git pull --rebase origin main`, puis `git push origin main`. |
| `Permission denied` ou `403` | L'invitation au dépôt n'a pas été acceptée, ou le compte connecté n'est pas le bon. |
