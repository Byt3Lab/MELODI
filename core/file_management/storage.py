from __future__ import annotations

from typing import TYPE_CHECKING, Union, List
from werkzeug.utils import secure_filename

if TYPE_CHECKING:
    from core import Application
    from .storage_interface import StorageInterface

from .aws_s3_storage import S3Storage
from .local_storage import LocalStorage
from .custom_api_storage import CustomAPIStorage
from .gc_storage import GoogleCloudStorage

class Storage:
    """
    Main Storage class acting as a Facade/Context for the Strategy pattern.
    """
    def __init__(self, app: Application | None = None):
        self.app = app
        self.backend: StorageInterface = self._initialize_backend()

    def _initialize_backend(self) -> StorageInterface:
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
