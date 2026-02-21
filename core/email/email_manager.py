from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from core import Application
    from core.module import Module

class EmailManager:
    def __init__(self, app: Application):
        self.app = app

    async def send_email(self, to: str, subject: str, body: str):
        # Implement email sending logic here
        pass