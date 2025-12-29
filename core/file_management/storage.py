from __future__ import annotations

from typing import TYPE_CHECKING, Union, List, Optional, Dict, Any
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from abc import ABC, abstractmethod
import shutil

if TYPE_CHECKING:
    from core import Application

from core.utils import create_dir_if_not_exist, join_paths

# Try importing external libraries, handle if missing
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

try:
    from google.cloud import storage as gcs
except ImportError:
    gcs = None

import requests

class StorageBackend(ABC):
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

class LocalStorage(StorageBackend):
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

class S3Storage(StorageBackend):
    """
    Implementation of storage on AWS S3.
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, region_name=None):
        if not boto3:
            raise ImportError("boto3 is required for S3 storage.")
        
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket_name = bucket_name

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        key = self._get_safe_path(filename, path_dir)
        
        # Determine ACL
        acl = 'public-read' if visibility == 'public' else 'private'
        
        try:
            # Check if file is a file-like object or bytes
            if hasattr(file, 'read'):
                file.seek(0)
                data = file.read()
            else:
                data = file

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ACL=acl,
                Metadata={
                    'access_rights': access_rights,
                    'created_at': self._now()
                }
            )
            
            # Construct metadata
            metadata = {
                "filename": filename,
                "path": key,
                "created_at": self._now(),
                "modified_at": self._now(),
                "access_rights": access_rights,
                "visibility": visibility,
                "size": len(data) if isinstance(data, bytes) else 0, # Approximation if not bytes
                "backend": "s3",
                "url": f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            }
            return metadata
        except ClientError as e:
            print(f"S3 Error: {e}")
            return False

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        key = self._get_safe_path(filename, path_dir)
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise FileNotFoundError(f"S3 File {key} not found: {e}")

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        key = self._get_safe_path(filename, path_dir)
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return {
                "filename": filename,
                "path": key,
                "modified_at": response.get('LastModified').isoformat() if response.get('LastModified') else None,
                "size": response.get('ContentLength'),
                "content_type": response.get('ContentType'),
                "backend": "s3",
                "custom_metadata": response.get('Metadata', {})
            }
        except ClientError as e:
            raise FileNotFoundError(f"S3 Metadata for {key} not found: {e}")

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        # S3 update is essentially an overwrite
        result = self.save(new_file, filename, path_dir)
        return bool(result)

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        key = self._get_safe_path(filename, path_dir)
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

class GoogleCloudStorage(StorageBackend):
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

class CustomAPIStorage(StorageBackend):
    """
    Implementation of storage via a Custom API.
    Expects endpoints for upload, download, etc.
    """
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.headers = {'Authorization': f'Bearer {api_key}'}

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        # This is a hypothetical implementation assuming a standard multipart/form-data upload
        safe_path = self._get_safe_path(filename, path_dir)
        
        files = {'file': (filename, file)}
        data = {
            'path': safe_path,
            'access_rights': access_rights,
            'visibility': visibility
        }
        
        try:
            if hasattr(file, 'seek'):
                file.seek(0)
                
            response = requests.post(f"{self.api_url}/upload", files=files, data=data, headers=self.headers)
            response.raise_for_status()
            return response.json() # Expecting metadata back
        except requests.RequestException as e:
            print(f"Custom API Error: {e}")
            return False

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.get(f"{self.api_url}/files", params={'path': safe_path}, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise FileNotFoundError(f"Custom API File {safe_path} not found: {e}")

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.get(f"{self.api_url}/metadata", params={'path': safe_path}, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
             raise FileNotFoundError(f"Custom API Metadata for {safe_path} not found: {e}")

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        # Assuming update is same as save/overwrite
        result = self.save(new_file, filename, path_dir)
        return bool(result)

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.delete(f"{self.api_url}/files", params={'path': safe_path}, headers=self.headers)
            return response.status_code == 200
        except requests.RequestException:
            return False

class Storage:
    """
    Main Storage class acting as a Facade/Context for the Strategy pattern.
    """
    def __init__(self, app: Application | None = None):
        self.app = app
        self.backend: StorageBackend = self._initialize_backend()

    def _initialize_backend(self) -> StorageBackend:
        if not self.app:
            # Default to local if no app context (e.g. testing without config)
            # Or raise error. For now, assuming local default.
            return LocalStorage(base_path="./storage")

        storage_type = self.app.config.get('STORAGE_TYPE', 'local').lower()

        if storage_type == 's3':
            return S3Storage(
                aws_access_key_id=self.app.config.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=self.app.config.get('AWS_SECRET_ACCESS_KEY'),
                bucket_name=self.app.config.get('AWS_BUCKET_NAME'),
                region_name=self.app.config.get('AWS_REGION')
            )
        elif storage_type == 'gcs':
            return GoogleCloudStorage(
                bucket_name=self.app.config.get('GCS_BUCKET_NAME'),
                credentials_path=self.app.config.get('GOOGLE_APPLICATION_CREDENTIALS')
            )
        elif storage_type == 'custom_api':
            return CustomAPIStorage(
                api_url=self.app.config.get('CUSTOM_STORAGE_API_URL'),
                api_key=self.app.config.get('CUSTOM_STORAGE_API_KEY')
            )
        else:
            # Default to local
            return LocalStorage(base_path=self.app.config.get('PATH_DIR_STORAGE', './storage'))

    # --------------------------
    # 🔹 PROXY METHODS
    # --------------------------
    def save(self, file, path_dir: Union[str, List[str]] = "", access_rights="rw", visibility="private"):
        """
        Sauvegarde un fichier uploadé et crée ses métadonnées.
        """
        # Adapt old signature to new backend signature
        # Old: save(self, file, path_dir="", access_rights="rw", visibility="private")
        # Backend: save(self, file, filename, path_dir, ...)
        # We need to extract filename from file object if possible
        
        filename = secure_filename(file.filename)
        return self.backend.save(file, filename, path_dir, access_rights, visibility)

    def read(self, filename, path_dir: Union[str, List[str]] = ''):
        """
        Retourne le contenu d’un fichier.
        """
        return self.backend.read(filename, path_dir)

    def get_metadata(self, filename, path_dir: Union[str, List[str]] = ''):
        """
        Retourne les métadonnées d’un fichier.
        """
        return self.backend.get_metadata(filename, path_dir)

    def update(self, filename, new_file, path_dir: Union[str, List[str]] = ''):
        """
        Remplace le contenu d’un fichier et met à jour les métadonnées.
        """
        return self.backend.update(filename, new_file, path_dir)

    def delete(self, filename, path_dir: Union[str, List[str]] = ''):
        """
        Supprime un fichier et son fichier de métadonnées.
        """
        return self.backend.delete(filename, path_dir)
