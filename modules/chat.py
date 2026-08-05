import time
import asyncio
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import BOT_USERNAME, BOT_NICKNAMES, STICKERS
from helpers import (
    safe_ai, get_fallback_reply, get_memory,
    is_bot_banned, users, chat_logs
)

try:
    from function import get_bot_extras
except ImportError:
    def get_bot_extras(name):
        return ""


async def chatgpt_typing(update, context, text):
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(0.3)
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_to_message_id=update.message.message_id,
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text
    lower_text = text.lower()

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    REAL_DATE = now.strftime("%d %B %Y")
    REAL_DAY = now.strftime("%A")

    if "date" in lower_text:
        await update.message.reply_text(
            f"📅 Aaj ki date hai {REAL_DATE}\n📆 Aaj {REAL_DAY} hai 😊"
        )
        return

    if is_bot_banned(user.id):
        return

    if update.effective_chat.type != "private":
        mentioned = f"@{BOT_USERNAME.lower()}" in lower_text
        nickname_called = any(nick in lower_text for nick in BOT_NICKNAMES)
        replied_to_bot = (
            update.message.reply_to_message
            and update.message.reply_to_message.from_user
            and update.message.reply_to_message.from_user.is_bot
        )
        if not mentioned and not nickname_called and not replied_to_bot:
            return

    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "last_seen": time.time(),
        }},
        upsert=True,
    )

    if "joke" in lower_text or "funny" in lower_text:
        system = "Tell me a Hinglish joke with emojis."
    elif "shayari" in lower_text or "love" in lower_text or "sad" in lower_text:
        system = (
            "Write a beautiful 8 to 10 line Hindi shayari, "
            "deep emotional, poetic, with emojis."
        )
    else:
        system = "Reply shortly in Hinglish with emojis."

    system += f"\n\n👤 User Info:\nName: {user.first_name}"
    system += get_bot_extras(user.first_name)

    user_memory = get_memory(user.id)
    if user_memory:
        system += "\n\n🧠 SAVED MEMORY:\n"
        for key, value in user_memory.items():
            system += f"- {key}: {value}\n"

    system += "\n(Instructions: User ke naam aur memory ka use karke friendly reply karo)"
    system += "\n\nImportant: Har reply me 2-4 relevant emojis zaroor use karo. Friendly aur expressive raho."

    reply = safe_ai([
        {"role": "system", "content": system},
        {"role": "user", "content": text},
    ])

    if "dikkat aa rahi hai" in reply or "AI busy" in reply or "try karo" in reply:
        reply = get_fallback_reply(user.id, text, user.first_name or "Friend")

    MAX_LEN = 4000
    if len(reply) > MAX_LEN:
        reply = reply[:MAX_LEN]

    name = user.first_name or "Friend"
    final_reply = f"*{name}*,\n{reply.strip()}"

    await chatgpt_typing(update, context, final_reply)

    # Sticker logic
    try:
        sticker_to_send = None
        lower = text.lower()
        if any(w in lower for w in ["love", "pyar", "miss", "dil"]):
            sticker_to_send = STICKERS.get("love")
        elif any(w in lower for w in ["haha", "lol", "haso", "funny", "joke"]):
            sticker_to_send = STICKERS.get("laugh")
        elif any(w in lower for w in ["cool", "mast", "fire", "op"]):
            sticker_to_send = STICKERS.get("cool")
        elif any(w in lower for w in ["sad", "dukhi", "rona", "cry"]):
            sticker_to_send = STICKERS.get("sad")
        elif any(w in lower for w in ["hi", "hello", "hey", "namaste"]):
            sticker_to_send = STICKERS.get("hi")
        elif any(w in lower for w in ["kiss", "chumma", "muah"]):
            sticker_to_send = STICKERS.get("kiss")

        if sticker_to_send:
            await context.bot.send_sticker(
                chat_id=update.effective_chat.id,
                sticker=sticker_to_send,
            )
    except Exception as e:
        print("Sticker error:", e)

    chat_logs.insert_one({
        "user_id": user.id,
        "text": final_reply,
        "time": time.time(),
    })


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
