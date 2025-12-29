import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock werkzeug and core.storage.storage to avoid import errors
from unittest.mock import MagicMock
sys.modules['werkzeug'] = MagicMock()
sys.modules['werkzeug.utils'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['flask'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['sqlalchemy.ext'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
# Also mock core.storage.storage if needed, but werkzeug should be enough if that's the only error

from core.cache import Cache

class TestCacheService(unittest.TestCase):

    def test_in_memory_cache(self):
        print("\nTesting MemoryCache...")
        cache = Cache(backend="memory")
        
        # Test Set/Get
        cache.set("foo", "bar")
        self.assertEqual(cache.get("foo"), "bar")
        
        # Test Exists
        self.assertTrue(cache.exists("foo"))
        
        # Test Delete
        cache.delete("foo")
        self.assertIsNone(cache.get("foo"))
        self.assertFalse(cache.exists("foo"))
        
        # Test TTL
        cache.set("expired", "value", ttl=1)
        self.assertEqual(cache.get("expired"), "value")
        time.sleep(1.1)
        self.assertIsNone(cache.get("expired"))

        # Test Clear
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        self.assertIsNone(cache.get("a"))
        self.assertIsNone(cache.get("b"))
        print("MemoryCache tests passed.")

    def test_file_cache(self):
        print("\nTesting FileCache...")
        test_dir = ".test_cache"
        cache = Cache(backend="file", cache_dir=test_dir)
        
        try:
            # Test Set/Get
            cache.set("foo", "bar")
            self.assertEqual(cache.get("foo"), "bar")
            
            # Test Persistence (create new instance)
            cache2 = Cache(backend="file", cache_dir=test_dir)
            self.assertEqual(cache2.get("foo"), "bar")
            
            # Test Exists
            self.assertTrue(cache.exists("foo"))
            
            # Test Delete
            cache.delete("foo")
            self.assertIsNone(cache.get("foo"))
            self.assertFalse(cache.exists("foo"))
            
            # Test TTL
            cache.set("expired", "value", ttl=1)
            self.assertEqual(cache.get("expired"), "value")
            time.sleep(1.1)
            self.assertIsNone(cache.get("expired"))

            # Test Clear
            cache.set("a", 1)
            cache.clear()
            self.assertIsNone(cache.get("a"))
            self.assertFalse(os.path.exists(test_dir) and os.listdir(test_dir)) # Dir might exist but empty or recreated
            
        finally:
            if os.path.exists(test_dir):
                import shutil
                shutil.rmtree(test_dir)
        print("FileCache tests passed.")

    @patch('core.cache.cache.redis')
    def test_redis_cache(self, mock_redis_module):
        print("\nTesting RedisCache (Mocked)...")
        
        # Setup mock client
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        
        cache = Cache(backend="redis", host='localhost', port=6379)
        
        # Test Set
        import pickle
        cache.set("foo", "bar")
        mock_client.set.assert_called_with("foo", pickle.dumps("bar"), ex=None)
        
        # Test Get
        mock_client.get.return_value = pickle.dumps("bar")
        self.assertEqual(cache.get("foo"), "bar")
        mock_client.get.assert_called_with("foo")
        
        # Test Delete
        cache.delete("foo")
        mock_client.delete.assert_called_with("foo")
        
        # Test Clear
        cache.clear()
        mock_client.flushdb.assert_called_once()
        
        # Test Exists
        mock_client.exists.return_value = 1
        self.assertTrue(cache.exists("foo"))
        mock_client.exists.assert_called_with("foo")
        
        print("RedisCache tests passed.")

    def test_remember(self):
        print("\nTesting Cache.remember...")
        cache = Cache(backend="memory")
        
        # First call, should execute callback
        val = cache.remember("key", lambda: "computed", ttl=10)
        self.assertEqual(val, "computed")
        self.assertEqual(cache.get("key"), "computed")
        
        # Second call, should return cached value
        val = cache.remember("key", lambda: "new_computed", ttl=10)
        self.assertEqual(val, "computed") # Should still be old value
        
        print("Cache.remember tests passed.")

if __name__ == '__main__':
    unittest.main()
