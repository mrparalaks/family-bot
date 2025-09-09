import aiohttp
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiohttp.client_exceptions import ClientError, ClientConnectionError, ClientPayloadError

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

# Кэш
__cache = {}
CACHE_TTL = 600  # 10 минут


# ---------- Вспомогательные функции ----------

def _get_from_cache(key: tuple):
    """Получение данных из кэша (если не протух)."""
    now = time.time()
    if key in __cache:
        ts, data = __cache[key]
        if now - ts < CACHE_TTL:
            return data
    return None


def _save_to_cache(key: tuple, data: dict):
    """Сохраняем данные в кэш."""
    __cache[key] = (time.time(), data)


async def _fetch(endpoint: str, params: dict, cache_key: tuple) -> dict:
    """Универсальная функция запросов к OpenWeather с кэшем и обработкой ошибок."""
    cached = _get_from_cache(cache_key)
    if cached:
        return cached

    url = f"{BASE_URL}/{endpoint}"
    params["appid"] = WEATHER_API_KEY

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                try:
                    data = await response.json()
                except Exception:
                    return {"cod": "500", "message": "Ошибка обработки JSON от сервера"}

                if response.status == 200:
                    _save_to_cache(cache_key, data)

                return data
    except (ClientError, ClientConnectionError, ClientPayloadError) as e:
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


async def fetch_nextday(city: str, units: str = "metric", lang: str = "ru") -> dict:
    """
    Прогноз на следующий день с шагом 3 часа (6, 9, 12, 15, 18, 21, 24 часа).
    """
    data = await _fetch(
        "forecast",
        {"q": city, "units": units, "lang": lang},
        (city.lower(), "nextday")
    )
    return data


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
        f"🌍 Город: {city}\n"
        f"🌡 Температура: {temp}°C\n"
        f"🤔 Ощущается как: {feels_like}°C\n"
        f"☁️ {description}"
    )


def format_forecast(data: dict) -> str:
    """Форматирование прогноза на несколько дней."""
    if str(data.get("cod")) != "200":
        return f"⚠️ Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["city"]["name"]
    forecast_list = data["list"]

    # Берём каждые 8 записей (~раз в сутки)
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


def format_nextday(data: dict) -> str:
    """Форматирование прогноза на следующий день с шагом 3 часа."""
    if str(data.get("cod")) != "200":
        return f"⚠️ Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["city"]["name"]
    forecast_list = data["list"]

    if not forecast_list:
        return f"⚠️ Не удалось получить прогноз для {city}"

    # Определяем следующие 24 часа от текущего времени
    now = datetime.now()
    next_day = now + timedelta(days=1)
    next_day_start = datetime(next_day.year, next_day.month, next_day.day)
    next_day_end = next_day_start + timedelta(hours=24)

    # Фильтруем только данные следующего дня
    items_next_day = [
        item for item in forecast_list
        if next_day_start <= datetime.fromtimestamp(item["dt"]) < next_day_end
    ]

    if not items_next_day:
        return f"⚠️ Не удалось получить данные для следующего дня в {city}"

    lines = [f"📅 Прогноз погоды на следующий день: {city}"]
    for item in items_next_day:
        dt = datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
        temp = round(item["main"]["temp"])
        feels_like = round(item["main"]["feels_like"])
        description = item["weather"][0]["description"].capitalize()
        lines.append(
            f"\n📍 {dt}\n"
            f"🌡 {temp}°C (ощущается как {feels_like}°C)\n"
            f"☁️ {description}"
        )

    return "\n".join(lines)