"""
/joke — Random joke
"""

from telegram.ext import CommandHandler
import requests

async def joke(update, context):
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any?type=single", timeout=10)
        data = r.json()
        joke_text = data.get("joke", "Joke nahi mila 😅")
    except:
        joke_text = "Abhi joke service down hai 🥲"

    name = update.effective_user.first_name or "Bhai"
    await update.message.reply_text(f"*{name}*,\n😂 {joke_text}", parse_mode="Markdown")

def register(app):
    app.add_handler(CommandHandler("joke", joke))
