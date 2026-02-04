from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from .model import Model
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.application import Application

class DataBase():
    def __init__(self, app:Application):
        self.app = app
        self.engine = None

    def init_database(self):
        url = self.app.config.get_db_url()
        # Ensure the URL uses an async driver
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            
        self.engine = create_async_engine(url)

    async def create_all(self, model:Model|list[Model]):
        async with self.engine.begin() as conn:
            if isinstance(model, list):
                for m in model:
                    await conn.run_sync(m.metadata.create_all)
            else:
                await conn.run_sync(model.metadata.create_all)

    async def drop_all(self, model:Model|list[Model]):
        async with self.engine.begin() as conn:
            if isinstance(model, list):
                for m in model:
                    await conn.run_sync(m.metadata.drop_all)
            else:
                await conn.run_sync(model.metadata.drop_all)

    async def execute(self, query: str | Any, params: dict = None, query_type: str = "read"):
        if isinstance(query, str):
            query = text(query)
            
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            
            if query_type == "read":
                return [dict(row._mapping) for row in result]
            
            await session.commit()
            return result
        
    async def close_engine(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            
    def get_engime(self):
        return self.engine
    
    def get_session(self) -> AsyncSession:
        return AsyncSession(self.engine)
    
    def migrations():
        pass