from core.db import Model
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class UserModel(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    is_sudo: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[str] = mapped_column(String(50))
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email}, is_sudo={self.is_sudo})>"