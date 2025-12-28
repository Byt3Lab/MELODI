from abc import ABC, abstractmethod
from typing import Any, Optional, Union

class CacheInterface(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Retrieve a value from the cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache with an optional TTL (in seconds)."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all values from the cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        pass

