from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from models.all import Base


class SearchIndex(Base):
    __tablename__ = "indices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    milvus_index_name = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    is_private = Column(Boolean, default=False, nullable=False)
    llm_type = Column(String, default=None, nullable=True)
    token = Column(String, default=None, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    user = relationship("User", back_populates="search_indexes")
    chat = relationship("Chat", back_populates="search_index")
    access = relationship("Access", back_populates="search_index")
    favorite = relationship("Favorite", back_populates="search_index")
    rating = relationship("Ratings", back_populates="search_index")
    telegram_bots = relationship("TelegramBot", back_populates="search_index")