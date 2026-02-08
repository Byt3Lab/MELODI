# API Reference

## Core Classes

### Application

`core.application.Application`

The main application class.

- `init()`: Initializes components.
- `async build()`: Loads modules and prepares the app (Async).
- `run()`: Starts the web server.

### Module

`core.module.Module`

Base class for all modules.

- `load()`: Called when the module is loaded.
- `init(app, dirname)`: Initializes the module with the app instance.
- `add_router(router)`: Registers a sub-router.

### WebRouter

`core.router.WebRouter`

Handles web routes and template rendering.

- `add_route(path, methods)`: Decorator to add a route.
- `async render_template(template_name, **context)`: Renders a template (Async).

## Managers

### ModuleManager

`core.module.ModuleManager`

Handles loading and dependency resolution of modules.

### ServiceManager

`core.service.ServiceManager`

Registry for application services.

- `register(module_name, service_name, service)`: Registers a service.
- `get(service_name)`: Retrieves a service.
