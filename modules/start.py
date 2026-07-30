import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import START_IMAGES, SUPPORT_CHANNEL
from helpers.decorators import is_owner


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    me = await context.bot.get_me()
    user = update.effective_user

    caption = (
        f"✨ <b>HEY <a href='tg://user?id={user.id}'>{user.first_name}</a></b>\n\n"
        f"❖ <b>WELCOME TO {me.first_name}</b>\n\n"
        "➤ Fast AI Chat\n"
        "➤ AI Image Generator\n"
        "➤ 100+ Stylish Fonts\n"
        "➤ Memory System\n"
        "➤ Group Moderation\n"
        "➤ GitHub Integration\n"
        "➤ Smart Auto Replies\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Choose an option below 👇</b>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤖 Chat", callback_data="menu_chat"),
            InlineKeyboardButton("🖼 AI Image", callback_data="menu_image"),
        ],
        [
            InlineKeyboardButton("🎨 Fonts", callback_data="menu_fonts"),
            InlineKeyboardButton("⚙ Settings", callback_data="menu_settings"),
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="help_home"),
            InlineKeyboardButton("👑 Owner", callback_data="menu_owner"),
        ],
        [
            InlineKeyboardButton("❤️ Support", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("☕ Donate", url="https://t.me/SANATANI_BACHA"),
        ],
    ])

    await update.message.reply_photo(
        photo=random.choice(START_IMAGES),
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def start_from_callback(update, context):
    query = update.callback_query
    me = await context.bot.get_me()
    user = query.from_user

    caption = (
        f"✨ <b>HEY <a href='tg://user?id={user.id}'>{user.first_name}</a></b>\n\n"
        f"❖ <b>WELCOME TO {me.first_name}</b>\n\n"
        "➤ Fast AI Chat\n"
        "➤ AI Image Generator\n"
        "➤ 100+ Stylish Fonts\n"
        "➤ Memory System\n"
        "➤ Group Moderation\n"
        "➤ GitHub Integration\n"
        "➤ Smart Auto Replies\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Choose an option below 👇</b>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤖 Chat", callback_data="menu_chat"),
            InlineKeyboardButton("🖼 AI Image", callback_data="menu_image"),
        ],
        [
            InlineKeyboardButton("🎨 Fonts", callback_data="menu_fonts"),
            InlineKeyboardButton("⚙ Settings", callback_data="menu_settings"),
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="help_home"),
            InlineKeyboardButton("👑 Owner", callback_data="menu_owner"),
        ],
        [
            InlineKeyboardButton("❤️ Support", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("☕ Donate", url="https://t.me/SANATANI_BACHA"),
        ],
    ])

    try:
        await query.edit_message_caption(
            caption=caption, parse_mode="HTML", reply_markup=keyboard
        )
    except Exception:
        await query.message.reply_photo(
            photo=random.choice(START_IMAGES),
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    last_msg_id = context.user_data.get("last_menu_msg")
    if last_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=query.message.chat_id, message_id=last_msg_id
            )
        except Exception:
            pass

    msg = None

    if data == "menu_chat":
        msg = await query.message.reply_text(
            "💬 <b>AI Chat Ready!</b>\n\n"
            "Bas message bhejo, main reply karunga 🤖\n"
            "Group me @botusername ya naam leke call karo.",
            parse_mode="HTML",
        )
    elif data == "menu_image":
        msg = await query.message.reply_text(
            "🖼 <b>AI Image Generator</b>\n\n"
            "Use:\n<code>/image cyberpunk indian boy 4k</code>\n\n"
            "Example:\n<code>/image lord krishna digital art</code>",
            parse_mode="HTML",
        )
    elif data == "menu_fonts":
        msg = await query.message.reply_text(
            "🎨 <b>Stylish Fonts</b>\n\n"
            "Use:\n<code>/font Apna Text Yahan</code>\n\n"
            "Example:\n<code>/font Kaise ho</code>",
            parse_mode="HTML",
        )
    elif data == "menu_settings":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇮🇳 Hindi", callback_data="hi"),
                InlineKeyboardButton("🇬🇧 English", callback_data="en"),
            ],
            [InlineKeyboardButton("🏠 Home", callback_data="home")],
        ])
        msg = await query.message.reply_text(
            "⚙ <b>Settings</b>\n\nLanguage choose karo:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    elif data == "menu_owner":
        from modules.owner import owner_info
        await owner_info(update, context)
        return

    if msg:
        context.user_data["last_menu_msg"] = msg.message_id


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
