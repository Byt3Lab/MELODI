from base.repositories.user_repository import UserRepository
from core.service import Service

class UserService(Service):
    async def list_users(self):
        data = await UserRepository(self.module).get_all_users()
        print(data)
        # return self.response(data=data)