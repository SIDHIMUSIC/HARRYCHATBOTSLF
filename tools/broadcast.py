"""
/broadcast  — Advanced broadcast (users + tgusersdb)
/bcstats    — Stats
Owner only | Background mode (Heroku safe)
"""

import asyncio
from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID, SUPPORT_CHANNEL, MONGO_URI
from helpers.database import users
from pymongo import MongoClient

SLEEP_PER_MSG = 0.05
PROGRESS_EVERY = 40


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def get_all_user_ids():
    ids = set()

    # Native users
    try:
        for u in users.find({}, {"user_id": 1}):
            if "user_id" in u:
                ids.add(u["user_id"])
    except Exception:
        pass

    # Migrated tgusersdb
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

    unique = len(get_all_user_ids())

    text = (
        f"📊 <b>BROADCAST STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Native users: <code>{native}</code>\n"
        f"📥 Migrated (tgusersdb): <code>{migrated}</code>\n"
        f"🔀 Unique total: <code>{unique}</code>\n\n"
        f"📌 <code>/broadcast your message</code>\n"
        f"📌 Reply karke bhi <code>/broadcast</code>"
    )
    await status.edit_text(text, parse_mode="HTML")


async def _run_broadcast(context, status_msg, all_ids, mode, text_msg=None, target_msg=None):
    """Background me chalta hai — bot hang nahi hota"""
    total = len(all_ids)
    sent = failed = 0

    for i, uid in enumerate(all_ids, 1):
        try:
            if mode == "text":
                await context.bot.send_message(chat_id=uid, text=text_msg)
            else:
                await target_msg.copy(chat_id=uid)
            sent += 1
        except Exception:
            failed += 1

        if i % PROGRESS_EVERY == 0 or i == total:
            try:
                percent = round((i / total) * 100, 1)
                filled = int(10 * i / total)
                bar = "█" * filled + "░" * (10 - filled)

                await status_msg.edit_text(
                    f"📤 <b>Broadcasting (background)</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{bar} {percent}%\n\n"
                    f"✅ Sent: <code>{sent}</code>\n"
                    f"❌ Failed: <code>{failed}</code>\n"
                    f"📊 {i}/{total}",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        await asyncio.sleep(SLEEP_PER_MSG)

    # Final
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Support", url=SUPPORT_CHANNEL)]
        ])
        await status_msg.edit_text(
            f"✅ <b>Broadcast Complete</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"📨 Sent: <code>{sent}</code>\n"
            f"❌ Failed: <code>{failed}</code>\n"
            f"👥 Total: <code>{total}</code>\n"
            f"🎯 Success: <code>{round((sent/total)*100, 1) if total else 0}%</code>",
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception:
        pass


async def broadcast(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only")

    # Input check
    if update.message.reply_to_message:
        mode = "copy"
        target_msg = update.message.reply_to_message
        text_msg = None
    elif context.args:
        mode = "text"
        text_msg = " ".join(context.args)
        target_msg = None
    else:
        return await update.message.reply_text(
            "❌ <b>Use:</b>\n\n"
            "1️⃣ <code>/broadcast Hello everyone</code>\n"
            "2️⃣ Message pe reply karke <code>/broadcast</code>\n\n"
            "Stats: <code>/bcstats</code>",
            parse_mode="HTML"
        )

    status = await update.message.reply_text("🔄 Users collect kar raha hu...")

    # Heavy work thread me
    all_ids = await asyncio.to_thread(get_all_user_ids)
    total = len(all_ids)

    if total == 0:
        return await status.edit_text("❌ Koi user nahi mila")

    await status.edit_text(
        f"📤 <b>Broadcast started in background</b>\n"
        f"👥 Users: <code>{total}</code>\n"
        f"⏳ Bot on rahega, wait karo...",
        parse_mode="HTML"
    )

    # Background task — handler turant free
    context.application.create_task(
        _run_broadcast(context, status, all_ids, mode, text_msg, target_msg)
    )


def register(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("bc", broadcast))
    app.add_handler(CommandHandler("bcstats", bcstats))
