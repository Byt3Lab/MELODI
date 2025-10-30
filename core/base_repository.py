from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application

class BaseRepository:
    def __init__(self, app:Application | None = None):
        self.app = app