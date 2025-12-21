from core.db import Repository
from base.models import UserModel

class UserRepository(Repository):
    def get_all_users (self, filter:None|dict=None, limit: int = 30, offset: int = 0, count: bool = False):
        with self.get_session() as session:
            q = session.query(UserModel)
            if filter:
                pass  # Implement filtering logic here

            if count:
                return q.count()
            return q.limit(limit).offset(offset).all()

    def create_user(self, user_data: dict):
        with self.get_session() as session:
            user = UserModel(**user_data)
            session.add(user)
            session.commit()
            return user
    
    def get_user_by_username(self, username: str):
        with self.get_session() as session:
            return session.query(UserModel).filter_by(username=username).first()
        
    def get_user_by_email(self, email: str):
        with self.get_session() as session:
            return session.query(UserModel).filter_by(email=email).first()
    
    def get_user_by_id(self, user_id: str):
        with self.get_session() as session:
            return session.query(UserModel).filter_by(user_id=user_id).first()
        
    def delete_user(self, user_id: str):
        with self.get_session() as session:
            user = session.query(UserModel).filter_by(user_id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
        
    def update_user(self, user_id: str, update_data: dict):
        with self.get_session() as session:
            user = session.query(UserModel).filter_by(user_id=user_id).first()
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                session.commit()
                return user
            return None
        
    def activate_user(self, user_id: str):
        return self.update_user(user_id, {"is_active": True})
    
    def deactivate_user(self, user_id: str):
        return self.update_user(user_id, {"is_active": False})
    
    def set_user_sudo(self, user_id: str, is_sudo: bool):
        return self.update_user(user_id, {"is_sudo": is_sudo})
    
    def count_users(self, filter:None|dict=None):
        return self.get_all_users(filter=filter, count=True)
    
    def search_users(self, query: str, limit: int = 30, offset: int = 0):
        with self.get_session() as session:
            q = session.query(UserModel).filter(
                (UserModel.username.ilike(f"%{query}%")) |
                (UserModel.email.ilike(f"%{query}%")) |
                (UserModel.first_name.ilike(f"%{query}%")) |
                (UserModel.last_name.ilike(f"%{query}%"))
            )
            return q.limit(limit).offset(offset).all()
        
    def user_sudo_exists(self):
        with self.get_session() as session:
            return session.query(UserModel).filter_by(is_sudo=True).first() is not None