from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
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
        self.engine = create_engine(url)

    def create_all(self, model:Model|list[Model]):
        if isinstance(model, list):
            for m in model:
                m.metadata.create_all(self.engine)
        else:
            model.metadata.create_all(self.engine) 

    def drop_all(self, model:Model|list[Model]):
        if isinstance(model, list):
            for m in model:
                m .metadata.drop_all(self.engine)
        else:
            model.metadata.drop_all(self.engine)

    def execute(self, query: str | Any, params: dict = None, query_type: str = "read"):
        if isinstance(query, str):
            query = text(query)
            
        with self.get_session() as session:
            result = session.execute(query, params or {})
            
            if query_type == "read":
                return [dict(row._mapping) for row in result]
            
            session.commit()
            return result
        
    def close_engine(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None
            
    def get_engime(self):
        return self.engine
    
    def get_session (self):
        return Session(self.engine)
    
    def migrations():
        pass