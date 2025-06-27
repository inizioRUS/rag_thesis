from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, INTEGER
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from models.all import Base


class Ratings(Base):
    __tablename__ = "rating"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    index_id = Column(UUID(as_uuid=True), ForeignKey("indices.id"), nullable=False)
    score = Column(INTEGER, nullable=False)

    user = relationship("User", back_populates="rating")
    search_index = relationship("SearchIndex", back_populates="rating")
