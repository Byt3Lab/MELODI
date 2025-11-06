from __future__ import annotations
from core.router import WebRouter
from core.router import APIRouter
from core.utils import join_paths, path_exist
from .module import Module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Application

class ApplicationModule(Module):
    def __init__(self, name:str, router_name:str):
        self.router_name = router_name
        self.router:WebRouter | None = None
        self.admin_router:WebRouter | None = None
        self.api_router:APIRouter | None = None
    
        super().__init__(type_module="APPLICATION", name=name)

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

        self.router = WebRouter(name=self.name, app=self.app, template_folder=path_template_folder, dirname_module=self.dirname)
        self.admin_router = WebRouter(app=self.app, name=self.router_name+"_admin", dirname_module=self.dirname)
        self.api_router = APIRouter(app=self.app, name=self.router_name+"_api")

    def _run(self):
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

    def get_router(self)->WebRouter:
        return self.router
    
    def get_api_router(self)->APIRouter:
        return self.api_router
    
    def serve_static_directory(self,prefix_path:str, path_dir:str):
        self.app.server.serve_static_directory(prefix_path=prefix_path, path_directory=path_dir)
