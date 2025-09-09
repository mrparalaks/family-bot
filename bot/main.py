import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

# Загружаем переменные окружения (.env)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "❌ Переменная окружения BOT_TOKEN не задана. "
        "Создай файл .env и добавь BOT_TOKEN='твой_токен'"
    )

# Импорт роутеров
from bot.handlers import weather, forecast, nextday, gif, menu

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(menu.router)       # главное меню с кнопкой
    dp.include_router(weather.router)    # команда /weather
    dp.include_router(forecast.router)   # команда /forecast
    dp.include_router(nextday.router)    # команда /nextday
    dp.include_router(gif.router)        # команды /gif

    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())