# Architecture Overview

MELODI follows a modular architecture designed to be flexible and extensible.

## Core Components

The `core/` directory contains the fundamental building blocks of the application:

- **Application**: The main entry point (`core/application.py`). It initializes the server, database, and modules.
- **Router**: Handles web and API routing (`core/router/`). It wraps Flask's routing system.
- **Module Manager**: Loads and manages modules (`core/module/module_manager.py`).
- **Service Manager**: Manages services that can be shared between modules.
- **Widget Manager**: Manages UI widgets.

## Modules

Modules are self-contained units of functionality located in `modules/`. Each module has:

- `module.py`: Defines the module class inheriting from `ApplicationModule`.
- `infos.json`: Metadata about the module (name, version, dependencies).
- `templates/`: HTML templates.
- `static/`: Static assets (CSS, JS, images).

## Plugins

Plugins are lightweight extensions located in `plugins/`. They are loaded dynamically and can extend existing functionality without modifying the core or modules.

## Database

MELODI uses SQLAlchemy for ORM. The database configuration is handled in `core/db/`.

## Request Lifecycle

1.  Request hits the Flask server.
2.  `FlaskAdapter` routes the request to the appropriate `WebRouter` or `APIRouter`.
3.  The router executes the view function defined in the module.
4.  The view function may interact with services or the database.
5.  A response (HTML or JSON) is returned.
