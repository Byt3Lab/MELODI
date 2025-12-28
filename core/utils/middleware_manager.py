from typing import Any


class middleware_manager:
    def __init__(self):
        self.middlewares:dict[str,dict[str, Any]] = {}
    
    def register_middlewares(self, module_name: str, middlewares: dict):
        if module_name in self.middlewares:
            return
        self.middlewares[module_name] = middlewares

    def get_module_middlewares(self, module_name:str) -> Any|None:
        return self.middlewares.get(module_name, None)

    def get_middleware(self, module_name: str, middleware:str) -> Any|None:
        return self.middlewares.get(module_name, None).get(middleware, None)