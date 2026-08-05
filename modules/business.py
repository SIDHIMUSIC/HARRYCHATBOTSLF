import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import OWNER_ID
from helpers import safe_ai, users, chat_logs


async def business_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.business_message
    if not message or not message.text:
        return

    user = message.from_user
    text = message.text.strip()
    lower_text = text.lower()

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

    # ================= PROFESSIONAL SYSTEM PROMPT =================
    system = f"""You are a highly professional executive assistant working for a reputed organization.

Your communication style:
- Extremely professional, polite and clear
- Use clean Hinglish (formal tone)
- Keep replies short and precise (maximum 3-4 lines)
- No casual language, no jokes, no unnecessary emojis
- Sound like a senior executive assistant of a large company

Guidelines:
- If the user talks about work, promotion, meeting, project, payment, investigation or any business matter → reply with high professionalism.
- If you need more details, ask politely and clearly.
- If you don't have exact information, say: "I will check this and update you shortly."
- Never sound friendly in a casual way.
- Never use words like "yaar", "bhai", "mast", "op" etc.

User's name: {user.first_name}
"""

    reply = safe_ai([
        {"role": "system", "content": system},
        {"role": "user", "content": text},
    ])

    if len(reply) > 3500:
        reply = reply[:3500]

    final_reply = reply.strip()

    # Send reply
    try:
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=final_reply,
            business_connection_id=message.business_connection_id
        )
    except Exception as e:
        print("Business reply error:", e)

    # ================= OWNER NOTIFICATION =================
    important_keywords = [
        "promotion", "promo", "slot", "meeting", "kaam", "work",
        "payment", "paisa", "investigation", "enquiry", "business",
        "deal", "project", "client", "urgent", "important", "collab"
    ]

    if any(word in lower_text for word in important_keywords):
        try:
            notify = (
                f"🔔 *Business Message Alert*\n\n"
                f"👤 From: {user.first_name} (`{user.id}`)\n"
                f"💬 Message:\n{text}\n\n"
                f"✅ Bot ne professional reply de diya hai."
            )
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=notify,
                parse_mode="Markdown"
            )
        except Exception as e:
            print("Owner notify error:", e)

    # Log
    chat_logs.insert_one({
        "user_id": user.id,
        "text": final_reply,
        "type": "business",
        "time": time.time(),
    })


def register(app):
    app.add_handler(MessageHandler(
        filters.UpdateType.BUSINESS_MESSAGE & filters.TEXT,
        business_chat
    ))
