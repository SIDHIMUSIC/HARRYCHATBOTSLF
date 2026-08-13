"""
Fast offline migration
heroku run python tools/migrate_offline.py
"""

from pymongo import MongoClient
import os
import sys

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
SOURCE_DB = "Yukki"
TARGET_DB = "telegram_bot"
COLLECTIONS = ["tgusersdb", "chats"]
BATCH_SIZE = 200


def log(msg):
    print(msg, flush=True)


def main():
    log("=" * 40)
    log("🚀 Fast Offline Migration")
    log("=" * 40)

    if not MONGO_URI:
        log("❌ MONGODB_URI missing")
        sys.exit(1)

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")
    log("✅ MongoDB connected")

    source = client[SOURCE_DB]
    target = client[TARGET_DB]
    log(f"📂 {SOURCE_DB} → {TARGET_DB}")

    src_cols = source.list_collection_names()
    log(f"Source collections: {src_cols}")

    for name in COLLECTIONS:
        log(f"\n🔄 {name}")

        if name not in src_cols:
            log(f"⏭ source mein nahi")
            continue

        # pehle se existing IDs nikal lo (fast duplicate check)
        existing = set()
        key = "user_id" if name == "tgusersdb" else "chat_id"

        if name in target.list_collection_names():
            for doc in target[name].find({}, {key: 1}):
                if key in doc:
                    existing.add(doc[key])
            log(f"   Already in target: {len(existing)}")

        inserted = skipped = total = 0
        batch = []

        for doc in source[name].find({}):
            total += 1
            d = {k: v for k, v in doc.items() if k != "_id"}

            uid = d.get(key)
            if uid is not None and uid in existing:
                skipped += 1
                continue

            batch.append(d)
            if uid is not None:
                existing.add(uid)

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
                log(f"   +{inserted} inserted | {skipped} skipped")

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

        log(f"✅ {name}: +{inserted} | skip {skipped} | total {total}")

    tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in target.list_collection_names() else 0
    tc = target["chats"].count_documents({}) if "chats" in target.list_collection_names() else 0
    log("-" * 40)
    log(f"📊 Final → {tu} users | {tc} chats")
    log("✅ DONE")
    client.close()


if __name__ == "__main__":
    main()
