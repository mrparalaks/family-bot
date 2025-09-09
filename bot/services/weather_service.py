import aiohttp
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from aiohttp.client_exceptions import ClientError, ClientConnectorError

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

# Единый кэш
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
                except Exception as e:
                    return {"cod": "500", "message": f"Ошибка разбора ответа JSON: {e}"}

                if response.status == 200:
                    _save_to_cache(cache_key, data)

                return data
    except (ClientError, ClientConnectorError) as e:
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
    humidity = data["main"].get("humidity")
    wind_speed = data.get("wind", {}).get("speed")

    lines = [
        f"🌍 Город: {city}",
        f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)",
        f"☁️ {description}"
    ]

    if humidity is not None:
        lines.append(f"💧 Влажность: {humidity}%")
    if wind_speed is not None:
        lines.append(f"💨 Ветер: {wind_speed} м/с")

    return "\n".join(lines)


def format_forecast(data: dict) -> str:
    """Форматирование прогноза на несколько дней (~каждые 24 часа)."""
    if str(data.get("cod")) != "200":
        return f"⚠️ Ошибка: {data.get('message', 'не удалось получить данные')}"

    city = data["city"]["name"]
    forecast_list = data["list"]
    days = forecast_list[::8]  # каждые 8 записей ~24 часа

    if not days:
        return f"⚠️ Не удалось получить прогноз для {city}"

    lines = [f"📅 Прогноз погоды для города {city}:"]
    for item in days:
        dt = datetime.fromtimestamp(item["dt"]).strftime("%d.%m (%a) %H:%M")
        temp = round(item["main"]["temp"])
        feels_like = round(item["main"]["feels_like"])
        description = item["weather"][0]["description"].capitalize()
        humidity = item["main"].get("humidity")
        wind_speed = item.get("wind", {}).get("speed")

        lines.append(
            f"\n📍 {dt}\n"
            f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"☁️ {description}"
        )
        if humidity is not None:
            lines[-1] += f"\n💧 Влажность: {humidity}%"
        if wind_speed is not None:
            lines[-1] += f"\n💨 Ветер: {wind_speed} м/с"

    return "\n".join(lines)