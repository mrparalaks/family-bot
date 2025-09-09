import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
if not GIPHY_API_KEY:
    raise RuntimeError("❌ Переменная окружения GIPHY_API_KEY не задана. Добавьте её в .env")

GIPHY_RANDOM_URL = "https://api.giphy.com/v1/gifs/random"

async def fetch_random_gif(tag: str = None) -> str:
    """
    Получает случайную GIF с Giphy.
    Если указан тег — по теме.
    Возвращает URL картинки или None, если не удалось.
    """
    params = {
        "api_key": GIPHY_API_KEY,
        "rating": "pg"  # ограничение по возрасту
    }
    if tag:
        params["tag"] = tag

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GIPHY_RANDOM_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data["data"]["images"]["original"]["url"]
    except Exception:
        return None