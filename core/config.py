import os
import pathlib
import json
from core.utils import create_dir_if_not_exist, path_exist, read_file, join_paths, read_file, write_file
from core.utils.file_permissions import FilePermissions

# from doteenv import load_dotenv

# load_dotenv()

class Config:
    PATH_DIR_RACINE = pathlib.Path(__file__).parent.parent.resolve()
    PATH_DIR_CONFIG = join_paths(PATH_DIR_RACINE, "config")
    PATH_DIR_CORE = join_paths(PATH_DIR_RACINE, "core")
    PATH_DIR_BASE_MODULE = join_paths(PATH_DIR_RACINE, "base")
    PATH_DIR_MODULES = join_paths(PATH_DIR_RACINE, "modules")
    PATH_DIR_STORAGE = join_paths(PATH_DIR_RACINE, "storage")
    TYPE_DISTRIBUTION = "cloud"
    PREFIX_DB = "ml_"
    allow_request = True
    path_template_404_not_found: str = ""
    infos_org = {}
    secret_key = "default_secret_key"
    jwt_secret_key = "default_secret_key"

    def __init__(self):
        self.ensure_storage_directories()
        self.ensure_config_directories()
        self.ensure_modules_directories()

        self.db_config = self.load_db_config()
        self.DB_PROVIDER = self.db_config.get("db_provider") or "postgresql"
        self.DB_USER = self.db_config.get("db_user") or "postgres"
        self.DB_PASSWORD = self.db_config.get("db_password") or "password"
        self.DB_HOST = self.db_config.get("db_host") or "localhost"
        self.DB_PORT = self.db_config.get("db_port") or "5432"
        self.DB_NAME = self.db_config.get("db_name") or "melodi_db"
        
        self.load_infos_org()
        self.load_secret_key()
        self.load_jwt_secret_key()
        self.load_type_distribution()
        self.load_prefix_db()

    def load_prefix_db(self):
        path = join_paths(self.PATH_DIR_CONFIG, "prefix_db.txt")
        if path_exist(path):
            self.PREFIX_DB = read_file(path_file=path).strip()
        else:
            self.PREFIX_DB = "ml_"
            write_file(path_file=path, content=self.PREFIX_DB)

    def load_type_distribution(self):
        path = join_paths(self.PATH_DIR_CONFIG, "type_distribution.txt")
        if path_exist(path):
            self.TYPE_DISTRIBUTION = read_file(path_file=path).strip()
            if self.TYPE_DISTRIBUTION not in ["cloud", "local"]:
                self.TYPE_DISTRIBUTION = "cloud"
        else:
            self.TYPE_DISTRIBUTION = "cloud"
            write_file(path_file=path, content=self.TYPE_DISTRIBUTION)

    def load_secret_key(self):
        path = join_paths(self.PATH_DIR_CONFIG, "secret_key.txt")
        if path_exist(path):
            self.secret_key = read_file(path_file=path).strip()
        else:
            self.secret_key = os.urandom(24).hex()
            write_file(path_file=path, content=self.secret_key)

    def load_jwt_secret_key(self):
        path = join_paths(self.PATH_DIR_CONFIG, "jwt_secret_key.txt")
        if path_exist(path):
            self.jwt_secret_key = read_file(path_file=path).strip()
        else:
            self.jwt_secret_key = os.urandom(24).hex()
            write_file(path_file=path, content=self.jwt_secret_key)

    def set_db_config(self, config:dict):
        self.db_config = config
        self.DB_PROVIDER = config.get("db_provider") or self.DB_PROVIDER
        self.DB_USER = config.get("db_user") or self.DB_USER
        self.DB_PASSWORD = config.get("db_password") or self.DB_PASSWORD
        self.DB_HOST = config.get("db_host") or self.DB_HOST
        self.DB_PORT = config.get("db_port") or self.DB_PORT
        self.DB_NAME = config.get("db_name") or self.DB_NAME

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

    def is_production(self):
        return os.environ.get("MELODI_ENV", "dev") == "prod"

    def save_infos_org(self, data):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_org.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        self.infos_org = data

    def get_db_url(self):
        # Seul PostgreSQL est supporté
        provider = "postgresql"
        lib = "+asyncpg"

        return f"{provider}{lib}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def ensure_config_directories(self):
        create_dir_if_not_exist(self.PATH_DIR_CONFIG)
        
        fp = FilePermissions(self.PATH_DIR_CONFIG)
        fp.set_permissions({"read":True,"write":True,"execute":True})
        
        path_init_py = join_paths(self.PATH_DIR_CONFIG, "__init__.py")
        write_file(path_file=path_init_py, content="")

    def ensure_modules_directories(self):
        create_dir_if_not_exist(self.PATH_DIR_MODULES)

        fp = FilePermissions(self.PATH_DIR_MODULES)
        fp.set_permissions({"read":True,"write":True,"execute":True})

        path_init_py = join_paths(self.PATH_DIR_MODULES, "__init__.py")
        write_file(path_file=path_init_py, content="")

    def ensure_storage_directories(self):
        create_dir_if_not_exist(self.PATH_DIR_STORAGE)
        
        fp = FilePermissions(self.PATH_DIR_STORAGE)
        fp.set_permissions({"read":True,"write":True,"execute":True})

        path_init_py = join_paths(self.PATH_DIR_STORAGE, "__init__.py")
        write_file(path_file=path_init_py, content="")

        create_dir_if_not_exist(join_paths(self.PATH_DIR_STORAGE, "tmp_uploads"))
        create_dir_if_not_exist(join_paths(self.PATH_DIR_STORAGE, "uploads"))
        create_dir_if_not_exist(join_paths(self.PATH_DIR_STORAGE, "logs"))
        create_dir_if_not_exist(join_paths(self.PATH_DIR_STORAGE, "cache"))
        # os.chmod(join_paths(self.PATH_DIR_STORAGE, "tmp_uploads"), 0o777)
        # os.chmod(join_paths(self.PATH_DIR_STORAGE, "uploads"), 0o777)
        # os.chmod(join_paths(self.PATH_DIR_STORAGE, "logs"), 0o777)
        # os.chmod(join_paths(self.PATH_DIR_STORAGE, "cache"), 0o777)