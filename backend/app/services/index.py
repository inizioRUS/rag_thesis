import uuid

from models.index import SearchIndex
from schemas.index import IndexCreate
from core.db import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import joinedload


async def create_new_index(index_in: IndexCreate):
    db_index = SearchIndex(
        id=index_in.id,
        milvus_index_name=index_in.milvus_index_name,
        name=index_in.name,
        description=index_in.description,
        is_private=index_in.is_private,
        user_id=index_in.user_id
    )

    async with SessionLocal() as session:
        async with session.begin():
            session.add(db_index)

        await session.commit()
        await session.refresh(db_index)

        return db_index


async def get_public_indices_page(page: int, per_page: int):
    async with SessionLocal() as session:
        async with session.begin():
            offset = (page - 1) * per_page
            result = await session.execute(
                select(SearchIndex).where(SearchIndex.is_private == False)
                .offset(offset)
                .limit(per_page)
            )
        return result.scalars().all()


async def get_user_indices(user_id: uuid.UUID):
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(SearchIndex).where(SearchIndex.user_id == user_id)
            )
        return result.scalars().all()


async def get_current_index(index_id: uuid.UUID) -> SearchIndex | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(SearchIndex).filter(SearchIndex.id == index_id))
    return result.scalar_one_or_none()


async def get_tg_bot_by_index(index_id: uuid.UUID) -> SearchIndex | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = (await session.execute(select(SearchIndex).filter(SearchIndex.id == index_id).options(joinedload(SearchIndex.telegram_bots)))).first()
    return result[0].telegram_bots
