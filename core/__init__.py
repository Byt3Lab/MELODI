import pathlib
from core.utils import join_paths, path_exist, read_file

PATH_DIR_RACINE = pathlib.Path(__file__).parent.parent.resolve()
PATH_DIR_CONFIG = join_paths(PATH_DIR_RACINE, "config")
PATH_DIR_CORE = join_paths(PATH_DIR_RACINE, "core")
PATH_DIR_BASE_MODULE = join_paths(PATH_DIR_RACINE, "base")
PATH_DIR_MODULES = join_paths(PATH_DIR_RACINE, "modules")

def get_prefix_table():
    path = join_paths(PATH_DIR_CONFIG, "prefix_table.txt")
    if path_exist(path):
        return read_file(path_file=path).strip().lower()
    return ""

from .config import Config
from .application import Application