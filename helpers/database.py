from pymongo import MongoClient
from config import MONGO_URI

db = MongoClient(MONGO_URI)["telegram_bot"]

users = db.users
bot_bans = db.bot_bans
ban_logs = db.ban_logs
spam = db.spam
chat_logs = db.chat_logs
badwords = db.badwords
codes = db.codes
