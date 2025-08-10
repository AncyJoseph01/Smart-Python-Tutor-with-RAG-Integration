from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from .database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # stored hashed

    @validates("email")
    def convert_lowercase(self, key, value):
        return value.lower()