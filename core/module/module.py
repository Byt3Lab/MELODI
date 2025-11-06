from __future__ import annotations

from typing import TYPE_CHECKING
from core.utils import Translation

if TYPE_CHECKING:
    from core.application import Application

class Module:
    def __init__(self, name:str, type_module:str):
        self.name: str = name
        self.dirname: str = ""
        self.type_module:str = type_module
        self.app:Application | None = None
        self.translation = None

    def init_translation(self, default_lang:str):
        path_dir = []

        if self.dirname == "base":
            path_dir = [self.app.config.PATH_DIR_RACINE, self.dirname, "langs"]
        else:
            path_dir = [self.app.config.PATH_DIR_MODULES, self.dirname, "langs"]

        self.translation = Translation(path_dir, default_lang)

    def load(self):
        pass

    def stop(self):
        print(f"Stopping module {self.name}")
        pass

    def _run():
        pass
 
    def register_service(self, name_service:str|None=None):
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
    
    def register_widget(self, name_widget:str|None=None, infos={}):
        def decorator (func):
            if callable(func):
                if not name_widget:
                    self.app.widget_manager.register(name_module=self.dirname, name_widget= func.__name__, widget=func, infos=infos)
                self.app.widget_manager.register(name_module=self.dirname, name_widget= name_widget, widget=func, infos=infos)
                return
            
            if name_widget:
                self.app.widget_manager.register(name_module=self.dirname, name_widget= name_widget, widget=func, infos=infos)
        return decorator

    def translate(self, filename:list[str]|str, keys:list[str]|str, lang:str|None = None, ):
        if self.translation == None:
            return {}
        
        return self.translation.translate(filename, keys, lang)