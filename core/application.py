import os

from core.home_page_manager import HomePageManager
from core.menu_item_manager import MenuItemManager
from core.module_manager import ModuleManager
from core.plugin_manager import PluginManager
from core.adapters.flask_adapter import FlaskAdapter
from core.service_manager import ServiceManager
from core.utils import TimerManager, EventListener, create_dir, create_dir_if_not_exist, join_paths, read_file
from core.database import DataBase
from core.config import Config
from core.router import Router
from core.api_router import APIRouter
from core.widget_manager import WidgetManager

class Application:
    def __init__(self):
        self.server = FlaskAdapter()
        self.init()

    def init(self):
        self.config = Config()
        self.event_listener = EventListener(app=self)
        self.timer_manager = TimerManager(app=self)
        self.db = DataBase(self)
        self.router = Router(name="main", app=self)
        self.api_router = APIRouter(app=self, name="main_api")
        self.module_manager = ModuleManager(app=self)
        self.plugin_manager = PluginManager(app=self)
        self.service_manager = ServiceManager(app=self)
        self.widget_manager = WidgetManager(app=self)
        self.menu_item_manager = MenuItemManager(app=self)
        self.home_page_manager = HomePageManager(app=self)
        
        create_dir_if_not_exist(join_paths(self.config.PATH_DIR_CONFIG))
        create_dir_if_not_exist(join_paths(self.config.PATH_DIR_STORAGE))

    def restart(self):
        # self.stop()
        # self.init()
        # self.run()
        pass

    def stop(self):
        self.server.clear()

    def run(self, host="0.0.0.0", port=5001, debug=True):
        self.db.init_database()

        self.register_request_maintenance()

        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        base_module.load()

        self.module_manager.load_modules()

        base_module.run()

        self.module_manager.run_modules()

        self.register_routers()

        self.register_route_not_found()

        self.server.app.run(host=host, port=port, debug=debug)
    

    def register_routers(self):
        self.server.add_router(self.api_router.get_router(), url_prefix="/api")
        self.server.add_router(self.router.get_router())

    def register_route_not_found(self):
        def route_not_found(path):
            from flask import render_template_string
            if os.path.exists(self.config.path_template_404_not_found):
                return render_template_string(read_file(self.config.path_template_404_not_found), path=path, hide_header=True, hide_footer=True), 404
            return render_template_string(f"route : {path} not found 404"), 404

        self.server.app.route("/<path:path>")(route_not_found)

    def register_request_maintenance(self):
        @self.server.app.before_request
        def before_request():
            if not self.config.allow_request:
                return "Service Unavailable for maintenance", 503