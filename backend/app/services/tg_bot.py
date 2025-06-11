import time
import aiohttp
import yaml
from models.tg_bot import TelegramBot
from schemas.tg_bot import TelegramBotCreate

from services.index import get_current_index

# Словарь с запущенными ботами
running_bots = {}
from core.db import SessionLocal
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio

def read_config():
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


config = read_config()
ml_address = config.get("ml", {}).get("address")
ml_port = config.get("ml", {}).get("port")


async def get_ml_response(message: str, index_name: str, llm_type:str, token:str):
    url = f"http://{ml_address}:{ml_port}/get_answer"  # URL вашего ML-сервиса
    data = {
        "message": message,
        "index_name": index_name,
        "llm_type": llm_type,
        "token": token

    }

    # Отправляем запрос к ML-сервису асинхронно
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()  # Получаем ответ в формате JSON
                return result.get('reply', 'Ошибка получения ответа от сервиса.')
            else:
                return "Ошибка запроса к сервису."
async def create_new_tg_bot(bot_in: TelegramBotCreate):
    db_index = TelegramBot(
        bot_url=bot_in.bot_url,
        token=bot_in.token,
        search_index_id=bot_in.search_index_id,
    )

    async with SessionLocal() as session:
        async with session.begin():
            session.add(db_index)

        await session.commit()
        await session.refresh(db_index)

        return db_index


async def start_bot(index_id: str, token: str, llm_type, token_llm):
    print("Проверка")
    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def handle_start(message: Message):
        await message.answer(f"👋 Привет! Ты подключился к индексу {index_id}")

    @dp.message()
    async def handle_message(message: Message):
        ml_response = await get_ml_response(message.text, index_id, llm_type, token_llm)
        await message.answer(f"🔍 Ты сказал: {message.text}\nОтвет от сервиса: {ml_response}")

    try:
        print(f"🚀 Запуск Telegram-бота: {index_id}")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print(f"🛑 Бот {index_id} остановлен вручную.")
        await bot.session.close()


async def launch_bot(index_name: str, token: str, llm_type:str, token_llm:str):
    if index_name in running_bots:
        print(f"Бот для индекса {index_name} уже запущен.")
        return

    # Запускаем бота как фоновую задачу
    task = asyncio.create_task(start_bot(index_name, token, llm_type, token_llm))
    running_bots[index_name] = task
    print(f"Бот запущен для индекса {index_name}.")


def stop_bot(index_id: str):
    if index_id in running_bots:
        task = running_bots.pop(index_id)
        task.cancel()
        print(f"Бот остановлен для индекса {index_id}.")
