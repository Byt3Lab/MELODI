from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class ServiceManager:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.services:dict[str,dict[str,object]]  = {}
        self.managers:dict[str,"ServiceManager"] = {}

    def new_manager(self, name):
        self.managers[name] = ServiceManager(self.app)

    def get_manager(self, name)->"ServiceManager":
        return self.managers[name]
    
    def register(self, name_module:str, name_service:str, service):
        if not name_module in self.services:
            self.services[name_module] = {}
        
        self.services[name_module][name_service] = service

    def get(self, name_module:str, name_service:str=None):
        try:
            if isinstance(name_service):
                return self.services[name_module][name_service]
            return self.services[name_module]
        except:
            return None
        
    def remove(self,name_module = None, name_service = None):
        try:
            if isinstance(name_module, str):
                if isinstance(name_service, str):
                    del self.services[name_module][name_service]
                    return True
                del self.services[name_module]
                return True
            return False
        except:
            return False