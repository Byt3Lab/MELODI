from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.module import Module

class Repository:
    def __init__(self, module:Module | None = None):
        self.module = module
        self.db = self.module.app.db
        
    def get_session(self):
        return self.db.get_session()

    def execute(self, query: str | Any, params: dict = None, query_type: str = "read"):
        return self.db.execute(query, params, query_type)