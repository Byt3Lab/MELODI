import os
import pathlib
import json
from core.utils import path_exist, read_file, join_paths
# from doteenv import load_dotenv

# load_dotenv()

class Config:
    PATH_DIR_RACINE = pathlib.Path(__file__).parent.parent.resolve()
    PATH_DIR_CONFIG = join_paths(PATH_DIR_RACINE, "config")
    PATH_DIR_CORE = join_paths(PATH_DIR_RACINE, "core")
    PATH_DIR_BASE_MODULE = join_paths(PATH_DIR_RACINE, "base")
    PATH_DIR_MODULES = join_paths(PATH_DIR_RACINE, "modules")
    PATH_DIR_PLUGINS = join_paths(PATH_DIR_RACINE, "plusgins")
    PATH_DIR_STORAGE = join_paths(PATH_DIR_RACINE, "storage")
    allow_request = True
    path_template_404_not_found: str = ""
    infos_entreprise = {}
    
    DB_URL = os.environ.get("db_url") or "sqlite:///erp.db"
    DB_USER = os.environ.get("db_user") or "user"
    DB_PASSWORD = os.environ.get("db_password") or "root"
    DB_HOST = os.environ.get("db_host") or "localhost"
    DB_PORT = os.environ.get("db_port") or "5432"
    DB_PROVIDER = os.environ.get("db_provider") or "sqlite"
    DB_NAME = os.environ.get("db_name") or "melodi_database"

    # // postgresql://user:password@host:port/dbname

    def __init__(self):
        self.load_infos_entreprise()

    def load_infos_entreprise(self):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_entreprise.json")
        if not path_exist(path):
            return
        self.infos_entreprise = json.loads(read_file(path_file=path))

    def is_installed(self):
        return False 
        return path_exist(join_paths(self.PATH_DIR_CONFIG, "infos_entreprise.json"))

    def save_infos_entreprise(self, data):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_entreprise.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        self.infos_entreprise = data