from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Application
    from .service import Service

class ServiceManager:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.services:dict[str,dict[str,Service]]  = {}

    def register(self, name_module:str, name_service:str, service:Service):
        if not isinstance(service, Service):
            return
        
        if not name_module in self.services:
            self.services[name_module] = {}
        
        self.services[name_module][name_service] = service

    def get(self, name_module:str, name_service:str=None):
        try:
            return self.services[name_module][name_service]
        except:
            return None
        
    def remove(self,name_module:str, name_service:str|None = None):
        try:
            if isinstance(name_service, str):
                del self.services[name_module][name_service]
                return True
            del self.services[name_module]
            return True
        except:
            return False