from __future__ import annotations

from typing import TYPE_CHECKING

from core.utils import join_paths, path_exist, write_file

if TYPE_CHECKING:
    from .application import Application

class HomePageManager:
    def __init__(self, app:Application):
        self.app = app
        self.home_page_on = self.app.config.home_page_on
        self.home_pages = {}

    def render_home_page(self):
        if self.home_page_on in self.home_pages:
            res = self.home_pages[self.home_page_on]

            if callable(res):
                res = res()

            if isinstance(res, str):
                return res
            else:
                return str(res)
            
        return None
    
    def register_home_page(self, name: str, home_page):
        self.home_pages[name] = home_page

    def list_home_pages(self):
        return list(self.home_pages.keys())
    
    def set_home_page_on(self, name):
        if name in self.home_pages:
            path_file = join_paths(self.app.config.PATH_DIR_CONFIG, "home_page_on.txt")

            write_file(path_file, name)
            self.home_page_on = name

    def clear(self):
        path_file = join_paths(self.app.config.PATH_DIR_CONFIG, "home_page_on.txt")
        write_file(path_file, "")
        self.home_page_on = ""