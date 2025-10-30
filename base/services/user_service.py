from base.repository.user_repository import UserRepository
from core.base_service import BaseService

class UserService(BaseService):
    def list_users(self):
        data = UserRepository.get_all_users()
        return self.response(data=data)