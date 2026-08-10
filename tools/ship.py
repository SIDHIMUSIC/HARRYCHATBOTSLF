"""
/ship — Ship two people
Usage: /ship Name1 Name2
"""

from telegram.ext import CommandHandler
import random

async def ship(update, context):
    if len(context.args) < 2:
        return await update.message.reply_text(
            "❌ Use like this:\n"
            "`/ship Rahul Priya`\n"
            "`/ship Harry Hermione`",
            parse_mode="Markdown"
        )

    name1 = context.args[0]
    name2 = " ".join(context.args[1:])

    percent = random.randint(1, 100)

    if percent >= 80:
        emoji = "💘"
        status = "Perfect Match!"
    elif percent >= 60:
        emoji = "💖"
        status = "Strong Connection"
    elif percent >= 40:
        emoji = "💛"
        status = "There's a chance"
    elif percent >= 20:
        emoji = "💙"
        status = "Just friends maybe"
    else:
        emoji = "💔"
        status = "Not looking good"

    ship_name = name1[:3] + name2[-3:]

    text = (
        f"{emoji} *Shipping Result*\n\n"
        f"💕 {name1}  +  {name2}\n"
        f"💘 Ship Name: *{ship_name}*\n\n"
        f"🔥 Love Percentage: *{percent}%*\n"
        f"📌 Status: _{status}_"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

def register(app):
    app.add_handler(CommandHandler("ship", ship))
