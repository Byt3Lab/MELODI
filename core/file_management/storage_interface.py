from abc import ABC, abstractmethod

from typing import Union, List, Dict, Any
from werkzeug.utils import secure_filename
from datetime import datetime

class StorageInterface(ABC):
    """
    Abstract base class for storage backends.
    """
    
    @abstractmethod
    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        pass

    @abstractmethod
    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        pass

    @abstractmethod
    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        pass

    @abstractmethod
    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        pass

    @abstractmethod
    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        pass
    
    def _get_safe_path(self, filename: str, path_dir: Union[str, List[str]] = "") -> str:
        """Helper to construct a safe relative path."""
        safe_name = secure_filename(filename)
        if isinstance(path_dir, str):
            path_parts = [path_dir] if path_dir else []
        elif isinstance(path_dir, list):
            path_parts = path_dir
        else:
            path_parts = []
        
        # Filter empty strings
        path_parts = [p for p in path_parts if p]
        
        if not path_parts:
            return safe_name
            
        return "/".join(path_parts + [safe_name])

    def _now(self):
        return datetime.utcnow().isoformat()
