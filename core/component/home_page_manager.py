from __future__ import annotations

from typing import TYPE_CHECKING

from core.utils import join_paths, path_exist, read_file, write_file

if TYPE_CHECKING:
    from core import Application

class HomePageManager:
    def __init__(self, app:Application):
        self.app = app
        self.home_page_on = ""
        self.home_pages:dict = {}
        self.load_home_page_on()

    def load_home_page_on(self):
        path = join_paths(self.app.config.PATH_DIR_CONFIG, "home_page_on.txt")
        
        if not path_exist(path):
            return
        self.home_page_on = read_file(path_file=path).strip()
        
    def render_home_page(self):
        try:
            res = self.home_pages[self.home_page_on]["home_page"]

            if callable(res):
                res = res()

            if isinstance(res, str):
                return res
            else:
                return str(res)
        except:
            return None
    
    def register_home_page(self, name_module:str, infos, home_page):
        self.home_pages[name_module] = {home_page, infos}

    def list(self):
        return self.home_pages
    
    def on(self, name_module):
        try:
            path_file = join_paths(self.app.config.PATH_DIR_CONFIG, "home_page_on.txt")

            write_file(path_file, name_module)
            self.home_page_on = name_module
        except:
            return False

    def clear(self):
        path_file = join_paths(self.app.config.PATH_DIR_CONFIG, "home_page_on.txt")
        write_file(path_file, "")
        self.home_page_on = ""