from core.router import APIRouter
from base.services import HomePageService, WidgetService, InstallService

class BaseApiRoutes(APIRouter):
    def load(self):
        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)

        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))

        routes = [
            {"path": "/status", "methods": ["GET"], "handler": self.status},
            {"path": "/test_async", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async2", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async3", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async4", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async5", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async6", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async7", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async8", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async9", "methods": ["GET"], "handler": self.test_async},
            {"path": "/test_async10", "methods": ["GET"], "handler": self.test_async},
            {"path": "/login", "methods": ["GET"], "handler": self.login},
            {"path": "/register", "methods": ["GET"], "handler": self.register},
            {"path": "/logout", "methods": ["GET"], "handler": self.logout},
            {"path": "/users", "methods": ["GET"], "handler": self.admin_users},
            {"path": "/profile", "methods": ["GET"], "handler": self.profile},
            {"path": "/settings/home_page/<path:home_page>/on", "methods": ["GET"], "handler": self.settings_home_page_on},
            {"path": "/settings/home_page_clear", "methods": ["GET"], "handler": self.settings_home_page_clear},
            {"path": "/modules", "methods": ["GET"], "handler": self.admin_modules},
            {"path": "/modules/<path:mod>/off", "methods": ["GET"], "handler": self.off_module},
            {"path": "/modules/<path:mod>/on", "methods": ["GET"], "handler": self.on_module},
            {"path": "/<path:path>", "methods": ["GET"], "handler": self.not_found},
        ]

        self.add_many_routes(routes)

    def load_installer(self):
        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))
        installer_routes = [
            {"path": "/install", "methods": ["POST"], "handler": self.install},
            {"path": "/<path:path>", "methods": ["GET"], "handler": self.not_found},
        ]

        self.add_many_routes(installer_routes)

    def login(self):
        data = {"p":"login"}

        return self.render_json(data)
    
    def register(self):
        data = {"p":"register"}

        return self.render_json(data)
    
    def logout(self):
        data = {"p":"logout"}

        return self.render_json(data)

    def admin_users(self):
        data = {}

        return self.render_json(data)

    def profile(self):
        data = {"p":"profile"}

        return self.render_json(data)

    def settings_home_page_on(self, home_page):
        self.home_page_service.on(home_page)
        return self.render_json()
    
    def settings_home_page_clear(self):
        self.home_page_service.clear()
        return self.render_json()

    def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        data = {"modules":modules,"modules_len":modules_len}

        return self.render_json(data)
    
    def on_module(self,mod:str):
        self.app.module_manager.on_module(mod)

        data = {"module":mod}

        return self.render_json(data)

    def off_module(self, mod:str):
        self.app.module_manager.off_module(mod)
        
        data = {mod}

        return self.render_json(data)

    def status(self):
        return self.render_json(data={"status": "Admin API is working!"}, status_code=200)

    def install(self):
        req = self.get_request()

        data = req.get_json()

        install_service = InstallService(self)

        res = install_service.install(data)

        return self.render_json(data=res.data, status_code=res.status_code)
        
    def not_found(self,path):
        data = {"end_point_not_found":path}

        return self.render_json(data,status_code=404) 

    async def test_async(self):
        import asyncio
        import time

        start = time.time()
        print(f"Début de la requête à {start}")
        await asyncio.sleep(3)  # Pause asynchrone de 5 secondes
        end = time.time()
        print(f"Fin de la requête à {end}")
        return self.render_json({"start": start, "end": end, "duration": end - start})