"""
/quote — Random motivational quote
"""

from telegram.ext import CommandHandler
import requests

async def quote(update, context):
    try:
        r = requests.get("https://api.quotable.io/random", timeout=10)
        data = r.json()
        quote_text = data.get("content", "Quote nahi mila")
        author = data.get("author", "Unknown")
    except:
        quote_text = "Abhi quote service down hai 🥲"
        author = ""

    name = update.effective_user.first_name or "Bhai"
    
    if author:
        text = f"*{name}*,\n✨ \"{quote_text}\"\n\n— _{author}_"
    else:
        text = f"*{name}*,\n✨ {quote_text}"

    await update.message.reply_text(text, parse_mode="Markdown")

def register(app):
    app.add_handler(CommandHandler("quote", quote))
