import aiohttp
import os
import time
from dotenv import load_dotenv


# Загружаем переменные окружения (.env)
load_dotenv()

# API-ключ OpenWeather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"

__cache = {}
CACHE_TTL = 600

async def fetch_weather(city: str, units: str = "metric", lang: str = "ru") -> dict:
    """
    Базовая функция для запроса текущей погоды в OpenWeather API.
    Возвращает словарь с данными.
    """
    cache_key = (city.lower(), "weather")
    now = time.time()

    if cache_key in __cache:
        ts, data = __cache[cache_key]
        if now - ts < CACHE_TTL:
            return data


    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": units,
        "lang": lang
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

            if response.status == 200:
                __cache[cache_key] = (now, data)

            return data

async def fetch_forecast(city: str, days: int = 3, units: str = "metric", lang: str = "ru") -> dict:
    """
    Функция для получения прогноза погоды (на несколько дней).
    """

    cache_key = (city.lower(), f"forecast_{days}")
    now = time.time()

    if cache_key in __cache:
        ts, data = __cache[cache_key]
        if now - ts < CACHE_TTL:
            return data

    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": units,
        "lang": lang,
        "cnt": days * 8
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

            if response.status == 200:
                __cache[cache_key] = (now, data)

            return data

def format_weather(data: dict) -> str:
    """
    Функция для форматирования ответа в красивый текст для пользователя.
    """
    if data.get("cod") != 200:
        return f"Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["name"]
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    feels_like = data["main"]["feels_like"]

    return (
        f"🌍 Город: {city}\n"
        f"🌡 Температура: {temp}°C\n"
        f"🤔 Ощущается как: {feels_like}°C\n"
        f"☁️ {description.capitalize()}"
    )