# Modules & Plugins

## Creating a New Module

To create a new module, create a directory in `modules/` (e.g., `modules/my_module`).

### 1. Structure

```
modules/my_module/
├── __init__.py
├── module.py
├── infos.json
├── templates/
└── static/
```

### 2. `infos.json`

```json
{
    "version": "1.0",
    "name": "my_module",
    "title": "My Custom Module",
    "description": "A description of what this module does.",
    "depends": {
        "modules": []
    }
}
```

### 3. `module.py`

```python
from core.module import ApplicationModule

class MyModule(ApplicationModule):
    def load(self):
        super().load()
        # Register routes
        self.router.add_route("/", methods=["GET"])(self.index)

    def index(self):
        return self.router.render_template("index.html")

module = MyModule(
    name="my_module", router_name="my_module"
)
```

### 4. Templates

Create `templates/my_module/index.html`. Note that you should create a subdirectory with the module name inside `templates` to avoid conflicts.

## Creating a Plugin

Plugins are single Python files in `plugins/`.

Example `plugins/hello.py`:

```python
def run(app):
    print("Hello from plugin!")
    
    # You can register routes or services here
    @app.server.app.route("/hello")
    def hello():
        return "Hello World"
```
