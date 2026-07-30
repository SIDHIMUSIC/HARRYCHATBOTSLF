from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from helpers.decorators import is_owner

HELP_HOME = (
    "📚 <b>HELP CENTER</b>\n\n"
    "Select a category below."
)

HELP_TEXT = (
    "🤖 <b>BOT FULL FUNCTION LIST</b>\n"
    "━━━━━━━━━━━━━━━━━━\n\n"
    "<b>Basic Commands</b>\n"
    "/start – Bot start\n"
    "/help – All functions\n"
    "/id – User & Chat ID\n"
    "/language – Hindi / English\n\n"
    "<b>AI Image</b>\n"
    "/image &lt;prompt&gt; – AI Image\n\n"
    "<b>Auto Replies</b>\n"
    "• joke / funny → Joke\n"
    "• shayari / love / sad → Shayari\n"
    "• GM / GN → Auto Reply\n\n"
    "<b>Admin</b>\n"
    "/ban  /unban\n\n"
    "<b>👑 Owner Commands</b>\n"
    "/save /mycodes /suggest /commit\n"
    "/botban /botunban /stats /broadcast\n"
)


async def help_cmd(update, context):
    buttons = [
        [
            InlineKeyboardButton("📌 Basic", callback_data="help_basic"),
            InlineKeyboardButton("🖼 AI Image", callback_data="help_image"),
        ],
        [
            InlineKeyboardButton("🤖 Auto", callback_data="help_auto"),
            InlineKeyboardButton("🛡 Admin", callback_data="help_admin"),
        ],
    ]
    if is_owner(update.effective_user.id):
        buttons.append([InlineKeyboardButton("👑 Owner", callback_data="help_owner")])
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="help_close")])
    keyboard = InlineKeyboardMarkup(buttons)

    target = update.callback_query.message if update.callback_query else update.message
    await target.reply_text(
        HELP_TEXT, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True
    )


async def help_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help_home":
        text = HELP_HOME
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📌 Basic", callback_data="help_basic"),
                InlineKeyboardButton("🖼 AI Image", callback_data="help_image"),
            ],
            [
                InlineKeyboardButton("🤖 Auto", callback_data="help_auto"),
                InlineKeyboardButton("🛡 Admin", callback_data="help_admin"),
            ],
            [InlineKeyboardButton("👑 Owner", callback_data="help_owner")],
            [
                InlineKeyboardButton("🏠 Home", callback_data="home"),
                InlineKeyboardButton("❌ Close", callback_data="help_close"),
            ],
        ])
    elif data == "help_basic":
        text = "<b>📌 BASIC COMMANDS</b>\n\n/start\n/help\n/id\n/language"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅ Back", callback_data="help_home"),
            InlineKeyboardButton("❌ Close", callback_data="help_close"),
        ]])
    elif data == "help_image":
        text = "<b>🖼 AI IMAGE</b>\n\n/image prompt"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅ Back", callback_data="help_home"),
            InlineKeyboardButton("❌ Close", callback_data="help_close"),
        ]])
    elif data == "help_auto":
        text = "<b>🤖 AUTO FEATURES</b>\n\n• Joke\n• Shayari\n• Good Morning\n• Memory\n• Auto Reply"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅ Back", callback_data="help_home"),
            InlineKeyboardButton("❌ Close", callback_data="help_close"),
        ]])
    elif data == "help_admin":
        text = "<b>🛡 ADMIN</b>\n\n/ban\n/unban\n/addbadword\n/removebadword"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅ Back", callback_data="help_home"),
            InlineKeyboardButton("❌ Close", callback_data="help_close"),
        ]])
    elif data == "help_owner":
        if not is_owner(query.from_user.id):
            return await query.answer("Owner Only", show_alert=True)
        text = (
            "<b>👑 OWNER COMMANDS</b>\n\n"
            "/save /mycodes /delcode /clearcodes\n"
            "/suggest /commit /rollback\n"
            "/broadcast /stats /botban /botunban"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅ Back", callback_data="help_home"),
            InlineKeyboardButton("❌ Close", callback_data="help_close"),
        ]])
    elif data == "help_close":
        await query.message.delete()
        return
    else:
        return

    try:
        await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        await query.message.reply_text(
            text, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True
        )


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
