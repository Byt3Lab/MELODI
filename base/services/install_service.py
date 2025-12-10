from core.service import Service
from base.models.user_model import UserModel
from werkzeug.security import generate_password_hash

class InstallService(Service):
    def install(self, form_data):
        # Save company info
        company_info = {
            "name": form_data.get("company_name"),
            "address": form_data.get("company_address"),
            "email": form_data.get("company_email")
        }
        self.app.config.save_infos_entreprise(company_info)

        # Create admin user
        with self.app.db.get_session() as session:
            admin_user = UserModel(
                username=form_data.get("admin_username"),
                password=generate_password_hash(form_data.get("admin_password")),
                email=form_data.get("admin_email")
            )
            session.add(admin_user)
            session.commit()
        
        return True
