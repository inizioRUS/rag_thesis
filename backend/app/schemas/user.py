from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):
    id: UUID
    username: str
    password: str


class UserOut(BaseModel):
    id: UUID
    username: str

    class Config:
        orm_mode = True
