# adapters/flask_adapter.py
from flask import Flask, Blueprint, send_from_directory, Request, g
from .web_server_interface import WebServerInterface
from ..request_context import RequestContext

class FlaskAdapter(WebServerInterface):
    def __init__(self):
        self.app = Flask(__name__,template_folder='.')

    def add_route(self, path: str, handler, methods=None):
        self.app.route(path, methods=methods or ["GET"])(handler)

    def run(self, host="127.0.0.1", port=5000):
        self.app.run(host=host, port=port)

    def serve_static_directory(self, path_directory: str, prefix_path: str):
        def handler(filename):
            return send_from_directory(path_directory, filename)
        bp = Blueprint(f'static_{prefix_path}', __name__)
        bp.route(f'/static{prefix_path}/<path:filename>')(handler)
        self.app.register_blueprint(bp)

    def serve_template(self, template_name: str, **context):
        from flask import render_template
        return render_template(template_name, **context)
    

    def add_middleware(self, middleware):
        self.app.before_request(middleware)        

    def add_router(self, router:Blueprint, url_prefix:str=""):
        self.app.register_blueprint(router, url_prefix=url_prefix)

    def add_error_handler(self, error_code, handler):
        pass

    def set_request_context(self, callback=None):
        ctx = self.get_request_context()    
            
        if not isinstance(ctx, Request) :
            g.ctx = RequestContext()
            ctx = g.ctx

        if callable(callback):
            g.ctx = callback(ctx)
    
    def get_request_context(self)-> RequestContext | None : 
        if hasattr(g, "ctx"):  
            return g.ctx
        return RequestContext()