from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Msg_in(BaseModel):
    id: UUID
    user_id: UUID
    chat_id: UUID
    content: dict
    text: str
    timestamp: datetime