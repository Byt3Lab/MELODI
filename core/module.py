from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from core.router import Router
from core.api_router import APIRouter
from core.utils import join_paths, path_exist

if TYPE_CHECKING:
    from core.application import Application

@dataclass
class Module:
    name: str
    router_name: str
    version: str = "0.1"
    app:Application | None = None
    router:Router | None = None
    admin_router:Router | None = None
    api_router:APIRouter | None = None
    dirname: str=""

    def add_router(self, router:Router, url_prefix=''):
        self.router.add_router(router, url_prefix=url_prefix)
    
    def add_api_router(self, router:APIRouter, url_prefix=''):
        self.api_router.add_router(router, url_prefix=url_prefix)

    def add_many_routers(self, routers:list[Router]):
        for router in routers:
            self.add_router(router=router)

    def add_many_api_routers(self, routers:list[APIRouter]):
        for router in routers:
            self.add_api_router(router=router)

    def init(self, app:Application, dirname:str):
        self.app = app
        self.dirname = dirname

        if self.dirname == "base":
            path_template_folder = self.app.config.PATH_DIR_BASE_MODULE + f"/templates"
        else:
            path_template_folder = self.app.config.PATH_DIR_MODULES + f"/{self.dirname}/templates"

        if not path_exist(path_template_folder):
            path_template_folder = None

        self.router = Router(name=self.name, app=self.app, template_folder=path_template_folder, dirname_module=self.dirname)
        self.admin_router = Router(app=self.app, name=self.router_name+"_admin", dirname_module=self.dirname)
        self.api_router = APIRouter(app=self.app, name=self.router_name+"_api")

    def load(self):
        pass

    def stop(self):
        print(f"Stopping module {self.name}")
        pass

    def run(self):
        if self.app is None:
            raise ValueError("Application instance is not set for the module.")
        self.app.router.add_router(self.router)
        self.app.api_router.add_router(self.api_router)

        if self.dirname == "base":
            path_dir = join_paths(self.app.config.PATH_DIR_BASE_MODULE, "static")
            prefix_url = "/base"
        else:
            path_dir = join_paths(self.app.config.PATH_DIR_MODULES, self.dirname, "static")
            prefix_url = "/" + self.dirname
            
        if path_exist(path_dir):    
            self.serve_static_directory(prefix_path=prefix_url, path_dir=path_dir)


    def get_router(self)->Router:
        return self.router
    
    def get_api_router(self)->APIRouter:
        return self.api_router
    
    def serve_static_directory(self,prefix_path:str, path_dir:str):
        self.app.server.serve_static_directory(prefix_path=prefix_path, path_directory=path_dir)

    def add_service(self, name_service:str|None=None):
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
    