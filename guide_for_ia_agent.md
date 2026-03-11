# Guide Pratique pour Agent IA : Projet MELODI

Ce document a pour but de fournir à tout agent IA intervenant sur le projet **MELODI** les informations essentielles pour comprendre l'architecture, le contexte technique, et les conventions de développement. Lisez ce guide avant d'effectuer des modifications majeures.

## 1. Contexte du Projet

**MELODI** est un ERP (Progiciel de Gestion Intégré) orienté web, modulaire et hautement extensible, entièrement codé en Python. 
Il a été conçu pour permettre l'ajout facile de nouvelles fonctionnalités métiers via un système de **modules** isolés, sans avoir à modifier le cœur de l'application.

## 2. Pile Technologique (Tech Stack)

* **Langage** : Python 3.10+ (Fortement axé sur l'asynchrone avec `async` / `await`).
* **Framework Web** : [Quart](https://quart.palletsprojects.com/) (un framework asynchrone compatible avec l'API Flask).
* **Base de Données** : PostgreSQL (connecté via `asyncpg`).
* **Frontend** : Rendu côté serveur via Jinja2 (`render_template_string`), HTML, CSS, JS classique.
* **Architecture** : Modulaire, basée sur la séparation entre le "Core" (moteur), le module "Base" (système par défaut) et les "Modules" (métiers).

## 3. Structure du Projet

L'arborescence racine du projet est la suivante :

* `core/` : **Le cœur du framework**. Gère le routage (`router.py`), la gestion des modules (`module.py`), la base de données (`db/`), les websockets, les événements, et le cache. *Règle : Ne modifier qu'en cas de nécessité absolue et d'accord explicite de l'utilisateur.*
* `base/` : **Le module principal système**. Fournit le socle commun de l'ERP (connexion, layout d'administration, panneau de configuration, gestionnaire de modules). C'est le premier module chargé par l'application.
* `modules/` : **Dossier de destination pour tous les modules personnalisés**. C'est ici que le développement métier intervient majoritairement. Chaque dossier représente un module et doit contenir au minimum `infos.json` et `module.py`.
* `config/` : Configuration de l'application (fichiers `db_conf.json`, clés secrètes, et un éventuel fichier `instal.lock` qui indique si l'ERP est déjà installé).
* `storage/` : Dossier généré pour stocker les fichiers (uploads, cache, logs).
* `main.py` : Point d'entrée de l'application. Lance le serveur via `core.Application()`.

## 4. Concepts Clés et Conventions

### 4.1. L'Asynchrone par défaut
Puisque le framework sous-jacent est Quart, **presque tout doit être asynchrone**.
* Utilisez toujours `async def` pour les définitions de routes.
* Utilisez `await` pour toute interaction avec la base de données, l'ouverture de fichiers volumineux, ou les appels réseau.

### 4.2. Gestion de la Base de Données (DB)
Il n'y a pas d'ORM lourd par défaut. Le framework possède son connecteur maison (dans `core/db/`).
* Les exécutions SQL se font typiquement de manière asynchrone :
  ```python
  res = await app.db.execute("SELECT * FROM users WHERE id = $1;", user_id)
  ```

### 4.3. Création et Structure d'un Module
Un module placé dans `modules/` doit minimalement comporter :
1. **`infos.json`** : Métadonnées du module (version, name, title, description).
2. **`module.py`** : La classe/logique du module. Il doit utiliser l'API du Core pour s'enregistrer, rajouter des routes au routeur (`app.router` ou `app.api_router`), et se greffer aux événements.

### 4.4. Le Routage
Le projet encapsule le routeur de Quart dans `core.router.WebRouter` et `core.router.APIRouter`. 
Exemple d'ajout de route dans un module :
```python
@app.router.add_route("/ma-route", methods=["GET"])
async def ma_route_handler():
    # Logique de traitement
    return await app.router.render_template_string(...)
```

### 4.5. Événements et Hooks
L'architecture de MELODI supporte un système d'événements (`HookManager`, `ActionManager`, `EventListener`) permettant aux modules de communiquer entre eux de manière découplée et de modifier le comportement sans toucher au code principal.

## 5. 🤖 Règles d'Or pour l'Agent IA

1. **Vérifier avant de Modifier** : Utilisez `list_dir` ou `view_file` pour analyser les définitions réelles de fonctions ou de classes dans le `core/` avant d'émettre des hypothèses.
2. **Respecter la Séparation des Préoccupations** : N'ajoutez pas de logique métier dans `core/`. Si une fonctionnalité spécifique doit être ajoutée, elle doit aller dans `base/` (si liée au système d'exploitation de l'ERP) ou dans un module dédié au sein de `modules/`.
3. **Privilégier l'UI / UX** : Comme spécifié par l'utilisateur dans les directives générales pour les web apps, l'esthétique et les retours asynchrones sont importants. Pas de conception brouillonne : fournissez des SVG utiles, respectez les thèmes modernes et réactifs en place, notamment pour l'interface Admin.
4. **Maintenir l'Asynchronisme** : N'utilisez **jamais** de fonctions bloquantes (`time.sleep()`, ou I/O disque synchrone dans les routes) qui ruineraient les performances de la boucle d'événements (`asyncio`).
5. **Logs de Bugs Communs** : Des erreurs courantes rencontrées dans MELODI incluent l'erreur "Exec format error" (mauvais interpréteur ou droits d'exécution sur certains scripts), et des erreurs liées aux contexts ("Not within a request context" lors de l'usage des websockets). Faites très attention aux contexts asynchrones globaux vs contexts de requêtes HTTP.

---
*Ce fichier est lu comme préambule. Servez-vous des informations décrites ici pour prendre les bonnes décisions architecturales et produire du code robuste et performant sur MELODI.*
