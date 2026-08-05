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


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.business_message or update.message
    if not message or not message.text:
        return

    print("🔥 MESSAGE RECEIVED:", message.text, flush=True)

    user = message.from_user
    text = message.text
    lower_text = text.lower()

    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    REAL_DATE = now.strftime("%d %B %Y")
    REAL_DAY = now.strftime("%A")

    if "date" in lower_text:
        await send_reply(context, message, f"📅 Aaj ki date hai {REAL_DATE}\n📆 Aaj {REAL_DAY} hai 😊")
        return

    if is_bot_banned(user.id):
        return

    if message.chat.type != "private":
        mentioned = f"@{BOT_USERNAME.lower()}" in lower_text
        nickname_called = any(nick in lower_text for nick in BOT_NICKNAMES)
        replied_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.is_bot
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

    if len(reply) > 4000:
        reply = reply[:4000]

    name = user.first_name or "Friend"
    final_reply = f"*{name}*,\n{reply.strip()}"

    try:
        await context.bot.send_chat_action(message.chat.id, "typing")
        await asyncio.sleep(0.4)
    except:
        pass

    await send_reply(context, message, final_reply)

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
                chat_id=message.chat.id,
                sticker=sticker_to_send,
                business_connection_id=getattr(message, "business_connection_id", None)
            )
    except Exception as e:
        print("Sticker error:", e, flush=True)

    chat_logs.insert_one({
        "user_id": user.id,
        "text": final_reply,
        "time": time.time(),
    })


async def send_reply(context, message, text):
    try:
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode="Markdown",
            business_connection_id=getattr(message, "business_connection_id", None)
        )
        print("✅ Reply sent successfully", flush=True)
    except Exception as e:
        print("❌ Reply failed:", e, flush=True)


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, chat))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE & filters.TEXT, chat))
