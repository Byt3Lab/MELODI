from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..application import Application

import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename


class Storage:
    """
    Classe de gestion des fichiers et de leurs métadonnées.
    """
    def __init__(self, app:Application | None = None):
        self.app = app
        self.base_path = self.app.config.PATH_DIR_STORAGE

    def _get_file_path(self, filename):
        return os.path.join(self.base_path, secure_filename(filename))

    def _get_meta_path(self, filename):
        safe_name = secure_filename(filename)
        return os.path.join(self.base_path, f"{safe_name}.meta.json")

    def _now(self):
        return datetime.utcnow().isoformat()

    # --------------------------
    # 🔹 CRÉATION / UPLOAD
    # --------------------------
    def save(self, file, access_rights="rw", visibility="private"):
        """
        Sauvegarde un fichier uploadé et crée ses métadonnées.
        """
        filename = secure_filename(file.filename)
        file_path = self._get_file_path(filename)
        meta_path = self._get_meta_path(filename)

        file.save(file_path)

        metadata = {
            "filename": filename,
            "created_at": self._now(),
            "modified_at": self._now(),
            "access_rights": access_rights,  # ex: rw / r / rwx
            "visibility": visibility,        # public / private
            "size": os.path.getsize(file_path),
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return metadata

    # --------------------------
    # 🔹 LECTURE
    # --------------------------
    def read(self, filename):
        """
        Retourne le contenu d’un fichier.
        """
        file_path = self._get_file_path(filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier {filename} introuvable.")

        with open(file_path, "rb") as f:
            return f.read()

    def get_metadata(self, filename):
        """
        Retourne les métadonnées d’un fichier.
        """
        meta_path = self._get_meta_path(filename)
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Métadonnées pour {filename} introuvables.")

        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # --------------------------
    # 🔹 MODIFICATION
    # --------------------------
    def update(self, filename, new_file):
        """
        Remplace le contenu d’un fichier et met à jour les métadonnées.
        """
        file_path = self._get_file_path(filename)
        meta_path = self._get_meta_path(filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier {filename} introuvable.")

        new_file.save(file_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r+", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata["modified_at"] = self._now()
                metadata["size"] = os.path.getsize(file_path)
                f.seek(0)
                json.dump(metadata, f, indent=4)
                f.truncate()

        return True

    # --------------------------
    # 🔹 SUPPRESSION
    # --------------------------
    def delete(self, filename):
        """
        Supprime un fichier et son fichier de métadonnées.
        """
        file_path = self._get_file_path(filename)
        meta_path = self._get_meta_path(filename)

        deleted = False

        for path in [file_path, meta_path]:
            if os.path.exists(path):
                os.remove(path)
                deleted = True

        return deleted

