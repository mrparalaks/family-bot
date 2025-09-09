import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os

from bot.handlers.weather import router as weather_router
from bot.handlers.forecast import router as forecast_router
from bot.handlers.nextday import router as nextday_router

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

# --- Команда /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer("Привет! 👋 Я семейный бот. Готов к работе.")

# --- Команда /help ---
@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        "Я могу выполнять такие команды:\n"
        "/start - приветствие\n"
        "/help - список команд\n\n"
        "/weather <город> - текущая погода\n"
        "/forecast <город> - прогноз на 3 дня\n"
        "/nextday <город> - прогноз на следующий день с шагом 3 часа"
    )

# --- Подключаем роутеры ---
dp.include_router(weather_router)
dp.include_router(forecast_router)
dp.include_router(nextday_router)

# --- Эхо-хэндлер для обычного текста ---
@dp.message(lambda message: not message.text.startswith("/"))
async def echo_message(message: types.Message) -> None:
    await message.answer(f"Ты сказал: {message.text}")

# --- Точка входа ---
async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)  # skip_updates=True -> не обрабатываем старые апдейты

if __name__ == "__main__":
    asyncio.run(main())