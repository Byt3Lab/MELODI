from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class GlobalData:
    def __init__(self, app:Application | None = None):
        self.app = app
        self.data:dict[str,dict[str,object]] = {}

    def add(self, data_name, value):
        self.data[data_name] = value

    def get(self, data_name):
        try:
            return self.data[data_name]
        except:
            return None
        
    def remove(self, data_name:str):
        try:
            del self.data[data_name]
            return True
        except:
            return False        
