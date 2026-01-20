from core.db import Repository
from base.models import UserModel
from sqlalchemy import select, func

class UserRepository(Repository):
    async def get_all_users(self, filter:None|dict=None, limit: int = 30, offset: int = 0, count: bool = False):
        async with self.get_session() as session:
            if count:
                stmt = select(func.count()).select_from(UserModel)
                result = await session.execute(stmt)
                return result.scalar()
            
            stmt = select(UserModel)
            if filter:
                pass  # Implement filtering logic here
            
            stmt = stmt.limit(limit).offset(offset)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def create_user(self, user_data: dict):
        async with self.get_session() as session:
            user = UserModel(**user_data)
            session.add(user)
            await session.commit()
            return user
    
    async def get_user_by_username(self, username: str):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(username=username)
            result = await session.execute(stmt)
            return result.scalars().first()
        
    async def get_user_by_email(self, email: str):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(email=email)
            result = await session.execute(stmt)
            return result.scalars().first()
    
    async def get_user_by_id(self, user_id: str):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(user_id=user_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        
    async def delete_user(self, user_id: str):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(user_id=user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False
        
    async def update_user(self, user_id: str, update_data: dict):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(user_id=user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                await session.commit()
                return user
            return None
        
    async def activate_user(self, user_id: str):
        return await self.update_user(user_id, {"is_active": True})
    
    async def deactivate_user(self, user_id: str):
        return await self.update_user(user_id, {"is_active": False})
    
    async def set_user_sudo(self, user_id: str, is_sudo: bool):
        return await self.update_user(user_id, {"is_sudo": is_sudo})
    
    async def count_users(self, filter:None|dict=None):
        return await self.get_all_users(filter=filter, count=True)
    
    async def search_users(self, query: str, limit: int = 30, offset: int = 0):
        async with self.get_session() as session:
            stmt = select(UserModel).filter(
                (UserModel.username.ilike(f"%{query}%")) |
                (UserModel.email.ilike(f"%{query}%")) |
                (UserModel.first_name.ilike(f"%{query}%")) |
                (UserModel.last_name.ilike(f"%{query}%"))
            ).limit(limit).offset(offset)
            
            result = await session.execute(stmt)
            return result.scalars().all()
        
    async def user_sudo_exists(self):
        async with self.get_session() as session:
            stmt = select(UserModel).filter_by(is_sudo=True)
            result = await session.execute(stmt)
            return result.scalars().first() is not None