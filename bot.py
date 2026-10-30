import os
import asyncio
import requests
from dotenv import load_dotenv
from telethon import TelegramClient, events
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

def send_api_request(action):
    try:
        response = requests.post(OPENWRT_API_URL, json={"action": action}, timeout=12)
        if response.status_code == 200:
            data = response.json()
            return data.get("output", "Tidak ada output.")
        else:
            return f"Error HTTP Status: {response.status_code}"
    except Exception as e:
        return f"Gagal terhubung ke HTTP API OpenWrt: {str(e)}"

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        row=[
            KeyboardButtonRow([
                KeyboardButton("📊 Status Sistem"),
                KeyboardButton("🌐 Info Interface")
            ]),
            KeyboardButtonRow([
                KeyboardButton("🔄 Restart Network"),
                KeyboardButton("♻️ Reboot OpenWrt")
            ])
        ],
        resize=True
    )

# Variabel global untuk bot client
bot = None

async def start_handler(event):
    user_id = event.sender_id
    if not is_authorized(user_id):
        await event.respond("❌ Maaf, Anda tidak memiliki izin untuk mengakses bot ini.")
        return

    await event.respond(
        "👋 **Halo! Selamat datang di OpenWrt HTTP API Bot.**\n"
        "Gunakan tombol di bawah untuk mengontrol router:",
        buttons=get_main_keyboard()
    )

async def handle_buttons(event):
    user_id = event.sender_id
    text = event.raw_text

    valid_texts = ["📊 Status Sistem", "🌐 Info Interface", "🔄 Restart Network", "♻️ Reboot OpenWrt"]
    if text not in valid_
