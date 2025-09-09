# bot/main.py

import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from bot.handlers.weather import router as weather_router
from bot.handlers.forecast import router as forecast_router
from bot.handlers.nextday import router as nextday_router
from bot.handlers.gif import router as gif_router
from bot.handlers import menu  # роутер с кнопками

# Загружаем переменные окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "❌ Переменная окружения BOT_TOKEN не задана. "
        "Создай файл .env и добавь BOT_TOKEN='твой_токен'"
    )

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Подключаем роутеры ---
dp.include_router(menu.router)       # меню-кнопки (в нём и приветствие /start)
dp.include_router(weather_router)
dp.include_router(forecast_router)
dp.include_router(nextday_router)
dp.include_router(gif_router)

# --- Точка входа ---
async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
