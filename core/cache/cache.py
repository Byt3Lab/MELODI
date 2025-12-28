from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING
from .memory_cache import MemoryCache
from .file_cache import FileCache
from .redis_cache import RedisCache

if TYPE_CHECKING:
   from .cache_interface import CacheInterface

class Cache:
    """
    Main Cache service class that delegates to a configured backend.
    """
    
    def __init__(self, type: str = "memory", **kwargs):
        self.backend: CacheInterface
        
        if type == "memory":
            self.backend = MemoryCache()
        elif type == "file":
            self.backend = FileCache(**kwargs)
        elif type == "redis":
            self.backend = RedisCache(**kwargs)
        else:
            raise ValueError(f"Unsupported cache type: {type}")

    def get(self, key: str) -> Any:
        return self.backend.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self.backend.set(key, value, ttl)

    def delete(self, key: str) -> None:
        self.backend.delete(key)

    def clear(self) -> None:
        self.backend.clear()

    def exists(self, key: str) -> bool:
        return self.backend.exists(key)

    def remember(self, key: str, callback, ttl: Optional[int] = None) -> Any:
        """
        Get an item from the cache, or execute the given callback and store the result.
        """
        value = self.get(key)
        if value is not None:
            return value
        
        value = callback()
        self.set(key, value, ttl)
        return value