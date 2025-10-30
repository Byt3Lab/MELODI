from core import Module
from core.utils import join_paths

title="module d'administration de l'applicaion"
description = "Module d'administration de l'application"

class Base(Module):
    def load(self):
        from .routes import AdminRoutes, AdminApiRoutes

        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')

        def xample_widget():
            return "<div><h3>Base Widget</h3><p>This is a sample widget from the Base module.</p></div>"
        
        self.app.widget_manager.register_widget("base", xample_widget)

        routes = AdminRoutes(name="base", app=self.app, dirname_module=self.dirname)
        api_routes = AdminApiRoutes(name="base", app=self.app)

        routes.load()
        api_routes.load()

        self.add_router(routes) 
        self.add_api_router(api_routes) 
        
        super().load()
    
module = Base(
    name="base", 
    router_name="base", 
    version="0.1", 
)