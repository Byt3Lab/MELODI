from core.db import Repository
from base.models import UserModel

class UserRepository(Repository):
    def get_all_users (self):
        with self.db.get_session() as session:
            user = UserModel()
            res = session.get(user)
            print(res)