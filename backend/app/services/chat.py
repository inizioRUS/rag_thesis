import uuid
from datetime import timezone

from models.index import SearchIndex
from models.chat import Chat
from schemas.index import IndexCreate
from core.db import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from schemas.chat import ChatCreate

from models.msg import ChatMessage

from schemas.msg import Msg_in


async def create_new_chat(chat_in: ChatCreate):
    db_chat = Chat(
        id=chat_in.id,
        user_id=chat_in.user_id,
        index_id=chat_in.index_id,
        name=chat_in.name,
        msg_index_name=chat_in.msg_index_name,
        working_context=chat_in.working_context
    )

    async with SessionLocal() as session:
        async with session.begin():
            session.add(db_chat)

        await session.commit()
        await session.refresh(db_chat)

        return db_chat


async def get_chat_by_id(id: uuid.UUID, user_id: uuid.UUID) -> SearchIndex | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = (await session.execute(select(Chat).filter(Chat.id == id, Chat.user_id == user_id)))
    return result.scalars().first()


async def get_msgs_by_chat(id: uuid.UUID) -> SearchIndex | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = (await session.execute(select(ChatMessage).filter(ChatMessage.chat_id == id)))
    return result.scalars().all()


async def put_msg_by_chat(msg_in: Msg_in) -> SearchIndex | None:
    db_msg = ChatMessage(
        id=msg_in.id,
        user_id=msg_in.user_id,
        chat_id=msg_in.chat_id,
        content=msg_in.content,
        text=msg_in.text,
        timestamp=msg_in.timestamp.replace(tzinfo=None),
    )
    async with SessionLocal() as session:
        async with session.begin():
            session.add(db_msg)

        await session.commit()
        await session.refresh(db_msg)

        return db_msg


async def get_msgs_by_chat_last_k(id: uuid.UUID, k: int) -> SearchIndex | None:
    async with SessionLocal() as session:
        async with session.begin():
            result = (await session.execute(select(ChatMessage).filter(ChatMessage.chat_id == id)))
    return result.scalars().all()


async def update_working_context(id: uuid.UUID, new_working_context: str) -> Chat:
    async with SessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Chat).filter(Chat.id == id)
            )
            chat = result.scalar_one_or_none()

            if chat is not None:
                chat.working_context = new_working_context
                print("Deb")
                await session.flush()  # применяет изменения в рамках транзакции

            return chat  # вернёт обновлённый объект или None
