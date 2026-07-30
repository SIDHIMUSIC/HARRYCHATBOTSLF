import requests
from config import OPENROUTER_KEY, MODEL
from helpers.memory import get_memory
from helpers.database import chat_logs


def safe_ai(messages: list) -> str:
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://t.me/SANATANI_BACHA",
                "X-Title": "Harry ChatBot",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7,
            },
            timeout=60,
        )
        data = r.json()
        if "choices" not in data:
            return "⚠️ AI busy hai, thodi der baad try karo."
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("AI ERROR:", e)
        return "🙂 Abhi thodi dikkat aa rahi hai, baad me try karo."


def get_fallback_reply(user_id: int, text: str, name: str) -> str:
    lower = text.lower()

    memory = get_memory(user_id)
    if memory:
        for key, value in memory.items():
            if key in lower or str(value).lower() in lower:
                return f"*{name}*,\nHaan yaad hai! {key} → {value} 🧠"

    if any(w in lower for w in ["hi", "hello", "hey", "namaste"]):
        return f"*{name}*,\nHeyy! Kaise ho? 😊"
    if any(w in lower for w in ["kaise ho", "how are you", "kya haal"]):
        return f"*{name}*,\nMain theek hoon, tum batao ❤️"
    if any(w in lower for w in ["bye", "alvida", "good night", "gn"]):
        return f"*{name}*,\nBye bye! Take care 🌙"
    if any(w in lower for w in ["love", "pyar", "miss"]):
        return f"*{name}*,\nAww ❤️ Main bhi!"
    if any(w in lower for w in ["thank", "shukriya", "thanks"]):
        return f"*{name}*,\nWelcome yaar 🥰"

    try:
        last_chats = list(
            chat_logs.find({"user_id": user_id}).sort("time", -1).limit(8)
        )
        if last_chats:
            user_msgs = []
            for c in reversed(last_chats):
                msg = c.get("text", "")
                if msg and len(msg) < 120:
                    user_msgs.append(msg)
            if user_msgs:
                for old in user_msgs:
                    old_lower = old.lower()
                    if any(w in old_lower for w in lower.split() if len(w) > 3):
                        return f"*{name}*,\nPehle bhi aisa kuch baat hui thi 🙂\nYaad hai: _{old[:80]}_"
                last = user_msgs[-1]
                return (
                    f"*{name}*,\nAI abhi thoda down hai 😅\n\n"
                    f"Last baat thi:\n_{last[:100]}_\n\n"
                    f"Phir se try karo thodi der baad ❤️"
                )
    except Exception as e:
        print("Fallback chat error:", e)

    if memory:
        mem_text = "\n".join([f"• {k}: {v}" for k, v in list(memory.items())[:3]])
        return f"*{name}*,\nAI thoda busy hai 😅\n\nTumhari yaadein:\n{mem_text}"

    return f"*{name}*,\nAI abhi thoda down hai, thodi der baad try karo 🙂"
