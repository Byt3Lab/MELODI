from __future__ import annotations

import json
from typing import TYPE_CHECKING

from core.utils import join_paths, path_exist, read_file

if TYPE_CHECKING:
    from .application import Application

class WidgetManager:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.path_file = join_paths(self.app.config.PATH_DIR_CONFIG, "widgets_on.json")
        self.widgets_on = []
        self.widgets:dict[str,object] = {}
        self.load_widgets_on()
    
    def load_widgets_on(self):
        if not path_exist(self.path_file):
            self.widgets_on = []
            return
        self.widgets_on = json.loads(read_file(path_file=self.path_file))

    def register(self, name_module:str, name_widget: str, widget, infos):
        if not name_module in self.widgets:
            self.widgets[name_module] = {}

        self.widgets[name_module][name_widget] = {widget, infos}

    def remove(self, name_module:str, name_widget: str):
        try:
            if isinstance(name_module, str):
                if isinstance(name_module, str):
                    del self.widgets[name_module][name_widget]
                    return True
                del self.widgets[name_module]
                return True
            return False
        except:
            return False
        
    def list(self):
        return self.widgets
    
    def clear(self):
        self.widgets.clear()

    def get(self, name_module:str, name_widget: str):
        try:
            return self.widgets[name_module][name_widget]["widget"]
        except:
            return None
    
    def render(self, name_module:str, name_widget: str):
        try:
            widget = self.get(name_module, name_widget)

            if callable(widget):
                return widget()

            if isinstance(widget, str):
                return widget
            
            return None
        except:
            return None
        

    def on(self):
        pass