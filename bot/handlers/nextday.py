from aiogram import Router, types
from aiogram.filters import Command
from bot.services.weather_service import fetch_nextday, format_nextday

router = Router()

@router.message(Command("nextday"))
async def send_nextday(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пожалуйста, укажи город. Пример: /nextday Москва")
        return
    city = parts[1]
    data = await fetch_nextday(city)
    text = format_nextday(data)
    await message.answer(text)