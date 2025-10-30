from __future__ import annotations
from typing import TYPE_CHECKING

from core.base_router import BaseRouter
from core.utils import path_exist, read_file

if TYPE_CHECKING:
    from core.application import Application

class Router(BaseRouter):
    def __init__(self, name:str, app:Application,  template_folder=None, dirname_module="", module=None):
        self.template_folder = template_folder
        self.dirname_module = dirname_module
        
        super().__init__(app=app, name=name, module=module)
    
    def render_template(self, template_name: str, **context):
        from flask import render_template
        
        if not self.dirname_module  == "":
            template_name = self.dirname_module +"/"+ template_name

        return render_template(template_name, **context)
    
    def render_template_(self, template_name: str, **context):
        from flask import render_template

        return render_template(template_name, **context)
    
    def render_template_string(self, template_string: str, **context):
        from flask import render_template_string
        return render_template_string(template_string, **context)
    
    def render_template_from_file(self, path_file: str, **context):
        template_string = ""
        if path_exist(path_file):
            template_string = read_file(path_file=path_file)
        return self.render_template_string(template_string, **context)