from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from core import Application
    from core.module import Module
    from .request_context import RequestContext

class Router:
    def __init__(self, app:Application, name:str, module:Module|None = None):
        self.app = app
        self.module = module

        if(not hasattr(self, "template_folder")):
            self.template_folder = None

        import_name = name

        self.router = Blueprint(name,import_name, template_folder=self.template_folder)

    def add_route(self, path: str, methods=None):
        def decorator(f):
            return self.router.route(path, methods=methods)(f)
        return decorator

    def before_request(self):
        def decorator(f):
            return self.router.before_request(f)
        return decorator
        
    def get_request():
        from flask import request
        return request
    
    def make_response(self, content, status_code=200, headers=None):
        from flask import make_response
        response = make_response(content, status_code)
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        return response
    
    def set_request_context(self,callback=None):
        self.app.server.set_request_context(callback=callback)

    def get_request_context(self)-> RequestContext:
        return self.app.server.get_request_context()
    
    def get_router(self):
        return self.router

    def add_router(self, router:Router, url_prefix=''):
        self.router.register_blueprint(router.get_router(), url_prefix=url_prefix)

    def redirect(self, location: str, code: int = 302):
        from flask import redirect
        return redirect(location, code=code)
    
    def url_for(self, endpoint: str, **values):
        from flask import url_for
        return url_for(endpoint, **values)
    
    def abort(self, code: int, description: str = None):
        from flask import abort
        return abort(code, description=description)
    
    def get_current_request_path(self) -> str:
        from flask import request
        return request.path
    
    def get_current_request_method(self) -> str:
        from flask import request
        return request.method   
    
    def get_current_request_args(self) -> dict:
        from flask import request
        return request.args.to_dict()
    
    def get_current_request_form(self) -> dict:
        from flask import request
        return request.form.to_dict()
    
    def get_current_request_json(self) -> dict:
        from flask import request
        return request.get_json()   
    
    def translate(self, filename:list[str]|str, keys:list[str]|str, lang:str|None = None, ):
        return self.module.translate(filename, keys, lang)