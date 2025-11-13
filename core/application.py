from core.router import WebRouter, APIRouter
from core.utils import TimerManager, EventListener, Storage, create_dir_if_not_exist, join_paths, path_exist, read_file
from core.component import HomePageManager, MenuItemManager, WidgetManager
from core.module import ModuleManager
from core.adapters.flask_adapter import FlaskAdapter
from core.service import ServiceManager
from core.db import DataBase
from core.config import Config

class Application:
    def __init__(self):
        self.server = FlaskAdapter()
        self.init()

    def init(self):
        self.config = Config()
        self.event_listener = EventListener()
        self.timer_manager = TimerManager()
        self.db = DataBase(self)
        self.router = WebRouter(name="main", app=self)
        self.api_router = APIRouter(app=self, name="main_api")
        self.module_manager = ModuleManager(app=self)
        self.service_manager = ServiceManager(app=self)
        self.widget_manager = WidgetManager(app=self)
        self.menu_item_manager = MenuItemManager(app=self)
        self.home_page_manager = HomePageManager(app=self)
        self.storage = Storage(app=self)
        
        create_dir_if_not_exist(join_paths(self.config.PATH_DIR_STORAGE))

    def restart(self):
        # self.stop()
        # self.init()
        # self.run()
        pass

    def stop(self):
        self.server.clear()

    def build(self):
        self.db.init_database()

        self.register_request_maintenance()

        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        base_module.load()

        self.module_manager.load_modules()

        base_module._run()

        self.module_manager.run_modules()

        self.register_routers()

        self.register_route_not_found()

    def run(self, host="0.0.0.0", port=5001, debug=True):
        self.server.app.run(host=host, port=port, debug=debug)

    def get_server(self):
        return self.server.app

    def register_routers(self):
        self.server.add_router(self.api_router.get_router(), url_prefix="/api")
        self.server.add_router(self.router.get_router())

    def register_route_not_found(self):
        def route_not_found(path):
            from flask import render_template_string
            if path_exist(self.config.path_template_404_not_found):
                return render_template_string(read_file(self.config.path_template_404_not_found), path=path, hide_header=True, hide_footer=True), 404
            return render_template_string(f"route : {path} not found 404"), 404

        self.server.app.route("/<path:path>")(route_not_found)

    def register_request_maintenance(self):
        @self.server.app.before_request
        def before_request():
            if not self.config.allow_request:
                return "Service Unavailable for maintenance", 503