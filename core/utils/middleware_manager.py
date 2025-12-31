from typing import Any, Callable

class MiddlewareManager:
    def __init__(self):
        self.middlewares:dict[str,dict[str, Callable]] = {}
    
    def register_middlewares(self, module_name: str, middlewares: dict[str,Callable]):
        if module_name in self.middlewares:
            return
        self.middlewares[module_name] = middlewares

    def get_module_middlewares(self, module_name:str) -> dict[str,Callable]|None:
        return self.middlewares.get(module_name, None)

    def get_middleware(self, module_name: str, middleware:str) -> Callable|None:
        return self.middlewares.get(module_name, None).get(middleware, None)