from __future__ import annotations
from typing import TYPE_CHECKING, Any
import os
import re
from sqlalchemy import text
from core.utils import join_paths, path_exist

if TYPE_CHECKING:
    from core.application import Application

class Migration:
    def __init__(self, app:Application):
        self.app = app

    async def run_migrations(self):
        """Scanne les dossiers de migration pour chaque module et applique les scripts SQL dans l'ordre."""
        await self._create_tracking_table()
        
        modules = self._get_modules_to_migrate()
       
        for module_name, module_path in modules:
            migrations_dir = join_paths(module_path, "migrations")
            if not path_exist(migrations_dir):
                continue
            
            parsed_files = self._get_migration_files(migrations_dir)
            if not parsed_files:
                continue
            
            current_db_version = await self._get_current_module_version(module_name)
            files_to_run = [f for f in parsed_files if f[0] > current_db_version]
            if not files_to_run:
                continue

            async with self.app.db.get_session() as session:
                for version, filename in files_to_run:
                    success = await self._execute_migration_file(
                        session, module_name, version, filename, migrations_dir
                    )
                    if not success:
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
        """Récupère la liste de tous les modules (base + installés) à vérifier."""
        modules = []
        if path_exist(self.app.config.PATH_DIR_BASE_MODULE):
            modules.append(("base", self.app.config.PATH_DIR_BASE_MODULE))
        
        for module_name in self.app.module_manager.list_modules_installs:
            modules.append((module_name, join_paths(self.app.config.PATH_DIR_MODULES, module_name)))
            
        return modules

    def _get_migration_files(self, migrations_dir: str) -> list[tuple[int, str]]:
        """Extrait et trie les fichiers de migration valides."""
        try:
            sql_files = [f for f in os.listdir(migrations_dir) if f.endswith('.sql')]
        except Exception as e:
            print(f"Erreur lors de la lecture du dossier de migrations {migrations_dir}: {e}")
            return []

        parsed_files = []
        for f in sql_files:
            match = re.search(r'v(\d+)', f)
            if not match:
                match = re.search(r'(\d+)', f)
            if match:
                version = int(match.group(1))
                parsed_files.append((version, f))

        parsed_files.sort(key=lambda x: x[0])
        return parsed_files

    async def _get_current_module_version(self, module_name: str) -> int:
        """Récupère la version actuelle du module depuis la base de données."""
        res = await self.app.db.execute(
            "SELECT current_version FROM schema_migrations WHERE module_name = :module_name", 
            {"module_name": module_name}
        )
        return res[0]["current_version"] if res else 0

    async def _execute_migration_file(self, session, module_name: str, version: int, filename: str, migrations_dir: str) -> bool:
        """Exécute un fichier de migration dans une transaction et met à jour la base de données."""
        file_path = join_paths(migrations_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                sql_content = fh.read()

            # Exécuter le script SQL dans la transaction courante
            await session.execute(text(sql_content))

            # Mettre à jour la table de suivi
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
            
            # Validation de la transaction pour cette migration
            await session.commit()
            print(f"Migration réussie pour {module_name} : {filename} (version {version})")
            return True

        except Exception as e:
            # Si erreur, on annule les opérations de ce fichier
            await session.rollback()
            print(f"Migration échouée pour {module_name} (fichier {filename}): {e}")
            return False
