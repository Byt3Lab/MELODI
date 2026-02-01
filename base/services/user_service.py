from base.repositories.user_repository import UserRepository
from core.service import Service

class UserService(Service):
    async def list_users(self):
        data = await UserRepository(self.module).get_all_users()
        print(data)
        # return self.response(data=data)

    async def authenticate (self, username: str, password: str):
        print("Authenticating user:", username)
        print("With password:", password)

        return True
        user = await UserRepository(self.module).get_user_by_username(username)

        if user and user.check_password(password):
            # Authentication successful
            return True
        return False