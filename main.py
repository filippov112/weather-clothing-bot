import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import TEMPERATURE_RANGES, SPECIAL_CONDITIONS, API_SETTINGS

# Настройка логов
logging.basicConfig(level=logging.INFO)

load_dotenv()
# Загрузка токенов
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Состояния пользователя
user_state = {}

# Клавиатура с датами
date_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сегодня"), KeyboardButton(text="Завтра")],
        [KeyboardButton(text="Послезавтра")]
    ],
    resize_keyboard=True
)


async def get_weather_forecast(city: str, date_offset: int = 0) -> dict | None:
    try:
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": API_SETTINGS["units"],
            "lang": API_SETTINGS["lang"],
            "cnt": 40  # Получаем больше прогнозов для точности
        }

        response = requests.get(API_SETTINGS["weather_url"], params=params, timeout=10)
        response.raise_for_status()  # Проверка HTTP ошибок

        data = response.json()

        if data.get("cod") != "200":
            logging.error(f"API error: {data.get('message', 'Unknown error')}")
            return None

        target_date = (datetime.now() + timedelta(days=date_offset)).date()
        forecasts = [f for f in data["list"]
                     if datetime.fromtimestamp(f["dt"]).date() == target_date]

        if not forecasts:
            logging.error(f"No forecast for {target_date}")
            return None

        # Выбираем прогноз ближе к полудню
        best_forecast = min(forecasts,
                            key=lambda f: abs(datetime.fromtimestamp(f["dt"]).hour - 12))

        return {
            "date": target_date.strftime("%d.%m.%Y"),
            "temp": best_forecast["main"]["temp"],
            "feels_like": best_forecast["main"]["feels_like"],
            "description": best_forecast["weather"][0]["description"],
            "wind": best_forecast["wind"]["speed"],
            "humidity": best_forecast["main"]["humidity"],
            "rain": "rain" in best_forecast and best_forecast["rain"].get("3h", 0) > 0,
            "snow": "snow" in best_forecast and best_forecast["snow"].get("3h", 0) > 0
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    except (KeyError, ValueError) as e:
        logging.error(f"Data parsing error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None


def get_clothing_recommendation(weather: dict) -> str:
    recommendations = []

    # Проверка температурных диапазонов
    for temp_range in TEMPERATURE_RANGES:
        if temp_range["min_temp"] <= weather["temp"] < temp_range["max_temp"]:
            recommendations.append(
                f"{temp_range['description']}: {temp_range['recommendation']}"
            )
            break

    # Проверка специальных условий
    for condition in SPECIAL_CONDITIONS:
        if condition["condition"](weather):
            recommendations.append(
                f"{condition['description']}: {condition['recommendation']}"
            )

    return "\n".join(recommendations)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу выбрать одежду по погоде.\n"
        "Выбери дату:",
        reply_markup=date_keyboard
    )


@dp.message(lambda message: message.text.lower() in ["сегодня", "завтра", "послезавтра"])
async def select_date(message: types.Message):
    user_state[message.from_user.id] = {
        "date_offset": 0 if message.text.lower() == "сегодня" else 1 if message.text.lower() == "завтра" else 2
    }
    await message.answer("Из какого ты города?", reply_markup=types.ReplyKeyboardRemove())


@dp.message()
async def handle_city(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_state:
        await message.answer("Сначала выберите дату!")
        return

    city = message.text
    date_offset = user_state[user_id]["date_offset"]

    await message.answer("⏳ Запрашиваю прогноз погоды...")

    try:
        weather = await get_weather_forecast(city, date_offset)
        if weather is None:
            await message.answer("❌ Не удалось получить прогноз. Проверьте название города и попробуйте позже.")
            return

        recommendation = get_clothing_recommendation(weather)

        response = (
            f"📅 Дата: {weather['date']}\n"
            f"📍 Город: {city}\n\n"
            f"🌡️ Температура: {weather['temp']:.1f}°C (ощущается как {weather['feels_like']:.1f}°C)\n"
            f"🌤️ Погода: {weather['description'].capitalize()}\n"
            f"💨 Ветер: {weather['wind']} м/с\n"
            f"💧 Влажность: {weather['humidity']}%\n\n"
            f"🧥 **Рекомендации по одежде:**\n{recommendation}"
        )

        await message.answer(response, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.")

    finally:
        if user_id in user_state:
            del user_state[user_id]


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
