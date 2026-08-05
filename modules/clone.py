import requests
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID
from helpers.clones import (
    save_clone, get_user_clones, get_all_clones,
    delete_clone, get_clone, get_clone_by_token
)
from helpers.decorators import is_owner


async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        print(f"Clone command by {user.id}", flush=True)

        if not context.args:
            await update.message.reply_text(
                "🤖 **Clone Your Bot**\n\n"
                "Usage:\n"
                "`/clone your_bot_token`\n\n"
                "Example:\n"
                "`/clone 123456789:AAHxxxx...`",
                parse_mode="Markdown"
            )
            return

        token = context.args[0].strip()
        print(f"Token received: {token[:15]}...", flush=True)

        # Verify token
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = r.json()
        print(f"Telegram response: {data}", flush=True)

        if not data.get("ok"):
            await update.message.reply_text("❌ Invalid Token. Sahi token bhejo.")
            return

        bot_info = data["result"]
        bot_id = bot_info["id"]
        bot_username = bot_info.get("username", "Unknown")
        bot_name = bot_info.get("first_name", "Unknown")

        # Already exists?
        if get_clone_by_token(token):
            await update.message.reply_text("⚠️ Yeh token pehle se cloned hai.")
            return

        # Save
        save_clone(user.id, token, bot_username, bot_id, bot_name)
        print("Clone saved successfully", flush=True)

        await update.message.reply_text(
            f"✅ **Bot Cloned Successfully!**\n\n"
            f"🤖 Name: {bot_name}\n"
            f"🔗 @{bot_username}\n"
            f"🆔 `{bot_id}`",
            parse_mode="Markdown"
        )

        # Notify owner
        try:
            await context.bot.send_message(
                OWNER_ID,
                f"🆕 New Clone\n\n"
                f"User: {user.first_name} (`{user.id}`)\n"
                f"Bot: @{bot_username}"
            )
        except Exception as e:
            print("Owner notify error:", e, flush=True)

    except Exception as e:
        print(f"Clone error: {e}", flush=True)
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


async def my_clones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clones_list = get_user_clones(update.effective_user.id)
    if not clones_list:
        return await update.message.reply_text("Aapka koi cloned bot nahi hai.")

    text = "🤖 **Aapke Cloned Bots:**\n\n"
    for i, c in enumerate(clones_list, 1):
        text += f"{i}. @{c.get('bot_username')} — `{c.get('bot_id')}`\n"
    await update.message.reply_text(text, parse_mode="Markdown")


async def all_clones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Sirf Owner use kar sakta hai.")

    clones_list = get_all_clones()
    if not clones_list:
        return await update.message.reply_text("Koi clone nahi hai.")

    text = f"🤖 **Total Clones: {len(clones_list)}**\n\n"
    for i, c in enumerate(clones_list, 1):
        text += f"{i}. @{c.get('bot_username')} | Owner: `{c.get('owner_id')}`\n"
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
    await update.message.reply_text(f"✅ Clone `{bot_id}` delete ho gaya.")


def register(app):
    app.add_handler(CommandHandler("clone", clone_command))
    app.add_handler(CommandHandler("myclones", my_clones))
    app.add_handler(CommandHandler("clones", all_clones))
    app.add_handler(CommandHandler("delclone", del_clone))
    print("✅ Clone module loaded", flush=True)
