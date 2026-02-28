from core.router import WebRouter, APIRouter
from core.utils import TimerManager, EventListener, MiddlewareManager, path_exist, read_file, run_sync
from core.component import HomePageManager, Registry
from core.module import ModuleManager
from core.adapters.quart_adapter import QuartAdapter
from core.db import DataBase
from core.config import Config
from core.file_management import Storage
from core.cache import Cache
from core.utils import HookManager
from core.utils import ActionManager
from core.websocket import WebSocketManager
from core.email import EmailManager

class Application:
    def __init__(self):
        self.server = QuartAdapter()
        self.init()

    def init(self):
        self.config = Config()
        self.db = DataBase(self)
        self.router = WebRouter(name="main", app=self, module=None)
        self.api_router = APIRouter(app=self, name="main_api")
        
        self.event_listener = EventListener()
        self.timer_manager = TimerManager()
        self.module_manager = ModuleManager(app=self)
        self.home_page_manager = HomePageManager(app=self)
        self.hook_manager = HookManager()
        self.action_manager = ActionManager()
        self.middleware_manager = MiddlewareManager()
        self.websocket_manager = WebSocketManager(app=self)
        self.email_manager = EmailManager(app=self)
        self.registry = Registry(app=self)

        # self.storage = Storage(app=self)
        self.app_is_installed = self.config.is_installed()
        self.user_sudo_exist = False
        self.cache = Cache()
        
        self.server.app.secret_key = self.config.secret_key
        
        @self.server.app.context_processor
        async def inject_registry():
            return dict(registry=self.registry)
        
        self.server.app.before_serving(self.build)
        self.server.app.before_serving(self.websocket_manager.start)

    async def restart(self):
        import sys
        import os
        import asyncio
        print("Restarting application...")
        
        if self.db:
            await self.db.close_engine()
            
        self.stop()
        
        if self.config.is_production():
            import signal
            print("Sending SIGHUP to parent process for restart...")
            os.kill(os.getppid(), signal.SIGHUP)
            return

        # Give a moment for resources to be released
        await asyncio.sleep(0.5)

        # Close all open file descriptors except stdin, stdout, stderr
        # to ensure the listening socket is not inherited by the new process.
        import resource
        max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if max_fd == resource.RLIM_INFINITY:
            max_fd = 1024
        
        for fd in range(3, max_fd):
            try:
                os.close(fd)
            except OSError:
                pass

        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def stop(self):
        self.server.clear()

    async def build(self):
        if not self.app_is_installed:
            await self.build_installer()
            return
        
        self.db.init_database()
        self.user_sudo_exist = await self.verify_user_sudo_exist()
        
        if not self.user_sudo_exist:
            self.app_is_installed = False
            await self.build_installer()
            return
        
        self.user_sudo_exist = True

        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        
        await base_module.load()
        
        await self.module_manager.load_modules()

        base_module._run()

        self.module_manager.run_modules()
        
        self.register_route_not_found()
        
        self.register_routers()

    async def build_installer(self):
        from base.module import module as base_module

        base_module.init(app=self, dirname="base")
        await base_module.load_installer()
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
        async def route_not_found(path):
            if not self.app_is_installed:
                return self.router.redirect("/")

            path_file_not_found = self.config.path_template_404_not_found
            if path_exist(path_file_not_found):
                return await self.router.render_template_string(read_file(self.config.path_template_404_not_found), path=path, hide_header=True, hide_footer=True), 404
            return await self.router.render_template_string(f"route : {path} not found 404"), 404

        async def api_route_not_found_path(path):
            return self.api_router.render_json({"error": "route not found", "path": path}), 404

        async def api_route_not_found_root():
            return self.api_router.render_json({"error": "route not found", "path": "/"}), 404

        self.router.add_route("/<path:path>")(route_not_found)
        self.api_router.add_route("/")(api_route_not_found_root)
        self.api_router.add_route("/<path:path>")(api_route_not_found_path)

    async def verify_user_sudo_exist(self):
        try:
            res = await self.db.execute("SELECT user_id from users WHERE is_sudo = true LIMIT 1;")
                
            if len(res) > 0:
                return True
        except Exception as e:
            print("Database connection error:", e)
            return False

        return False