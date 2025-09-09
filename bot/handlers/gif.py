from aiogram import Router, types
from aiogram.filters import Command
from bot.services.gif_service import fetch_random_gif

router = Router()

@router.message(Command("gif"))
async def send_gif(message: types.Message) -> None:
    gif_url = await fetch_random_gif()
    if gif_url:
        await message.answer_animation(gif_url)
    else:
        await message.answer("Упс! Не удалось получить GIF. Попробуй ещё раз.")