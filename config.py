import os
from dotenv import load_dotenv
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid.strip()) for uid in raw_users.split(",") if uid.strip().isdigit()]
OPENWRT_API_URL = os.getenv("OPENWRT_API_URL", "http://192.168.1.1/cgi-bin/botapi")

def is_authorized(user_id):
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS

# Menu Utama Interaktif
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        rows=[
            KeyboardButtonRow([
                KeyboardButton("📊 Status Sistem"),
                KeyboardButton("🌐 Info Interface")
            ]),
            KeyboardButtonRow([
                KeyboardButton("👥 Klien WiFi"),
                KeyboardButton("💽 Penyimpanan")
            ]),
            KeyboardButtonRow([
                KeyboardButton("🔄 Restart Network"),
                KeyboardButton("♻️ Reboot OpenWrt")
            ])
        ],
        resize=True
    )
