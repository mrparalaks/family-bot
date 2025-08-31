import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import os
from dotenv import load_dotenv
from bot.handlers.weather import router as weather_router

# Загружаем переменные окружения из .env
load_dotenv()

# Читаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError(
        "Переменная окружения BOT_TOKEN не задана. "
        "Создай файл .env и добавь BOT_TOKEN='твой_реальный_токен'"
    )

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Хэндлер на команду /start ---
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! 👋 Я семейный бот. Готов к работе.")

# --- Хэндлер на команду /help ---
@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Я могу выполнять такие команды:\n"
        "/start - приветствие\n"
        "/help - список команд\n\n"
        "/weather <город> - текущая погода\n"
        "/forecast <город> - прогноз на 3 дня"
    )

# --- Подключаем погодный router ---
dp.include_router(weather_router)

# --- Эхо-хэндлер для обычного текста ---
@dp.message(lambda message: not message.text.startswith("/"))
async def echo_message(message: Message) -> None:
    """
    Отправляет обратно любое текстовое сообщение,
    кроме команд (начинающихся с /).
    """
    await message.answer(f"Ты сказал: {message.text}")

# --- Точка входа: запуск long polling ---
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())