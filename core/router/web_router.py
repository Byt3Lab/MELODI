from __future__ import annotations
from typing import TYPE_CHECKING

from .router import Router
from core.utils import path_exist, read_file

if TYPE_CHECKING:
    from core import Application
    from core.module import Module

class WebRouter(Router):
    def __init__(self, name:str, app:Application, module:Module|None, template_folder=None):
        self.template_folder = template_folder
        self.dirname_module = ""

        from core.module import Module

        if isinstance(module, Module):
            self.dirname_module = module.dirname
        
        super().__init__(app=app, name=name, module=module)
    
    async def render_template(self, template_name: str, **context):
        from quart import render_template
        
        if not self.dirname_module  == "":
            template_name = self.dirname_module +"/"+ template_name

        return await render_template(template_name, **context)
    
    async def render_template_(self, template_name: str, **context):
        from quart import render_template

        return await render_template(template_name, **context)
    
    async def render_template_string(self, template_string: str, **context):
        from quart import render_template_string
        return await render_template_string(template_string, **context)
    
    async def render_template_from_file(self, path_file: str, **context):
        template_string = ""
        if path_exist(path_file):
            template_string = read_file(path_file=path_file)
        return await self.render_template_string(template_string, **context)