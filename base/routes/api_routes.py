from core.router import APIRouter
from base.services import HomePageService, WidgetService, InstallService

class BaseApiRoutes(APIRouter):
    def load(self):
        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)

        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))

        from base.routes.base_api_controller import BaseAPIController

        base_api_controller = BaseAPIController(router=self)
        base_api_controller.load()

        self.add_route(path="/login", methods=["POST"], before_request=[self.get_middleware("api_guest_only")])(base_api_controller.login)

        routes = [
            {"path": "/status", "methods": ["GET"], "handler": base_api_controller.status},
            {"path": "/test_async", "methods": ["GET"], "handler": base_api_controller.test_async},
            {"path": "/settings/home_page/<path:home_page>/on", "methods": ["GET"], "handler": base_api_controller.settings_home_page_on},
            {"path": "/settings/home_page_clear", "methods": ["GET"], "handler": base_api_controller.settings_home_page_clear},
            {"path": "/modules", "methods": ["GET"], "handler": base_api_controller.admin_modules,
                "children": [
                    {"path": "/install/upload", "methods": ["POST"], "handler": base_api_controller.upload_module_to_install},
                    {"path": "/update/upload", "methods": ["POST"], "handler": base_api_controller.upload_module_to_update},
                    {"path": "/<path:mod>/off", "methods": ["GET"], "handler": base_api_controller.off_module},
                    {"path": "/<path:mod>/on", "methods": ["GET"], "handler": base_api_controller.on_module},
                    {"path": "/<path:mod>/remove", "methods": ["GET"], "handler": base_api_controller.remove_module}
                ]
            },
            {"path": "/core/upload", "methods": ["POST"], "handler": base_api_controller.upload_core_to_update},
            {"path": "/restart_server", "methods": ["GET"], "handler": base_api_controller.restart_server},
            {"path": "/<path:path>", "methods": ["GET"], "handler": base_api_controller.not_found},
        ]

        self.add_many_routes(routes, before_request=[self.get_middleware("api_auth_required")])

    def load_installer(self):
        self.before_request()(self.get_middleware("check_maintenance"))
        self.after_request()(self.get_middleware("deny_iframe"))
        installer_routes = [
            {"path": "/install", "methods": ["POST"], "handler": self.install},
            {"path": "/<path:path>", "methods": ["GET"], "handler": self.not_found},
        ]

        self.add_many_routes(installer_routes)
        