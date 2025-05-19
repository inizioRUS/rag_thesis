from pydantic import BaseModel
from uuid import UUID


class IndexCreate(BaseModel):
    id: UUID
    name: str
    description: str
    milvus_index_name:str
    is_private: bool
    user_id: UUID
