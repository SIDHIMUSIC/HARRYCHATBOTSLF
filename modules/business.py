import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import OWNER_ID
from helpers import safe_ai, users, chat_logs

# ================= CONFIG =================
# Yahan apna Group Chat ID daalna (jaise -100xxxxxxxxxx)
BUSINESS_GROUP_ID = -1004294248635   # ← Yahan apna GC ID daalna

# Owner ka username (tag ke liye)
OWNER_USERNAME = "SANATANI_BACCHA"


async def business_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.business_message
    if not message:
        return

    user = message.from_user
    text = message.text.strip() if message.text else ""
    lower_text = text.lower() if text else ""

    # User save
    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "last_seen": time.time(),
        }},
        upsert=True,
    )

    # ================= CHECK IF FIRST MESSAGE =================
    # Agar user pehle kabhi baat nahi kiya toh introduction do
    is_first = not chat_logs.find_one({"user_id": user.id, "type": "business"})

    if is_first or lower_text in ["hi", "hello", "hey", "namaste", "hii"]:
        intro = (
            f"Good day {user.first_name},\n\n"
            f"Harry Sir is currently busy with some important work and resting 💤\n\n"
            f"I am his personal assistant. Please let me know how I can help you."
        )
        try:
            await context.bot.send_message(
                chat_id=message.chat.id,
                text=intro,
                business_connection_id=message.business_connection_id
            )
        except Exception as e:
            print("Intro error:", e)
        return

    # ================= PROFESSIONAL REPLY =================
    system = f"""You are a highly professional personal assistant of Harry Sir.

Rules:
- Always reply in clean and formal Hinglish.
- Be extremely professional and polite.
- Keep reply short (maximum 3 lines).
- No jokes, no casual words like yaar, bhai, mast, op.
- If user asks for promotion, slot, work, editing, or any service → reply professionally and say you will inform Harry Sir.
- Never say you are an AI.

User name: {user.first_name}
"""

    if text:
        reply = safe_ai([
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ])
        final_reply = reply.strip()[:3000]
    else:
        final_reply = "Thank you. I have noted your message and will inform Harry Sir."

    # Send reply to user
    try:
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=final_reply,
            business_connection_id=message.business_connection_id
        )
    except Exception as e:
        print("Business reply error:", e)

    # ================= FORWARD TO GROUP + TAG OWNER =================
    important_keywords = [
        "promotion", "promo", "slot", "edit", "name", "photo", "pic",
        "poster", "thumbnail", "work", "kaam", "meeting", "payment",
        "deal", "project", "urgent", "important", "collab"
    ]

    has_media = bool(message.photo or message.document or message.video)
    is_important = any(word in lower_text for word in important_keywords) or has_media

    if is_important:
        try:
            # Text message to group
            caption = (
                f"🔔 *New Business Request*\n\n"
                f"👤 From: [{user.first_name}](tg://user?id={user.id})\n"
                f"🆔 `{user.id}`\n"
                f"💬 Message: {text or 'Media received'}\n\n"
                f"@{OWNER_USERNAME}"
            )

            if message.photo:
                await context.bot.send_photo(
                    chat_id=BUSINESS_GROUP_ID,
                    photo=message.photo[-1].file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            elif message.document:
                await context.bot.send_document(
                    chat_id=BUSINESS_GROUP_ID,
                    document=message.document.file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    chat_id=BUSINESS_GROUP_ID,
                    text=caption,
                    parse_mode="Markdown"
                )

        except Exception as e:
            print("Group forward error:", e)

    # Log
    chat_logs.insert_one({
        "user_id": user.id,
        "text": final_reply,
        "type": "business",
        "time": time.time(),
    })


def register(app):
    app.add_handler(MessageHandler(
        filters.UpdateType.BUSINESS_MESSAGE,
        business_chat
    ))
