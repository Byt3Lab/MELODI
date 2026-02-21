from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from .socket_provider_interface import SocketProviderInterface

if TYPE_CHECKING:
    from quart import Websocket

logger = logging.getLogger(__name__)


class LocalProvider(SocketProviderInterface):
    """In-process WebSocket provider.

    All clients are stored in a plain dict. Broadcasts iterate over
    the dict and send to every socket directly — no external service
    is needed.  Use this provider for single-node deployments or
    local development.
    """

    def __init__(self) -> None:
        self._clients: dict[str, Websocket] = {}

    # ------------------------------------------------------------------
    # SocketProviderInterface
    # ------------------------------------------------------------------

    async def register(self, client_id: str, socket: "Websocket") -> None:
        self._clients[client_id] = socket
        logger.debug("LocalProvider: registered client %s (total=%d)", client_id, len(self._clients))

    async def unregister(self, client_id: str) -> None:
        self._clients.pop(client_id, None)
        logger.debug("LocalProvider: unregistered client %s (total=%d)", client_id, len(self._clients))

    async def publish(self, channel: str, message: str) -> None:
        """Send *message* to every locally-connected client."""
        if not self._clients:
            return
        await asyncio.gather(
            *(sock.send(message) for sock in self._clients.values()),
            return_exceptions=True,
        )

    async def publish_to(self, client_id: str, message: str) -> None:
        """Send *message* to one specific client (if connected to this node)."""
        socket = self._clients.get(client_id)
        if socket is None:
            logger.warning("LocalProvider: client %s not found, message dropped", client_id)
            return
        await socket.send(message)

    def get_local_clients(self) -> dict[str, "Websocket"]:
        return dict(self._clients)

    async def close(self) -> None:
        self._clients.clear()
        logger.debug("LocalProvider: closed, all clients cleared")
