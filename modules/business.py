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
    has_link = "http://" in lower_text or "https://" in lower_text or "t.me/" in lower_text

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
    if any(w in lower_text for w in ["promotion", "promo", "slot", "price", "rate"]) or has_link:
        final_reply = (
            f"Thank you {user.first_name}.\n\n"
            f"I have received your promotion request.\n"
            f"I will check with Harry Sir and update you soon."
        )
    elif has_photo or "edit" in lower_text or "name" in lower_text or "poster" in lower_text:
        final_reply = (
            f"Thank you {user.first_name}.\n\n"
            f"I have received your editing request.\n"
            f"I will inform Harry Sir shortly."
        )
    elif text:
        try:
            system = f"""You are professional personal assistant of Harry Sir.
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
            final_reply = "Thank you for your message. I will inform Harry Sir."
    else:
        final_reply = "Thank you. I have received your message."

    # Important message pe last line add karo
    final_reply += "\n\n✅ Harry Sir has been informed."

    await send_reply(context, message, final_reply)

    # ========== FORWARD TO GROUP ==========
    # Ab almost har message GC mein jayega
    should_forward = has_photo or has_document or has_link or len(text) > 2

    if should_forward and BUSINESS_GROUP_ID:
        try:
            safe_name = "".join(c for c in (user.first_name or "User") if c.isalnum() or c.isspace())[:25] or "User"

            caption = (
                f"🔔 New Message\n\n"
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
