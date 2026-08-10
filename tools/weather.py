"""
/weather — Current weather of any city
Usage: /weather Delhi
       /weather Mumbai
       /weather New York
"""

from telegram.ext import CommandHandler
import requests


# Weather code to emoji + description
WEATHER_CODES = {
    0: ("☀️", "Clear sky"),
    1: ("🌤", "Mainly clear"),
    2: ("⛅", "Partly cloudy"),
    3: ("☁️", "Overcast"),
    45: ("🌫", "Fog"),
    48: ("🌫", "Depositing rime fog"),
    51: ("🌦", "Light drizzle"),
    53: ("🌦", "Moderate drizzle"),
    55: ("🌧", "Dense drizzle"),
    61: ("🌧", "Slight rain"),
    63: ("🌧", "Moderate rain"),
    65: ("🌧", "Heavy rain"),
    71: ("❄️", "Slight snow"),
    73: ("❄️", "Moderate snow"),
    75: ("❄️", "Heavy snow"),
    80: ("🌦", "Slight rain showers"),
    81: ("🌧", "Moderate rain showers"),
    82: ("⛈", "Violent rain showers"),
    95: ("⛈", "Thunderstorm"),
    96: ("⛈", "Thunderstorm with slight hail"),
    99: ("⛈", "Thunderstorm with heavy hail"),
}


async def weather(update, context):
    if not context.args:
        return await update.message.reply_text(
            "❌ Use like this:\n"
            "`/weather Delhi`\n"
            "`/weather Mumbai`\n"
            "`/weather New York`",
            parse_mode="Markdown"
        )

    city = " ".join(context.args)
    name = update.effective_user.first_name or "Bhai"

    try:
        # 1. City name → Latitude Longitude
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_res = requests.get(geo_url, params={
            "name": city,
            "count": 1,
            "language": "en"
        }, timeout=10)

        geo_data = geo_res.json()

        if not geo_data.get("results"):
            return await update.message.reply_text(
                f"*{name}*,\n❌ City nahi mili: `{city}`",
                parse_mode="Markdown"
            )

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")

        # 2. Weather data lo
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_res = requests.get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "timezone": "auto"
        }, timeout=10)

        data = weather_res.json()
        current = data["current"]

        temp = current["temperature_2m"]
        feels_like = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]

        emoji, condition = WEATHER_CODES.get(code, ("🌡", "Unknown"))

        text = (
            f"{emoji} *Weather in {city_name}, {country}*\n\n"
            f"🌡 Temperature: *{temp}°C*\n"
            f"🤒 Feels like: *{feels_like}°C*\n"
            f"💧 Humidity: *{humidity}%*\n"
            f"💨 Wind: *{wind} km/h*\n"
            f"☁️ Condition: *{condition}*"
        )

        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        print("Weather error:", e)
        await update.message.reply_text(
            f"*{name}*,\n⚠️ Weather service abhi down hai, thodi der baad try karo.",
            parse_mode="Markdown"
        )


def register(app):
    app.add_handler(CommandHandler("weather", weather))
