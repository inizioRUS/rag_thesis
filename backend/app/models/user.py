from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from models.all import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    # Связь с индексами
    search_indexes = relationship("SearchIndex", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")