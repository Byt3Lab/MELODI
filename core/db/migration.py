from __future__ import annotations
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
        if self.current_session:
            return await self.current_session.execute(text(sql_query), params or {})
        else:
            return await self.app.db.execute(sql_query, params)

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
        if not parsed_files:
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
                    print(f"L'exécution des migrations a été interrompue pour le module {module_name}.")
                    break

    async def _create_tracking_table(self):
        """Crée la table de suivi globale des migrations si elle n'existe pas."""
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            module_name VARCHAR(255) PRIMARY KEY,
            current_version INT NOT NULL DEFAULT 0,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.app.db.execute(table_creation_query, query_type="write")

    def _get_modules_to_migrate(self) -> list[tuple[str, str]]:
        """Récupère la liste de tous les modules (base + installés) à vérifier, triés par dépendances."""
        modules_paths = self._build_modules_paths_dict()
        return self._sort_modules_topologically(modules_paths)

    def _build_modules_paths_dict(self) -> dict[str, str]:
        """Construit un dictionnaire contenant les chemins des modules installés et de base."""
        modules_paths = {}
        if path_exist(self.app.config.PATH_DIR_BASE_MODULE):
            modules_paths["base"] = self.app.config.PATH_DIR_BASE_MODULE
        
        for module_name in self.app.module_manager.list_modules_installs:
            modules_paths[module_name] = join_paths(self.app.config.PATH_DIR_MODULES, module_name)
            
        return modules_paths

    def _sort_modules_topologically(self, modules_paths: dict[str, str]) -> list[tuple[str, str]]:
        """Effectue un tri topologique des modules basé sur leurs dépendances (infos.json)."""
        # 1. Construire le graphe des dépendances
        graph = {m: [] for m in modules_paths}
        
        for m in modules_paths:
            if m == "base":
                continue # 'base' n'a pas de dépendances explicites à traiter ici
            
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

    async def _get_current_module_version(self, module_name: str) -> int:
        """Récupère la version actuelle du module depuis la base de données."""
        query = "SELECT current_version FROM schema_migrations WHERE module_name = :module_name"
        res = await self.app.db.execute(query, {"module_name": module_name})
        return res[0]["current_version"] if res else 0

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
            await self._run_python_migration_if_exists(module_name, version, sql_filename, migrations_dir)

            # 2. Exécuter le script SQL
            await self._run_sql_migration(session, sql_file_path)

            # 3. Mettre à jour la table de suivi
            await self._update_tracking_version(session, module_name, version)
            
            # Validation de la transaction pour cette migration
            await session.commit()
            print(f"Migration réussie pour {module_name} : {sql_filename} (version {version})")
            return True

        except Exception as e:
            # Si erreur, on annule toutes les opérations de ce fichier
            await session.rollback()
            print(f"Migration échouée pour {module_name} (fichier {sql_filename}): {e}")
            return False
            
        finally:
            self.current_session = None

    async def _run_python_migration_if_exists(self, module_name: str, version: int, sql_filename: str, migrations_dir: str):
        """Cherche et exécute un fichier Python correspondant à la migration s'il est présent."""
        py_filename = sql_filename[:-4] + ".py" if sql_filename.endswith(".sql") else None
        
        if not py_filename:
            return
            
        py_file_path = join_paths(migrations_dir, py_filename)
        
        if path_exist(py_file_path):
            spec = importlib.util.spec_from_file_location(f"migration_{module_name}_{version}", py_file_path)
            if spec and spec.loader:
                py_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(py_module)
                if hasattr(py_module, "migrate"):
                    await py_module.migrate(self)

    async def _run_sql_migration(self, session, sql_file_path: str):
        """Lit et exécute le contenu d'un fichier SQL dans la session courante."""
        with open(sql_file_path, 'r', encoding='utf-8') as fh:
            sql_content = fh.read()

        if sql_content.strip():
            await session.execute(text(sql_content))

    async def _update_tracking_version(self, session, module_name: str, version: int):
        """Met à jour ou insère la nouvelle version atteinte par le module dans la base."""
        check_res = await session.execute(
            text("SELECT 1 FROM schema_migrations WHERE module_name = :m"), 
            {"m": module_name}
        )
        exists = check_res.first() is not None

        if exists:
            await session.execute(
                text("UPDATE schema_migrations SET current_version = :v, last_update = CURRENT_TIMESTAMP WHERE module_name = :m"),
                {"v": version, "m": module_name}
            )
        else:
            await session.execute(
                text("INSERT INTO schema_migrations (module_name, current_version) VALUES (:m, :v)"),
                {"m": module_name, "v": version}
            )
