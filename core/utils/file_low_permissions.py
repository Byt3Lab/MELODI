import os
import stat
import platform

class FileLawPermissions:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.is_windows = platform.system() == "Windows"

    def check_permissions(self) -> dict[str, bool]:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Le chemin '{self.path}' n'existe pas.")

        return {
            "read": os.access(self.path, os.R_OK),
            "write": os.access(self.path, os.W_OK),
            "execute": os.access(self.path, os.X_OK)
        }

    def set_permissions(self, permissions: dict[str, bool]) -> bool:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Le chemin '{self.path}' n'existe pas.")

        try:
            is_dir = os.path.isdir(self.path)
            mode = 0
            
            # Lecture
            if permissions.get('read'):
                mode |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            
            # Écriture
            if permissions.get('write'):
                mode |= stat.S_IWUSR
                # Note: Sur Unix, l'écriture sur un dossier permet de supprimer/créer des fichiers
            
            # Exécution
            # Règle d'or : Un dossier a BESOIN de l'exécution pour être parcouru
            if permissions.get('execute') or (is_dir and permissions.get('read')):
                mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

            os.chmod(self.path, mode)

            if self.is_windows:
                # Gestion spécifique de l'attribut lecture seule
                if permissions.get('write'):
                    os.chmod(self.path, stat.S_IWRITE)
                else:
                    os.chmod(self.path, stat.S_IREAD)

            return True
        except PermissionError:
            print(f"Erreur : Privilèges insuffisants pour modifier {self.path}")
            return False
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return False

    def set_permissions_recursive(self, permissions: dict[str, bool]) -> bool:
        """Applique les permissions au dossier et à tout son contenu."""
        if not os.path.isdir(self.path):
            return self.set_permissions(permissions) # Si c'est un fichier, simple chmod

        try:
            for root, dirs, files in os.walk(self.path):
                # Appliquer au dossier courant
                FileLawPermissions(root).set_permissions(permissions)
                # Appliquer aux fichiers
                for f in files:
                    FileLawPermissions(os.path.join(root, f)).set_permissions(permissions)
            return True
        except Exception as e:
            print(f"Erreur récursive : {e}")
            return False
        
    def __repr__(self):
        return f"FileLawPermissions(path='{self.path}')"