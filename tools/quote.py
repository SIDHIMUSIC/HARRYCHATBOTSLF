"""
/quote — Random motivational quote (with fallbacks)
"""

from telegram.ext import CommandHandler
import requests
import random

def get_quote():
    # Multiple free sources
    sources = [
        # Source 1
        {
            "url": "https://api.quotable.io/random",
            "parse": lambda d: (d.get("content"), d.get("author"))
        },
        # Source 2
        {
            "url": "https://zenquotes.io/api/random",
            "parse": lambda d: (d[0].get("q"), d[0].get("a")) if isinstance(d, list) else (None, None)
        },
        # Source 3
        {
            "url": "https://dummyjson.com/quotes/random",
            "parse": lambda d: (d.get("quote"), d.get("author"))
        },
    ]

    random.shuffle(sources)

    for source in sources:
        try:
            r = requests.get(source["url"], timeout=8)
            if r.status_code == 200:
                data = r.json()
                quote, author = source["parse"](data)
                if quote:
                    return quote.strip(), author
        except:
            continue

    # Final fallback (hardcoded)
    fallbacks = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
        ("Success is not final, failure is not fatal: It is the courage to continue that counts.", "Winston Churchill"),
        ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ]
    return random.choice(fallbacks)


async def quote(update, context):
    name = update.effective_user.first_name or "Bhai"
    
    quote_text, author = get_quote()

    if author:
        text = f"*{name}*,\n✨ \"{quote_text}\"\n\n— _{author}_"
    else:
        text = f"*{name}*,\n✨ \"{quote_text}\""

    await update.message.reply_text(text, parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("quote", quote))
