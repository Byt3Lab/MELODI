import os
import time
import shutil
from .cache_interface import CacheInterface
from typing import Any, Optional
import pickle

class FileCache(CacheInterface):
    """File-based cache implementation."""

    def __init__(self, cache_dir: str = ".cache_storage"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_path(self, key: str) -> str:
        # Simple hashing or sanitization could be added here
        return os.path.join(self.cache_dir, f"{key}.pickle")

    def get(self, key: str) -> Any:
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            
            if "expiry" in data and data["expiry"] and data["expiry"] < time.time():
                self.delete(key)
                return None
            
            return data["value"]
        except (EOFError, pickle.UnpicklingError, FileNotFoundError):
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        path = self._get_path(key)
        expiry = time.time() + ttl if ttl else None
        data = {"value": value, "expiry": expiry}
        
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def delete(self, key: str) -> None:
        path = self._get_path(key)
        if os.path.exists(path):
            os.remove(path)

    def clear(self) -> None:
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir)

    def exists(self, key: str) -> bool:
        path = self._get_path(key)
        if not os.path.exists(path):
            return False
        
        # Check expiry without full load if possible, but pickle requires load.
        # We'll just use get() logic for simplicity or just check file existence 
        # but that might return expired keys. 
        # For correctness, let's check expiry.
        return self.get(key) is not None

