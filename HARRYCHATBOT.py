"""
HARRY CHATBOT — Professional Modular Architecture
Made with ❤️ by Harry (@SANATANI_BACHA)
"""

import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes

from config import TOKEN, OWNER_ID, LOG_GROUP_ID
from utils.auto_loader import load_modules, load_tools


# ================= GLOBAL ERROR HANDLER =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error_text = "".join(
        traceback.format_exception(None, context.error, context.error.__traceback__)
    )

    try:
        if update and getattr(update, "effective_message", None):
            await update.effective_message.reply_text(
                "❌ Bot me thodi dikkat aa gayi hai\n"
                "Owner ko report bhej di gayi hai 🙂"
            )
    except Exception:
        pass

    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🚨 *BOT ERROR (PRIVATE)*\n\n```\n{error_text[:3500]}\n```",
            parse_mode="Markdown",
        )
    except Exception as e:
        print("OWNER DM FAILED:", e)

    try:
        if LOG_GROUP_ID:
            await context.bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=f"🚨 *BOT ERROR*\n\n```\n{error_text[:3500]}\n```",
                parse_mode="Markdown",
            )
    except Exception as e:
        print("LOG GROUP FAILED:", e)

    print("BOT ERROR:\n", error_text)


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # 1️⃣ Core modules auto-load
    print("\n🔄 Loading modules...")
    load_modules(app)

    # 2️⃣ Tools auto-load (tools/ folder)
    print("\n🔄 Loading tools...")
    load_tools(app)

    # 3️⃣ Error handler
    app.add_error_handler(error_handler)

    print("""
\033[96m
██╗  ██╗ █████╗ ██████╗ ██████╗ ██╗   ██╗
██║  ██║██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
███████║███████║██████╔╝██████╔╝ ╚████╔╝ 
██╔══██║██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  
██║  ██║██║  ██║██║  ██║██║  ██║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
\033[0m
\033[95m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑  HARRY • AI CHATBOT  (Modular)
📢  Telegram : @SANATANI_BACHA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\033[0m
""")

    # ========== IMPORTANT: Business Mode support ==========
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=[
            "message",
            "edited_message",
            "callback_query",
            "inline_query",
            "business_connection",
            "business_message",
            "edited_business_message",
            "deleted_business_messages",
        ],
        close_loop=False,
    )


if __name__ == "__main__":
    main()
