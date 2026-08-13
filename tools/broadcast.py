"""
/broadcast  — Advanced broadcast (users + tgusersdb migrated)
/bcstats    — Broadcast related stats
Owner only | Auto-loaded tool
"""

import asyncio
from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID, SUPPORT_CHANNEL
from helpers.database import users
from pymongo import MongoClient
from config import MONGO_URI

# ============ SETTINGS ============
SLEEP_PER_MSG = 0.07          # flood se bachne ke liye
PROGRESS_EVERY = 50           # har 50 pe progress update
# ==================================


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def get_all_user_ids():
    """
    Normal users + migrated tgusersdb dono se unique user_ids nikalta hai
    """
    ids = set()

    # 1. Native users collection
    try:
        for u in users.find({}, {"user_id": 1}):
            if "user_id" in u:
                ids.add(u["user_id"])
    except Exception:
        pass

    # 2. Migrated tgusersdb
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["telegram_bot"]
        if "tgusersdb" in db.list_collection_names():
            for u in db["tgusersdb"].find({}, {"user_id": 1}):
                if "user_id" in u:
                    ids.add(u["user_id"])
        client.close()
    except Exception:
        pass

    return list(ids)


async def bcstats(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only")

    status = await update.message.reply_text("📊 Stats nikal raha hu...")

    try:
        native = users.count_documents({})
    except Exception:
        native = 0

    migrated = 0
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["telegram_bot"]
        if "tgusersdb" in db.list_collection_names():
            migrated = db["tgusersdb"].count_documents({})
        client.close()
    except Exception:
        pass

    all_ids = get_all_user_ids()
    unique = len(all_ids)

    text = (
        f"📊 <b>BROADCAST STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Native users: <code>{native}</code>\n"
        f"📥 Migrated (tgusersdb): <code>{migrated}</code>\n"
        f"🔀 Unique total: <code>{unique}</code>\n\n"
        f"✅ Broadcast in unique users ko jayega\n"
        f"📌 Command: <code>/broadcast your message</code>"
    )
    await status.edit_text(text, parse_mode="HTML")


async def broadcast(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only command")

    # Message nikaalo
    if update.message.reply_to_message:
        # Reply karke bhi broadcast kar sakte ho (text/photo/video)
        target_msg = update.message.reply_to_message
        mode = "copy"
    elif context.args:
        text_msg = " ".join(context.args)
        mode = "text"
    else:
        return await update.message.reply_text(
            "❌ <b>Kaise use kare:</b>\n\n"
            "1️⃣ <code>/broadcast Hello everyone</code>\n"
            "2️⃣ Kisi message pe reply karke <code>/broadcast</code>\n\n"
            "Stats dekhne ke liye: <code>/bcstats</code>",
            parse_mode="HTML"
        )

    # Users collect
    status = await update.message.reply_text("🔄 Users collect kar raha hu...")
    all_ids = get_all_user_ids()
    total = len(all_ids)

    if total == 0:
        return await status.edit_text("❌ Koi user nahi mila database me")

    await status.edit_text(
        f"📤 <b>Broadcast Start</b>\n"
        f"👥 Total unique users: <code>{total}</code>\n"
        f"⏳ Please wait...",
        parse_mode="HTML"
    )

    sent = failed = 0

    for i, uid in enumerate(all_ids, 1):
        try:
            if mode == "text":
                await context.bot.send_message(chat_id=uid, text=text_msg)
            else:
                # reply wala message copy karo
                await target_msg.copy(chat_id=uid)

            sent += 1
        except Exception:
            failed += 1

        # Progress update
        if i % PROGRESS_EVERY == 0 or i == total:
            try:
                percent = round((i / total) * 100, 1)
                bar_len = 10
                filled = int(bar_len * i / total)
                bar = "█" * filled + "░" * (bar_len - filled)

                await status.edit_text(
                    f"📤 <b>Broadcasting...</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{bar} {percent}%\n\n"
                    f"✅ Sent: <code>{sent}</code>\n"
                    f"❌ Failed: <code>{failed}</code>\n"
                    f"📊 Progress: <code>{i}/{total}</code>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        await asyncio.sleep(SLEEP_PER_MSG)

    # Final report
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Support", url=SUPPORT_CHANNEL)]
    ])

    await status.edit_text(
        f"✅ <b>Broadcast Complete</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📨 Successfully Sent: <code>{sent}</code>\n"
        f"❌ Failed / Blocked: <code>{failed}</code>\n"
        f"👥 Total Targeted: <code>{total}</code>\n\n"
        f"🎯 Success Rate: <code>{round((sent/total)*100, 1) if total else 0}%</code>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


def register(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("bc", broadcast))          # short alias
    app.add_handler(CommandHandler("bcstats", bcstats))
