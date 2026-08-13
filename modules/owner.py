from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from config import SUPPORT_CHANNEL
from helpers.decorators import is_owner
from helpers.database import users, bot_bans, chat_logs
import time


# ================= PREMIUM EMOJI =================
PE = {
    "crown": "6026292029179301727",
    "star": "6026162407066309019",
    "fire": "6321353301707203203",
    "heart": "6267140231632262769",
    "owner": "6147603715462271535",
    "support": "6145175650190759830",
}


def pe(name: str, fallback: str = "✨") -> str:
    """Message text ke liye — parse_mode=HTML ke saath."""
    eid = (PE.get(name) or "").strip()
    if not eid or not eid.isdigit():
        return fallback
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'


def pe_works(name: str) -> bool:
    eid = (PE.get(name) or "").strip()
    return bool(eid and eid.isdigit())


def make_btn(text: str, url: str = None, callback_data: str = None, pe_name: str = None):
    """
    Button banata hai.
    - text: plain text only (HTML mat daalo)
    - pe_name: PE dict ka key → icon_custom_emoji_id try
    """
    kwargs = {"text": text}
    if url:
        kwargs["url"] = url
    if callback_data:
        kwargs["callback_data"] = callback_data

    if pe_name and pe_works(pe_name):
        kwargs["icon_custom_emoji_id"] = PE[pe_name].strip()

    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        # Purani library me icon_custom_emoji_id nahi → plain button
        kwargs.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(**kwargs)


async def owner_info(update, context):
    owner_name = "𓆩◕🇭𝐀𝐑𝐑𝐘◕𓆪 =‌𐏓 ⤨⃝🇮🇳™"
    owner_username = "SANATANI_BACHA"

    crown = pe("crown", "👑")
    star = pe("star", "✨")
    fire = pe("fire", "🚀")
    heart = pe("heart", "💎")

    text = (
        f"<b>{crown} ʙᴏᴛ ᴏᴡɴᴇʀ ᴘʀᴏғɪʟᴇ{star}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{star} ᴛʜɪs ɪɴᴛᴇʟʟɪɢᴇɴᴛ ᴀɪ ʙᴏᴛ ɪs ᴘʀᴏᴜᴅʟʏ ᴄʀᴀғᴛᴇᴅ,\n"
        "ᴏᴡɴᴇᴅ ᴀɴᴅ ᴍᴀɴᴀɢᴇᴅ ʙʏ\n\n"
        f"👤 <b><a href='https://t.me/{owner_username}'>{owner_name}</a></b>\n"
        f"🔗 @{owner_username}\n\n"
        f"{fire} ᴀ ᴘᴀssɪᴏɴᴀᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ & ᴛᴇᴄʜ ᴇɴᴛʜᴜsɪᴀsᴛ\n"
        "• sᴍᴀʀᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ 🤖\n"
        "• sᴇᴄᴜʀᴇ sʏsᴛᴇᴍs 🔐\n"
        f"• sᴍᴏᴏᴛʜ ᴜsᴇʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ {heart}\n\n"
        "💡 ᴠɪsɪᴏɴ\n"
        "ᴄʀᴇᴀᴛɪɴɢ ᴘᴏᴡᴇʀғᴜʟ, ʀᴇʟɪᴀʙʟᴇ ᴀɴᴅ\n"
        "ᴜsᴇʀ-ғʀɪᴇɴᴅʟʏ ᴀɪ ʙᴏᴛs\n"
        "ᴛʜᴀᴛ ᴍᴀᴋᴇ ᴛᴇʟᴇɢʀᴀᴍ sᴍᴀʀᴛᴇʀ ⚡\n\n"
        "👇 ᴄᴏɴɴᴇᴄᴛ & sᴛᴀʏ ᴜᴘᴅᴀᴛᴇᴅ"
    )

    keyboard = InlineKeyboardMarkup([
        [make_btn("❍ 𝐎ᴡɴᴇʀ ❍", url=f"https://t.me/{owner_username}", pe_name="owner")],
        [make_btn("❍ Support Channel ❍", url=SUPPORT_CHANNEL, pe_name="support")],
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


async def id_cmd(update, context):
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"👤 **Your ID:** `{user.id}`\n"
        f"💬 **Chat ID:** `{chat.id}`\n"
        f"📍 **Chat Type:** `{chat.type}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def pe_status(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Owner only")

    lines = ["🔍 <b>Premium Emoji Status</b>\n"]
    for name, eid in PE.items():
        ok = pe_works(name)
        status = "✅ READY" if ok else "❌ OFF (normal emoji)"
        show = eid if eid else "—"
        lines.append(f"• <b>{name}</b>: {status}\n  <code>{show}</code>")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


def register(app):
    app.add_handler(CommandHandler("owner", owner_info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("pestatus", pe_status))
