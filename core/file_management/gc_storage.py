from __future__ import annotations

from typing import Union, List, Dict, Any

from .storage_interface import StorageInterface

try:
    from google.cloud import storage as gcs
except ImportError:
    gcs = None

class GoogleCloudStorage(StorageInterface):
    """
    Implementation of storage on Google Cloud Storage.
    """
    def __init__(self, bucket_name, credentials_path=None):
        if not gcs:
            raise ImportError("google-cloud-storage is required for GCS.")
        
        if credentials_path:
            self.client = gcs.Client.from_service_account_json(credentials_path)
        else:
            self.client = gcs.Client() # Use default environment credentials
            
        self.bucket = self.client.bucket(bucket_name)

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        blob_name = self._get_safe_path(filename, path_dir)
        blob = self.bucket.blob(blob_name)
        
        if hasattr(file, 'read'):
            file.seek(0)
            blob.upload_from_file(file)
        else:
            blob.upload_from_string(file)
            
        if visibility == 'public':
            blob.make_public()
            
        metadata = {
            "filename": filename,
            "path": blob_name,
            "created_at": self._now(),
            "modified_at": self._now(),
            "access_rights": access_rights,
            "visibility": visibility,
            "size": blob.size,
            "backend": "gcs",
            "url": blob.public_url
        }
        
        # Store custom metadata on the blob
        blob.metadata = {'access_rights': access_rights}
        blob.patch()
        
        return metadata

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        blob_name = self._get_safe_path(filename, path_dir)
        blob = self.bucket.blob(blob_name)
        if not blob.exists():
             raise FileNotFoundError(f"GCS File {blob_name} not found.")
        return blob.download_as_bytes()

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        blob_name = self._get_safe_path(filename, path_dir)
        blob = self.bucket.get_blob(blob_name)
        if not blob:
            raise FileNotFoundError(f"GCS Metadata for {blob_name} not found.")
            
        return {
            "filename": filename,
            "path": blob_name,
            "modified_at": blob.updated.isoformat() if blob.updated else None,
            "size": blob.size,
            "content_type": blob.content_type,
            "backend": "gcs",
            "custom_metadata": blob.metadata
        }

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        result = self.save(new_file, filename, path_dir)
        return bool(result)

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        blob_name = self._get_safe_path(filename, path_dir)
        blob = self.bucket.blob(blob_name)
        if blob.exists():
            blob.delete()
            return True
        return False
