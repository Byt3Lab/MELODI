from core.router import WebRouter, APIRouter
from core.utils import TimerManager, EventListener, MiddlewareManager, path_exist, read_file
from core.component import HomePageManager, MenuItemManager, WidgetManager
from core.module import ModuleManager
from core.adapters.flask_adapter import FlaskAdapter
from core.service import ServiceManager
from core.db import DataBase
from core.config import Config
from core.file_management import Storage
from core.cache import Cache
class Application:
    def __init__(self):
        self.server = FlaskAdapter()
        self.init()

    def init(self):
        self.config = Config()
        self.event_listener = EventListener()
        self.timer_manager = TimerManager()
        self.db = DataBase(self)
        self.router = WebRouter(name="main", app=self, module=None)
        self.api_router = APIRouter(app=self, name="main_api")
        self.module_manager = ModuleManager(app=self)
        self.service_manager = ServiceManager(app=self)
        self.widget_manager = WidgetManager(app=self)
        self.menu_item_manager = MenuItemManager(app=self)
        self.home_page_manager = HomePageManager(app=self)
        self.middleware_manager = MiddlewareManager()
        # self.storage = Storage(app=self)
        self.app_is_installed = self.config.is_installed()
        self.user_sudo_exist = False
        self.cache = Cache()
        
    def restart(self):
        import sys
        import os
        print("Restarting application...")
        
        if self.db:
            self.db.close_engine()
            
        self.stop()
        
        if self.config.is_production():
            import signal
            print("Sending SIGHUP to parent process for restart...")
            os.kill(os.getppid(), signal.SIGHUP)
            return

        python = sys.executable
        os.execl(python, python, *sys.argv)

    def stop(self):
        self.server.clear()

    def build(self):
        if not self.app_is_installed:
            self.build_installer()
            return
        
        self.db.init_database()
        self.user_sudo_exist = self.verify_user_sudo_exist()
        
        if not self.user_sudo_exist:
            self.app_is_installed = False
            self.build_installer()
            return
        
        self.user_sudo_exist = True

        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        base_module.load()
        
        self.module_manager.load_modules()

        base_module._run()

        self.module_manager.run_modules()
        
        self.register_route_not_found()
        
        self.register_routers()

    def build_installer(self):
        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        base_module.load_installer()
        base_module._run()

        self.register_route_not_found()
        self.register_routers()

    def run(self, host="0.0.0.0", port=5000, debug=True):
        self.server.app.run(host=host, port=port, debug=debug)

    def get_server(self):
        return self.server.app

    def register_routers(self):
        self.server.add_router(self.router.get_router())
        self.server.add_router(self.api_router.get_router(), url_prefix="/api")

    def register_route_not_found(self):
        def route_not_found(path):
            if not self.app_is_installed:
                return self.router.redirect("/")

            path_file_not_found = self.config.path_template_404_not_found
            if path_exist(path_file_not_found):
                return self.router.render_template_string(read_file(self.config.path_template_404_not_found), path=path, hide_header=True, hide_footer=True), 404
            return self.router.render_template_string(f"route : {path} not found 404"), 404

        def api_route_not_found(path):
            return self.api_router.render_json({"error": "route not found", "path": path}), 404

        def api_route_not_found():
            return self.api_router.render_json({"error": "route not found", "path": "/  "}), 404

        self.router.add_route("/<path:path>")(route_not_found)
        self.api_router.add_route("/")(api_route_not_found)
        self.api_router.add_route("/<path:path>")(api_route_not_found)

    def verify_user_sudo_exist(self):
        try:
            res = self.db.execute_sql("SELECT user_id from users WHERE is_sudo = true LIMIT 1;")

            if res.first():
                return True
        except Exception as e:
            print("Database connection error:", e)
            return False

        return False