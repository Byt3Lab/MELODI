from __future__ import annotations

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..application import Application

class  Storage:
    def __init__(self, app:Application | None = None):
        self.app = app

    