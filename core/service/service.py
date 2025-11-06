from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..module.module import Module

class Service:
    def __init__(self, module:Module):
        self.module = module
        
    def response(self, data=None, status="success", code=200, message=""):
        return {
            "data": data,
            "status": status,
            "code": code,
            "message": message
        }
    
    def add_service(self, name_service:str|None=None):
        def decorator (func):
            self.module.add_service(name_service)(func)
        return  decorator
    
    def get_service(self, name_module:str, name_service:str):
        return self.module.app.service_manager.get(name_module,name_service)