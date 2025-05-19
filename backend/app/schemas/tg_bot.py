from pydantic import BaseModel, HttpUrl
from uuid import UUID


class TelegramBotCreate(BaseModel):
    bot_url: str
    token: str
    search_index_id: UUID
