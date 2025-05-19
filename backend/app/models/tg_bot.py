from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.all import Base


class TelegramBot(Base):
    __tablename__ = 'telegram_bots'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_url = Column(String, nullable=False)
    token = Column(String, nullable=False)
    search_index_id = Column(UUID(as_uuid=True), ForeignKey('indices.id'))  # Поле для связи

    # Связь с индексом
    search_index = relationship("SearchIndex", back_populates="telegram_bots")