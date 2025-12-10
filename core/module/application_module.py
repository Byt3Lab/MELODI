from .module import Module

class ApplicationModule(Module):
    def __init__(self, name:str, router_name:str):
        super().__init__(type_module="APPLICATION", name=name, router_name=router_name)