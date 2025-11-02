from __future__ import annotations

import importlib.util
import json
import os
import sys
from typing import TYPE_CHECKING
from .module import Module

if TYPE_CHECKING:
    from .application import Application
    from .module import Module
    
class ModuleManager:
    """Gère l'ensemble des modules de l'application.

    Responsibilities:
    - charger dynamiquement les modules depuis un dossier
    - tenir un registre des modules chargés
    - fournir des opérations d'ajout / récupération
    """

    def __init__(self, app: Application | None = None):
        self.app = app
        self.modules: dict[str, Module] = {}
        self.modules_on: list[str] = self.app.config.modules_on

    def add_module(self, module: Module, name_module:str):
        """Enregistre une instance de module dans le registre."""
        self.modules[name_module] = module

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

        PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES

        if not os.path.isdir(PATH_DIR_MODULES):
            return

        list_modules = os.listdir(PATH_DIR_MODULES)

        # parcourir les éléments du dossier modules

        for current_module_dirname in list_modules:
            if (current_module_dirname.startswith("_")):
                continue

            path_dir_to_current_module = os.path.join(PATH_DIR_MODULES, current_module_dirname)

            if not os.path.isdir(path_dir_to_current_module):
                continue

            path_file_to_current_module_py = os.path.join(path_dir_to_current_module, "module.py")

            if not os.path.exists(path_file_to_current_module_py):
                # skip directories without python module.py in dir of current_module_dirname
                continue

            module_name_space = f"modules.{current_module_dirname}.module"

            try:
                mod = self._load_module_from_path(module_name_space, path_file_to_current_module_py)
            except Exception as e:
                # erreur d'import, ignorer ou logger
                print(f"Erreur lors de l'import du module {current_module_dirname}: {e}")
                continue

            # chercher l'objet `module` à l'intérieur
            module_instance = getattr(mod, "module", None)

            if module_instance is None:
                print(f"Aucun objet `module` de type Module trouvé dans {current_module_dirname}, skipped.")
                continue

            # assurer que c'est bien une instance de Module
            if not isinstance(module_instance, Module):
                print(f"Objet `module` dans {current_module_dirname} n'est pas une instance de Module, skipped.")
                continue

            if not self.isOn(current_module_dirname):
                continue

            # appeler la méthode load() si disponible
            try:
                if hasattr(module_instance, "load"):
                    module_instance.init(app=self.app, dirname=current_module_dirname)
                    module_instance.load()
            except Exception as e:
                print(f"Erreur pendant module.load() pour {current_module_dirname}: {e}")

            # ajouter au registre d'application
            try:
                self.add_module(module_instance, current_module_dirname)
            except Exception as e:
                print(f"Erreur lors de l'enregistrement du module {current_module_dirname}: {e}")

    def run_modules(self):
        """Appelle la méthode `_run()` de chaque module chargé."""
        for module_name, module in self.modules.items():
            try:
                module.run()
            except Exception as e:
                print(f"Erreur lors de l'exécution du module {module_name}: {e}")

    def isOn(self, dirname:str)->bool:
        return dirname in self.modules_on

    def on_module(self, name_module):
        if self.isOn(name_module):
            return

        if self.module_exists(name_module):
            self.modules_on.append(name_module)
            self.set_file_modules_on()


    def off_module(self, name_module):
        print(f"Désactivation du module {name_module}")

        if name_module not in self.modules_on:
            return
        
        self.modules_on.remove(name_module)
        self.set_file_modules_on()

    def set_file_modules_on(self):
        PATH_FILE_MODULES_ON = self.app.config.PATH_DIR_CONFIG + "/modules_on.json"

        with open(PATH_FILE_MODULES_ON, "w", encoding="utf-8") as fh:
                content = json.dumps(self.modules_on, indent=4, ensure_ascii=False)
                fh.write(f"{content}")

    def module_exists(self, name_module)->bool:
        PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES
        path_module = os.path.join(PATH_DIR_MODULES, name_module)
        return os.path.isdir(path_module)
    
    def del_module(self, name_module):
        pass

    def resolve_load_order(self) -> list[str]:
        """
        Lit le fichier de manifeste de chaque module activé (manifest.json ou infos.json),
        extrait les dépendances et retourne la liste des modules à charger dans l'ordre
        (tri topologique). Lève RuntimeError en cas de dépendances manquantes ou de cycle.
        """

        from collections import deque
        import json

        PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES
        if not os.path.isdir(PATH_DIR_MODULES):
            return []

        # Collecter les modules activés et leurs dépendances
        deps_map: dict[str, list[str]] = {}
        for entry in os.listdir(PATH_DIR_MODULES):
            if entry.startswith("_"):
                continue
            entry_path = os.path.join(PATH_DIR_MODULES, entry)
            if not os.path.isdir(entry_path):
                continue
            if not self.isOn(entry):
                continue

            manifest_path = os.path.join(entry_path, "infos.json"),

            manifest = None
            
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as fh:
                        manifest = json.load(fh)
                except Exception as exc:
                    raise RuntimeError(f"Impossible de lire {manifest_path} pour le module '{entry}': {exc}")

            deps = []
            if manifest:
                raw = manifest.get("depends") if isinstance(manifest, dict) else None

                if raw is not None:
                    if isinstance(raw, str):
                        deps = [raw.strip()] if raw.strip() else []
                    elif isinstance(raw, (list, tuple)):
                        deps = [str(d).strip() for d in raw if str(d).strip()]
                    else:
                        raise RuntimeError(f"Dépendances du module '{entry}' mal formées dans le manifeste.")
            deps_map[entry] = deps

        nodes = set(deps_map.keys())

        # Vérifier que toutes les dépendances existent parmi les modules activés
        missing = {}
        for mod, deps in deps_map.items():
            for d in deps:
                if d not in nodes:
                    missing.setdefault(mod, []).append(d)
        if missing:
            msgs = [f"{m} -> {', '.join(ds)}" for m, ds in missing.items()]
            raise RuntimeError(f"Dépendances manquantes pour des modules activés: {'; '.join(msgs)}")

        # Construire graphe inverse pour Kahn (arcs: dep -> module)
        graph: dict[str, set[str]] = {n: set() for n in nodes}
        indeg: dict[str, int] = {n: 0 for n in nodes}
        for mod, deps in deps_map.items():
            for d in deps:
                graph[d].add(mod)
                indeg[mod] += 1

        # Kahn
        q = deque([n for n, deg in indeg.items() if deg == 0])
        order: list[str] = []
        while q:
            n = q.popleft()
            order.append(n)
            for nb in graph[n]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    q.append(nb)

        if len(order) != len(nodes):
            # il y a un cycle
            remaining = [n for n, deg in indeg.items() if deg > 0]
            raise RuntimeError(f"Cycle détecté dans les dépendances des modules: {', '.join(remaining)}")

        return order

    def list_modules(self):
        """
        Parcourt le dossier des modules et retourne une liste d'objets décrivant chaque module.
        Chaque entrée a la forme :
          { "name": <nom_du_module>, "path": <chemin_du_dossier>, "infos": <contenu_json|None>, "enabled": <bool> }
        """
        import json

        PATH_DIR_MODULES = self.app.config.PATH_DIR_MODULES

        modules = []

        if not os.path.isdir(PATH_DIR_MODULES):
            return modules

        for entry in os.listdir(PATH_DIR_MODULES):
            # ignorer les fichiers/dirs cachés ou de configuration
            if entry.startswith("_"):
                continue

            entry_path = os.path.join(PATH_DIR_MODULES, entry)
            if not os.path.isdir(entry_path):
                continue

            infos = None
            infos_file = os.path.join(entry_path, "infos.json")
            if os.path.exists(infos_file):
                try:
                    with open(infos_file, "r", encoding="utf-8") as fh:
                        infos = json.load(fh)
                except Exception as exc:
                    # retourner l'erreur dans le champ infos pour faciliter le debug
                    infos = {"_error": f"Impossible de lire infos.json: {exc}"}

            modules.append({
                "name": entry,
                "path": entry_path,
                "infos": infos,
                "enabled": entry in getattr(self, "modules_on", [])
            })
        return modules