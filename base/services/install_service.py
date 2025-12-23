from core.service import Service
from base.repositories import UserRepository
from core.utils import join_paths, path_exist, write_file
class InstallService(Service):
    def install(self, data:None|dict):
        if data is None:
            return self.response(data={"message":"Contenu JSON manquant ou invalide"}, status_code=400)

        # 2. Extraire les variables du dictionnaire
        db_config:dict|None = data.get('db_config', None)

        if db_config is None:
            return self.response(data={"message":"Configuration de la base de données manquante"}, status_code=400)

         # Extraire les paramètres de configuration de la base de données   
        self.db_provider = db_config.get('provider')
        self.db_user = db_config.get('user')
        self.db_password = db_config.get('password')
        self.db_host = db_config.get('host')
        self.db_port = db_config.get('port')
        self.db_name = db_config.get('name')
        
        admin_user:dict|None = data.get('admin_user', None)
        
        if admin_user is None:
            return self.response(data={"message":"Configuration de l'utilisateur administrateur manquante"}, status_code=400)    
        
        self.admin_username = admin_user.get('username')
        self.admin_email = admin_user.get('email')
        self.admin_password = admin_user.get('password')
        self.admin_first_name = admin_user.get('first_name')
        self.admin_last_name = admin_user.get('last_name')

        if not self.validate_form_data(data):
            return self.response(data={"message":"Données de formulaire manquantes ou invalides"}, status_code=400)
        
        # Mettre à jour la config AVANT d'initialiser la base de données
        self.app.config.set_db_config({
            "db_provider": self.db_provider,
            "db_user": self.db_user,
            "db_password": self.db_password,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name
        })
        
        try:
            self._init_database()
        except Exception as e:
            return self.response(data={"message":"Erreur de connexion à la base de données: " + str(e)}, status_code=500)

        try:
            self.app.db.execute_sql("SELECT 1")
        except Exception as e:
            return self.response(data={"message":"Erreur de connexion à la base de données: " + str(e)}, status_code=500)
        
        try:
            self._create_all_base_tables()
        except Exception as e:
            return self.response(data={"message":"Erreur lors de la création des tables de base: " + str(e)}, status_code=500)  

        try:
            self._save_db_config()
        except Exception as e:
            return self.response(data={"message":"Erreur lors de la sauvegarde de la configuration de la base de données: " + str(e)}, status_code=500)
        
        try:
            user_exist = self.app.verify_user_sudo_exist()
            if user_exist:
                self._lock_installation()
                return self.response(data={"message":"Un utilisateur administrateur existe déjà. Installation annulée."}, status_code=400)  
        except Exception as e:
            return self.response(data={"message":"Erreur lors de la vérification de l'utilisateur administrateur: " + str(e)}, status_code=500)
        
        try:
            self._create_admin_user()
        except Exception as e:
            return self.response(data={"message":"Erreur lors de la création de l'utilisateur administrateur: " + str(e)}, status_code=500)
        
        try:
            self._lock_installation()
        except Exception as e:
            return self.response(data={"message":"Erreur lors du verrouillage de l'installation: " + str(e)}, status_code=500)
        
        return self.response(data={"message":"ok"}, status_code=200)

    def validate_form_data(self, data:dict)->bool:
        required_db_fields = ['provider', 'user', 'password', 'host', 'port', 'name']
        required_admin_fields = ['username', 'email', 'password', 'first_name', 'last_name']

        db_config = data.get('db_config', {})
        admin_user = data.get('admin_user', {})

        for field in required_db_fields:
            if field not in db_config or not db_config[field]:
                print("missing field:", field)
                return False

        for field in required_admin_fields:
            if field not in admin_user or not admin_user[field]:
                print("missing field:", field)
                return False

        if db_config.get("provider", "") != 'postgresql':
            return False
        
        if len(admin_user.get("password", "")) < 4:
            return False
        
        if "@" not in admin_user.get("email", ""):
            return False
        
        if len(admin_user.get("username", "")) < 4:
            return False
        
        return True

    def _save_db_config(self):
        mapping = {
            "db_provider": self.db_provider,
            "db_user": self.db_user,
            "db_password": self.db_password,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_name": self.db_name
        }

        db_conf_path = join_paths(self.app.config.PATH_DIR_CONFIG, "db_conf.json")

        if not path_exist(db_conf_path):
            write_file(db_conf_path, "")

        import json

        write_file(db_conf_path, json.dumps(mapping))
        self.app.config.set_db_config(mapping)

    def _init_database(self):
        self.app.db.close_engine()
        self.app.db.init_database()

    def _create_admin_user(self):
        from core.utils.password import hash_password

        user_repo = UserRepository(module=self.module)

        existing_admin = user_repo.user_sudo_exists()

        if existing_admin:
            raise Exception("Un utilisateur administrateur existe déjà.")

        from core.utils.generate import gen_id_by_uuid4

        user_id = gen_id_by_uuid4(prefix="user_")
        password = hash_password(self.admin_password)

        new_admin = {
            "user_id": user_id,
            "username": self.admin_username,
            "password": password,
            "email": self.admin_email,
            "is_sudo": True,
            "is_active": True,
            "first_name": self.admin_first_name,
            "last_name": self.admin_last_name
        }
        
        user_repo.create_user(new_admin)

    def _create_all_base_tables(self):
        from core.db import Model
        import base.models  # Importer pour enregistrer le modèle

        self.app.db.create_all(Model)

    def _lock_installation(self):
        install_lock_path = join_paths(self.app.config.PATH_DIR_CONFIG, "instal.lock")
    
        write_file(install_lock_path, "")
