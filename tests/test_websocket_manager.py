"""Tests for the WebSocket provider layer.

Run with:
    cd /path/to/MELODI
    source venv/bin/activate
    python -m pytest tests/test_websocket_manager.py -v
"""
from __future__ import annotations

import asyncio
import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Path setup & heavy-dependency stubs (mirrors test_cache.py style)
# ---------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Stub out heavy libs that the provider files themselves don't need
# (quart is referenced only in TYPE_CHECKING blocks at import time)
_quart_mock = MagicMock()
_quart_mock.Websocket = MagicMock
sys.modules.setdefault("quart", _quart_mock)

# ---------------------------------------------------------------------------
# Import providers DIRECTLY (skip core/__init__ to avoid the full app chain)
# ---------------------------------------------------------------------------
import importlib.util as _ilu

def _import_path(name: str, path: str):
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "websocket"))

_import_path("core.websocket.socket_provider_interface", os.path.join(_BASE, "socket_provider_interface.py"))
_import_path("core.websocket.local_provider",            os.path.join(_BASE, "local_provider.py"))
_import_path("core.websocket.redis_provider",            os.path.join(_BASE, "redis_provider.py"))
_import_path("core.websocket.websocket_manager",         os.path.join(_BASE, "websocket_manager.py"))

from core.websocket.local_provider import LocalProvider
from core.websocket.socket_provider_interface import SocketProviderInterface


def _run(coro):
    """Helper to run a coroutine in tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_socket(client_id: str = "c1") -> MagicMock:
    sock = MagicMock()
    sock.send = AsyncMock()
    return sock


# ---------------------------------------------------------------------------
# LocalProvider tests
# ---------------------------------------------------------------------------

class TestLocalProvider(unittest.TestCase):

    def setUp(self):
        self.provider = LocalProvider()

    def test_implements_interface(self):
        self.assertIsInstance(self.provider, SocketProviderInterface)

    def test_register_and_get_local_clients(self):
        sock = _make_socket()
        _run(self.provider.register("c1", sock))
        clients = self.provider.get_local_clients()
        self.assertIn("c1", clients)
        self.assertIs(clients["c1"], sock)

    def test_unregister(self):
        sock = _make_socket()
        _run(self.provider.register("c1", sock))
        _run(self.provider.unregister("c1"))
        self.assertNotIn("c1", self.provider.get_local_clients())

    def test_unregister_unknown_is_noop(self):
        # Should not raise
        _run(self.provider.unregister("does_not_exist"))

    def test_publish_sends_to_all(self):
        socks = [_make_socket(f"c{i}") for i in range(3)]
        for i, s in enumerate(socks):
            _run(self.provider.register(f"c{i}", s))

        _run(self.provider.publish("ws", "hello"))

        for s in socks:
            s.send.assert_awaited_once_with("hello")

    def test_publish_empty_clients_is_noop(self):
        # Should not raise when no clients are connected
        _run(self.provider.publish("ws", "hello"))

    def test_publish_to_specific_client(self):
        s1, s2 = _make_socket("c1"), _make_socket("c2")
        _run(self.provider.register("c1", s1))
        _run(self.provider.register("c2", s2))

        _run(self.provider.publish_to("c1", "targeted"))

        s1.send.assert_awaited_once_with("targeted")
        s2.send.assert_not_called()

    def test_publish_to_unknown_drops_silently(self):
        # Should not raise
        _run(self.provider.publish_to("ghost", "hi"))

    def test_close_clears_clients(self):
        _run(self.provider.register("c1", _make_socket()))
        _run(self.provider.close())
        self.assertEqual(self.provider.get_local_clients(), {})


# ---------------------------------------------------------------------------
# RedisProvider tests (mocked)
# ---------------------------------------------------------------------------

class TestRedisProvider(unittest.TestCase):
    """Test RedisProvider without a real Redis server using mocks."""

    def _make_redis_mock(self):
        """Return a mock redis.asyncio.Redis instance."""
        mock_client = MagicMock()
        mock_client.sadd = AsyncMock()
        mock_client.srem = AsyncMock()
        mock_client.publish = AsyncMock()
        mock_client.smembers = AsyncMock(return_value=set())
        mock_client.aclose = AsyncMock()

        mock_pubsub = MagicMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.aclose = AsyncMock()
        # Simulate an empty async generator so the listener task exits cleanly.
        async def _empty_listen():
            return
            yield  # make it a generator
        mock_pubsub.listen = _empty_listen
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        return mock_client, mock_pubsub

    def _make_provider(self):
        """Instantiate a RedisProvider with a mocked Redis client."""
        # Import here so the mock of aioredis is isolated per test.
        with patch.dict("sys.modules", {"redis": MagicMock(), "redis.asyncio": MagicMock()}):
            from core.websocket.redis_provider import RedisProvider as _RP  # noqa: F401

        mock_client, mock_pubsub = self._make_redis_mock()

        import core.websocket.redis_provider as rp_module
        original_aioredis = rp_module.aioredis

        # Patch aioredis inside the module so __init__ doesn't fail.
        fake_aioredis = MagicMock()
        fake_aioredis.Redis.return_value = mock_client
        rp_module.aioredis = fake_aioredis

        provider = rp_module.RedisProvider(mock_client, node_id="test-node")

        rp_module.aioredis = original_aioredis  # restore
        return provider, mock_client, mock_pubsub

    def test_register_calls_sadd(self):
        try:
            import core.websocket.redis_provider as rp_module
        except ImportError:
            self.skipTest("redis not installed")

        provider, mock_client, _ = self._make_provider()
        sock = _make_socket()
        _run(provider.register("c1", sock))
        mock_client.sadd.assert_awaited_once()

    def test_unregister_calls_srem(self):
        try:
            import core.websocket.redis_provider as rp_module
        except ImportError:
            self.skipTest("redis not installed")
        provider, mock_client, _ = self._make_provider()
        sock = _make_socket()
        _run(provider.register("c1", sock))
        _run(provider.unregister("c1"))
        mock_client.srem.assert_awaited_once()

    def test_publish_calls_redis_publish(self):
        try:
            import core.websocket.redis_provider as rp_module
        except ImportError:
            self.skipTest("redis not installed")
        provider, mock_client, _ = self._make_provider()
        _run(provider.publish("ws", "hello world"))
        mock_client.publish.assert_awaited_once()
        args = mock_client.publish.await_args
        # First arg is the channel name, second is the payload JSON
        self.assertIn("melodi:ws:broadcast", args[0])

    def test_publish_to_local_client_sends_directly(self):
        """If the target client is local, no Redis round-trip."""
        try:
            import core.websocket.redis_provider as rp_module
        except ImportError:
            self.skipTest("redis not installed")
        provider, mock_client, _ = self._make_provider()
        sock = _make_socket()
        _run(provider.register("c1", sock))
        _run(provider.publish_to("c1", "direct"))
        sock.send.assert_awaited_once_with("direct")
        # Redis publish should NOT have been called for local clients
        mock_client.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# WebSocketBackend factory tests
# ---------------------------------------------------------------------------

class TestWebSocketBackend(unittest.TestCase):

    def _make_app(self):
        app = MagicMock()
        app.server.app.websocket = MagicMock(return_value=lambda fn: fn)
        return app

    def test_local_factory_creates_local_provider(self):
        from core.websocket.websocket_manager import WebSocketBackend
        from core.websocket.local_provider import LocalProvider
        app = self._make_app()
        backend = WebSocketBackend.local(app)
        self.assertIsInstance(backend.manager.provider, LocalProvider)

    def test_start_registers_route(self):
        from core.websocket.websocket_manager import WebSocketBackend
        app = self._make_app()
        backend = WebSocketBackend.local(app, rule="/ws")
        backend.start()
        app.server.app.websocket.assert_called_once_with("/ws")

    def test_create_async_local(self):
        from core.websocket.websocket_manager import WebSocketBackend
        from core.websocket.local_provider import LocalProvider
        app = self._make_app()
        backend = _run(WebSocketBackend.create_async(app, backend="local"))
        self.assertIsInstance(backend.manager.provider, LocalProvider)

    def test_create_async_unknown_backend_raises(self):
        from core.websocket.websocket_manager import WebSocketBackend
        app = self._make_app()
        with self.assertRaises(ValueError):
            _run(WebSocketBackend.create_async(app, backend="unknown"))


if __name__ == "__main__":
    unittest.main()
