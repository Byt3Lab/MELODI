from flask import Response
from core.router import APIRouter
from base.services import HomePageService, WidgetService
import os
from pathlib import Path

from core.utils import join_paths, path_exist, write_file
class BaseApiRoutes(APIRouter):
    def load(self):
        self.home_page_service = HomePageService(module=self.module)
        self.widget_service = WidgetService(module=self.module)

        self.after_request()(self.deny_iframe)
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

    def load_installer(self):
        self.after_request()(self.deny_iframe)
        self.add_route("/install", methods=["POST"])(self.install)
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
        db_config:dict|None = data.get('db_config', None)

        if db_config is None:
            return self.render_json(data={"message":"Configuration de la base de données manquante"}, status_code=400)

         # Extraire les paramètres de configuration de la base de données   
        db_provider = db_config.get('db_provider')
        db_user = db_config.get('db_user')
        db_password = db_config.get('db_password')
        db_host = db_config.get('db_host')
        db_port = db_config.get('db_port')
        db_name = db_config.get('db_name')
        
        user_admin:dict|None = data.get('user_admin', None)
        
        if user_admin is None:
            return self.render_json(data={"message":"Configuration de l'utilisateur administrateur manquante"}, status_code=400)    
        
        admin_username = user_admin.get('admin_username')
        admin_email = user_admin.get('admin_email')
        admin_password = user_admin.get('admin_password')
        admin_first_name = user_admin.get('first_name')
        admin_last_name = user_admin.get('last_name')

        def save_db_config():
            mapping = {
                "db_provider": db_provider,
                "db_user": db_user,
                "db_password": db_password,
                "db_host": db_host,
                "db_port": db_port,
                "db_name": db_name
            }

            db_conf_path = join_paths(self.app.config.PATH_DIR_CONFIG, "db_conf.json")

            if not path_exist(db_conf_path):
                write_file(db_conf_path, "")

            import json

            write_file(db_conf_path, json.dumps(mapping))
            self.app.config.set_db_config(mapping)

        def create_admin_user():
            from core.utils.password import hash_password
            from base.models.user_model import UserModel as User

            try:
                self.app.db.close_engine()
                self.app.db.init_database()

                User.metadata.create_all(self.app.db.engine)

                session = self.app.db.get_session()

                existing_admin = session.query(User).filter_by(is_sudo=True).first()

                if existing_admin:
                    return  # L'utilisateur administrateur existe déjà

                new_admin = User(
                    username=admin_username,
                    email=admin_email,
                    password=hash_password(admin_password),
                    is_active=True,
                    is_sudo=True,
                    first_name=admin_first_name,
                    last_name=admin_last_name
                )
                
                with session.begin():
                    session.add(new_admin)

            except Exception as e:
                return self.render_json(data={"message":"Erreur de connexion à la base de données: " + str(e)}, status_code=500)

        def lock_installation():
            install_lock_path = join_paths(self.app.config.PATH_DIR_CONFIG, "instal.lock")
        
            write_file(install_lock_path, "")

        save_db_config()
        create_admin_user()
        lock_installation()

        return self.render_json(data={"message":"ok"}, status_code=200)

    def not_found(self,path):
        data = {"end_point_not_found":path}

        return self.render_json(data,status_code=404) 