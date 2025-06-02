# Конфигурация температурных диапазонов и рекомендаций
TEMPERATURE_RANGES = [
    {
        "min_temp": -50,
        "max_temp": 0,
        "description": "❄️ Сильный мороз",
        "recommendation": "Теплая зимняя куртка, шапка, шарф, перчатки, термобельё"
    },
    {
        "min_temp": 0,
        "max_temp": 10,
        "description": "🥶 Холодно",
        "recommendation": "Пуховик/демисезонная куртка, шапка, тёплый свитер"
    },
    {
        "min_temp": 10,
        "max_temp": 18,
        "description": "🧥 Прохладно",
        "recommendation": "Ветровка/джинсовка, лёгкий свитер/кофта"
    },
    {
        "min_temp": 18,
        "max_temp": 25,
        "description": "👕 Тепло",
        "recommendation": "Футболка/рубашка, джинсы/шорты"
    },
    {
        "min_temp": 25,
        "max_temp": 50,
        "description": "🔥 Жара",
        "recommendation": "Лёгкая одежда, головной убор, солнцезащитные очки"
    }
]

# Дополнительные условия
SPECIAL_CONDITIONS = [
    {
        "condition": lambda w: w["wind"] > 10,
        "description": "💨 Сильный ветер",
        "recommendation": "Ветровка/непродуваемая одежда"
    },
    {
        "condition": lambda w: w["rain"],
        "description": "☔ Ожидается дождь",
        "recommendation": "Возьмите зонт или дождевик"
    },
    {
        "condition": lambda w: w["snow"],
        "description": "❄️ Ожидается снег",
        "recommendation": "Наденьте непромокаемую обувь"
    }
]

# Настройки API
API_SETTINGS = {
    "weather_url": "http://api.openweathermap.org/data/2.5/forecast",
    "units": "metric",
    "lang": "ru"
}