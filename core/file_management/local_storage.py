from __future__ import annotations

import json
import os
from typing import Union, List, Dict, Any

from core.utils import create_dir_if_not_exist, join_paths

from .storage_interface import StorageInterface

class LocalStorage(StorageInterface):
    """
    Implementation of storage on the local filesystem.
    """
    def __init__(self, base_path: str):
        self.base_path = base_path
        create_dir_if_not_exist(self.base_path)

    def _get_full_path(self, relative_path: str) -> str:
        return join_paths(self.base_path, relative_path)

    def _get_meta_path(self, relative_path: str) -> str:
        return f"{self._get_full_path(relative_path)}.meta.json"

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        relative_path = self._get_safe_path(filename, path_dir)
        full_path = self._get_full_path(relative_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            file.save(full_path)
        except Exception as e:
            print(f"Error saving file locally: {e}")
            return False

        metadata = {
            "filename": filename,
            "path": relative_path,
            "created_at": self._now(),
            "modified_at": self._now(),
            "access_rights": access_rights,
            "visibility": visibility,
            "size": os.path.getsize(full_path),
            "backend": "local"
        }

        meta_path = self._get_meta_path(relative_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return metadata

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        relative_path = self._get_safe_path(filename, path_dir)
        full_path = self._get_full_path(relative_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {relative_path} not found.")

        with open(full_path, "rb") as f:
            return f.read()

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        relative_path = self._get_safe_path(filename, path_dir)
        meta_path = self._get_meta_path(relative_path)
        
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata for {relative_path} not found.")

        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        relative_path = self._get_safe_path(filename, path_dir)
        full_path = self._get_full_path(relative_path)
        meta_path = self._get_meta_path(relative_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {relative_path} not found.")

        new_file.save(full_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r+", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata["modified_at"] = self._now()
                metadata["size"] = os.path.getsize(full_path)
                f.seek(0)
                json.dump(metadata, f, indent=4)
                f.truncate()
        return True

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        relative_path = self._get_safe_path(filename, path_dir)
        full_path = self._get_full_path(relative_path)
        meta_path = self._get_meta_path(relative_path)

        deleted = False
        for path in [full_path, meta_path]:
            if os.path.exists(path):
                os.remove(path)
                deleted = True
        return deleted
