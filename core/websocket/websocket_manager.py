from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING

from quart import Websocket

from .socket_provider_interface import SocketProviderInterface
from .local_provider import LocalProvider

if TYPE_CHECKING:
    from core import Application

logger = logging.getLogger(__name__)


class Client:
    """Represents a connected WebSocket client on this node."""

    def __init__(self, client_id: str, socket: Websocket) -> None:
        self.id = client_id
        self.socket = socket


class WebSocketManager:
    """Handles a single WebSocket endpoint and delegates storage/fanout to a provider.

    The provider is injected and can be swapped at runtime:
    - :class:`LocalProvider`  → single-node, in-memory (default)
    - :class:`RedisProvider`  → multi-node via Redis Pub/Sub

    The manager is unaware of the provider's internals — it only calls the
    interface methods defined by :class:`SocketProviderInterface`.
    """

    BROADCAST_CHANNEL = "ws"

    def __init__(self, app: "Application", provider: SocketProviderInterface, rule: str = "/ws") -> None:
        self.app = app
        self.provider = provider
        self.rule = rule

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self, socket: Websocket) -> Client:
        await socket.accept()
        client = Client(client_id=str(id(socket)), socket=socket)
        await self.provider.register(client.id, socket)
        logger.info("WebSocket client connected: %s", client.id)
        return client

    async def disconnect(self, client: Client) -> None:
        await self.provider.unregister(client.id)
        logger.info("WebSocket client disconnected: %s", client.id)

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def broadcast(self, message: str) -> None:
        """Send *message* to **all** connected clients (all nodes in Redis mode)."""
        await self.provider.publish(self.BROADCAST_CHANNEL, message)

    async def send_to(self, client_id: str, message: str) -> None:
        """Send *message* to a specific client identified by *client_id*."""
        await self.provider.publish_to(client_id, message)

    # ------------------------------------------------------------------
    # Backward-compatible helpers
    # ------------------------------------------------------------------

    async def send_message_to_all_clients(self, message: str) -> None:
        """Alias for :meth:`broadcast` (backward compatibility)."""
        await self.broadcast(message)

    async def send_message_to_client(self, client_id: str, message: str) -> None:
        """Alias for :meth:`send_to` (backward compatibility).

        .. note::
            The signature changed from ``(websocket, message)`` to
            ``(client_id, message)`` to support cross-node routing.
        """
        await self.send_to(client_id, message)

    # ------------------------------------------------------------------
    # Request handler
    # ------------------------------------------------------------------

    async def run(self) -> None:
        """Main WebSocket handler — registered as the Quart route handler."""
        from quart import websocket

        token = websocket.args.get("token")
        logger.debug("WebSocket connection, token=%s", token)

        client = await self.connect(websocket)
        try:
            while True:
                msg = await websocket.receive()
                logger.debug("Received from %s: %s", client.id, msg)
                await websocket.send("pong")
        except Exception as exc:
            logger.debug("WebSocket closed for %s: %s", client.id, exc)
        finally:
            await self.disconnect(client)

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.app.server.app.websocket(self.rule)(self.run)


class WebSocketBackend:
    """Factory that creates a :class:`WebSocketManager` with the right provider.

    Example — local (default)::

        backend = WebSocketBackend(app, backend="local")
        backend.start()

    Example — Redis::

        backend = await WebSocketBackend.create_async(app, backend="redis",
                                                      host="redis", port=6379)
        backend.start()
    """

    def __init__(
        self,
        app: "Application",
        provider: SocketProviderInterface,
        rule: str = "/ws",
    ) -> None:
        self.manager = WebSocketManager(app, provider, rule)

    # ------------------------------------------------------------------
    # Sync factory (local only — no async setup needed)
    # ------------------------------------------------------------------

    @classmethod
    def local(cls, app: "Application", rule: str = "/ws") -> "WebSocketBackend":
        """Create a local (in-process) backend. No external services required."""
        return cls(app, LocalProvider(), rule)

    # ------------------------------------------------------------------
    # Async factory (supports Redis)
    # ------------------------------------------------------------------

    @classmethod
    async def create_async(
        cls,
        app: "Application",
        backend: str = "local",
        rule: str = "/ws",
        **kwargs,
    ) -> "WebSocketBackend":
        """Async factory.

        Parameters
        ----------
        backend:
            ``"local"`` or ``"redis"``.
        **kwargs:
            Forwarded to the provider constructor (e.g. ``host``, ``port``,
            ``password`` for Redis).
        """
        if backend == "local":
            provider: SocketProviderInterface = LocalProvider()
        elif backend == "redis":
            from .redis_provider import RedisProvider
            provider = await RedisProvider.create(**kwargs)
        else:
            raise ValueError(f"Unknown WebSocket backend: {backend!r}. Choose 'local' or 'redis'.")

        return cls(app, provider, rule)

    # ------------------------------------------------------------------
    # Delegation helpers
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Register the WebSocket route on the Quart application."""
        self.manager.start()

    async def broadcast(self, message: str) -> None:
        await self.manager.broadcast(message)

    async def send_to(self, client_id: str, message: str) -> None:
        await self.manager.send_to(client_id, message)