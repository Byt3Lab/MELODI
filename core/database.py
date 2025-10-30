from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from core.model import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.application import Application

class DataBase():
    def __init__(self, app:Application):
        self.app = app
        self.engine = None

    def init_database(self):
        self.engine = create_engine(self.app.config.DB_URL, echo=False)

    def create_all(self):
        BaseModel.metadata.create_all(self.engine) 
    
    def get_session (self):
        return Session(self.engine)
    
    def migrations():
        pass