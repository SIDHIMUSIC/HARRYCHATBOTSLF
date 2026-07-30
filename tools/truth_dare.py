"""
Truth & Dare — Auto-loaded tool
Naya tool banana ho to bas aise file banao + register(app) likho.
"""

from telegram.ext import CommandHandler
from helpers.ai import safe_ai


async def truth(update, context):
    user = update.effective_user
    name = user.first_name or "Friend"

    system = (
        "You are playing a Truth game with the user. "
        "Ask ONLY one creative, fun truth question. "
        "Be human-like and playful. "
        "Do NOT explain rules. "
        "Do NOT ask name, age, or boring questions."
    )

    reply = safe_ai([
        {"role": "system", "content": system},
        {"role": "user", "content": "truth"},
    ])

    final_reply = f"*{name}*,\n📸 Truth:\n{reply.strip()}"
    await update.message.reply_text(final_reply, parse_mode="Markdown")


async def dare(update, context):
    user = update.effective_user
    name = user.first_name or "Friend"

    system = (
        "You are playing a Dare game with the user. "
        "Give ONLY one fun and SAFE dare. "
        "Dare must be doable in chat. "
        "No illegal, dangerous, or harmful tasks. "
        "Do NOT explain rules."
    )

    reply = safe_ai([
        {"role": "system", "content": system},
        {"role": "user", "content": "dare"},
    ])

    final_reply = f"*{name}*,\n😈 Dare:\n{reply.strip()}"
    await update.message.reply_text(final_reply, parse_mode="Markdown")


def register(app):
    """Yeh function auto-loader call karega."""
    app.add_handler(CommandHandler("truth", truth))
    app.add_handler(CommandHandler("dare", dare))
