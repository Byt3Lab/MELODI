from flask import Response
from core.router import APIRouter
from base.services import HomePageService, WidgetService

class BaseApiRoutes(APIRouter):
    def load(self):
        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)

        self.after_request()(self.deny_iframe)

        if not self.app.app_is_installed:
            self.add_route("/install", methods=["POST"])(self.install)
            self.add_route('/<path:path>', methods=['GET'])(self.not_found)
            return

        self.add_route("/status", methods=["GET"])(self.status)
        self.add_route("/login", methods=["GET"])(self.login)
        self.add_route("/register", methods=["GET"])(self.register)
        self.add_route("/logout", methods=["GET"])(self.logout)
        self.add_route('/users', methods=['GET'])(self.admin_users)
        self.add_route('/profile', methods=['GET'])(self.profile)
        self.add_route('/settings/home_page/<path:home_page>/on', methods=['GET'])(self.settings_home_page_on)
        self.add_route('/settings/home_page_clear', methods=['GET'])(self.settings_home_page_clear)
        self.add_route('/modules', methods=['GET'])(self.admin_modules)
        self.add_route('/modules/<path:mod>/off', methods=['GET'])(self.off_module)
        self.add_route('/modules/<path:mod>/on', methods=['GET'])(self.on_module)
        self.add_route('/<path:path>', methods=['GET'])(self.not_found)


    def deny_iframe(self,response: Response) -> Response:
        response.headers['X-Frame-Options'] = 'DENY'
        return response
     
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

        if data is None:
            return self.render_json(data={"message":"Contenu JSON manquant ou invalide"}, status_code=400)

        # 2. Extraire les variables du dictionnaire
        db_provider = data.get('db_provider')
        db_user = data.get('db_user')
        db_password = data.get('db_password')
        db_host = data.get('db_host')
        db_port = data.get('db_port')
        db_name = data.get('db_name')
        
        return self.render_json(data={"message":"ok"}, status_code=200)

    def not_found(self,path):
        data = {"end_point_not_found":path}

        return self.render_json(data,status_code=404) 