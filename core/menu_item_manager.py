from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class MenuItemManager:
    def __init__(self, app: Application):
        self.app = app
        self.menu_items = {}