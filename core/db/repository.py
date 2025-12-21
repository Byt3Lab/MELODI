from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.module import Module

class Repository:
    def __init__(self, module:Module | None = None):
        self.module = module
        self.db = self.module.app.db
        
    def get_session(self):
        return self.db.get_session()