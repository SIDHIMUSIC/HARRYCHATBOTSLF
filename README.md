# 👑 HARRY CHATBOT

> Professional Modular Telegram AI Bot  
> Made with ❤️ by **Harry** ([@SANATANI_BACHA](https://t.me/SANATANI_BACHA))

---

## 📁 Structure

```
HARRYCHATBOT/
├── HARRYCHATBOT.py      ← Main entry point
├── config.py            ← ENV + settings
├── helpers/             ← Database, AI, Memory, Decorators
│   ├── ai.py
│   ├── database.py
│   ├── decorators.py
│   └── memory.py
├── modules/             ← Core features
│   ├── start.py
│   ├── help.py
│   ├── chat.py
│   └── owner.py
├── tools/               ← 🔥 AUTO-LOADED plugins
│   └── truth_dare.py
├── utils/
│   └── auto_loader.py   ← Auto load system
├── requirements.txt
└── .env.example
```

---

## 🚀 How to add NEW feature (Auto Load)

1. `tools/` folder me naya file banao, e.g. `tools/joke.py`
2. Usme function + `register(app)` likho:

```python
from telegram.ext import CommandHandler

async def joke(update, context):
    await update.message.reply_text("Ek joke...")

def register(app):
    app.add_handler(CommandHandler("joke", joke))
```

3. Bot restart karo — **automatic load** ho jayega.  
   Manual `CommandHandler` main file me add karne ki **zarurat nahi**.

---

## ⚙ Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# .env me values bharo
python HARRYCHATBOT.py
```

---

## ✨ Features

- Modular architecture
- Auto-load tools system
- AI chat + MongoDB fallback
- Stickers on keywords
- Memory system (`/teach`)
- Group moderation
- Owner dashboard
- Clean professional code

---

© 2026 Harry • MIT License
