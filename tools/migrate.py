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
BATCH_SIZE = 100          # ek baar me itne docs
SLEEP_BETWEEN_BATCH = 0.3 # Heroku ko thoda rest
# ================================


def _client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not found in config")
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def _count(db, name):
    try:
        return db[name].count_documents({})
    except Exception:
        return 0


def _list_cols(db):
    try:
        return db.list_collection_names()
    except Exception:
        return []


async def db_info(update, context):
    if not is_owner(update.effective_user.id):
        return

    try:
        def work():
            client = _client()
            source = client[SOURCE_DB]
            target = client[TARGET_DB]
            src_cols = _list_cols(source)
            t_cols = _list_cols(target)
            return {
                "src_users": _count(source, "tgusersdb") if "tgusersdb" in src_cols else 0,
                "src_chats": _count(source, "chats") if "chats" in src_cols else 0,
                "tgt_users": _count(target, "tgusersdb") if "tgusersdb" in t_cols else 0,
                "tgt_chats": _count(target, "chats") if "chats" in t_cols else 0,
                "src_cols": src_cols,
                "t_cols": t_cols,
            }

        data = await asyncio.to_thread(work)

        await update.message.reply_text(
            f"🗂 <b>DB INFO</b>\n\n"
            f"<b>Source ({SOURCE_DB}):</b>\n"
            f"• Users: <code>{data['src_users']}</code>\n"
            f"• Chats: <code>{data['src_chats']}</code>\n"
            f"• Collections: <code>{', '.join(data['src_cols']) or 'none'}</code>\n\n"
            f"<b>Target ({TARGET_DB}):</b>\n"
            f"• Users: <code>{data['tgt_users']}</code>\n"
            f"• Chats: <code>{data['tgt_chats']}</code>\n"
            f"• Collections: <code>{', '.join(data['t_cols']) or 'none'}</code>\n\n"
            f"➡ <code>/migrate</code> se copy start karo",
            parse_mode="HTML",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ <code>{e}</code>", parse_mode="HTML")


def _migrate_one_collection(source, target, name):
    """Ek collection ko batch me migrate karta hai (blocking)."""
    if name not in source.list_collection_names():
        return f"⏭ <code>{name}</code>: source mein nahi", 0, 0

    cursor = source[name].find({}, batch_size=BATCH_SIZE)
    inserted = skipped = total = 0
    batch = []

    for doc in cursor:
        total += 1
        d = dict(doc)
        d.pop("_id", None)

        # duplicate check
        exists = False
        if name == "tgusersdb" and "user_id" in d:
            exists = target[name].find_one({"user_id": d["user_id"]}, {"_id": 1}) is not None
        elif name == "chats" and "chat_id" in d:
            exists = target[name].find_one({"chat_id": d["chat_id"]}, {"_id": 1}) is not None

        if exists:
            skipped += 1
            continue

        batch.append(d)

        if len(batch) >= BATCH_SIZE:
            try:
                target[name].insert_many(batch, ordered=False)
                inserted += len(batch)
            except Exception:
                # fallback one by one
                for item in batch:
                    try:
                        target[name].insert_one(item)
                        inserted += 1
                    except Exception:
                        skipped += 1
            batch = []

    # remaining
    if batch:
        try:
            target[name].insert_many(batch, ordered=False)
            inserted += len(batch)
        except Exception:
            for item in batch:
                try:
                    target[name].insert_one(item)
                    inserted += 1
                except Exception:
                    skipped += 1

    return f"✅ <code>{name}</code>: +{inserted} | skip {skipped} | src {total}", inserted, skipped


async def migrate_db(update, context):
    if not is_owner(update.effective_user.id):
        return

    status = await update.message.reply_text(
        f"⏳ <b>Migrating</b>\n<code>{SOURCE_DB}</code> → <code>{TARGET_DB}</code>...\n"
        f"Please wait, batch mode chal raha hai.",
        parse_mode="HTML",
    )

    lines = [
        f"📂 Source: <code>{SOURCE_DB}</code>",
        f"📁 Target: <code>{TARGET_DB}</code>",
        "",
    ]

    try:
        client = await asyncio.to_thread(_client)
        source = client[SOURCE_DB]
        target = client[TARGET_DB]

        for name in COLLECTIONS:
            # har collection alag thread me chalao taaki event loop free rahe
            result_line, _, _ = await asyncio.to_thread(
                _migrate_one_collection, source, target, name
            )
            lines.append(result_line)

            # progress update
            try:
                await status.edit_text("\n".join(lines) + "\n\n⏳ still working...", parse_mode="HTML")
            except Exception:
                pass

            await asyncio.sleep(SLEEP_BETWEEN_BATCH)

        # final counts
        def final_counts():
            t_cols = target.list_collection_names()
            tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in t_cols else 0
            tc = target["chats"].count_documents({}) if "chats" in t_cols else 0
            return tu, tc

        tu, tc = await asyncio.to_thread(final_counts)
        lines.append(f"\n📊 <b>{TARGET_DB} now:</b> {tu} users | {tc} chats")
        lines.append("\n✅ <b>Migration complete</b>")

        await status.edit_text("\n".join(lines), parse_mode="HTML")

    except Exception as e:
        await status.edit_text(f"❌ <code>{e}</code>", parse_mode="HTML")


def register(app):
    app.add_handler(CommandHandler("dbinfo", db_info))
    app.add_handler(CommandHandler("migrate", migrate_db))
