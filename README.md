# 👑 HARRY CHATBOT

> Professional Modular Telegram AI Bot  
> Made with ❤️ by **Harry** ([@SANATANI_BACHA](https://t.me/SANATANI_BACCHA))

---

## 🚀 Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/SIDHIMUSIC/trryfreetg)

> Button dabao → ENV variables bharo → Deploy. Bas!

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
├── app.json             ← Heroku config
├── Procfile
├── runtime.txt
├── requirements.txt
└── .env.example
```

---

## 🔥 How to add NEW feature (Auto Load)

1. `tools/` folder me naya file banao, e.g. `tools/joke.py`
2. Usme function + `register(app)` likho:

```python
from telegram.ext import CommandHandler

async def joke(update, context):
    await update.message.reply_text("Ek joke...")

def register(app):
    app.add_handler(CommandHandler("joke", joke))
```

3. Bot restart → **automatic load**.  
   Manual `CommandHandler` main file me add karne ki **zarurat nahi**.

---

## ⚙ Manual Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# .env me values bharo
python HARRYCHATBOT.py
```

### Required ENV

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | @BotFather se token |
| `OPENROUTER_API_KEY` | openrouter.ai se key |
| `MONGODB_URI` | MongoDB connection string |
| `OWNER_ID` | Tumhara Telegram user ID |

---

## ✨ Features

- Modular professional architecture
- Auto-load tools system
- AI chat + MongoDB offline fallback
- Stickers on keywords
- Memory system
- Owner dashboard & broadcast
- Group-ready
- One-click Heroku deploy

---

## ☁ Other Deploy Options

### Railway
1. New Project → Deploy from GitHub
2. ENV variables add karo
3. Start command: `python HARRYCHATBOT.py`

### Render
1. Web Service / Background Worker
2. Build: `pip install -r requirements.txt`
3. Start: `python HARRYCHATBOT.py`

---

## 👨‍💻 Developer

**Harry** · [@SANATANI_BACHA](https://t.me/SANATANI_BACHA)

⭐ Star this repo if you like it.

---

© 2026 Harry · MIT License
