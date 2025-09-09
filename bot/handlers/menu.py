from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.services.weather_service import (
    fetch_weather,
    fetch_nextday,
    fetch_forecast,
    format_weather,
    format_nextday,
    format_forecast,
)
from bot.services.gif_service import fetch_random_gif

router = Router()

# --- Состояния FSM ---
class WeatherStates(StatesGroup):
    waiting_for_city = State()

class GifStates(StatesGroup):
    waiting_for_tag = State()


# --- Главное меню ---
@router.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Текущая погода", callback_data="weather")],
        [InlineKeyboardButton(text="Прогноз на завтра", callback_data="nextday")],
        [InlineKeyboardButton(text="Прогноз на 3 дня", callback_data="forecast")],
        [InlineKeyboardButton(text="Гифка по теме", callback_data="gif_tag")],
        [InlineKeyboardButton(text="Случайная гифка", callback_data="gif_random")],
    ])
    await message.answer("Привет 👋\nВыбери, что тебя интересует:", reply_markup=keyboard)


# --- Обработка кнопок погоды ---
@router.callback_query(F.data.in_({"weather", "nextday", "forecast"}))
async def show_city_menu(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data  # weather / nextday / forecast
    await state.update_data(action=action)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Псков", callback_data="city_Псков")],
        [InlineKeyboardButton(text="Колпино", callback_data="city_Колпино")],
        [InlineKeyboardButton(text="Санкт-Петербург", callback_data="city_Санкт-Петербург")],
        [InlineKeyboardButton(text="Другой город", callback_data="city_other")],
    ])
    await callback.message.answer("Выбери город:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("city_"))
async def process_city(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")  # weather / nextday / forecast
    city = callback.data.split("_", 1)[1]

    if city == "other":
        await callback.message.answer("Напиши название города:")
        await state.set_state(WeatherStates.waiting_for_city)
    else:
        await send_weather(callback.message, action, city)


@router.message(WeatherStates.waiting_for_city)
async def process_custom_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    action = data.get("action")
    city = message.text
    await send_weather(message, action, city)
    await state.clear()


async def send_weather(message: types.Message, action: str, city: str):
    if action == "weather":
        data = await fetch_weather(city)
        text = format_weather(data)
    elif action == "nextday":
        data = await fetch_nextday(city)
        text = format_nextday(data)
    else:  # forecast
        data = await fetch_forecast(city, days=3)
        text = format_forecast(data)

    await message.answer(text)


# --- Обработка гифок ---
@router.callback_query(F.data == "gif_random")
async def send_random_gif(callback: types.CallbackQuery):
    url = await fetch_random_gif()
    if url:
        await callback.message.answer_animation(url)
    else:
        await callback.message.answer("Упс! Гифка сейчас недоступна, попробуй позже.")


@router.callback_query(F.data == "gif_tag")
async def ask_gif_tag(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Напиши одним словом тему гифки (например: cat, smile, love)")
    await state.set_state(GifStates.waiting_for_tag)


@router.message(GifStates.waiting_for_tag)
async def send_gif_by_tag(message: types.Message, state: FSMContext):
    tag = message.text.strip()
    url = await fetch_random_gif(tag)
    await state.clear()
    if url:
        await message.answer_animation(url)
    else:
        await message.answer("Увы, ничего не нашлось 😢 Попробуй другой тег.")