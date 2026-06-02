from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any
import os
import re
import importlib.util
from sqlalchemy import text
from core.utils import join_paths, path_exist

if TYPE_CHECKING:
    from core.application import Application

class Migration:
    """
    Gère le système de migrations de la base de données pour l'application MELODI.
    
    Ce gestionnaire permet de :
    - Créer et suivre l'état des migrations dans une table `schema_migrations`.
    - Exécuter les migrations (`.py` et `.sql`) dans l'ordre de dépendance des modules.
    - Garantir que chaque migration est exécutée de façon transactionnelle.
    """
    
    def __init__(self, app: Application):
        self.app = app
        self.current_session = None

    async def execute_safe_query(self, sql_query: str, params: dict = None) -> Any:
        """
        Exécute une requête SQL de façon sécurisée (dans la transaction courante si applicable).
        Particulièrement utile pour les scripts de migration Python qui accompagnent le SQL.
        """
        return await self.app.db.execute(query=sql_query, params=params, session=self.current_session)

    async def run_migrations(self):
        """Scanne les dossiers de migration pour chaque module et applique les scripts dans l'ordre."""
        await self._create_tracking_table()
        
        modules = self._get_modules_to_migrate()
    
        for module_name, module_path in modules:
            await self._run_migrations_for_module(module_name, module_path)

    async def _run_migrations_for_module(self, module_name: str, module_path: str):
        """Traite et exécute les fichiers de migration nécessaires pour un module spécifique."""
        migrations_dir = join_paths(module_path, "migrations")
        
        if not path_exist(migrations_dir):
            return

        parsed_files = self._get_migration_files(migrations_dir)

        if len(parsed_files) == 0:
            return
        
        current_db_version = await self._get_current_module_version(module_name)
        files_to_run = [f for f in parsed_files if f[0] > current_db_version]
        
        if not files_to_run:
            return

        async with self.app.db.get_session() as session:
            for version, filename in files_to_run:
                success = await self._execute_migration_file(
                    session, module_name, version, filename, migrations_dir
                )
                if not success:
                    await session.rollback()
                    self.app.module_manager.off_module(module_name)
                    print(f"L'exécution des migrations a été interrompue pour le module {module_name}.")
                    break

    async def _create_tracking_table(self):
        """Crée la table de suivi globale des migrations si elle n'existe pas."""
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS {PREFIX_TABLE}schema_migrations (
            module_name VARCHAR(255) PRIMARY KEY,
            current_version INT NOT NULL DEFAULT 0,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        query = table_creation_query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)

        await self.app.db.execute(query = query, query_type="write")

    async def _update_tracking_version(self, session, module_name: str, version: int):
        """Met à jour ou insère la nouvelle version atteinte par le module dans la base."""
        query = "SELECT 1 FROM {PREFIX_TABLE}schema_migrations WHERE module_name = :m"
        query = query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)
        check_res = await self.app.db.execute(query = query, params = {"m": module_name})

        if len(check_res) == 1:
            exists = True
        else:
            exists = False

        if exists:
            query = "UPDATE {PREFIX_TABLE}schema_migrations SET current_version = :v, last_update = CURRENT_TIMESTAMP WHERE module_name = :m"
            query = query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)
            await self.app.db.execute(query = query, params = {"v": version, "m": module_name}, query_type="write")
        else:
            query = "INSERT INTO {PREFIX_TABLE}schema_migrations (module_name, current_version) VALUES (:m, :v)"
            query = query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)
            await self.app.db.execute(query = query, params = {"m": module_name, "v": version}, query_type="write")

    async def _get_current_module_version(self, module_name: str) -> int:
        """Récupère la version actuelle du module depuis la base de données."""
        query = "SELECT current_version FROM {PREFIX_TABLE}schema_migrations WHERE module_name = :module_name"
        query = query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)
        res = await self.app.db.execute(query = query, params = {"module_name": module_name})
        if len(res) == 0:
            return 0
        return res[0]["current_version"]

    def _get_modules_to_migrate(self) -> list[tuple[str, str]]:
        """Récupère la liste de tous les modules (base + installés) à vérifier, triés par dépendances."""
        modules_paths = self._build_modules_paths_dict()
        return self._sort_modules_topologically(modules_paths)

    def _build_modules_paths_dict(self) -> dict[str, str]:
        """Construit un dictionnaire contenant les chemins des modules activés et de base."""
        modules_paths = {}
        if path_exist(self.app.config.PATH_DIR_BASE_MODULE):
            modules_paths["base"] = self.app.config.PATH_DIR_BASE_MODULE
        
        for module_name in self.app.module_manager.list_modules_installs:
            if self.app.module_manager.isOn(module_name):
                modules_paths[module_name] = join_paths(self.app.config.PATH_DIR_MODULES, module_name)
            
        return modules_paths

    def _sort_modules_topologically(self, modules_paths: dict[str, str]) -> list[tuple[str, str]]:
        """Effectue un tri topologique des modules basé sur leurs dépendances (infos.json)."""
        # 1. Construire le graphe des dépendances
        graph = {m: [] for m in modules_paths}
        
        for m in modules_paths:
            if m == "base":
                continue
            
            infos = self.app.module_manager.get_module_infos(m)
            if infos and "depends" in infos and "modules" in infos["depends"]:
                for dep in infos["depends"]["modules"]:
                    try:
                        dep_name = self.app.module_manager.parse_module_name(dep).get("name")
                        if dep_name in modules_paths and dep_name != m:
                            graph[m].append(dep_name)
                    except Exception:
                        pass # Dépendance mal formée ignorée

        # 2. Tri topologique via DFS (Depth-First Search)
        visited = set()
        temp_mark = set()
        sorted_modules = []

        def visit(node):
            if node in temp_mark:
                return # Dépendance circulaire détectée et ignorée
            if node not in visited:
                temp_mark.add(node)
                if node in graph:
                    for str_dep in graph[node]:
                        visit(str_dep)
                temp_mark.remove(node)
                visited.add(node)
                sorted_modules.append(node)

        for m in modules_paths:
            visit(m)

        return [(m, modules_paths[m]) for m in sorted_modules]

    def _get_migration_files(self, migrations_dir: str) -> list[tuple[int, str]]:
        """Extrait et trie les fichiers de migration SQL valides (ex: 001_init.sql, v2_update.sql)."""
        try:
            sql_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
        except Exception as e:
            print(f"Erreur lors de la lecture du dossier de migrations {migrations_dir}: {e}")
            return []

        parsed_files = []
        for f in sql_files:
            match = re.search(r'v?(\d+)', f) # Supporte 'v1' ou '1'
            if match:
                version = int(match.group(1))
                parsed_files.append((version, f))

        parsed_files.sort(key=lambda x: x[0])
        return parsed_files

    async def _execute_migration_file(self, session, module_name: str, version: int, sql_filename: str, migrations_dir: str) -> bool:
        """
        Exécute un fichier de migration dans une transaction sécurisée.
        Si un fichier Python du même nom existe, sa fonction asynchrone `migrate` est exécutée en premier.
        Ensuite, le script SQL est exécuté. Enfin, la version est mise à jour.
        """
        sql_file_path = join_paths(migrations_dir, sql_filename)
        
        try:
            self.current_session = session

            # 1. Exécuter le script Python associé (s'il existe)
            should_run_sql = await self._run_python_migration_if_exists(module_name, version, sql_filename, migrations_dir)

            # 2. Exécuter le script SQL
            if should_run_sql is True:
                await self._run_sql_migration(session, sql_file_path, migrations_dir, version)

                # 3. Mettre à jour la table de suivi
                await self._update_tracking_version(session, module_name, version)
                
                # Validation de la transaction pour cette migration
                await session.commit()
                print(f"Migration réussie pour {module_name} : {sql_filename} (version {version})")
                return True

            raise Exception(f"Migration annulée pour {module_name} (fichier {sql_filename}): le script Python a renvoyé False")
        except Exception as e:
            # Si erreur, on annule toutes les opérations de ce fichier
            await session.rollback()
            await self.app.module_manager.off_module(module_name)
            print(f"Migration échouée pour {module_name} (fichier {sql_filename}): {e}")
            return False
            
        finally:
            self.current_session = None

    async def _run_python_migration_if_exists(self, module_name: str, version: int, sql_filename: str, migrations_dir: str):
        """Cherche et exécute un fichier Python correspondant à la migration s'il est présent."""
        py_filename = sql_filename[:-4] + ".py" if sql_filename.endswith(".sql") else None
        
        if not py_filename:
            return True
            
        py_file_path = join_paths(migrations_dir, py_filename)
        
        if path_exist(py_file_path):
            spec = importlib.util.spec_from_file_location(f"migration_{module_name}_{version}", py_file_path)
            if spec and spec.loader:
                py_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(py_module)
                if hasattr(py_module, "migrate"):
                    options = {
                        "migration": self,
                        "module_name": module_name,
                        "version": version,
                        "sql_filename": sql_filename,
                        "migrations_dir": migrations_dir
                    }
                    return await py_module.migrate(options)
        return True

    def _get_migration_data(self, migrations_dir: str, version: int) -> dict:
        """Récupère les données de migration pour un module."""
        migration_data_path = join_paths(migrations_dir, f"v{version}_data.json")
        
        if path_exist(migration_data_path):
            with open(migration_data_path, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        
        return {}

    def _format_sql_query(self, query: str, migrations_dir: str, version: int) -> str:
        """Remplace les balises {PREFIX_TABLE} et {migration_data} de façon sécurisée."""
        
        query = query.replace("{PREFIX_TABLE}", self.app.config.PREFIX_TABLE)
        
        migration_data = self._get_migration_data(migrations_dir, version)
                
        for key, value in migration_data.items():
            placeholder = "{+"+key+"+}"
            query = query.replace(placeholder, str(value))
        
        return query

    async def _run_sql_migration(self, session, sql_file_path: str, migrations_dir: str, version: int):
        """Lit et exécute le contenu d'un fichier SQL dans la session courante."""
        with open(sql_file_path, 'r', encoding='utf-8') as fh:
            sql_content = fh.read()

        sql_content = self._format_sql_query(sql_content, migrations_dir, version)

        if sql_content.strip():
            await self.app.db.execute(query=sql_content,session=session)

    async def remove_tracking_migration_for_module(self):
        pass

    async def remove_all_tracking_migrations(self):
        pass