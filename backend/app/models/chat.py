from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.all import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    index_id = Column(UUID(as_uuid=True), ForeignKey("indices.id"), nullable=False)
    name = Column(String, nullable=False)
    msg_index_name = Column(String, nullable=False)
    working_context = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat")
    search_index = relationship("SearchIndex", back_populates="chat")
    chat_messages = relationship("ChatMessage", back_populates="chat")