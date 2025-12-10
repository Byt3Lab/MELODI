from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Application

class MenuItemManager:
    def __init__(self, app: Application):
        self.app = app
        self.menu_items:dict[dict[list]] = {}

    def get(self, name_module, name_menu_item):
        return self.menu_items.get(name_module, {}).get(name_menu_item)

    def add(self, name_module, name_menu_item, menu_item):
        if name_module not in self.menu_items:
            self.menu_items[name_module] = {}
        
        if name_menu_item not in self.menu_items[name_module]:
            self.menu_items[name_module][name_menu_item] = []
        
        self.menu_items[name_module][name_menu_item].append(menu_item)