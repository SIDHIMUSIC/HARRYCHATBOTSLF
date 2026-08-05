import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import OWNER_ID
from helpers import safe_ai, users, chat_logs

# ================= CONFIG =================
BUSINESS_GROUP_ID = -1004294248635
OWNER_USERNAME = "SANATANI_BACCHA"


async def business_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.business_message
    if not message:
        return

    user = message.from_user
    text = (message.text or message.caption or "").strip()
    lower_text = text.lower()
    has_photo = bool(message.photo)
    has_document = bool(message.document)

    print(f"📩 Business from {user.first_name}: {text or '[Media]'}", flush=True)

    # Save user
    try:
        users.update_one(
            {"user_id": user.id},
            {"$set": {
                "first_name": user.first_name,
                "username": user.username,
                "last_seen": time.time(),
            }},
            upsert=True,
        )
    except Exception as e:
        print("DB Error:", e, flush=True)

    # ========== FIRST MESSAGE ==========
    is_first = not chat_logs.find_one({"user_id": user.id, "type": "business"})

    if is_first or lower_text in ["hi", "hello", "hey", "hii", "namaste", "hy", "hye"]:
        intro = (
            f"Good day {user.first_name},\n\n"
            f"Harry Sir is currently busy with some work 💤\n\n"
            f"I am his personal assistant. Please tell me how I can help you."
        )
        await send_reply(context, message, intro)
        return

    # ========== REPLY LOGIC ==========
    is_important = has_photo or has_document or any(w in lower_text for w in [
        "promotion", "promo", "slot", "edit", "name", "photo", "poster",
        "work", "kaam", "payment", "price", "rate", "link", "http"
    ])

    if has_photo or "edit" in lower_text:
        final_reply = (
            f"Thank you {user.first_name}.\n\n"
            f"I have received your editing request.\n"
            f"I will inform  Sir shortly."
        )
    elif any(w in lower_text for w in ["promotion", "promo", "slot", "price"]):
        final_reply = (
            f"Thank you for your interest in promotion.\n\n"
            f"I will check available slots with Harry Sir and update you soon."
        )
    elif text:
        try:
            system = f"""You are professional personal assistant of Boss.
Reply in clean formal Hinglish.
Keep it short (2-3 lines).
Be polite.
User name: {user.first_name}"""
            reply = safe_ai([
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ])
            final_reply = reply.strip()[:2000]
        except:
            final_reply = "Thank you for your message. I will inform  Sir."
    else:
        final_reply = "Thank you. I have received your message."

    if is_important:
        final_reply += "\n\n✅  Sir has been informed."

    await send_reply(context, message, final_reply)

    # ========== FORWARD TO GROUP ==========
    if is_important and BUSINESS_GROUP_ID:
        try:
            safe_name = "".join(c for c in (user.first_name or "User") if c.isalnum() or c.isspace())[:30] or "User"

            caption = (
                f"🔔 New Work Request\n\n"
                f"From: {safe_name}\n"
                f"ID: {user.id}\n"
                f"Message: {text or 'Media received'}\n\n"
                f"@{OWNER_USERNAME}"
            )

            if has_photo:
                await context.bot.send_photo(
                    chat_id=BUSINESS_GROUP_ID,
                    photo=message.photo[-1].file_id,
                    caption=caption
                )
            elif has_document:
                await context.bot.send_document(
                    chat_id=BUSINESS_GROUP_ID,
                    document=message.document.file_id,
                    caption=caption
                )
            else:
                await context.bot.send_message(
                    chat_id=BUSINESS_GROUP_ID,
                    text=caption
                )
            print("✅ Sent to group", flush=True)
        except Exception as e:
            print("❌ Group error:", e, flush=True)

    # Log
    try:
        chat_logs.insert_one({
            "user_id": user.id,
            "text": final_reply,
            "type": "business",
            "time": time.time(),
        })
    except:
        pass


async def send_reply(context, message, text):
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
