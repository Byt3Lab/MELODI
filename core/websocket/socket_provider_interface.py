from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Websocket


class SocketProviderInterface(ABC):
    """Abstract interface for WebSocket backend providers.

    Implementations must handle:
    - Local socket registration / unregistration on this node.
    - Broadcasting messages to all clients (across all nodes in Redis mode).
    - Targeting a specific client by its ID.
    """

    @abstractmethod
    async def register(self, client_id: str, socket: "Websocket") -> None:
        """Register a new locally-connected WebSocket client."""

    @abstractmethod
    async def unregister(self, client_id: str) -> None:
        """Unregister a WebSocket client that has disconnected."""

    @abstractmethod
    async def publish(self, channel: str, message: str) -> None:
        """Broadcast a message to ALL clients on the given channel.

        In Redis mode this fan-outs across every application node.
        """

    @abstractmethod
    async def publish_to(self, client_id: str, message: str) -> None:
        """Send a message to a specific client identified by *client_id*.

        Best-effort: if the client is not connected to this node and the
        backend is local-only, the message is silently dropped.
        """

    @abstractmethod
    def get_local_clients(self) -> dict[str, "Websocket"]:
        """Return the sockets that are connected to *this* process/node."""

    @abstractmethod
    async def close(self) -> None:
        """Gracefully tear down the provider (cancel tasks, close connections)."""
