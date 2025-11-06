from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Application

class MenuItemManager:
    def __init__(self, app: Application):
        self.app = app
        self.menu_items = {}
        self.managers:dict[str,"MenuItemManager"] = {}

    def new_manager(self, name):
        self.managers[name] = MenuItemManager(self.app)

    def get_manager(self, name)->"MenuItemManager":
        return self.managers[name]
    