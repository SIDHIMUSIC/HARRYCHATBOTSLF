import requests
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from config import OWNER_ID
from helpers.clones import (
    save_clone, get_user_clones, get_all_clones,
    delete_clone, get_clone, get_clone_by_token
)
from helpers.decorators import is_owner

WAITING_TOKEN = 1


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Agar command ke saath token diya hai
    if context.args:
        token = context.args[0].strip()
        return await process_token(update, context, token)

    # Agar sirf /clone likha hai
    await update.message.reply_text(
        "🤖 **Clone Your Bot**\n\n"
        "Apna Bot Token bhejo (@BotFather se milta hai)\n\n"
        "Example:\n`123456789:AAHxxxx...`\n\n"
        "Ya direct aise bhi bhej sakte ho:\n"
        "`/clone 123456789:AAHxxxx...`\n\n"
        "Cancel ke liye /cancel likho.",
        parse_mode="Markdown"
    )
    return WAITING_TOKEN


async def clone_receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    return await process_token(update, context, token)


async def process_token(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str):
    user = update.effective_user

    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = r.json()

        if not data.get("ok"):
            await update.message.reply_text("❌ Invalid Token. Sahi token bhejo.")
            return ConversationHandler.END

        bot_info = data["result"]
        bot_id = bot_info["id"]
        bot_username = bot_info.get("username", "Unknown")
        bot_name = bot_info.get("first_name", "Unknown")

        if get_clone_by_token(token):
            await update.message.reply_text("⚠️ Yeh token pehle se cloned hai.")
            return ConversationHandler.END

        save_clone(user.id, token, bot_username, bot_id, bot_name)

        await update.message.reply_text(
            f"✅ **Bot Cloned Successfully!**\n\n"
            f"🤖 Name: {bot_name}\n"
            f"🔗 @{bot_username}\n"
            f"🆔 `{bot_id}`\n\n"
            f"Owner ko notify kar diya gaya hai.",
            parse_mode="Markdown"
        )

        # Notify Owner
        try:
            await context.bot.send_message(
                OWNER_ID,
                f"🆕 **New Clone**\n\n"
                f"👤 [{user.first_name}](tg://user?id={user.id})\n"
                f"🆔 `{user.id}`\n"
                f"🤖 @{bot_username}\n"
                f"📛 {bot_name}",
                parse_mode="Markdown"
            )
        except:
            pass

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

    return ConversationHandler.END


async def cancel_clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Clone cancel ho gaya.")
    return ConversationHandler.END


async def my_clones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clones_list = get_user_clones(update.effective_user.id)

    if not clones_list:
        return await update.message.reply_text("Aapka koi cloned bot nahi hai.")

    text = "🤖 **Aapke Cloned Bots:**\n\n"
    for i, c in enumerate(clones_list, 1):
        text += f"{i}. @{c.get('bot_username')} — `{c.get('bot_id')}`\n"

    text += "\nDelete karne ke liye:\n`/delclone bot_id`"
    await update.message.reply_text(text, parse_mode="Markdown")


async def all_clones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Sirf Main Owner use kar sakta hai.")

    clones_list = get_all_clones()
    if not clones_list:
        return await update.message.reply_text("Koi clone nahi hai.")

    text = f"🤖 **Total Clones: {len(clones_list)}**\n\n"
    for i, c in enumerate(clones_list, 1):
        text += (
            f"{i}. @{c.get('bot_username')}\n"
            f"   👤 Owner: `{c.get('owner_id')}`\n"
            f"   🆔 `{c.get('bot_id')}`\n\n"
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def del_clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: `/delclone bot_id`", parse_mode="Markdown")

    try:
        bot_id = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Invalid bot_id")

    clone = get_clone(bot_id)
    if not clone:
        return await update.message.reply_text("❌ Clone nahi mila.")

    user_id = update.effective_user.id

    if user_id != OWNER_ID and clone.get("owner_id") != user_id:
        return await update.message.reply_text("❌ Aap is clone ko delete nahi kar sakte.")

    delete_clone(bot_id)
    await update.message.reply_text(f"✅ Clone `{bot_id}` delete ho gaya.", parse_mode="Markdown")


def register(app):
    conv = ConversationHandler(
        entry_points=[CommandHandler("clone", clone_command)],
        states={
            WAITING_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, clone_receive_token)]
        },
        fallbacks=[CommandHandler("cancel", cancel_clone)],
    )
    app.add_handler(conv, group=0)
    app.add_handler(CommandHandler("myclones", my_clones))
    app.add_handler(CommandHandler("clones", all_clones))
    app.add_handler(CommandHandler("delclone", del_clone))
