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
    
    def register_service(self, name_service:str|None=None):
        def decorator (func):
            name_module = self.dirname
            ns = name_service

            if callable(func):
                if not ns:
                    ns = func.__name__
                    self.app.service_manager.register(name_module, ns, func)
                    return
                self.app.service_manager.register(name_module, ns, func)
                return
            
            if ns:
                self.app.service_manager.register(name_module, ns, func)

        return  decorator
    
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