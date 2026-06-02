from core.router import WebRouter

class BaseRoutes(WebRouter):
    async def load (self):
        from base.services import HomePageService, WidgetService, InstallService

        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)
        self.install_service = InstallService(module=self.module)
        
        from ..controllers.base_controller import BaseController

        base_controller = BaseController(router=self)
        base_controller.load()

        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))
        
        self.add_route("/", methods=["GET"])(base_controller.home)
        self.add_route("/static_base_icons", methods=["GET"])(base_controller.static_base_icons)
        self.add_route("/static_module_img", methods=["GET"])(base_controller.static_module_img)
        self.add_route("/static_org_img", methods=["GET"])(base_controller.static_org_img)

        self.add_many_routes([
            {"path": "/login", "methods": ["GET", 'post'], "handler": base_controller.login},
            {"path": "/register", "methods": ["GET"], "handler": base_controller.register},
        ], before_request=[self.get_middleware("guest_only")])

        self.add_many_routes([
            {"path": "/logout", "methods": ["GET"], "handler": base_controller.logout},
            {"path": "/admin", "methods": ["GET"], "handler": base_controller.admin_dashboard,
                "children": [
                    {"path": "/base/users", "methods": ["GET"], "handler": base_controller.admin_users},
                    {"path": "/base/profile", "methods": ["GET"], "handler": base_controller.profile},
                    {"path": "/base/settings", "methods": ["GET"], "handler": base_controller.admin_settings,
                        "children": [
                            {"path": "/widgets", "methods": ["GET"], "handler": base_controller.settings_widgets},
                            {"path": "/home_page", "methods": ["GET"], "handler": base_controller.settings_home_page},
                            {"path": "/home_page/<path:home_page>/on", "methods": ["GET"], "handler": base_controller.settings_home_page_on},
                            {"path": "/home_page_clear", "methods": ["GET"], "handler": base_controller.settings_home_page_clear}
                        ]
                    },
                    {"path": "/base/modules", "methods": ["GET"], "handler": base_controller.admin_modules,
                        "children": [
                            {"path": "/<path:mod>/off", "methods": ["GET"], "handler": base_controller.off_module},
                            {"path": "/<path:mod>/on", "methods": ["GET"], "handler": base_controller.on_module},
                            {"path": "/<path:mod>/delete", "methods": ["GET"], "handler": base_controller.delete_module}
                        ]
                    },
                    {"path": "/base/add_module", "methods": ["GET"], "handler": base_controller.admin_add_module},
                    {"path": "/base/notifications", "methods": ["GET"], "handler": base_controller.notifications},
                    {"path": "/base/logs", "methods": ["GET"], "handler": base_controller.logs},
                    {"path": "/base/update", "methods": ["GET"], "handler": base_controller.update,
                         "children": [
                            {"path": "/module/<path:mod>", "methods": ["GET"], "handler": base_controller.update_module}
                         ]
                    }
                ]
            }
        ], before_request=[self.get_middleware("auth_required")]) # self.get_middleware("admin_only")])

    def load_installer(self):
        from ..controllers.base_controller import BaseController

        base_controller = BaseController(router=self)
        base_controller.load()

        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))
        self.add_route("/", methods=["GET"])(base_controller.home_welcome)
        self.add_route("/install", methods=["GET"])(base_controller.install)

    def check_installation(self):
        request = self.get_request()

        if request.path == "/":
            return None
        
        if request.path == "/install":
            return None
        
        return self.redirect("/install")