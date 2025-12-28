from .cache_interface import CacheInterface
from typing import Any, Optional
import time

class MemoryCache(CacheInterface):
    """In-memory cache implementation using a dictionary."""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Any:
        if key in self._expiry and self._expiry[key] < time.time():
            self.delete(key)
            return None
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._cache[key] = value
        if ttl:
            self._expiry[key] = time.time() + ttl
        elif key in self._expiry:
             del self._expiry[key]

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]

    def clear(self) -> None:
        self._cache.clear()
        self._expiry.clear()

    def exists(self, key: str) -> bool:
        if key in self._expiry and self._expiry[key] < time.time():
            self.delete(key)
            return False
        return key in self._cache