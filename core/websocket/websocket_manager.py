from __future__ import annotations

import asyncio
import inspect
import json
import logging
from typing import Any, Callable, Coroutine, Optional, TYPE_CHECKING

from quart import Websocket

from .socket_provider_interface import SocketProviderInterface
from .local_provider import LocalProvider

if TYPE_CHECKING:
    from core import Application

logger = logging.getLogger(__name__)

# Type alias for a WebSocket handler function.
# It receives the parsed params dict and the connected Client,
# and must return a JSON-serialisable value (or a coroutine that does).
WsHandler = Callable[[dict, "Client"], Coroutine[Any, Any, Any]]


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

    def __init__(self, app: "Application", provider: SocketProviderInterface|None = None, rule: str = "/ws") -> None:
        if provider is None:
            provider = LocalProvider()
        self.app = app
        self.provider = provider
        self.rule = rule
        # Registry: { module_name: { function_name: handler } }
        self._registry: dict[str, dict[str, WsHandler]] = {}

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
    # Function registry
    # ------------------------------------------------------------------

    def register_function(self, module_name: str, function_name: str, handler: WsHandler) -> None:
        """Register *handler* under *module_name* / *function_name*.

        Called by :meth:`Module.register_ws_function` — you rarely need to
        call this directly.
        """
        if module_name not in self._registry:
            self._registry[module_name] = {}
        self._registry[module_name][function_name] = handler
        print(f"DEBUG: WS function registered: {module_name}.{function_name}")
        logger.debug("WS function registered: %s.%s", module_name, function_name)

    # ------------------------------------------------------------------
    # Message dispatching
    # ------------------------------------------------------------------

    async def _dispatch(self, raw: str, client: "Client") -> None:
        """Parse *raw* JSON and call the registered handler.

        Expected message format::

            {
                "id":       "<unique-message-id>",   # echoed back in the response
                "module":   "<module_name>",
                "function": "<function_name>",
                "params":   { ... }                  # key-value pairs
            }

        Response format (always sent back to the calling client)::

            {
                "id":     "<same-message-id>",
                "status": "ok" | "error",
                "result": <handler return value>  # only on success
                "error":  "<message>"             # only on error
            }
        """
        msg_id: str | None = None
        try:
            payload: dict = json.loads(raw)
            msg_id   = payload.get("id")
            module   = payload.get("module")
            function = payload.get("function")
            params   = payload.get("params", {})

            if not msg_id:
                raise ValueError("Missing required field 'id'.")
            if not module:
                raise ValueError("Missing required field 'module'.")
            if not function:
                raise ValueError("Missing required field 'function'.")
            if not isinstance(params, dict):
                raise ValueError("Field 'params' must be a JSON object.")

            module_handlers = self._registry.get(module)
            if module_handlers is None:
                print(f"DEBUG: WS registry keys: {list(self._registry.keys())}")
                print(f"DEBUG: WS requested module: {module}")
                raise LookupError(f"Module '{module}' not found in registry.")

            handler = module_handlers.get(function)
            if handler is None:
                raise LookupError(f"Function '{function}' not registered for module '{module}'.")

            if inspect.iscoroutinefunction(handler):
                result = await handler(params, client)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: handler(params, client))
            response = json.dumps({"id": msg_id, "status": "ok", "result": result})

        except (json.JSONDecodeError, ValueError, LookupError) as exc:
            logger.warning("WS dispatch error from %s: %s", client.id, exc)
            response = json.dumps({"id": msg_id, "status": "error", "error": str(exc)})
        except Exception as exc:
            logger.exception("Unhandled WS handler error for %s", client.id)
            response = json.dumps({"id": msg_id, "status": "error", "error": "Internal server error."})

        await self.send_to(client.id, response)

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
                await self._dispatch(msg, client)
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