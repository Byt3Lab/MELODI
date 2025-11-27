from base.repositories.user_repository import UserRepository
from core.service import Service

class UserService(Service):
    def list_users(self):
        data = UserRepository.get_all_users()
        return self.response(data=data)