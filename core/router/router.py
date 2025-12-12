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

    def add_route(self, path: str, methods=None, before_request:None|list[function]=None, after_request:None|list[function]=None):
        def decorator(f):
            def create_bp():
                bp = Blueprint(self.router.name+"_"+f.__name__+"_mw", self.router.import_name)
                return bp

            bp = None
            use_before = isinstance(before_request, list) and len(before_request) > 0
            use_after = isinstance(after_request, list) and len(after_request) > 0
            use_bp = use_before or use_after

            if not use_bp:
                return self.router.route(path, methods=methods)(f)
        
            bp = create_bp()

            if use_before:
                for bmw in before_request:
                    bp.before_request(bmw)

            if use_after:
                for amw in after_request:
                    bp.after_request(amw)
            
            bp.route(path, methods=methods)(f)
            return self.router.register_blueprint(bp)
        return decorator

    def add_many_routes(self, routes: list[dict], before_request:None|list[function]=None, after_request:None|list[function]=None):
        use_global_before = isinstance(before_request, list) and len(before_request) > 0
        use_global_after = isinstance(after_request, list) and len(after_request) > 0
        
        for route in routes:
            path = route.get("path")
            methods = route.get("methods", None)
            br = route.get("before_request", None)
            ar = route.get("after_request", None)
            handler = route.get("handler")

            if use_global_before:
                br = br if isinstance(br, list) else []
                br = before_request + br
            
            if use_global_after:
                ar = ar if isinstance(ar, list) else []
                ar = after_request + ar
               
            self.add_route(path, methods=methods, before_request=br, after_request=ar)(handler)
    
    def before_request(self):
        def decorator(f):
            return self.router.before_request(f)
        return decorator
    
    def after_request(self):
        def decorator(f):
            return self.router.after_request(f)
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