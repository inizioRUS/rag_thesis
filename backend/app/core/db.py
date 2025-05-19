from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.all import Base
from models.user import User
from models.index import SearchIndex
from models.chat import ChatMessage
from models.tg_bot import TelegramBot
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydatabase"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)