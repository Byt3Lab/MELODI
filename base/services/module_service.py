import os
import zipfile
import shutil
import json
import uuid
from werkzeug.utils import secure_filename
from core.utils import join_paths, create_dir_if_not_exist, read_file
from core.service import Service

class ModuleService(Service):
    async def remove_module(self, module_name: str) -> tuple[bool, str]:
        """
        Supprime un module du système.
        Retourne (True, message) si succès, ou (False, message_erreur).
        """
        if not module_name:
            return False, "Le nom du module est requis."
        
        target_dir = join_paths(self.app.config.PATH_DIR_MODULES, module_name)
        
        if not os.path.exists(target_dir):
            return False, f"Le module '{module_name}' n'existe pas."
        
        try:
            shutil.rmtree(target_dir)

            self.app.migration.remove_tracking_migration_for_module(module_name)
            
            if module_name in self.app.module_manager.list_modules_installs:
                self.app.module_manager.list_modules_installs.remove(module_name)
            return True, f"Module '{module_name}' supprimé avec succès."
        except Exception as e:
            return False, f"Erreur système lors de la suppression : {str(e)}"

    async def extract_and_install_zip(self, file_storage, options: dict = {}) -> tuple[bool, str]:
        """
        Gère l'extraction d'un module zippé et son installation dans le dossier modules/.
        Retourne (True, message) si succès, ou (False, message_erreur).
        """
        if not file_storage or not file_storage.filename.endswith('.zip'):
            return False, "Le fichier fourni n'est pas une archive ZIP valide."

        filename = secure_filename(file_storage.filename)
        # Create a temp directory for extraction
        temp_id = str(uuid.uuid4())
        temp_dir = join_paths(self.app.config.PATH_DIR_STORAGE_TEMP, temp_id)
        create_dir_if_not_exist(temp_dir, permissions={"read":True,"write":True,"execute":True})
        temp_zip_path = join_paths(temp_dir, filename)
        allow_update = options.get('allow_update', False)
        allow_backup = options.get('allow_backup', False)
        backup_already_exist = False

        try:
            # Save the uploaded file temporarily
            await file_storage.save(temp_zip_path)

            # If an expected hash was provided in the request, the controller should attach it
            # to the file_storage as attribute '_module_hash'. We check and verify it here.
            expected_hash = None
            try:
                expected_hash = getattr(file_storage, '_module_hash', None)
            except Exception:
                expected_hash = None

            if expected_hash:
                # Compute SHA-256 of the uploaded archive for integrity check
                import hashlib
                sha256 = hashlib.sha256()
                with open(temp_zip_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)

                calculated_hash = sha256.hexdigest()
                if expected_hash.strip().lower() != calculated_hash.lower():
                    return False, "Le hash fourni ne correspond pas à l'archive téléchargée (intégrité invalide)."

            # Extract the zip file
            extract_dir = join_paths(temp_dir, "extracted")
            create_dir_if_not_exist(extract_dir, permissions={"read":True,"write":True,"execute":True})
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Analyze the extracted content
            # A valid melting module might be either at the root of the ZIP
            # or wrapped in a single root folder.
            items = os.listdir(extract_dir)
            
            if len(items) == 1 and os.path.isdir(join_paths(extract_dir, items[0])):
                # It's wrapped in a single folder
                module_source_dir = join_paths(extract_dir, items[0])
            else:
                raise Exception("L'archive n'est pas un module valide.")

            # Validate presence of infos.json and module.py
            infos_path = join_paths(module_source_dir, "infos.json")
            module_py_path = join_paths(module_source_dir, "module.py")

            if not os.path.exists(infos_path) or not os.path.exists(module_py_path):
                return False, "L'archive ne contient pas un module valide (infos.json ou module.py manquant)."

            # Parse infos.json to get the module name
            try:
                infos_data = json.loads(read_file(infos_path))
                module_name = infos_data.get("name")
                if not module_name:
                    return False, "Le champ 'name' est manquant dans infos.json."
            except Exception as e:
                return False, f"Impossible de lire infos.json: {str(e)}"

            # Basic validation of module name (letters and underscores only)
            if not self.app.module_manager.is_valid_module_name(module_name):
                 return False, f"Le nom du module '{module_name}' est invalide."

            module_dir = self.app.config.PATH_DIR_MODULES
            target_dir = join_paths(module_dir, module_name)
            backup_dir = None
            
            try:
                if os.path.exists(target_dir):
                    if not allow_update:
                        return False, f"Un module nommé '{module_name}' existe déjà."

                    backup_dir = join_paths(self.app.config.PATH_DIR_STORAGE_BACKUPS, "module_backup_" + module_name + "_v" + infos_data.get("version", "0.0.0"))

                    if not os.path.exists(backup_dir):
                        create_dir_if_not_exist(backup_dir, permissions={"read":True,"write":True,"execute":True})
                        shutil.move(target_dir, backup_dir)
                    else:
                        backup_already_exist = True
                        shutil.rmtree(target_dir)
                
                shutil.move(module_source_dir, module_dir)
   
               # migration de la base de donnes
                self.app.migration._run_migrations_for_module(module_name, target_dir)
            except Exception as e:
                if backup_dir and os.path.exists(backup_dir):
                    shutil.move(backup_dir, target_dir)
                return False, f"Erreur système lors de l'installation : {str(e)}"
            finally:
                if backup_dir and os.path.exists(backup_dir) and not allow_backup and not backup_already_exist:
                    shutil.rmtree(backup_dir)

            if module_name not in self.app.module_manager.list_modules_installs:
                self.app.module_manager.list_modules_installs.append(module_name)
            
            return True, f"Module '{module_name}' installé avec succès."
        except zipfile.BadZipFile:
            return False, "Le fichier ZIP est corrompu."
        except Exception as e:
            return False, f"Erreur système lors de l'installation : {str(e)}"
        finally:
            # Clean up the temporary upload directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    async def extract_and_update_core_zip(self, file_storage, options: dict = {}) -> tuple[bool, str]:
        """
        Gère l'extraction d'un core zippé et son installation
        Retourne (True, message) si succès, ou (False, message_erreur).
        """
        
        core_dir = self.app.config.PATH_DIR_CORE
        base_dir = self.app.config.PATH_DIR_BASE

        if not file_storage or not file_storage.filename.endswith('.zip'):
            return False, "Le fichier fourni n'est pas une archive ZIP valide."

        filename = secure_filename(file_storage.filename)
        # Create a temp directory for extraction
        temp_id = str(uuid.uuid4())
        temp_dir = join_paths(self.app.config.PATH_DIR_STORAGE_TEMP, temp_id)
        create_dir_if_not_exist(temp_dir, permissions={"read":True,"write":True,"execute":True})
        temp_zip_path = join_paths(temp_dir, filename)

        try:
            # Save the uploaded file temporarily
            await file_storage.save(temp_zip_path)

            # If an expected hash was provided in the request, the controller should attach it
            # to the file_storage as attribute '_module_hash'. We check and verify it here.
            expected_hash = None
            try:
                expected_hash = getattr(file_storage, '_module_hash', None)
            except Exception:
                expected_hash = None

            if expected_hash:
                # Compute SHA-256 of the uploaded archive for integrity check
                import hashlib
                sha256 = hashlib.sha256()
                with open(temp_zip_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)

                calculated_hash = sha256.hexdigest()
                if expected_hash.strip().lower() != calculated_hash.lower():
                    return False, "Le hash fourni ne correspond pas à l'archive téléchargée (intégrité invalide)."

            # Extract the zip file
            extract_dir = join_paths(temp_dir, "extracted")
            create_dir_if_not_exist(extract_dir, permissions={"read":True,"write":True,"execute":True})
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            items = os.listdir(extract_dir)

            module_source_dir = join_paths(extract_dir, "melodi_erp")

            if len(items) == 1 and os.path.isdir(module_source_dir):
                # It's wrapped in a single folder
                pass
            else:
                raise Exception("L'archive n'est pas un module valide.")

            items = os.listdir(module_source_dir)

            if "base" not in items:
                return False, "L'archive ne contient pas un module valide (base manquant)."
            
            if "core" not in items:
                return False, "L'archive ne contient pas un module valide (core manquant)."
            
            base_source_dir = join_paths(module_source_dir, "base")
            core_source_dir = join_paths(module_source_dir, "core")
            files_source_dir = join_paths(module_source_dir, "files")

            # Validate presence of infos.json and module.py
            infos_path = join_paths(base_source_dir, "infos.json")
            module_py_path = join_paths(base_source_dir, "module.py")

            if not os.path.exists(infos_path) or not os.path.exists(module_py_path):
                return False, "L'archive ne contient pas un module valide (infos.json ou module.py manquant)."

            # Parse infos.json to get the module name
            try:
                infos_data = json.loads(read_file(infos_path))
                module_name = infos_data.get("name")
                if not module_name:
                    return False, "Le champ 'name' est manquant dans infos.json."
            except Exception as e:
                return False, f"Impossible de lire infos.json: {str(e)}"

            # Basic validation of module name (letters and underscores only)
            if not self.app.module_manager.is_valid_module_name(module_name):
                return False, f"Le nom du module '{module_name}' est invalide."

            racine_dir = self.app.config.PATH_DIR_RACINE

            # Nous ne sauvegardons que `core`, `base` et les fichiers situés au niveau de la racine
            backup_dir = None
            backed_items = []  # tuples (backup_path, original_path)
            try:
                backup_dir = join_paths(self.app.config.PATH_DIR_STORAGE_BACKUPS, "melodi_erp_backup_" + infos_data.get("version", "0.0.0"))

                # prepare fresh backup dir
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                create_dir_if_not_exist(backup_dir, permissions={"read":True,"write":True,"execute":True})

                # Backup existing `core` and `base` directories if present
                for name in ("core", "base"):
                    src = join_paths(racine_dir, name)
                    if os.path.exists(src):
                        dest = join_paths(backup_dir, name)
                        shutil.move(src, dest)
                        backed_items.append((dest, src))

                # Backup files/directories at racine that will be overwritten
                if os.path.exists(files_source_dir):
                    for item in os.listdir(files_source_dir):
                        src_item = join_paths(racine_dir, item)
                        if os.path.exists(src_item):
                            dest_item = join_paths(backup_dir, item)
                            shutil.move(src_item, dest_item)
                            backed_items.append((dest_item, src_item))

                # Deploy new `core` and `base` (move into place)
                if os.path.exists(core_source_dir):
                    shutil.move(core_source_dir, join_paths(racine_dir, "core"))
                if os.path.exists(base_source_dir):
                    shutil.move(base_source_dir, join_paths(racine_dir, "base"))

                # Deploy root-level files: copy and overwrite
                if os.path.exists(files_source_dir):
                    for item in os.listdir(files_source_dir):
                        src_new_item = join_paths(files_source_dir, item)
                        dest_path = join_paths(racine_dir, item)
                        if os.path.isdir(src_new_item):
                            if os.path.exists(dest_path):
                                if os.path.isdir(dest_path):
                                    shutil.rmtree(dest_path)
                                else:
                                    os.remove(dest_path)
                            shutil.copytree(src_new_item, dest_path)
                        else:
                            parent = os.path.dirname(dest_path)
                            if parent and not os.path.exists(parent):
                                create_dir_if_not_exist(parent, permissions={"read":True,"write":True,"execute":True})
                            shutil.copy2(src_new_item, dest_path)
            except Exception as e:
                # Rollback: remove any partially deployed new items and restore backups
                try:
                    # remove newly created core/base
                    new_core = join_paths(racine_dir, "core")
                    if os.path.exists(new_core) and os.path.isdir(new_core):
                        shutil.rmtree(new_core)
                    new_base = join_paths(racine_dir, "base")
                    if os.path.exists(new_base) and os.path.isdir(new_base):
                        shutil.rmtree(new_base)

                    # remove any files copied from files_source_dir
                    if os.path.exists(files_source_dir):
                        for item in os.listdir(files_source_dir):
                            dest_item = join_paths(racine_dir, item)
                            if os.path.exists(dest_item):
                                if os.path.isdir(dest_item):
                                    shutil.rmtree(dest_item)
                                else:
                                    os.remove(dest_item)

                    # restore backups
                    for backup_path, original_path in backed_items:
                        if os.path.exists(original_path):
                            if os.path.isdir(original_path):
                                shutil.rmtree(original_path)
                            else:
                                os.remove(original_path)
                        shutil.move(backup_path, original_path)
                except Exception:
                    # best-effort restore; swallow errors to return original exception
                    pass
                return False, f"Erreur système lors de l'installation : {str(e)}"
            finally:
                if backup_dir and os.path.exists(backup_dir) and not options.get("create_backup", True):
                    shutil.rmtree(backup_dir)

            if module_name not in self.app.module_manager.list_modules_installs:
                self.app.module_manager.list_modules_installs.append(module_name)
            
            return True, f"Module '{module_name}' installé avec succès."
            
        except zipfile.BadZipFile:
            return False, "Le fichier ZIP est corrompu."
        except Exception as e:
            return False, f"Erreur système lors de l'installation : {str(e)}"
        finally:
            # Clean up the temporary upload directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

        return True, "Core mis à jour avec succès."