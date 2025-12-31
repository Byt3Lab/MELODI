from core.router import WebRouter, RequestContext
from base.services import HomePageService, WidgetService, InstallService
from flask import Response, request

class BaseRoutes(WebRouter):
    def load (self):
        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)
        self.install_service = InstallService(module=self.module)

        self.before_request()(self.check_maintenance)
        self.after_request()(self.deny_iframe)
        
        self.add_route("/", methods=["GET"])(self.home)

        self.add_many_routes([
            {"path": "/login", "methods": ["GET"], "handler": self.login},
            {"path": "/register", "methods": ["GET"], "handler": self.register},
        ], before_request=[self.user_is_not_auth()])

        self.add_many_routes([
            {"path": "/logout", "methods": ["GET"], "handler": self.logout},
            {"path": "/admin", "methods": ["GET"], "handler": self.admin_dashboard,
                "children": [
                    {"path": "/users", "methods": ["GET"], "handler": self.admin_users},
                    {"path": "/profile", "methods": ["GET"], "handler": self.profile},
                    {"path": "/settings", "methods": ["GET"], "handler": self.admin_settings,
                        "children": [
                            {"path": "/widgets", "methods": ["GET"], "handler": self.settings_widgets},
                            {"path": "/home_page", "methods": ["GET"], "handler": self.settings_home_page},
                            {"path": "/home_page/<path:home_page>/on", "methods": ["GET"], "handler": self.settings_home_page_on},
                            {"path": "/home_page_clear", "methods": ["GET"], "handler": self.settings_home_page_clear}
                        ]
                    },
                    {"path": "/modules", "methods": ["GET"], "handler": self.admin_modules,
                        "children": [
                            {"path": "/<path:mod>/off", "methods": ["GET"], "handler": self.off_module},
                            {"path": "/<path:mod>/on", "methods": ["GET"], "handler": self.on_module}
                        ]
                    },
                    {"path": "/logs", "methods": ["GET"], "handler": self.logs}
                ]
            }
        ], before_request=[self.user_is_auth()])

    def load_installer(self):
        self.before_request()(self.check_installation)
        self.after_request()(self.deny_iframe)
        self.add_route("/", methods=["GET"])(self.home_welcome)
        self.add_route("/install", methods=["GET"])(self.install)

    def check_installation(self):
        request = self.get_request()

        if request.path == "/":
            return None
        
        if request.path == "/install":
            return None
        
        return self.redirect("/install")
        
    def check_maintenance(self):
        if not self.app.config.allow_request:
            return "Service Unavailable for maintenance", 503

    def user_is_auth(self):
        return self.get_middleware("user_is_auth")

    def user_is_not_auth(self):
        return self.get_middleware("user_is_not_auth")
          
    def br(self):
        def sr(ctx:RequestContext):
            ctx.data["hello"] = "hello wordl"
            return ctx
        
        self.set_request_context(callback=sr)

    def br2(self):
        ctx = self.get_request_context()
        print(ctx.data["hello"])

    def deny_iframe(self,response: Response) -> Response:
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def login(self):
        return self.render_template("login.html")
    
    def register(self):
        return self.render_template("register.html")
    
    def logout(self):
        return self.render_template("logout.html")
    
    def logs(self):
        return self.render_template("admin_logs.html")

    def admin_dashboard(self):
        widgets=self.app.widget_manager.list_widgets()

        for key,w in widgets.items():
            for key,i in w.items():
                wid = i["widget"]

                if callable(wid):
                    i["widget"] = wid()
                    continue
                if isinstance(wid, str):
                    i["widget"] = wid


        return self.render_template("admin_dashboard.html",widgets=widgets)

    def admin_users(self):
        return self.render_template("admin_users.html")

    def profile(self):
        return self.render_template("profile.html")

    def settings_widgets(self):
        widgets = self.app.widget_manager.list_widgets()
        return self.render_template("admin_widgets.html", widgets=widgets)

    def settings_home_page(self):
            home_page_on = self.app.home_page_manager.home_page_on
            home_pages = self.app.home_page_manager.list_home_pages()
            home_pages_len = len(home_pages)
            return self.render_template("admin_home_page.html", home_pages=home_pages, home_pages_len=home_pages_len, home_page_on=home_page_on)

    def settings_home_page_on(self, home_page):
        self.home_page_service.on(home_page)
        return self.redirect("/admin/settings/home_page")
    
    def settings_home_page_clear(self):
        self.home_page_service.clear()
        return self.redirect("/admin/settings/home_page")

    def admin_modules(self):
        modules = self.app.module_manager.list_modules()
        modules_len= len(modules)
        return self.render_template("admin_modules.html",modules=modules, modules_len=modules_len)

    def on_module(self,mod:str):
        self.app.module_manager.on_module(mod)
        self.app.restart()
        return self.redirect("/admin/modules")

    def off_module(self, mod:str):
        self.app.module_manager.off_module(mod)
        self.app.restart()
        return self.redirect("/admin/modules")
    
    def admin_settings(self):
        return self.render_template("admin_settings.html")

    def home(self): 
        home_page = self.app.home_page_manager.render_home_page() 
        
        if home_page: 
            return home_page

        return self.render_template("home.html")

    def home_welcome(self):
        return self.render_template("home_welcome.html")
    
    def install(self):
        return self.render_template("install/install.html")