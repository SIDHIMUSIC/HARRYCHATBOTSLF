"""
/advice — Random life advice
"""

from telegram.ext import CommandHandler
import requests
import random

def get_advice():
    sources = [
        "https://api.adviceslip.com/advice",
    ]

    for url in sources:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                advice = data.get("slip", {}).get("advice")
                if advice:
                    return advice
        except:
            continue

    # Fallback advices
    fallbacks = [
        "Hamesha apne goals pe focus rakho, distractions se door raho.",
        "Roz thoda sa progress karo, bada success aayega.",
        "Galti se mat daro, unse seekho.",
        "Apne aap pe vishwas rakho, baaki sab secondary hai.",
        "Time waste mat karo, yeh wapas nahi aata.",
        "Jo log tujhe down feel karaye, unse door reh.",
        "Hard work + consistency = Success.",
        "Apni health ka khayal rakh, baaki sab secondary hai.",
    ]
    return random.choice(fallbacks)


async def advice(update, context):
    name = update.effective_user.first_name or "Bhai"
    advice_text = get_advice()

    text = f"*{name}*,\n💡 *Advice for you:*\n\n_{advice_text}_"
    
    await update.message.reply_text(text, parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("advice", advice))
