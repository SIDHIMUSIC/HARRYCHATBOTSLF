from helpers.database import db
import time

learned = db.learned_replies


def save_learned_reply(word: str, reply: str, user_id: int = None):
    """User ke reply ko save karta hai"""
    if not word or not reply:
        return

    word = word.strip().lower()[:200]
    reply = reply.strip()[:1000]

    if len(word) < 2 or len(reply) < 2:
        return

    try:
        # Same word pe pehle se hai toh update mat karo, naya entry daalo
        learned.insert_one({
            "word": word,
            "reply": reply,
            "user_id": user_id,
            "time": time.time()
        })
    except Exception as e:
        print("Learning save error:", e)


def get_learned_reply(word: str):
    """Word ke hisaab se koi random learned reply nikalta hai"""
    if not word:
        return None

    word = word.strip().lower()[:200]

    try:
        results = list(learned.find({"word": word}).limit(20))
        if results:
            import random
            return random.choice(results)["reply"]
    except Exception as e:
        print("Learning get error:", e)

    return None
