import os
import zipfile
import shutil
import json
import uuid
from werkzeug.utils import secure_filename
from core.utils import join_paths, create_dir_if_not_exist, read_file
from core.service import Service

class ModuleService(Service):
    async def extract_and_install_zip(self, file_storage) -> tuple[bool, str]:
        """
        Gère l'extraction d'un module zippé et son installation dans le dossier modules/.
        Retourne (True, message) si succès, ou (False, message_erreur).
        """
        if not file_storage or not file_storage.filename.endswith('.zip'):
            return False, "Le fichier fourni n'est pas une archive ZIP valide."

        filename = secure_filename(file_storage.filename)
        # Create a temp directory for extraction
        temp_id = str(uuid.uuid4())
        temp_dir = join_paths(self.app.config.PATH_DIR_STORAGE, "temp_uploads", temp_id)
        create_dir_if_not_exist(temp_dir)
        
        temp_zip_path = join_paths(temp_dir, filename)
        
        try:
            # Save the uploaded file temporarily
            file_storage.save(temp_zip_path)
            
            # Extract the zip file
            extract_dir = join_paths(temp_dir, "extracted")
            create_dir_if_not_exist(extract_dir)
            
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
                # Files are directly at the root of the extract dir
                module_source_dir = extract_dir

            # Validate presence of infos.json and module.py
            infos_path = join_paths(module_source_dir, "infos.json")
            module_py_path = join_paths(module_source_dir, "module.py")

            if not os.path.exists(infos_path) or not os.path.exists(module_py_path):
                return False, "L'archive ne contient pas un module MELODI valide (infos.json ou module.py manquant)."

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

            # Target directory
            target_dir = join_paths(self.app.config.PATH_DIR_MODULES, module_name)
            
            # Check if module already exists
            if os.path.exists(target_dir):
                # Optionally, we could backup/overwrite, but for now we reject
                # To support update, we could remove the existing dir
                # shutil.rmtree(target_dir)
                return False, f"Un module nommé '{module_name}' existe déjà."

            # Move the validated folder to the modules directory
            shutil.move(module_source_dir, target_dir)

            # Try to load the newly installed module into the ModuleManager registry
            self.app.module_manager.list_modules_installs.append(module_name)
            # The user will need to enable it manually from the UI
            
            return True, f"Module '{module_name}' installé avec succès."
            
        except zipfile.BadZipFile:
            return False, "Le fichier ZIP est corrompu."
        except Exception as e:
            return False, f"Erreur système lors de l'installation : {str(e)}"
        finally:
            # Clean up the temporary upload directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
