from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, validates
from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # store hashed password

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    @validates("email")
    def convert_lowercase(self, key, value):
        return value.lower()


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)  # unique row id
    chat_session_id = Column(Integer, nullable=False, index=True)  # groups multiple Q&A in a session
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    query = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chats")
