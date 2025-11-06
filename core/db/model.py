from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Model(DeclarativeBase):
    mapped_collum = mapped_column
    Mapped = Mapped
    Integer = Integer
    String = String
    Float = Float
    Boolean = Boolean