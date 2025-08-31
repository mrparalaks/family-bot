from aiogram import Router, types
from aiogram.filters import Command
from bot.services.weather_service import fetch_weather, format_weather, fetch_forecast, format_forecast

# Создаем маршрутизатор (Router) для команды /weather
router = Router()

@router.message(Command("weather"))
async def send_weather(message: types.Message) -> None:
    """
    Обработчик команды /weather.
    Пользователь пишет: /weather <город>
    Бот отвечает текущей погодой.
    """
    # Разбиваем текст сообщения на слова
    parts = message.text.split(maxsplit=1)

    # Проверяем, указал ли пользователь город
    if len(parts) < 2:
        await message.answer("Пожалуйста, укажи город. Пример: /weather Москва")
        return
    
    city = parts[1] # Второе слово - название города

    # Получаем данные о погоде через сервис
    data = await fetch_weather(city)

    # Форматируем данные в красивый текст
    text = format_weather(data)

    # Отправляем пользователю
    await message.answer(text)

@router.message(Command("forecast"))
async def send_forecast(message: types.Message) -> None:
    """
    Обработчик команды /forecast.
    Пользователь пишет: /forecast <город>
    Бот отвечает прогнозом на несколько дней.
    """
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Пожалуйста, укажи город. Пример: /forecast Москва")
        return
    
    city = parts[1]

    # Получаем прогноз
    data = await fetch_forecast(city, days=3)

    # Форматируем прогноз
    text = format_forecast(data)

    # Отправляем пользователю
    await message.answer(text)