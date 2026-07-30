from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from config import SUPPORT_CHANNEL
from helpers.decorators import is_owner
from helpers.database import users, bot_bans, chat_logs
import time
import asyncio


async def owner_info(update, context):
    owner_name = "𓆩◕🇭𝐀𝐑𝐑𝐘◕𓆪 =‌𐏓 ⤨⃝🇮🇳™"
    owner_username = "SANATANI_BACHA"

    text = (
        "<b>👑 ʙᴏᴛ ᴏᴡɴᴇʀ ᴘʀᴏғɪʟᴇ✨</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "✨ ᴛʜɪs ɪɴᴛᴇʟʟɪɢᴇɴᴛ ᴀɪ ʙᴏᴛ ɪs ᴘʀᴏᴜᴅʟʏ ᴄʀᴀғᴛᴇᴅ,\n"
        "ᴏᴡɴᴇᴅ ᴀɴᴅ ᴍᴀɴᴀɢᴇᴅ ʙʏ\n\n"
        f"👤 <b><a href='https://t.me/{owner_username}'>{owner_name}</a></b>\n"
        f"🔗 @{owner_username}\n\n"
        "🚀 ᴀ ᴘᴀssɪᴏɴᴀᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ & ᴛᴇᴄʜ ᴇɴᴛʜᴜsɪᴀsᴛ\n"
        "• sᴍᴀʀᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ 🤖\n"
        "• sᴇᴄᴜʀᴇ sʏsᴛᴇᴍs 🔐\n"
        "• sᴍᴏᴏᴛʜ ᴜsᴇʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ 💎\n\n"
        "💡 ᴠɪsɪᴏɴ\n"
        "ᴄʀᴇᴀᴛɪɴɢ ᴘᴏᴡᴇʀғᴜʟ, ʀᴇʟɪᴀʙʟᴇ ᴀɴᴅ\n"
        "ᴜsᴇʀ-ғʀɪᴇɴᴅʟʏ ᴀɪ ʙᴏᴛs\n"
        "ᴛʜᴀᴛ ᴍᴀᴋᴇ ᴛᴇʟᴇɢʀᴀᴍ sᴍᴀʀᴛᴇʀ ⚡\n\n"
        "👇 ᴄᴏɴɴᴇᴄᴛ & sᴛᴀʏ ᴜᴘᴅᴀᴛᴇᴅ"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❍ 𝐎ᴡɴᴇʀ ❍", url=f"https://t.me/{owner_username}")],
        [InlineKeyboardButton("❍ Support Channel ❍", url=SUPPORT_CHANNEL)],
    ])

    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def stats(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only command")

    total_users = users.count_documents({})
    total_banned = bot_bans.count_documents({})
    total_groups = len(
        chat_logs.distinct("chat_id", {"chat_type": {"$in": ["group", "supergroup"]}})
    )
    since = time.time() - 86400
    daily_active = len(chat_logs.distinct("user_id", {"time": {"$gte": since}}))

    await update.message.reply_text(
        f"📊 **BOT DASHBOARD**\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"🔥 Daily Active Users: `{daily_active}`\n"
        f"👨‍👩‍👧‍👦 Total Groups: `{total_groups}`\n"
        f"🚫 Bot Banned Users: `{total_banned}`",
        parse_mode="Markdown",
    )


async def broadcast(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only command")
    if not context.args:
        return await update.message.reply_text("❌ Use:\n/broadcast Your message here")

    msg = " ".join(context.args)
    sent = failed = 0
    await update.message.reply_text("📤 Broadcast start ho raha hai...")

    for u in users.find({}, {"user_id": 1}):
        try:
            await context.bot.send_message(chat_id=u["user_id"], text=msg)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast complete\n\n📨 Sent: {sent}\n❌ Failed: {failed}"
    )


async def id_cmd(update, context):
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"👤 **Your ID:** `{user.id}`\n"
        f"💬 **Chat ID:** `{chat.id}`\n"
        f"📍 **Chat Type:** `{chat.type}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


def register(app):
    app.add_handler(CommandHandler("owner", owner_info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("id", id_cmd))
