from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .module import Module

class BaseRepository:
    def __init__(self, module:Module | None = None):
        self.module = module
        self.db = self.module.app.db
        