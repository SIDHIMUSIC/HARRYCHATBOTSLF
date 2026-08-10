"""
/qr — Text se QR Code generate kare
Usage: /qr https://t.me/SANATANI_BACHA
       /qr Hello World
"""

from telegram.ext import CommandHandler
from urllib.parse import quote


async def qr(update, context):
    if not context.args:
        return await update.message.reply_text(
            "❌ Use like this:\n"
            "`/qr https://t.me/SANATANI_BACHA`\n"
            "`/qr Hello World`\n"
            "`/qr Mera naam Harry hai`",
            parse_mode="Markdown"
        )

    text = " ".join(context.args)
    name = update.effective_user.first_name or "Bhai"

    # QR Code API (free, no key)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={quote(text)}"

    caption = (
        f"*{name}*,\n"
        f"📱 *QR Code Generated*\n\n"
        f"🔗 Text: `{text}`"
    )

    try:
        await update.message.reply_photo(
            photo=qr_url,
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        print("QR error:", e)
        await update.message.reply_text(
            f"*{name}*,\n⚠️ QR generate nahi ho paya.",
            parse_mode="Markdown"
        )


def register(app):
    app.add_handler(CommandHandler("qr", qr))
