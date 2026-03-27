# MELODI AI Agent Guidelines

Welcome to the MELODI project! This `AGENTS.md` provides critical context, architectural rules, and guidelines for any AI coding agent working on this repository.

## 1. Project Overview
**MELODI** is a modular, extensible, and web-oriented ERP (Enterprise Resource Planning) entirely coded in Python. 
It uses a robust core-module architecture where the engine (Core) handles routing, database connections, and events, while the main module (Base) provides standard ERP foundations (admin layout, auth, module manager). All new functional business logic is added as independent, hot-pluggable modules.

## 2. Tech Stack
- **Backend Language**: Python 3.10+ (Heavily asynchronous via `async`/`await`).
- **Web Framework**: [Quart](https://quart.palletsprojects.com/) (An async framework compatible with the Flask API).
- **Database**: PostgreSQL (connected via `asyncpg`, managed by the custom `core/db/database.py` wrapper).
- **Frontend**: Server-side rendering with Jinja2 (`render_template_string`), standard HTML/CSS/JS.

## 3. Architecture & Directory Structure
When navigating and editing the project, respect these directories:
- `core/`: The framework engine (Routing, Modules Manager, DB, WebSockets, Events). **Rule: Do not modify unless absolutely necessary and explicitly requested by the user.**
- `base/`: The default system module. Handles user authentication, admin layouts, and configuration.
- `modules/`: Target directory for all custom business modules. Each module must contain at minimum:
  - `infos.json` (metadata)
  - `module.py` (logic, mounting routes, registering hooks)
- `config/`: App configuration (`db_conf.json`, `instal.lock`).
- `storage/`: Generated files, uploads, and logs.

## 4. Code Style Guidelines & Conventions
- **Always Async**: Almost everything must be async to prevent blocking the event loop.
  - Prefix route handlers with `async def`.
  - Use `await` for DB queries, large file I/O, or network requests.
  - **Never** use synchronous blocking functions like `time.sleep()`.
- **Database Interaction**: No heavy ORM is used for queries. The custom `app.db` wrapper executes async SQL.
  - Example: `res = await app.db.execute("SELECT * FROM users WHERE id = $1;", user_id)`
  - Schema updates: New tables are created using `await app.db.create_all(Model)`. Schema alterations (adding columns) require raw `ALTER TABLE` execution.
- **UI/UX Aesthetics**: The frontend styling is a priority. Ensure responsive, modern, and sleek interfaces with high-quality colors, subtle hover effects, and crisp SVGs (following Nuxt UI / Vue aesthetics conceptually, even if using HTML/CSS/JS). No generic designs.

## 5. Security & Context Considerations
- **Context Errors**: Beware of `RuntimeError: Not within a request context`, especially within WebSocket handlers (`websocket_manager.py`) or background polling tasks. Always ensure you are requesting `request.args` ONLY when in a valid HTTP route.
- **Inter-Module Communication**: Use the event architecture (`HookManager`, `ActionManager`) to allow modules to communicate without hard coupling.
- **Execution Errors**: "Exec format error" can occur on bash scripts (`dev.sh`, `prod.sh`). Maintain correct shebangs (`#!/bin/bash`) and execute permissions.

## 6. Build and Test Commands
- **Run Dev Server**: `python3 main.py` or `./dev.sh`
- **Application Entry Point**: `main.py` triggers the `core.Application()` engine.
