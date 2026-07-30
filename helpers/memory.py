from helpers.database import users

def get_memory(user_id: int) -> dict:
    user = users.find_one({"user_id": user_id})
    if user and "memory" in user:
        return user["memory"]
    return {}
