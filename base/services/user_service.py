from base.repositories.user_repository import UserRepository
from core.service import Service

class UserService(Service):
    async def list_users(self):
        data = await UserRepository(self.module).get_all_users()
        print(data)
        # return self.response(data=data)

    async def authenticate (self, username: str, password: str):
        payload = {}

        rep = UserRepository(self.module)
        user = await rep.get_user_by_username_or_email(username=username)
        
        if user and await user.verify_password(password=password) :
            payload = {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "is_sudo": user.is_sudo
            }
            return payload
        print("Authentication failed for user:", username)
        return False