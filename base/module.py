from core.module import ApplicationModule
from core.utils import join_paths

class Base(ApplicationModule):
    def load(self):
        from base.routes import BaseRoutes, BaseApiRoutes

        self.init_translation("fr")

        PATH_DIR_BASE_MODULE = self.app.config.PATH_DIR_BASE_MODULE
        
        self.app.config.path_template_404_not_found = join_paths(PATH_DIR_BASE_MODULE, 'templates', 'base', '404.html')

        def xample_widget():
            return "<div><h3>Base Widget</h3><p>This is a sample widget from the Base module.</p></div>"
        
        self.register_widget("base")(xample_widget)

        routes = BaseRoutes(name="base", app=self.app, dirname_module=self.dirname)
        api_routes = BaseApiRoutes(name="base", app=self.app)

        routes.module = self
        api_routes.module = self
        
        routes.load()
        api_routes.load()

        self.add_router(routes) 
        self.add_api_router(api_routes) 
        
        super().load()
    
module = Base(
    name="base", 
    router_name="base", 
)