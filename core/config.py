import os
import pathlib
import json
from core.utils import create_dir_if_not_exist, path_exist, read_file, join_paths
# from doteenv import load_dotenv

# load_dotenv()

class Config:
    PATH_DIR_RACINE = pathlib.Path(__file__).parent.parent.resolve()
    PATH_DIR_CONFIG = join_paths(PATH_DIR_RACINE, "config")
    PATH_DIR_CORE = join_paths(PATH_DIR_RACINE, "core")
    PATH_DIR_BASE_MODULE = join_paths(PATH_DIR_RACINE, "base")
    PATH_DIR_MODULES = join_paths(PATH_DIR_RACINE, "modules")
    PATH_DIR_STORAGE = join_paths(PATH_DIR_RACINE, "storage")
    allow_request = True
    path_template_404_not_found: str = ""
    infos_org = {}


    # // postgresql://user:password@host:port/dbname

    def __init__(self):
        self.db_config = self.load_db_config()
        self.DB_PROVIDER = self.db_config.get("db_provider", "sqlite")
        self.DB_USER = self.db_config.get("db_user", "user")
        self.DB_PASSWORD = self.db_config.get("db_password", "password")
        self.DB_HOST = self.db_config.get("db_host", "localhost")
        self.DB_PORT = self.db_config.get("db_port", "5432")
        self.DB_NAME = self.db_config.get("db_name", "melodi_db")
        
        self.load_infos_org()

    def load_db_config(self):
        path = join_paths(self.PATH_DIR_CONFIG, "db_conf.json")
        if not path_exist(path):
            return {}
        return json.loads(read_file(path_file=path))
    
    def load_infos_org(self):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_org.json")
        if not path_exist(path):
            return
        self.infos_org = json.loads(read_file(path_file=path))

    def is_installed(self):
        return path_exist(join_paths(self.PATH_DIR_CONFIG, "instal.lock"))

    def save_infos_org(self, data):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_org.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        self.infos_org = data

    def get_db_url(self):
        if self.DB_PROVIDER == "sqlite":
            sqlite_path_dir = join_paths(self.PATH_DIR_RACINE, "sqlite")

            create_dir_if_not_exist(sqlite_path_dir)

            return f"sqlite:///sqlite/{self.DB_NAME}.db"
        return f"{self.DB_PROVIDER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"