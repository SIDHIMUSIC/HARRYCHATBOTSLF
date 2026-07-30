from config import OWNER_ID
from helpers.database import bot_bans

def is_owner(uid: int) -> bool:
    return uid == OWNER_ID

def is_bot_banned(uid: int) -> bool:
    return bot_bans.find_one({"user_id": uid}) is not None

async def is_admin(update, context) -> bool:
    if update.effective_chat.type == "private":
        return False
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    return member.status in ("administrator", "creator")
