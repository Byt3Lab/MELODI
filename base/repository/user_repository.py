from core.base_repository import BaseRepository
from base.models.user_model import UserModel

class UserRepository(BaseRepository):
    def get_all_users (self):
        with self.db.get_session() as session:
            user = UserModel()
            res = session.get(user)
            print(res)