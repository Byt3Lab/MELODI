# MELODI - Framework ERP Modulaire

MELODI est un **ERP (Progiciel de Gestion Intégré) modulaire et hautement extensible**, écrit entièrement en Python. 
Originellement basé sur Flask, l'architecture a été **migrée vers Quart** pour exploiter la puissance de l'asynchrone (`async`/`await`), offrant des performances accrues et une meilleure gestion de la concurrence pour les applications d'entreprise volumineuses.

## 🚀 Fonctionnalités Clés

- **Architecture Modulaire** : Chaque fonctionnalité métier est encapsulée dans un module autonome (`modules/`).
- **Web-Ready et 100% Asynchrone** : Basé sur **Quart** (ASGI), permettant des WebSocket natifs et des requêtes I/O non bloquantes.
- **Extensible sans modifier le cœur** : Système de *Hooks*, d'*Actions*, et d'*Événements* pour interagir entre modules sans couplage fort.
- **Interface d'administration intégrée** : Un module `base` fournit tout le socle (connexion, tableau de bord, gestions des modules).
- **Internationalisation (i18n)** : Support multi-langues natif pour tous les modules.
- **UI Réactive** : Intégration de `MelodiJS` pour le rendu réactif (type Vue.js) sans processus de build lourd.

## 🛠️ Installation et Démarrage

### Prérequis
- **Python 3.10** ou supérieur (Indispensable pour l'asynchrone évolué de Quart).

### Unix (Linux / macOS)

1. **Création de l'environnement et installation**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Démarrage du serveur Quart**
```bash
# Pour le développement
python3 main.py
```
*(Vous pouvez exécuter l'application avec des serveurs ASGI de production comme Hypercorn ou Uvicorn si besoin).*

### Windows

1. **Environnement et installation**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Démarrage**
```powershell
python main.py
```

### Via Docker

```bash
docker compose up --build
```
L'URL d'accès par défaut est : [http://localhost:8080](http://localhost:8080).

## 📂 Structure Principale du Projet

L'organisation des dossiers favorise la stricte séparation entre le socle technique et les règles métiers :

- `core/` : **Le cœur du framework**. Gère le routeur Quart (`WebRouter`, `APIRouter`), la résolution des dépendances (`ModuleManager`), la base de données asynchrone, et les événements (`hooks`, `listeners`). Ce dossier ne doit théoriquement jamais être modifié pour vos besoins métiers.
- `base/` : **Le module système**. Fournit le layout d'administration, l'authentification (`UserService`), la gestion des pages d'accueil, et le gestionnaire des autres modules.
- `modules/` : **Vos modules métiers personnalisés**. C'est ici que vous créerez des dossiers de modules contenant un `infos.json` et un fichier `module.py`.
- `config/` : Configuration globale (ex. `modules_on.json` gérant la liste d'activation).
- `storage/` : Stockage des fichiers statiques générés au runtime, bases SQLite ou logs.
- `docs/` : Documentation approfondie.

## 📖 Documentation Poussée (Développeurs)

Une documentation exhaustive est disponible au format **HTML** :
👉 [Ouvrir la documentation `docs/index.html`](docs/index.html) dans votre navigateur.

Vous y trouverez :
- Le tutoriel de **Création de Module** de A à Z.
- Explication des interfaces **APIRouter** vs **WebRouter**.
- Utilisation des **Middlewares**.
- Manipulation du **Dashboard** (Widgets et Menus).
- Les mécanismes de **Communication Inter-Modules** (ActionManager, HookManager, EventListener).
- Et bien plus !

## 🧾 Licence

Double licence : **AGPL v3** (Usage gratuit communautaire sous même licence) et **Commerciale** (Fermeture du code propriétaire).
Contact : gg.gomsugaetant@gmail.com
