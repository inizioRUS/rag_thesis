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
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    user = relationship("User", back_populates="search_indexes")
    chat_messages = relationship("ChatMessage", back_populates="search_index")
    telegram_bots = relationship("TelegramBot", back_populates="search_index")