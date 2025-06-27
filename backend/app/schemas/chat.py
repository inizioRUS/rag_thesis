from pydantic import BaseModel, HttpUrl
from uuid import UUID


class ChatCreate(BaseModel):
    id: UUID
    user_id: UUID
    index_id: UUID
    name: str
    msg_index_name: str
    working_context: str