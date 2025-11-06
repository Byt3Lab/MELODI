from __future__ import annotations
from .module import Module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Application

class PluginModule(Module):
    def __init__(self, name:str):
        super().__init__(type_module="PLUGING", name=name)

    def init(self, app:Application, direname:str):
        self.app = app
        self.dirname = direname