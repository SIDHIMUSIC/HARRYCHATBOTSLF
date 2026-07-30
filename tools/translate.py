"""
/tr — Translate text (AI based)
Auto-loaded tool

Use:
/tr hello
/tr en कैसे हो
/tr hi How are you
"""

from telegram.ext import CommandHandler
from helpers.ai import safe_ai


async def translate_cmd(update, context):
    if not context.args:
        return await update.message.reply_text(
            "❌ Use like:\n"
            "`/tr hello`\n"
            "`/tr en कैसे हो`\n"
            "`/tr hi How are you`",
            parse_mode="Markdown"
        )

    args = context.args

    # default target language = Hindi
    target_lang = "Hindi"
    text_parts = args

    # if first arg is short lang code
    if len(args) >= 2 and len(args[0]) <= 3:
        lang_map = {
            "hi": "Hindi",
            "en": "English",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
            "pa": "Punjabi",
            "ur": "Urdu",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ar": "Arabic",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
        }
        code = args[0].lower()
        if code in lang_map:
            target_lang = lang_map[code]
            text_parts = args[1:]

    text = " ".join(text_parts)

    prompt = (
        f"Translate the following text into {target_lang}.\n"
        "Only give the translated text, nothing else.\n\n"
        f"{text}"
    )

    reply = safe_ai([
        {"role": "system", "content": "You are a professional translator."},
        {"role": "user", "content": prompt}
    ])

    await update.message.reply_text(
        f"🌐 **Translated to {target_lang}:**\n\n{reply.strip()}",
        parse_mode="Markdown"
    )


def register(app):
    app.add_handler(CommandHandler("tr", translate_cmd))
