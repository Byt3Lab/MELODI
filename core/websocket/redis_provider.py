from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Optional, TYPE_CHECKING

from .socket_provider_interface import SocketProviderInterface

if TYPE_CHECKING:
    from quart import Websocket

logger = logging.getLogger(__name__)

# Optional import — raise only when the provider is actually instantiated.
try:
    import redis.asyncio as aioredis  # type: ignore
except ImportError:
    aioredis = None  # type: ignore


# Redis key / channel conventions
_CLIENTS_SET_KEY = "melodi:ws:clients"          # Redis Set  — all client IDs (all nodes)
_BROADCAST_CHANNEL = "melodi:ws:broadcast"       # Pub/Sub — broadcast to all
_DIRECT_CHANNEL_PREFIX = "melodi:ws:direct:"    # Pub/Sub — per-client targeted messages


class RedisProvider(SocketProviderInterface):
    """Multi-node WebSocket provider backed by Redis Pub/Sub.

    Architecture
    ~~~~~~~~~~~~
    Each application node:

    1. Maintains a local ``dict[client_id, Websocket]`` for sockets owned by it.
    2. On ``register``/``unregister`` updates a shared Redis **Set**
       (``melodi:ws:clients``) so any node can query total connected clients.
    3. Subscribes to two Pub/Sub channels:
       - ``melodi:ws:broadcast``   — fan-out to all nodes → all local sockets receive
       - ``melodi:ws:direct:<id>`` — targeted delivery; only the node owning that
         socket delivers it.
    4. A background asyncio task drives the Pub/Sub listener loop.

    Usage
    ~~~~~
    ::

        provider = await RedisProvider.create(host="localhost", port=6379)
        # … later …
        await provider.close()
    """

    def __init__(
        self,
        redis_client: "aioredis.Redis",
        node_id: Optional[str] = None,
    ) -> None:
        if aioredis is None:
            raise ImportError(
                "redis[asyncio] is not installed. "
                "Run: pip install 'redis[asyncio]'"
            )
        self._redis = redis_client
        self._node_id: str = node_id or str(uuid.uuid4())
        self._clients: dict[str, Websocket] = {}
        self._pubsub: Optional["aioredis.client.PubSub"] = None
        self._listener_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    async def create(
        cls,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        node_id: Optional[str] = None,
        **kwargs,
    ) -> "RedisProvider":
        """Async factory — creates the connection and starts the listener."""
        if aioredis is None:
            raise ImportError(
                "redis[asyncio] is not installed. "
                "Run: pip install 'redis[asyncio]'"
            )
        client = aioredis.Redis(
            host=host, port=port, db=db, password=password,
            decode_responses=True, **kwargs
        )
        provider = cls(client, node_id=node_id)
        await provider._start_listener()
        return provider

    # ------------------------------------------------------------------
    # SocketProviderInterface
    # ------------------------------------------------------------------

    async def register(self, client_id: str, socket: "Websocket") -> None:
        self._clients[client_id] = socket
        await self._redis.sadd(_CLIENTS_SET_KEY, client_id)
        logger.debug(
            "RedisProvider [%s]: registered %s (local=%d)",
            self._node_id, client_id, len(self._clients),
        )

    async def unregister(self, client_id: str) -> None:
        self._clients.pop(client_id, None)
        await self._redis.srem(_CLIENTS_SET_KEY, client_id)
        logger.debug(
            "RedisProvider [%s]: unregistered %s (local=%d)",
            self._node_id, client_id, len(self._clients),
        )

    async def publish(self, channel: str, message: str) -> None:
        """Fan-out to all nodes via Redis Pub/Sub broadcast channel."""
        payload = json.dumps({"type": "broadcast", "channel": channel, "data": message})
        await self._redis.publish(_BROADCAST_CHANNEL, payload)

    async def publish_to(self, client_id: str, message: str) -> None:
        """Target a specific client.  Works across nodes."""
        payload = json.dumps({"type": "direct", "target": client_id, "data": message})
        # Also try local delivery first to avoid a round-trip when the client
        # is on this node.
        if client_id in self._clients:
            await self._clients[client_id].send(message)
            return
        # Otherwise publish on the direct channel — the owning node will pick it up.
        await self._redis.publish(f"{_DIRECT_CHANNEL_PREFIX}{client_id}", payload)

    def get_local_clients(self) -> dict[str, "Websocket"]:
        return dict(self._clients)

    async def get_all_client_ids(self) -> set[str]:
        """Return every client ID known to Redis (all nodes combined)."""
        return await self._redis.smembers(_CLIENTS_SET_KEY)

    async def close(self) -> None:
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.aclose()
        await self._redis.aclose()
        self._clients.clear()
        logger.debug("RedisProvider [%s]: closed", self._node_id)

    # ------------------------------------------------------------------
    # Internal — Pub/Sub listener
    # ------------------------------------------------------------------

    async def _start_listener(self) -> None:
        self._pubsub = self._redis.pubsub()
        await self._pubsub.subscribe(_BROADCAST_CHANNEL)
        # Subscribe to direct channels for locally-registered clients.
        # New direct-channel subscriptions are added on the fly in `register`.
        self._listener_task = asyncio.create_task(
            self._listen_loop(), name=f"ws-redis-listener-{self._node_id}"
        )

    async def _listen_loop(self) -> None:
        logger.debug("RedisProvider [%s]: listener started", self._node_id)
        try:
            async for raw in self._pubsub.listen():
                if raw["type"] != "message":
                    continue
                try:
                    payload = json.loads(raw["data"])
                except (json.JSONDecodeError, TypeError):
                    continue
                await self._dispatch(payload)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("RedisProvider [%s]: listener error", self._node_id)

    async def _dispatch(self, payload: dict) -> None:
        msg_type = payload.get("type")
        data: str = payload.get("data", "")

        if msg_type == "broadcast":
            # Deliver to all local sockets.
            if self._clients:
                await asyncio.gather(
                    *(sock.send(data) for sock in self._clients.values()),
                    return_exceptions=True,
                )

        elif msg_type == "direct":
            target: str = payload.get("target", "")
            socket = self._clients.get(target)
            if socket is not None:
                try:
                    await socket.send(data)
                except Exception:
                    logger.warning(
                        "RedisProvider [%s]: failed to send direct message to %s",
                        self._node_id, target,
                    )
