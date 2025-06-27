from sqlalchemy import Column, String, ForeignKey
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
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=False, default="550e8400-e29b-41d4-a716-446655440000")

    # Связь с индексами
    search_indexes = relationship("SearchIndex", back_populates="user")
    chat = relationship("Chat", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    access = relationship("Access", back_populates="user")
    rating = relationship("Ratings", back_populates="user")
    favorite = relationship("Favorite", back_populates="user")
    role = relationship("Role", back_populates="user")
