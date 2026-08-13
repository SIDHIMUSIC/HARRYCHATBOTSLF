"""
/dbinfo  — Source & Target DB stats
/migrate — Light & Heroku-safe migration (memory friendly)
Owner only
"""

import asyncio
import gc
from telegram.ext import CommandHandler
from pymongo import MongoClient
from config import OWNER_ID, MONGO_URI

# ============ CONFIG ============
SOURCE_DB = "Yukki"
TARGET_DB = "telegram_bot"

# Sirf zaroori collections (baaki mat lo warna memory full)
COLLECTIONS = [
    "tgusersdb",
    "chats",
]

BATCH_SIZE = 50           # chhota batch = kam memory
SLEEP_BETWEEN_BATCH = 0.8 # zyada rest = Heroku happy
MAX_DOCS_PER_COLLECTION = 5000  # safety limit (badalo agar chaho)
# ================================


def _client():
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI not found")
    return MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=8000,
        maxPoolSize=5,          # kam connections
        connectTimeoutMS=8000,
    )


def is_owner(uid: int) -> bool:
    return uid == OWNER_ID


async def db_info(update, context):
    if not is_owner(update.effective_user.id):
        return

    try:
        def work():
            client = _client()
            source = client[SOURCE_DB]
            target = client[TARGET_DB]

            def safe_count(db, name):
                try:
                    return db[name].count_documents({})
                except Exception:
                    return 0

            src_cols = source.list_collection_names()
            t_cols = target.list_collection_names()

            return {
                "src_users": safe_count(source, "tgusersdb"),
                "src_chats": safe_count(source, "chats"),
                "tgt_users": safe_count(target, "tgusersdb"),
                "tgt_chats": safe_count(target, "chats"),
                "src_cols": src_cols,
                "t_cols": t_cols,
            }

        data = await asyncio.to_thread(work)

        text = (
            f"🗂 <b>DB INFO</b>\n\n"
            f"<b>Source ({SOURCE_DB}):</b>\n"
            f"• Users: <code>{data['src_users']}</code>\n"
            f"• Chats: <code>{data['src_chats']}</code>\n"
            f"• Collections: <code>{', '.join(data['src_cols'][:12]) or 'none'}</code>\n\n"
            f"<b>Target ({TARGET_DB}):</b>\n"
            f"• Users: <code>{data['tgt_users']}</code>\n"
            f"• Chats: <code>{data['tgt_chats']}</code>\n"
            f"• Collections: <code>{', '.join(data['t_cols'][:12]) or 'none'}</code>\n\n"
            f"➡ <code>/migrate</code> se copy start karo\n"
            f"⚠ Max {MAX_DOCS_PER_COLLECTION} docs per collection"
        )
        await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ <code>{e}</code>", parse_mode="HTML")


def _migrate_collection(source, target, name):
    """Memory-safe single collection migrate"""
    if name not in source.list_collection_names():
        return f"⏭ <code>{name}</code>: source mein nahi"

    inserted = skipped = total = 0
    batch = []

    cursor = source[name].find({}, no_cursor_timeout=False).batch_size(BATCH_SIZE)

    try:
        for doc in cursor:
            total += 1
            if total > MAX_DOCS_PER_COLLECTION:
                break

            d = {k: v for k, v in doc.items() if k != "_id"}

            # duplicate check (sirf important fields)
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
                    for item in batch:
                        try:
                            target[name].insert_one(item)
                            inserted += 1
                        except Exception:
                            skipped += 1
                batch = []
                gc.collect()  # memory free

        # last batch
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
    finally:
        cursor.close()
        gc.collect()

    return f"✅ <code>{name}</code>: +{inserted} | skip {skipped} | checked {total}"


async def migrate_db(update, context):
    if not is_owner(update.effective_user.id):
        return

    status = await update.message.reply_text(
        f"⏳ <b>Safe Migrating</b>\n"
        f"<code>{SOURCE_DB}</code> → <code>{TARGET_DB}</code>\n"
        f"Batch size: {BATCH_SIZE} | Max: {MAX_DOCS_PER_COLLECTION}",
        parse_mode="HTML",
    )

    lines = [
        f"📂 Source: <code>{SOURCE_DB}</code>",
        f"📁 Target: <code>{TARGET_DB}</code>",
        "",
    ]

    client = None
    try:
        client = await asyncio.to_thread(_client)
        source = client[SOURCE_DB]
        target = client[TARGET_DB]

        for name in COLLECTIONS:
            result = await asyncio.to_thread(_migrate_collection, source, target, name)
            lines.append(result)

            try:
                await status.edit_text(
                    "\n".join(lines) + "\n\n⏳ working...",
                    parse_mode="HTML"
                )
            except Exception:
                pass

            await asyncio.sleep(SLEEP_BETWEEN_BATCH)
            gc.collect()

        # final count
        def final():
            tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in target.list_collection_names() else 0
            tc = target["chats"].count_documents({}) if "chats" in target.list_collection_names() else 0
            return tu, tc

        tu, tc = await asyncio.to_thread(final)
        lines.append(f"\n📊 <b>{TARGET_DB} now:</b> {tu} users | {tc} chats")
        lines.append("✅ <b>Done (memory safe)</b>")

        await status.edit_text("\n".join(lines), parse_mode="HTML")

    except Exception as e:
        await status.edit_text(f"❌ <code>{e}</code>", parse_mode="HTML")
    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass
        gc.collect()


def register(app):
    app.add_handler(CommandHandler("dbinfo", db_info))
    app.add_handler(CommandHandler("migrate", migrate_db))
