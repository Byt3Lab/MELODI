from base.repositories.user_repository import UserRepository
from core.service import Service

class UserService(Service):
    def list_users(self):
        data = UserRepository(self.module).get_all_users()
        print(data)
        # return self.response(data=data)