import uuid
from sqlalchemy import select
from models.user import User
from schemas.user import UserCreate
from auth.hashing import hash_password
from core.db import SessionLocal

async def create_user(user_in: UserCreate):
    db_user = User(
        id=user_in.id,
        username=user_in.username,
        hashed_password=hash_password(user_in.password)
    )
    async with SessionLocal() as session:
        async with session.begin():
            session.add(db_user)

        await session.commit()
        await session.refresh(db_user)

        return db_user


async def get_current_user(user_id: uuid.UUID) -> User | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_all_users():
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User))
    return result.scalars().all()
