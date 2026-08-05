import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import OWNER_ID
from helpers import safe_ai, users, chat_logs

# ================= CONFIG =================
BUSINESS_GROUP_ID = None          # ← Yahan apna Group ID daalna (jaise -100xxxxxxxxxx)
OWNER_USERNAME = "SANATANI_BACHA"


async def business_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.business_message
    if not message:
        return

    user = message.from_user
    text = message.text.strip() if message.text else ""
    lower_text = text.lower() if text else ""
    has_photo = bool(message.photo)
    has_document = bool(message.document)

    print(f"📩 Business msg from {user.first_name}: {text or '[Media]'}", flush=True)

    # Save user
    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "last_seen": time.time(),
        }},
        upsert=True,
    )

    # ================= FIRST MESSAGE =================
    is_first = not chat_logs.find_one({"user_id": user.id, "type": "business"})

    if is_first or lower_text in ["hi", "hello", "hey", "hii", "namaste", "good morning", "good evening"]:
        intro = (
            f"Good day {user.first_name},\n\n"
            f"Harry Sir is currently occupied with some work and resting 💤\n\n"
            f"I am his personal assistant. Please tell me how I can help you."
        )
        await send_business_reply(context, message, intro)
        return

    # ================= GENERATE REPLY =================
    if has_photo or "edit" in lower_text or "name" in lower_text or "poster" in lower_text:
        final_reply = (
            f"Thank you {user.first_name}.\n\n"
            f"I have received your request for editing. "
            f"I will inform Harry Sir and get back to you shortly."
        )
    elif any(word in lower_text for word in ["promotion", "promo", "slot", "price", "rate"]):
        final_reply = (
            f"Thank you for your interest in promotion.\n\n"
            f"I will check the available slots with Harry Sir and update you soon."
        )
    elif text:
        system = f"""You are the professional personal assistant of Harry Sir.
Reply in clean formal Hinglish.
Keep it short (2-3 lines maximum).
Be polite and professional.
Never use casual words.
User name: {user.first_name}"""
        try:
            reply = safe_ai([
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ])
            final_reply = reply.strip()[:2500]
        except:
            final_reply = "Thank you for your message. I will inform Harry Sir."
    else:
        final_reply = "Thank you. I have noted your message and will inform Harry Sir."

    # Reply to user
    await send_business_reply(context, message, final_reply)

    # ================= FORWARD TO GROUP =================
    important = has_photo or has_document or any(w in lower_text for w in [
        "promotion", "promo", "slot", "edit", "name", "photo", "poster",
        "thumbnail", "work", "kaam", "payment", "urgent", "important"
    ])

    if important and BUSINESS_GROUP_ID:
        try:
            caption = (
                f"🔔 *New Work Request*\n\n"
                f"👤 From: [{user.first_name}](tg://user?id={user.id})\n"
                f"🆔 `{user.id}`\n"
                f"💬 {text or 'Media received'}\n\n"
                f"@{OWNER_USERNAME}"
            )

            if has_photo:
                await context.bot.send_photo(
                    chat_id=BUSINESS_GROUP_ID,
                    photo=message.photo[-1].file_id,
                    caption=caption,
                    parse_mode="Markdown"
                )
            elif has_document:
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
            print("✅ Forwarded to group", flush=True)
        except Exception as e:
            print("❌ Group forward error:", e, flush=True)

    # Log
    chat_logs.insert_one({
        "user_id": user.id,
        "text": final_reply,
        "type": "business",
        "time": time.time(),
    })


async def send_business_reply(context, message, text):
    try:
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            business_connection_id=message.business_connection_id
        )
        print("✅ Reply sent", flush=True)
    except Exception as e:
        print("❌ Reply failed:", e, flush=True)


def register(app):
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, business_chat))
    print("✅ Business handler loaded", flush=True)
