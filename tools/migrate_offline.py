"""
Offline migration script — bot ke bahar chalta hai
Heroku pe aise chalao:

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


def main():
    if not MONGO_URI:
        print("❌ MONGODB_URI not found")
        sys.exit(1)

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    source = client[SOURCE_DB]
    target = client[TARGET_DB]

    print(f"📂 {SOURCE_DB} → {TARGET_DB}")
    print("-" * 40)

    for name in COLLECTIONS:
        if name not in source.list_collection_names():
            print(f"⏭ {name}: source mein nahi")
            continue

        inserted = skipped = total = 0
        batch = []

        for doc in source[name].find({}).batch_size(BATCH_SIZE):
            total += 1
            if total > MAX_DOCS:
                print(f"⚠ {name}: max {MAX_DOCS} limit hit")
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
                print(f"  {name}: {inserted} inserted...", flush=True)

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

        print(f"✅ {name}: +{inserted} | skip {skipped} | total checked {total}")

    # final
    tu = target["tgusersdb"].count_documents({}) if "tgusersdb" in target.list_collection_names() else 0
    tc = target["chats"].count_documents({}) if "chats" in target.list_collection_names() else 0
    print("-" * 40)
    print(f"📊 {TARGET_DB} now → {tu} users | {tc} chats")
    print("✅ Done")
    client.close()


if __name__ == "__main__":
    main()
