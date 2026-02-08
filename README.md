# MELODI

MELODI est un ERP (progiciel de gestion) modulaire et extensible écrit en Python. Il offre une architecture robuste pour développer des applications métiers sur mesure grâce à son système de plugins et de modules.

## 🚀 Fonctionnalités Clés

- **Architecture Modulaire** : Système de modules isolés et plugins dynamiques.
- **Web-Ready** : Interface web intégrée basée sur **Quart** (Asynchrone).
- **Extensible** : Ajoutez des fonctionnalités sans modifier le cœur.
- **Base de Données** : Gestion simplifiée avec ORM intégré.
- **Async** : Support natif de l'asynchrone (async/await) pour des performances accrues.
- **Internationalisation** : Support multi-langues natif.

## 🛠️ Installation et Démarrage

### Prérequis
- Python 3.10 ou supérieur

### Linux / macOS

1. **Installation**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Démarrage**
```bash
python3 main.py
```

### Windows

1. **Installation**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Démarrage**
```powershell
python main.py
```

### Docker

1. **Construction et Démarrage**
```bash
docker compose up --build
```

2. **Accès**
L'application sera accessible à l'adresse [http://localhost:8080](http://localhost:8080).

## 📂 Structure du Projet

- `core/` : Le cœur du framework (Router, ModuleManager, DB, etc.)
- `modules/` : Vos modules métiers personnalisés
- `config/` : Fichiers de configuration
- `docs/` : Documentation développeur

## 📖 Documentation

Pour une documentation détaillée sur l'architecture et la création de modules, ouvrez `docs/index.html` dans votre navigateur.

## 🧾 Licence

Double licence : **AGPL v3** (communautaire) et **Commerciale** (entreprise).
Contact : [gg.gomsugaetant@gmail.com]
