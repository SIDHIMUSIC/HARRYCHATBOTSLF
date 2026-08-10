"""
/lyrics — Song lyrics nikalta hai
Usage: /lyrics Artist - Song Name
Example: /lyrics Ed Sheeran - Shape of You
"""

from telegram.ext import CommandHandler
import requests
from urllib.parse import quote


async def lyrics(update, context):
    if not context.args:
        return await update.message.reply_text(
            "❌ Use like this:\n"
            "`/lyrics Artist - Song Name`\n\n"
            "Example:\n"
            "`/lyrics Ed Sheeran - Shape of You`",
            parse_mode="Markdown"
        )

    query = " ".join(context.args)

    # Artist - Song format handle karo
    if " - " in query:
        artist, title = query.split(" - ", 1)
    else:
        # Agar - nahi hai to last word ko title maan lo
        parts = query.rsplit(" ", 1)
        if len(parts) == 2:
            artist, title = parts
        else:
            artist = query
            title = query

    artist = artist.strip()
    title = title.strip()

    name = update.effective_user.first_name or "Bhai"

    try:
        # lyrics.ovh API
        url = f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}"
        r = requests.get(url, timeout=12)

        if r.status_code == 200:
            data = r.json()
            lyrics_text = data.get("lyrics")

            if lyrics_text:
                # Bahut lamba lyrics truncate karo
                if len(lyrics_text) > 3800:
                    lyrics_text = lyrics_text[:3800] + "\n\n... (lyrics too long)"

                text = (
                    f"🎵 *{title}* — _{artist}_\n\n"
                    f"{lyrics_text}"
                )
                await update.message.reply_text(text, parse_mode="Markdown")
                return

        await update.message.reply_text(
            f"*{name}*,\n❌ Lyrics nahi mile is song ke.\n\n"
            f"Try karo:\n`/lyrics Artist - Song Name`",
            parse_mode="Markdown"
        )

    except Exception as e:
        print("Lyrics error:", e)
        await update.message.reply_text(
            f"*{name}*,\n⚠️ Lyrics service abhi down hai, thodi der baad try karo.",
            parse_mode="Markdown"
        )


def register(app):
    app.add_handler(CommandHandler("lyrics", lyrics))
