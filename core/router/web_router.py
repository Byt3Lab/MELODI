from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from flask import Response

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
    
    def get_session(self, key:str|None=None):
        from flask import session

        try:
            if isinstance(key, str):
                return session.get(key)
            return session
        except:
            return session
        
    def set_session(self, key:str, value):
        from flask import session

        try:
            session[key] = value
            return True
        except:
            return False
    
    def get_cookie(self, key:str):
        from flask import request

        return request.cookies.get(key)

    def set_cookie(
            self, response: Response, key:str, value:str, 
            max_age: timedelta | int | None = None,
            expires: str | datetime | int | float | None = None,
            path: str | None = "/",
            domain: str | None = None,
            secure: bool = False,
            httponly: bool = False,
            samesite: str | None = None,
            partitioned: bool = False,
        ):
        
        try:
            return response.set_cookie(key=key, value=value, max_age=max_age, expires=expires, path=path, domain=domain, secure=secure, httponly=httponly, samesite=samesite, partitioned=partitioned)
        except:
            # log
            return response
    
    def delete_cookie(self, response: Response, key:str):
        try:
            return response.delete_cookie(key=key)
        except:
            # log
            return response
        
class BasicWebRouter:
    def __init__(self, router:WebRouter):
        self.router = router
        self.routes = []

    def load(self):
        pass

    def get_routes(self):
        return self.routes