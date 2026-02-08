from quart import Response
from core.module import ApplicationModule
from core.router import WebRouter, APIRouter
from core.utils import join_paths
import json
class Base(ApplicationModule):
    async def load(self):
        self.init_load()
        from base.routes import BaseRoutes, BaseApiRoutes

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app, module=self)

        await routes.load()
        api_routes.load()

        self.add_router(routes) 
        self.add_api_router(api_routes) 
        
        super().load()
    
    async def load_installer(self):
        self.init_load()

        from base.routes import BaseRoutes, BaseApiRoutes

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app, module=self)

        routes.load_installer()
        api_routes.load_installer()

        self.add_router(routes) 
        self.add_api_router(api_routes)

    def init_load(self):
        self.init_translation("fr")

        self.add_404_not_found()

        self.register_widget("base_widget", self.base_widget)

        self.register_middlewares({
            "auth_required": self.auth_required_middleware,
            "guest_only": self.guest_only_middleware,
            "api_auth_required": self.api_auth_required_middleware,
            "api_guest_only": self.api_guest_only_middleware,
            "deny_iframe": self.deny_iframe_middelware,
            "check_maintenance": self.check_maintenance_middleware
        })

    def add_404_not_found(self):
        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')
        
    def base_widget(self):
        return "<div><h3>Base Widget</h3><p>This is a sample widget from the Base module.</p></div>"
    
    def auth_required_middleware(self,router:WebRouter):
        user = router.get_session("user_payload")
        if not user:
            return router.redirect("/login") 
        payload = json.loads(user)
        router.set_scope_attr("user_payload", payload)

    def guest_only_middleware(self, router:WebRouter):
        user = router.get_session("user_payload")

        if user:
            return router.redirect("/")
            
    def api_auth_required_middleware(self,router:APIRouter):
        payload = None

        user = router.get_session("user_payload")

        if user:
            payload = json.loads(user)
            return None
        
        auth_header = router.get_header("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            jwt_token = auth_header.split(" ")[1]
            
            payload = router.jwt_decode(jwt_token)
            
            if payload:
                router.set_scope_attr("user_payload", payload)
                return None
            
        return router.render_json({"error": "Unauthorized"}, status_code=401)
        
    def api_guest_only_middleware(self, router:APIRouter):
        user = router.get_session("user_payload")

        if user:
            return router.render_json({"error": "Unauthorized"}, status_code=400)
        
        if router.get_header("Authorization"):
            return router.render_json({"error": "Unauthorized"}, status_code=400)
        
    def deny_iframe_middelware(self,response: Response) -> Response:
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    def check_maintenance_middleware(self):
        if not self.app.config.allow_request:
            return "Service Unavailable for maintenance", 503

module = Base(
    name="base", 
    router_name="base", 
)