# MELODI

MELODI est un ERP (progiciel de gestion) multi-sectoriel écrit en Python. Le
projet vise à fournir une base modulaire et extensible pour gérer des modules
métiers (vente, stock, CRM, etc.) avec une architecture de plugins.


## Mission

Fournir une application serveur légère, modulaire et facilement extensible pour
gérer les processus métiers d'une petite à moyenne entreprise. Le projet est
organisé pour permettre l'ajout de modules/plugin sans modifier le coeur.

## Fonctionnalités (exemples)

- Architecture modulaire (plugins/modules séparés)
- Interface web (Flask ou adaptateur similaire)
- Authentification simple
- Modules métiers : vente, stock, CRM (exemples)
- Internationalisation (dossiers `translate/` pour les langues)

## Structure du projet (sommaire)

Quelques fichiers et dossiers importants :

- `main.py`, `wsgi.py` : points d'entrée de l'application
- `core/` : coeur de l'application (routes, gestion des modules, adaptateurs)
- `modules/` : modules métiers (ex : `sell`, `stock`, `crm`)
- `plugins/` : plugins dynamiques (exemples fournis)
- `static/`, `templates/` : ressources web
- `config/` : configurations et fichiers de base
- `requirements.txt` : dépendances Python

## Installation et démarrage

Ces instructions couvrent Linux et Windows. Elles supposent Python 3.10+
installé sur la machine.

### Linux / macOS

1. Créer et activer un environnement virtuel:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Installer les dépendances:

```bash
pip install -r requirements.txt
```

3. Lancer en mode développement (reload manuel selon votre setup):

```bash
python3 main.py
```

4. Déployer en production (exemple avec gunicorn) — Unix seulement:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
```

> Remarque: `gunicorn` n'est pas disponible nativement sur Windows. Sur
> Windows, utilisez un serveur WSGI compatible tel que `waitress` ou déployez
> derrière un reverse-proxy (IIS, nginx sur WSL, etc.).

### Windows

1. Créer et activer un environnement virtuel PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Si vous utilisez l'invite de commandes (cmd.exe):

```cmd
venv\Scripts\activate.bat
```

2. Installer les dépendances:

```powershell
pip install -r requirements.txt
```

3. Lancer l'application en développement:

```powershell
python main.py
```

4. Déploiement en production sur Windows (exemple avec waitress):

```powershell
pip install waitress
waitress-serve --listen=0.0.0.0:8000 wsgi:app
```

## Plugins dynamiques

Le projet contient un dossier `plugins/` où des fichiers Python peuvent être
chargés dynamiquement. Chaque plugin peut exposer une fonction `run()` qui
sera exécutée par le chargeur de plugins. Voir l'exemple de loader dans
`t3.py` fourni avec le dépôt.

## Dépannage rapide

- Si vous avez une erreur d'import, vérifiez que le `PYTHONPATH` ou l'environnement
    virtuel est correct. Activez `venv` avant d'exécuter.
- Pour les problèmes de permission sous Linux, vérifiez les droits du dossier
    et des fichiers (ex : `chmod -R u+rwX .`).

## Tests

Des tests unitaires simples sont présents dans le dossier `tests/`. Pour lancer
les tests:

```bash
source venv/bin/activate   # ou activate sur Windows
pip install -r requirements.txt
pytest -q
```

## Technologies

- Python 3.10+
- Flask (ou adaptateurs similaires)
- Gunicorn (Linux) / Waitress (Windows) pour la mise en production

## 🧾 Licence

Ce projet utilise un **modèle de double licence** :

- **AGPL v3** : pour un usage libre, éducatif ou communautaire  
- **Licence commerciale** : pour les entreprises qui souhaitent intégrer MonERP dans un service propriétaire

👉 Pour plus d'informations ou obtenir une licence commerciale :  
📧 [gg.gomsugaetant@gmail.com]  
🌐 [gomsugaetant.github.io]
