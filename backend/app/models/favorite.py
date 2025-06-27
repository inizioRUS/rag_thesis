from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.all import Base


class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    index_id = Column(UUID(as_uuid=True), ForeignKey("indices.id"), nullable=False)
    user = relationship("User", back_populates="favorite")
    search_index = relationship("SearchIndex", back_populates="favorite")
