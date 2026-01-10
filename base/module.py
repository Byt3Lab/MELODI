from flask import Response
from core.module import ApplicationModule
from core.utils import join_paths

class Base(ApplicationModule):
    def load(self):
        from base.routes import BaseRoutes, BaseApiRoutes

        self.init_translation("fr")

        self.add_404_not_found()

        self.register_widget("base_widget", self.base_widget)

        self.register_middlewares({
            "user_is_auth": self.user_is_auth_middleware,
            "user_is_not_auth": self.user_is_not_auth_middleware,
            "deny_iframe": self.deny_iframe_middelware,
            "check_maintenance": self.check_maintenance_middleware
        })

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app)

        routes.module = self
        api_routes.module = self

        routes.load()
        api_routes.load()

        self.add_router(routes) 
        self.add_api_router(api_routes) 
        
        super().load()
    
    def load_installer(self):
        from base.routes import BaseRoutes, BaseApiRoutes

        self.init_translation("fr")

        self.add_404_not_found()

        routes = BaseRoutes(name="base", app=self.app, module=self)
        api_routes = BaseApiRoutes(name="base", app=self.app)

        routes.module = self
        api_routes.module = self

        routes.load_installer()
        api_routes.load_installer()

        self.add_router(routes) 
        self.add_api_router(api_routes)

    def add_404_not_found(self):
        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')
        
    def base_widget(self):
        return "<div><h3>Base Widget</h3><p>This is a sample widget from the Base module.</p></div>"
    
    def user_is_auth_middleware(self,self_router, request=None):
        this = self_router

        user = this.get_session("user_id")

        if not user:
            return this.redirect("/login")  

    def user_is_not_auth_middleware(self, self_router, request=None):
        this = self_router

        user = this.get_session("user_id")

        if user:
            return this.redirect("/admin")
        
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