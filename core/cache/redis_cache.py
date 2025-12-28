from .cache_interface import CacheInterface
from typing import Any, Optional
import pickle

# Try to import redis, but don't fail if it's not installed
try:
    import redis
except ImportError:
    redis = None

class RedisCache(CacheInterface):
    """Redis-based cache implementation."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None, **kwargs):
        if redis is None:
            raise ImportError("Redis package is not installed. Please install it with 'pip install redis'.")
        self.client = redis.Redis(host=host, port=port, db=db, password=password, **kwargs)

    def get(self, key: str) -> Any:
        value = self.client.get(key)
        if value is not None:
            try:
                return pickle.loads(value)
            except pickle.UnpicklingError:
                return value # Return raw bytes if not pickled
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pickled_value = pickle.dumps(value)
        self.client.set(key, pickled_value, ex=ttl)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def clear(self) -> None:
        self.client.flushdb()

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))
