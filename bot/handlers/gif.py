from aiogram import Router, types
from aiogram.filters import Command
from bot.services.gif_service import fetch_random_gif

router = Router()

@router.message(Command("gif"))
async def send_gif(message: types.Message) -> None:
    parts = message.text.split(maxsplit=1)
    tag = parts[1] if len(parts) > 1 else None  # если есть слово после /gif, используем как тег

    gif_url = await fetch_random_gif(tag)
    if gif_url:
        await message.answer_animation(gif_url)
    else:
        await message.answer("Упс! Не удалось получить GIF. Попробуй ещё раз.")