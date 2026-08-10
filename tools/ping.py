"""
/ping — Advanced bot status check
With start image + support channel button
Auto-loaded tool
"""

import time
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler

try:
    from config import START_IMAGES, SUPPORT_CHANNEL
except Exception:
    START_IMAGES = [
        "https://graph.org/file/705cda02e63f4cb0bdb90-ce4d0ddd3a8cf38b5a.jpg",
        "https://graph.org/file/8c5e8ea95b69e682aed19-22090eb6bb17ce7a54.jpg",
        "https://graph.org/file/556615482003de63f32be-58c192c7e65004f9d4.jpg",
        "https://graph.org/file/bb129887cac5752f0f0f5-70aec0f85376516f16.jpg",
    ]
    SUPPORT_CHANNEL = "https://t.me/TG_BIO_STYLE"


async def ping(update, context):
    start = time.time()
    
    # Temporary message
    temp = await update.message.reply_text("🏓 Checking bot status...")
    
    end = time.time()
    ms = round((end - start) * 1000, 2)

    if ms < 100:
        status = "🚀 Ultra Fast"
        bar = "🟩🟩🟩🟩🟩"
    elif ms < 250:
        status = "⚡ Fast"
        bar = "🟩🟩🟩🟩⬜"
    elif ms < 500:
        status = "🙂 Normal"
        bar = "🟩🟩🟩⬜⬜"
    else:
        status = "🐌 Slow"
        bar = "🟩🟩⬜⬜⬜"

    caption = (
        f"🏓 <b>PONG!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"⏱ <b>Ping:</b> <code>{ms} ms</code>\n"
        f"📊 <b>Status:</b> {status}\n"
        f"📶 <b>Speed:</b> {bar}\n\n"
        f"✅ Bot is online & working\n"
        f"🤖 Powered by Harry AI"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Support Channel", url=SUPPORT_CHANNEL)]
    ])

    # Temp message delete karo
    try:
        await temp.delete()
    except Exception:
        pass

    # Ab naya message bhejo (reply force mat karo)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=random.choice(START_IMAGES),
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )


def register(app):
    app.add_handler(CommandHandler("ping", ping))
