from .module import Module

class PluginModule(Module):
    def __init__(self, name:str, router_name:str):
        super().__init__(type_module="PLUGING", name=name, router_name=router_name)