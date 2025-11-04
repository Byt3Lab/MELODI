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
    DB_URL = os.environ.get("url_database") or "sqlite:///erp.db"
    infos_entreprise = {}

    def __init__(self):
        self.load_infos_entreprise()

    def load_infos_entreprise(self):
        path = join_paths(self.PATH_DIR_CONFIG, "infos_entreprise.json")
        if not path_exist(path):
            self.infos_entreprise = {}
            return
        self.infos_entreprise = json.loads(read_file(path_file=path))