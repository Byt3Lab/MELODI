from base.repository.user_repository import UserRepository
from core import Service

class UserService(Service):
    def list_users(self):
        data = UserRepository.get_all_users()
        return self.response(data=data)