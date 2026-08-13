"""
Offline migration — bot ke bahar chalao
heroku run python tools/migrate_offline.py
"""

from pymongo import MongoClient
import os
import sys

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
SOURCE_DB = "Yukki"
TARGET_DB = "telegram_bot"

COLLECTIONS = ["tgusersdb", "chats"]
BATCH_SIZE = 100
MAX_DOCS = 10000


def log(msg):
    print(msg, flush=True)


def main():
    log("=" * 40)
    log("🚀 Offline Migration Start")
    log("=" * 40)

    if not MONGO_URI:
        log("❌ MONGODB_URI not found in ENV")
        sys.exit(1)

    log(f"🔗 Connecting to MongoDB...")
    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
        )
        # force connection test
        client.admin.command("ping")
        log("✅ MongoDB connected")
    except Exception as e:
        log(f"❌ Connection failed: {e}")
        sys.exit(1)

    source = client[SOURCE_DB]
    target = client[TARGET_DB]

    log(f"📂 {SOURCE_DB} → {TARGET_DB}")
    log("-" * 40)

    try:
        src_cols = source.list_collection_names()
        log(f"Source collections: {src_cols}")
    except Exception as e:
        log(f"❌ Cannot list source collections: {e}")
        sys.exit(1)

    for name in COLLECTIONS:
        log(f"\n🔄 Processing: {name}")

        if name not in src_cols:
            log(f"⏭ {name}: source mein nahi mila")
            continue

        try:
            total_in_source = source[name].count_documents({})
            log(f"   Source me total docs: {total_in_source}")
        except Exception as e:
            log(f"❌ Count failed: {e}")
            continue

        inserted = skipped = total = 0
        batch = []

        try:
            cursor = source[name].find({}).batch_size(BATCH_SIZE)

            for doc in cursor:
                total += 1
                if total > MAX_DOCS:
                    log(f"⚠ Max limit {MAX_DOCS} hit")
                    break

                d = {k: v for k, v in doc.items() if k != "_id"}

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
                    log(f"   Progress: +{inserted} inserted | {skipped} skipped")

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

            log(f"✅ {name}: +{inserted} | skip {skipped} | checked {total}")

        except Exception as e:
            log(f"❌ Error in {name}: {e}")

    # final counts
    log("-" * 40)
    try:
        tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in target.list_collection_names() else 0
        tc = target["chats"].count_documents({}) if "chats" in target.list_collection_names() else 0
        log(f"📊 {TARGET_DB} now → {tu} users | {tc} chats")
    except Exception as e:
        log(f"Final count error: {e}")

    log("✅ DONE")
    client.close()


if __name__ == "__main__":
    main()
