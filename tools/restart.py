"""
/restart — Owner only bot restart
"""

from telegram.ext import CommandHandler
from config import OWNER_ID
import os
import sys


async def restart(update, context):
    # Sirf Owner
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Sirf Owner use kar sakta hai.")

    await update.message.reply_text("🔄 Bot restart ho raha hai...")

    # Process ko band kar do → Heroku / Railway khud restart kar dega
    os.execl(sys.executable, sys.executable, *sys.argv)


def register(app):
    app.add_handler(CommandHandler("restart", restart))
