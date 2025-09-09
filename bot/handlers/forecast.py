from aiogram import Router, types
from aiogram.filters import Command
from bot.services.weather_service import fetch_forecast, format_forecast

router = Router()

@router.message(Command("forecast"))
async def send_forecast(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Пожалуйста, укажи город. Пример: /forecast Москва")
        return
    city = parts[1]
    data = await fetch_forecast(city)
    text = format_forecast(data)
    await message.answer(text)
