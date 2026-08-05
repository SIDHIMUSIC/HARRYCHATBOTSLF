from helpers.database import db
import time

clones = db.cloned_bots


def save_clone(owner_id: int, bot_token: str, bot_username: str, bot_id: int, bot_name: str):
    clones.update_one(
        {"bot_id": bot_id},
        {"$set": {
            "owner_id": owner_id,
            "bot_token": bot_token,
            "bot_username": bot_username,
            "bot_name": bot_name,
            "bot_id": bot_id,
            "created_at": time.time(),
            "is_active": True
        }},
        upsert=True
    )


def get_user_clones(owner_id: int):
    return list(clones.find({"owner_id": owner_id, "is_active": True}))


def get_all_clones():
    return list(clones.find({"is_active": True}))


def get_clone(bot_id: int):
    return clones.find_one({"bot_id": bot_id, "is_active": True})


def delete_clone(bot_id: int):
    clones.update_one(
        {"bot_id": bot_id},
        {"$set": {"is_active": False}}
    )


def get_clone_by_token(token: str):
    return clones.find_one({"bot_token": token, "is_active": True})
