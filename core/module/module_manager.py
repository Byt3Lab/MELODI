from __future__ import annotations
import importlib.util
import json
import os
import sys
from typing import TYPE_CHECKING
from core.utils import join_paths, path_exist, read_file
from .module import Module

if TYPE_CHECKING:
    from core import Application
    
class ModuleManager:
    """Gère l'ensemble des modules de l'application.

    Responsibilities:
    - charger dynamiquement les modules depuis un dossier
    - tenir un registre des modules chargés
    - fournir des opérations d'ajout / récupération
    """

    def __init__(self, app: Application | None = None):
        self.app = app
        self.PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES
        self.modules: dict[str, Module] = {}
        self.modules_infos: dict[str, object] = {}
        self.modules_on: list[str] = []
        self.list_modules_installs = []
        self.load_list_modules_installs()
        self.load_modules_on()
        self.check_modules_on()
        
    def load_modules_on(self):
        path = join_paths(self.app.config.PATH_DIR_CONFIG, "modules_on.json")
        if not path_exist(path):
            self.modules_on = [] 
            return
        self.modules_on = json.loads(read_file(path_file=path))

    def load_list_modules_installs(self):
        if not os.path.isdir(self.PATH_DIR_MODULES):
            return
        list = os.listdir(self.PATH_DIR_MODULES)

        for current_module_dirname in list:
            if current_module_dirname == "base" or not self.is_valid_module_name(current_module_dirname):
                continue

            if not os.path.isdir(join_paths(self.PATH_DIR_MODULES, current_module_dirname)):
                continue
            
            self.list_modules_installs.append(current_module_dirname)
            
    def get_module(self, name: str):
        return self.modules.get(name)

    def _load_module_from_path(self, module_name: str, path: str):
        """Charge un module Python depuis un chemin de fichier et retourne le module importé."""
        
        spec = importlib.util.spec_from_file_location(module_name, path)

        if spec is None or spec.loader is None:
            raise ImportError(f"Impossible de créer le spec pour {path}")
        
        module = importlib.util.module_from_spec(spec)
    
        # enregistrer temporairement pour permettre les imports relatifs
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        return module

    def load_modules(self):
        """Charge dynamiquement tous les modules présents dans `path_modules`.

        Chaque sous-dossier ou fichier doit exposer une variable `module` qui est
        une instance de `Module` (ou d'une sous-classe). Pour chaque module, on
        appelle `module.load()` puis `self.add_module(module)`.
        """

        # parcourir les éléments du dossier modules

        for current_module_dirname in self.list_modules_installs:
            self._load_module(current_module_dirname)

    def _load_module(self, name_module):
        if self.isLoad(name_module):
            return
        
        if not self.isOn(name_module):
            return

        if not self.isInstall(name_module):
            return

        path_dir_to_current_module = join_paths(self.PATH_DIR_MODULES, name_module)

        path_file_to_current_module_py = join_paths(path_dir_to_current_module, "module.py")

        if not path_exist(path_file_to_current_module_py):
            # skip directories without python module.py in dir of current_module_dirname
            return

        module_name_space = f"modules.{name_module}.module"

        try:
            mod = self._load_module_from_path(module_name_space, path_file_to_current_module_py)
        except Exception as e:
            # erreur d'import, ignorer ou logger
            print(f"Erreur lors de l'import du module {name_module}: {e}")
            return

        # chercher l'objet `module` à l'intérieur
        module_instance = getattr(mod, "module", None)

        if module_instance is None:
            print(f"Aucun objet `module` de type Module trouvé dans {name_module}, skipped.")
            return

        # assurer que c'est bien une instance de Module
        if not isinstance(module_instance, Module):
            print(f"Objet `module` dans {name_module} n'est pas une instance de Module, skipped.")
            return

        module_infos = self.get_module_infos(name_module)
    
        try:
            depends = module_infos["depends"]["modules"]
        except:
            depends = []

        for depend in depends:
            try:
                parse = self.parse_module_name(depend)
                name = parse.get("name", "")
                constraints = parse.get("constraints", [])

                version = self.get_module_infos(name).get("version")
            except:
                return

            if not self.check_compatibility(constraints, version):
                return
            
            try:
                self._load_module(name)
            except:
                # self.off_module(name_module)
                return
            
        # appeler la méthode load() si disponible
        try:
            module_instance.init(app=self.app, dirname=name_module)
            module_instance.load()
        except Exception as e:
            print(f"Erreur pendant module.load() pour {name_module}: {e}")

        # ajouter au registre d'application
        try:
            self.add_module(module_instance, name_module)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du module {name_module}: {e}")

    def run_modules(self):
        """Appelle la méthode `_run()` de chaque module chargé."""
        for module_name, module in self.modules.items():
            try:
                module._run()
            except Exception as e:
                print(f"Erreur lors de l'exécution du module {module_name}: {e}")

    def isOn(self, name_module:str)->bool:
        return name_module in self.modules_on

    def isLoad(self, name_module:str)->bool:
        return name_module in self.modules

    def isInstall(self, name_module):
        return name_module in self.list_modules_installs

    def on_module(self, name_module):
        if self.isOn(name_module):
            return True
        
        if not self.isInstall(name_module):
            return False
        
        path_file_module_py = join_paths(self.PATH_DIR_MODULES, name_module, "module.py")
        path_file_module_infos = join_paths(self.PATH_DIR_MODULES, name_module, "infos.json")
               
        if not path_exist(path_file_module_py) or not path_exist(path_file_module_infos):
            return False
        
        module_infos = self.get_module_infos(name_module)
        
        try:
            depends = module_infos["depends"]["modules"]
        except:
            depends = []
        
        for depend in depends:
            try:
                parse = self.parse_module_name(depend)
                name = parse.get("name", "")
                constraints = parse.get("constraints", [])

                version = self.get_module_infos(name).get("version")
            except:
                return False

            if not self.check_compatibility(constraints, version):
                return False
            
            if not self.on_module(name) == True:
                return False

        self.modules_on.append(name_module)
        self.set_file_modules_on()
        return True

    def off_module(self, name_module):
        if not self.isOn(name_module):
            return

        module_infos = self.get_module_infos(name_module)

        depends_by = self.get_depends_by(name_module)

        if len(depends_by) > 0 :
            for d in depends_by:
                if not d == name_module and self.isOn(d):
                    return
        try:
            depends = module_infos["depends"]["modules"]
        except:
            depends = []


        self.modules_on.remove(name_module)
        self.set_file_modules_on()

        for depend in depends:
            try:
                name = self.parse_module_name(depend).get("name", "")
            except:
                return False
            
            self.off_module(name)

        return True

    def get_module_infos(self,name_module):
        infos = {}

        if (name_module == "base"):
            path = join_paths(self.app.config.PATH_DIR_RACINE, name_module, "infos.json")
        else:
            path = join_paths(self.PATH_DIR_MODULES, name_module, "infos.json")

        if not path_exist(path):
            return None

        try:
            infos = json.loads(read_file(path_file=path))
        except:
            infos = {}
                    
        return infos
    
    def get_depends_by(self, name_module):
        depends_by = []

        for m, infos in self.modules_infos.items():
            try:
                depends = infos["depends"]["modules"]
            
                for depend in depends:
                    name = self.parse_module_name(depend).get("name", "")
                    
                    if name_module == name:
                        depends_by.append(m)
            except:
                continue

        return depends_by
    
    def set_file_modules_on(self):
        PATH_FILE_MODULES_ON = self.app.config.PATH_DIR_CONFIG + "/modules_on.json"

        with open(PATH_FILE_MODULES_ON, "w", encoding="utf-8") as fh:
            content = json.dumps(self.modules_on, indent=4, ensure_ascii=False)
            fh.write(f"{content}")

    def add_module(self, module: Module, name_module:str):
        """Enregistre une instance de module dans le registre."""
        self.modules_infos[name_module] = self.get_module_infos(name_module)
        self.modules[name_module] = module

    def module_exists(self, name_module)->bool:
        return os.path.isdir(join_paths(self.PATH_DIR_MODULES, name_module))
    
    def list_modules(self):
        """
        Parcourt le dossier des modules et retourne une liste d'objets décrivant chaque module.
        Chaque entrée a la forme :
          { "name": <nom_du_module>, "path": <chemin_du_dossier>, "infos": <contenu_json|None>, "enabled": <bool> }
        """
        import json

        PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES

        modules = []

        for module_name in self.list_modules_installs:
            entry_path = join_paths(PATH_DIR_MODULES, module_name)
            if not os.path.isdir(entry_path):
                continue

            infos = None
            infos_file = join_paths(entry_path, "infos.json")
            if os.path.exists(infos_file):
                try:
                    with open(infos_file, "r", encoding="utf-8") as fh:
                        infos = json.load(fh)
                except Exception as exc:
                    # retourner l'erreur dans le champ infos pour faciliter le debug
                    infos = {"_error": f"Impossible de lire infos.json: {exc}"}

            modules.append({
                "name": module_name,
                "path": entry_path,
                "infos": infos,
                "enabled": module_name in self.modules_on
            })
        return modules
    
    def check_modules_on(self):
        modules_on = [] 
        
        for module in self.modules_on:
            if self.isInstall(module):
                modules_on.append(module)
                continue
        
        self.modules_on = modules_on
        self.set_file_modules_on()

    def parse_module_name(self, requirement: str) -> dict:
        """
        Analyse une chaîne comme 'stock>=1.0.0,==2.2.2' ou 'users==1.2' ou 'compta'
        et retourne :
        {
            "name": "stock",
            "constraints": [
                { "operator": ">=", "version": "1.0.0" },
                { "operator": "==", "version": "2.2.2" }
            ]
        }
        """

        import re

        # Regex pour capturer le nom et les contraintes
        pattern = r"^([a-zA-Z0-9_\-]+)((?:[=<>!]+[\d\.]+(?:,)?)+)?$"
        match = re.match(pattern, requirement.strip())

        if not match:
            raise ValueError(f"Format invalide : {requirement}")

        name = match.group(1)
        constraints_str = match.group(2)

        constraints = []
        if constraints_str:
            # Trouver toutes les paires (opérateur, version)
            sub_pattern = r"([=<>!]+)\s*([\d\.]+)"
            for op, ver in re.findall(sub_pattern, constraints_str):
                constraints.append({
                    "operator": op,
                    "version": ver
                })

        return {
            "name": name,
            "constraints": constraints
        }
    
    def check_compatibility(self, constraints: list[dict[str, str]], target_version: str) -> bool:
        """
        Détermine si une version cible satisfait toutes les contraintes de version spécifiées.

        Args:
            constraints: Liste des dictionnaires de contraintes (opérateur, version).
            target_version: La version du module à vérifier (ex: "1.5.0").

        Returns:
            True si la version cible est compatible avec TOUTES les contraintes, False sinon.
        """

        from packaging.version import parse as parse_version

        # 1. Analyser la version cible une seule fois
        try:
            v_target = parse_version(target_version)
        except Exception:
            # Gérer les cas où la version cible est invalide
            print(f"Erreur: La version cible '{target_version}' est invalide.")
            return False
            
        # 2. Parcourir toutes les contraintes
        for constraint in constraints:
            op = constraint.get("operator")
            ver_str = constraint.get("version")
            
            # 3. Analyser la version de la contrainte
            try:
                v_constraint = parse_version(ver_str)
            except Exception:
                print(f"Avertissement: La contrainte '{op}{ver_str}' est invalide et ignorée.")
                continue

            # 4. Évaluer la contrainte
            is_satisfied = False
            
            if op == "==":
                is_satisfied = (v_target == v_constraint)
            elif op == ">=":
                is_satisfied = (v_target >= v_constraint)
            elif op == "<=":
                is_satisfied = (v_target <= v_constraint)
            elif op == ">":
                is_satisfied = (v_target > v_constraint)
            elif op == "<":
                is_satisfied = (v_target < v_constraint)
            elif op == "!=":
                is_satisfied = (v_target != v_constraint)
            else:
                # Opérateur inconnu
                print(f"Avertissement: Opérateur inconnu '{op}' ignoré.")
                continue
                
            # Si une seule contrainte n'est pas satisfaite, le module est incompatible
            if not is_satisfied:
                return False

        # Si toutes les contraintes ont été vérifiées et satisfaites
        return True

    def is_valid_module_name(self, name: str) -> bool:
        """
        Vérifie que le nom du module :
        - contient uniquement des lettres et des underscores (_)
        - ne commence pas par un underscore
        - ne contient pas de chiffres ni de caractères spéciaux
        """
        import re

        pattern = r"^[A-Za-z][A-Za-z_]*$"
        return bool(re.match(pattern, name))