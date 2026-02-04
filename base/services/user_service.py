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

        rep = UserRepository(self.module)
        user = await rep.get_user_by_username(username=username)
        
        if user :
            return True

        return False