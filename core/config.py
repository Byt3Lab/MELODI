import os
import pathlib
import json
from core.utils import read_file, join_paths
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
    modules_on = []
    widgets_on = []
    home_page_on = ""

    def __init__(self):
        self.load_infos_entreprise()
        self.load_modules_on()
        self.load_widgets_on()
        self.load_home_page_on()

    def load_infos_entreprise(self):
        self.infos_entreprise = json.loads(read_file(join_paths(self.PATH_DIR_CONFIG, "infos_entreprise.json")))

    def load_modules_on(self):
        self.modules_on = json.loads(read_file(join_paths(self.PATH_DIR_CONFIG, "modules_on.json")))

    def load_widgets_on(self):
        self.widgets_on = json.loads(read_file(join_paths(self.PATH_DIR_CONFIG, "widgets_on.json")))

    def load_home_page_on(self):
        self.home_page_on = read_file(join_paths(self.PATH_DIR_CONFIG, "home_page_on.txt")).strip()