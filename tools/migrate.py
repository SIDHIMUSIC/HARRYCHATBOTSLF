"""
/dbinfo  — Source & Target DB stats dikhata hai
/migrate — SOURCE_DB se TARGET_DB me selected collections copy karta hai
Owner only
"""

from telegram.ext import CommandHandler
from pymongo import MongoClient
from config import OWNER_ID, MONGO_URI

# ============ CONFIG ============
SOURCE_DB = "Yukki"   # yahan se data lega
TARGET_DB = "telegram_bot"        # yahan daleega

COLLECTIONS = [
    "tgusersdb",
    "chats",
    "sudoers",
    "blockedusers",
    "assistants",
    "chatstats",
    "userstats",
    "queries",
]
# ================================


def _client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI / MONGODB_URI not found in config")
    return MongoClient(MONGO_URI)


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def db_info(update, context):
    if not is_owner(update.effective_user.id):
        return

    try:
        client = _client()
        source = client[SOURCE_DB]
        target = client[TARGET_DB]

        src_cols = source.list_collection_names()
        t_cols = target.list_collection_names()

        src_users = source["tgusersdb"].count_documents({}) if "tgusersdb" in src_cols else 0
        src_chats = source["chats"].count_documents({}) if "chats" in src_cols else 0
        tgt_users = target["tgusersdb"].count_documents({}) if "tgusersdb" in t_cols else 0
        tgt_chats = target["chats"].count_documents({}) if "chats" in t_cols else 0

        await update.message.reply_text(
            f"🗂 <b>DB INFO</b>\n\n"
            f"<b>Source ({SOURCE_DB}):</b>\n"
            f"• Users: <code>{src_users}</code>\n"
            f"• Chats: <code>{src_chats}</code>\n"
            f"• Collections: <code>{', '.join(src_cols) if src_cols else 'none'}</code>\n\n"
            f"<b>Target ({TARGET_DB}):</b>\n"
            f"• Users: <code>{tgt_users}</code>\n"
            f"• Chats: <code>{tgt_chats}</code>\n"
            f"• Collections: <code>{', '.join(t_cols) if t_cols else 'none'}</code>\n\n"
            f"➡ <code>/migrate</code> se {SOURCE_DB} → {TARGET_DB} copy",
            parse_mode="HTML",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ <code>{e}</code>", parse_mode="HTML")


async def migrate_db(update, context):
    if not is_owner(update.effective_user.id):
        return

    status = await update.message.reply_text(
        f"⏳ <b>Migrating</b>\n<code>{SOURCE_DB}</code> → <code>{TARGET_DB}</code>...",
        parse_mode="HTML",
    )

    try:
        client = _client()
        source = client[SOURCE_DB]
        target = client[TARGET_DB]

        lines = [
            f"📂 Source: <code>{SOURCE_DB}</code>",
            f"📁 Target: <code>{TARGET_DB}</code>",
            "",
        ]
        src_cols = source.list_collection_names()

        for name in COLLECTIONS:
            if name not in src_cols:
                lines.append(f"⏭ <code>{name}</code>: source mein nahi")
                continue

            docs = list(source[name].find({}))
            if not docs:
                lines.append(f"📭 <code>{name}</code>: 0 docs")
                continue

            inserted = skipped = 0
            for d in docs:
                d = dict(d)
                d.pop("_id", None)

                # duplicate check
                if name == "tgusersdb" and "user_id" in d:
                    if target[name].find_one({"user_id": d["user_id"]}):
                        skipped += 1
                        continue
                elif name == "chats" and "chat_id" in d:
                    if target[name].find_one({"chat_id": d["chat_id"]}):
                        skipped += 1
                        continue

                try:
                    target[name].insert_one(d)
                    inserted += 1
                except Exception:
                    skipped += 1

            lines.append(
                f"✅ <code>{name}</code>: +{inserted} | skip {skipped} | src {len(docs)}"
            )

        t_cols = target.list_collection_names()
        tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in t_cols else 0
        tc = target["chats"].count_documents({}) if "chats" in t_cols else 0
        lines.append(f"\n📊 <b>{TARGET_DB} now:</b> {tu} users | {tc} chats")

        await status.edit_text("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await status.edit_text(f"❌ <code>{e}</code>", parse_mode="HTML")


def register(app):
    app.add_handler(CommandHandler("dbinfo", db_info))
    app.add_handler(CommandHandler("migrate", migrate_db))
