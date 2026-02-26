from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable
from core.router import WebRouter
from core.router import APIRouter
from core.utils import join_paths, path_exist, Translation

if TYPE_CHECKING:
    from core.application import Application

class Module:
    def __init__(self, name:str, type_module:str, router_name:str):
        self.name: str = name
        self.dirname: str = ""
        self.type_module:str = type_module
        self.app:Application | None = None
        self.translation = None
        self.router_name = router_name
        self.router:WebRouter | None = None
        self.api_router:APIRouter | None = None

    def init_translation(self, default_lang:str):
        path_dir = []

        if self.dirname == "base":
            path_dir = [self.app.config.PATH_DIR_RACINE, self.dirname, "langs"]
        else:
            path_dir = [self.app.config.PATH_DIR_MODULES, self.dirname, "langs"]

        self.translation = Translation(path_dir, default_lang)

    def load(self):
        pass

    def stop(self):
        print(f"Stopping module {self.name}")
        pass

    def add_router(self, router:WebRouter, url_prefix=''):
        self.router.add_router(router, url_prefix=url_prefix)
    
    def add_api_router(self, router:APIRouter, url_prefix=''):
        self.api_router.add_router(router, url_prefix=url_prefix)

    def init(self, app:Application, dirname:str):
        self.app = app
        self.dirname = dirname

        if self.dirname == "base":
            path_template_folder = self.app.config.PATH_DIR_BASE_MODULE + f"/templates"
        else:
            path_template_folder = self.app.config.PATH_DIR_MODULES + f"/{self.dirname}/templates"

        if not path_exist(path_template_folder):
            path_template_folder = None

        router_name = f'{self.type_module}_{self.dirname}'
        self.router = WebRouter(app=self.app, name=router_name, template_folder=path_template_folder, module=self)
        self.api_router = APIRouter(app=self.app, name=f'{self.router_name}_api')

    def _run(self):
        if self.app is None:
            raise ValueError("Application instance is not set for the module.")
        self.app.router.add_router(self.router)
        self.app.api_router.add_router(self.api_router, url_prefix=self.dirname)
        prefix_url = self.dirname

        if self.dirname == "base":
            path_dir_static = join_paths(self.app.config.PATH_DIR_BASE_MODULE, "static")
            path_dir_templates_melodijs = join_paths(self.app.config.PATH_DIR_BASE_MODULE, "templates", "melodijs")
        else:
            path_dir_static = join_paths(self.app.config.PATH_DIR_MODULES, self.dirname, "static")
            path_dir_templates_melodijs = join_paths(self.app.config.PATH_DIR_MODULES, self.dirname, "templates", "melodijs")
            
        if path_exist(path_dir_static):    
            self.app.server.serve_static_directory(name=f'{self.type_module}_{self.dirname}', prefix_path=prefix_url, path_directory=path_dir_static)

        if path_exist(path_dir_templates_melodijs):  
            self.app.server.serve_static_templates_melodijs_directory(name=f'{self.type_module}_{self.dirname}', prefix_path=prefix_url, path_directory=path_dir_templates_melodijs)

    def get_router(self)->WebRouter:
        return self.router
    
    def get_api_router(self)->APIRouter:
        return self.api_router
    
    def register_widget(self, name_widget:str|None=None, infos={}):
        def decorator (func):
            if callable(func):
                if not name_widget:
                    self.app.widget_manager.register(name_module=self.dirname, name_widget= func.__name__, widget=func, infos=infos)
                self.app.widget_manager.register(name_module=self.dirname, name_widget= name_widget, widget=func, infos=infos)
                return
            
            if name_widget:
                self.app.widget_manager.register(name_module=self.dirname, name_widget= name_widget, widget=func, infos=infos)
        return decorator

    def register_home_page(self, home_page, infos):
        self.app.home_page_manager.register(name_module=self.dirname, home_page=home_page, infos=infos)

    def register_middlewares(self, middlewares:dict[str, Callable]):
        self.app.middleware_manager.register_middlewares(module_name=self.dirname, middlewares=middlewares)
        
    def get_middlewares(self, module_name:str|None=None) -> dict[str, Callable]|None:
        if module_name is None:
            module_name = self.dirname
        return self.app.middleware_manager.get_module_middlewares(module_name=module_name)
    
    def get_middleware(self, middleware:str, module_name:str|None=None) -> Callable|None:
        if module_name is None:
            module_name = self.dirname
        return self.app.middleware_manager.get_middleware(module_name=module_name, middleware=middleware)

    def add_event_listener(self, event_name:str, listener:Callable, module_name:str|None=None):
        if module_name is None:
            module_name = self.dirname
        self.app.event_listener.add_event_listener(module_name, event_name, listener)

    def notify_event(self, event_name:str, data:Any=None, module_name:str|None=None):
        if module_name is None:
            module_name = self.dirname
        self.app.event_listener.notify_event(module_name, event_name, data)

    def translate(self, filename:list[str]|str, keys:list[str]|str, lang:str|None = None, ):
        if self.translation == None:
            return {}
        return self.translation.translate(filename, keys, lang)
    
    def run_background_task(self, func:Callable, *args, **kwargs):
        self.app.server.app.add_background_task(func, *args, **kwargs)

    # ------------------------------------------------------------------
    # Contribution Registry (Plugin-Base architecture)
    # ------------------------------------------------------------------

    def register_contribution(self, zone: str, item: dict):
        """Registers a raw dictionary configuration to a specific zone."""
        if hasattr(self.app, 'registry'):
            self.app.registry.register(zone, self.dirname, item)
            
    def register_navigation(self, label: str, icon: str, url: str, priority: int = 0):
        """
        Registers a navigation item (Sidebar)
        - label: The display name (e.g. 'Tableau de bord')
        - icon: FontAwesome classes (e.g. 'fas fa-chart-pie')
        - url: The route to navigate to
        - priority: Display order (higher appears first)
        """
        self.register_contribution("navigation", {
            "label": label,
            "icon": icon,
            "url": url,
            "priority": priority
        })

    def register_dashboard_widget(self, title: str, component: str, dimensions: dict = None, priority: int = 0):
        """
        Registers a widget to be rendered on the Dashboard.
        - title: Name of the widget
        - component: Component identifier or HTML generator
        - dimensions: Dict for grid sizing, e.g. {"w": 4, "h": 2}
        - priority: Display order
        """
        self.register_contribution("dashboard", {
            "title": title,
            "component": component,
            "dimensions": dimensions or {},
            "priority": priority
        })

    def register_statusbar_item(self, component: str, priority: int = 0):
        """
        Registers an item/widget to be rendered in the top Status Bar.
        - component: The HTML/Widget to render
        - priority: Display order
        """
        self.register_contribution("statusbar", {
            "component": component,
            "priority": priority
        })

    # ------------------------------------------------------------------
    # WebSocket function registry
    # ------------------------------------------------------------------

    def register_ws_function(self, function_name: str | None = None):
        """Decorator to register an async function as a WebSocket handler.

        The function will be callable by any connected client using the
        following JSON message format::

            {
                "id":       "<unique-message-id>",
                "module":   "<this module dirname>",
                "function": "<function_name>",
                "params":   { ... }
            }

        The handler signature must be::

            async def my_handler(params: dict, client: Client) -> Any: ...

        Example usage inside a module::

            @self.register_ws_function()
            async def get_info(params: dict, client) -> dict:
                return {"version": "1.0"}

            @self.register_ws_function("custom_name")
            async def some_func(params: dict, client) -> str:
                return "done"
        """
        def decorator(func: Callable) -> Callable:
            name = function_name if function_name else func.__name__
            ws_manager = getattr(self.app, "websocket_manager", None)
            if ws_manager is None:
                raise RuntimeError(
                    "No WebSocket manager (app.websocket_manager) found. "
                    "Make sure to initialise the WebSocketManager before registering WS functions."
                )
            if not self.dirname:
                print(f"WARNING: Module {self.name} is registering WS function {name} with EMPTY dirname!")
            
            print(f"DEBUG: Module {self.name} registering WS function {name} with dirname='{self.dirname}'")
            ws_manager.register_function(self.dirname, name, func)
            return func
        return decorator