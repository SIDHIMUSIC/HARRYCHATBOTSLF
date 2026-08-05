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
    has_link = "http" in lower_text or "t.me/" in lower_text

    print(f"📩 Business from {user.first_name}: {text or '[Media]'}", flush=True)

    # ========== USER DATA ==========
    user_data = users.find_one({"user_id": user.id}) or {}
    mode = user_data.get("biz_mode", "business")          # business / chatting
    lang = user_data.get("biz_lang", "hinglish")           # hinglish / hindi

    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "last_seen": time.time(),
        }},
        upsert=True,
    )

    # ========== MODE / LANGUAGE COMMANDS ==========
    if lower_text in ["mode", "mood", "/mode"]:
        await send_business_reply(context, message,
            "Please choose mode:\n\n"
            "1️⃣ Business Mode (Professional)\n"
            "2️⃣ Chatting Mode (Friendly)\n\n"
            "Reply with: `business` or `chatting`"
        )
        return

    if lower_text in ["business", "biz"]:
        users.update_one({"user_id": user.id}, {"$set": {"biz_mode": "business"}})
        await send_business_reply(context, message, "✅ Switched to *Business Mode* (Professional)")
        return

    if lower_text in ["chatting", "chat", "friendly"]:
        users.update_one({"user_id": user.id}, {"$set": {"biz_mode": "chatting"}})
        await send_business_reply(context, message, "✅ Switched to *Chatting Mode* (Friendly)")
        return

    if lower_text in ["language", "lang", "/lang"]:
        await send_business_reply(context, message,
            "Please choose language:\n\n"
            "1️⃣ Hinglish\n"
            "2️⃣ Hindi\n\n"
            "Reply with: `hinglish` or `hindi`"
        )
        return

    if lower_text == "hindi":
        users.update_one({"user_id": user.id}, {"$set": {"biz_lang": "hindi"}})
        await send_business_reply(context, message, "✅ भाषा हिंदी में बदल दी गई है।")
        return

    if lower_text == "hinglish":
        users.update_one({"user_id": user.id}, {"$set": {"biz_lang": "hinglish"}})
        await send_business_reply(context, message, "✅ Language changed to Hinglish.")
        return

    # ========== FIRST MESSAGE ==========
    is_first = not chat_logs.find_one({"user_id": user.id, "type": "business"})

    if is_first or lower_text in ["hi", "hello", "hey", "hii", "namaste"]:
        if lang == "hindi":
            intro = (
                f"नमस्ते {user.first_name} जी,\n\n"
                f"Harry Sir अभी कुछ महत्वपूर्ण काम में व्यस्त हैं 💤\n\n"
                f"मैं उनका पर्सनल असिस्टेंट हूँ। कृपया बताएं मैं आपकी कैसे मदद कर सकता हूँ?\n\n"
                f"(Mode बदलने के लिए `mode` लिखें)"
            )
        else:
            intro = (
                f"Good day {user.first_name},\n\n"
                f"Harry Sir is currently busy with some work 💤\n\n"
                f"I am his personal assistant. How can I help you?\n\n"
                f"(Type `mode` to change mode)"
            )
        await send_business_reply(context, message, intro)
        return

    # ========== GENERATE REPLY ==========
    is_important = has_photo or has_document or has_link or any(w in lower_text for w in [
        "promotion", "promo", "slot", "edit", "name", "photo", "poster",
        "thumbnail", "work", "kaam", "payment", "urgent", "important", "price", "rate"
    ])

    if mode == "chatting":
        # Friendly mode
        system = f"""You are a friendly assistant of Harry Sir.
Reply in {'pure Hindi' if lang == 'hindi' else 'Hinglish'}.
Be warm and helpful.
Keep reply short.
User name: {user.first_name}"""
    else:
        # Business mode
        system = f"""You are a highly professional personal assistant of Harry Sir.
Reply in {'pure Hindi' if lang == 'hindi' else 'clean formal Hinglish'}.
Be extremely professional and polite.
Keep reply short (2-3 lines).
No casual words.
User name: {user.first_name}"""

    try:
        if text:
            reply = safe_ai([
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ])
            final_reply = reply.strip()[:2500]
        else:
            final_reply = "Thank you. I have received your message." if lang != "hindi" else "धन्यवाद। आपका संदेश प्राप्त हो गया है।"
    except:
        final_reply = "Thank you. I will inform Harry Sir." if lang != "hindi" else "धन्यवाद। मैं Harry Sir को सूचित कर दूंगा।"

    # Important baat pe last mein add karo
    if is_important:
        if lang == "hindi":
            final_reply += "\n\n✅ Harry Sir को सूचित कर दिया गया है।"
        else:
            final_reply += "\n\n✅ Harry Sir has been informed about this."

    await send_business_reply(context, message, final_reply)

    # ========== FORWARD TO GROUP ==========
    if is_important and BUSINESS_GROUP_ID:
        try:
            safe_name = "".join(c for c in (user.first_name or "User") if c.isalnum() or c.isspace()) or "User"
            caption = (
                f"🔔 New Work Request\n\n"
                f"👤 From: {safe_name}\n"
                f"🆔 {user.id}\n"
                f"💬 {text or 'Media / Link received'}\n\n"
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
