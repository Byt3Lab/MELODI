from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class ServiceManager:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.services = {}

    def register(self, name_module:str, name_service:str, service):
        if not name_module in self.services:
            self.services[name_module] = {}
        
        self.services[name_module][name_service] = service

    def get(self, name_module:str, name_service:str):
        try:
            return self.services[name_module][name_service]
        except:
            return None