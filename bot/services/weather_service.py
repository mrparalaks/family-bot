import aiohttp
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from aiohttp.client_exceptions import ClientError

# Загружаем переменные окружения (.env)
load_dotenv()

# API-ключ OpenWeather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise RuntimeError(
        "❌ Переменная окружения WEATHER_API_KEY не задана. "
        "Создай .env и добавь WEATHER_API_KEY='твой_ключ'"
    )

BASE_URL = "https://api.openweathermap.org/data/2.5"


# ---------- Кэш ----------

class Cache:
    """Простой кэш с TTL (time-to-live)."""

    def __init__(self, ttl: int = 600):
        self._storage = {}
        self._ttl = ttl

    def get(self, key: tuple):
        """Получить данные из кэша, если не устарели."""
        now = time.time()
        if key in self._storage:
            ts, data = self._storage[key]
            if now - ts < self._ttl:
                return data
        return None

    def set(self, key: tuple, data: dict):
        """Сохранить данные в кэш."""
        self._storage[key] = (time.time(), data)


# Создаём единый экземпляр кэша
cache = Cache(ttl=600)


# ---------- Универсальная функция запроса ----------

async def _fetch(endpoint: str, params: dict, cache_key: tuple) -> dict:
    """Универсальный запрос к OpenWeather с кэшем и обработкой ошибок."""
    cached = cache.get(cache_key)
    if cached:
        return cached

    url = f"{BASE_URL}/{endpoint}"
    params["appid"] = WEATHER_API_KEY

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                data = await response.json()

                if response.status == 200:
                    cache.set(cache_key, data)

                return data
    except ClientError as e:
        return {"cod": "500", "message": f"Ошибка сети: {e}"}
    except Exception as e:
        return {"cod": "500", "message": f"Неизвестная ошибка: {e}"}


# ---------- Основные функции ----------

async def fetch_weather(city: str, units: str = "metric", lang: str = "ru") -> dict:
    """Запрос текущей погоды."""
    return await _fetch(
        "weather",
        {"q": city, "units": units, "lang": lang},
        (city.lower(), "weather")
    )


async def fetch_forecast(city: str, days: int = 3, units: str = "metric", lang: str = "ru") -> dict:
    """Запрос прогноза на несколько дней."""
    return await _fetch(
        "forecast",
        {"q": city, "units": units, "lang": lang, "cnt": days * 8},
        (city.lower(), f"forecast_{days}")
    )


# ---------- Форматирование ----------

def format_weather(data: dict) -> str:
    """Форматирование текущей погоды."""
    if str(data.get("cod")) != "200":
        return f"⚠️ Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["name"]
    temp = round(data["main"]["temp"])
    feels_like = round(data["main"]["feels_like"])
    description = data["weather"][0]["description"].capitalize()

    return (
        f"🌍 {city}\n"
        f"🌡 {temp}°C (ощущается как {feels_like}°C)\n"
        f"☁️ {description}"
    )


def format_forecast(data: dict) -> str:
    """Форматирование прогноза на несколько дней."""
    if str(data.get("cod")) != "200":
        return f"⚠️ Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["city"]["name"]
    forecast_list = data["list"]

    # Берём каждые 8 записей (~раз в сутки, т.к. шаг прогноза 3 часа)
    days = forecast_list[::8]

    if not days:
        return f"⚠️ Не удалось получить прогноз для {city}"

    lines = [f"📅 Прогноз погоды: {city}"]
    for item in days:
        dt = datetime.fromtimestamp(item["dt"]).strftime("%d.%m %H:%M")
        temp = round(item["main"]["temp"])
        feels_like = round(item["main"]["feels_like"])
        description = item["weather"][0]["description"].capitalize()
        lines.append(
            f"\n📍 {dt}\n"
            f"🌡 {temp}°C (ощущается как {feels_like}°C)\n"
            f"☁️ {description}"
        )

    return "\n".join(lines)