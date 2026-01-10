from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable
import uuid
from flask import Blueprint, make_response

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

    def add_route(self, path: str, methods: None|list[str] = None, before_request: None|list[Callable] = None, after_request: None|list[Callable] = None):
        def decorator(f: Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # 1. Exécution des middlewares 'before_request'
                if isinstance(before_request, list):
                    for callback in before_request:
                        response = callback(self_router=self, request=self.get_request())
                        # Si un before_request retourne une valeur, Flask interrompt 
                        # la suite et affiche cette valeur (comportement standard)
                        if response is not None:
                            return response

                # 2. Appel de la fonction de vue originale
                response = f(*args, **kwargs)
                
                # Conversion en objet réponse Flask pour le traitement 'after_request'
                response = make_response(response)

                # 3. Exécution des middlewares 'after_request'
                if isinstance(after_request, list):
                    for callback in after_request:
                        response = callback(response, self_router=self, request=self.get_request())
                
                return response

            # On enregistre le wrapper sur le routeur principal au lieu de f
            # On utilise l'ID de l'objet pour garantir l'unicité dans Flask
            wrapper.__name__ = f"{f.__name__}_{uuid.uuid4().hex}_{uuid.uuid4().hex}"
            self.router.route(path, methods=methods)(wrapper)
            
            # On retourne le wrapper pour conserver la chaîne de décoration
            return wrapper
        return decorator
    
    def _process_route(self, route: dict, path_prefix: str = "", inherited_before: None|list[function] = None, inherited_after: None|list[function] = None):
        """
        Recursively process a route and its children.
        
        Args:
            route: Route dictionary with path, methods, handler, and optional children
            path_prefix: Parent path to prepend to current route path
            inherited_before: Before request middleware inherited from parent routes
            inherited_after: After request middleware inherited from parent routes
        """
        # Extract route properties
        path = route.get("path", "")
        methods = route.get("methods", None)
        handler = route.get("handler")
        route_before = route.get("before_request", None)
        route_after = route.get("after_request", None)
        children = route.get("children", None)
        
        # Build full path by combining prefix with current path
        full_path = path_prefix + path
        
        # Merge inherited middleware with route-specific middleware
        # Inherited middleware runs first, then route-specific middleware
        combined_before = []
        if inherited_before and isinstance(inherited_before, list):
            combined_before.extend(inherited_before)
        if route_before and isinstance(route_before, list):
            combined_before.extend(route_before)
        
        combined_after = []
        if inherited_after and isinstance(inherited_after, list):
            combined_after.extend(inherited_after)
        if route_after and isinstance(route_after, list):
            combined_after.extend(route_after)
        
        # Convert empty lists to None for add_route compatibility
        final_before = combined_before if len(combined_before) > 0 else None
        final_after = combined_after if len(combined_after) > 0 else None
        
        # Register the route with combined middleware
        if handler:
            self.add_route(full_path, methods=methods, before_request=final_before, after_request=final_after)(handler)
        
        # Recursively process children if they exist
        if children and isinstance(children, list):
            for child_route in children:
                self._process_route(
                    child_route, 
                    path_prefix=full_path, 
                    inherited_before=combined_before if len(combined_before) > 0 else None,
                    inherited_after=combined_after if len(combined_after) > 0 else None
                )
    
    def add_many_routes(self, routes: list[dict], before_request:None|list[function]=None, after_request:None|list[function]=None):
        """
        Register multiple routes, supporting nested route structures.
        
        Args:
            routes: List of route dictionaries. Each route can have:
                - path: Route path (required)
                - methods: HTTP methods list (optional)
                - handler: Route handler function (required)
                - before_request: Middleware to run before handler (optional)
                - after_request: Middleware to run after handler (optional)
                - children: List of child routes (optional)
            before_request: Global before request middleware applied to all routes
            after_request: Global after request middleware applied to all routes
        """
        use_global_before = isinstance(before_request, list) and len(before_request) > 0
        use_global_after = isinstance(after_request, list) and len(after_request) > 0
        
        # Process each top-level route
        for route in routes:
            # Merge global middleware with route-specific middleware
            route_before = route.get("before_request", None)
            route_after = route.get("after_request", None)
            
            initial_before = []
            if use_global_before:
                initial_before.extend(before_request)
            if route_before and isinstance(route_before, list):
                initial_before.extend(route_before)
            
            initial_after = []
            if use_global_after:
                initial_after.extend(after_request)
            if route_after and isinstance(route_after, list):
                initial_after.extend(route_after)
            
            # Create a new route dict with merged middleware for processing
            route_copy = route.copy()
            route_copy["before_request"] = initial_before if len(initial_before) > 0 else None
            route_copy["after_request"] = initial_after if len(initial_after) > 0 else None
            
            # Process the route and its children recursively
            self._process_route(route_copy)
    
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
    
    def get_request(self):
        from flask import request
        return request
    
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
   
    def get_middlewares(self, module_name:str|None=None) -> dict[str, Any]|None:
        return self.module.get_middlewares(module_name)
    
    def get_middleware(self, middleware:str, module_name:str|None=None) -> Callable|None:
        return self.module.get_middleware(module_name=module_name, middleware=middleware)
    
    def translate(self, filename:list[str]|str, keys:list[str]|str, lang:str|None = None, ):
        return self.module.translate(filename, keys, lang)