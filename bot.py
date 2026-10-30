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

# Inisialisasi Bot Client tanpa langsung memanggil .start() di luar async
bot = TelegramClient("openwrt_http_bot", API_ID, API_HASH)

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

@bot.on(events.NewMessage(pattern="/start"))
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

@bot.on(events.NewMessage)
async def handle_buttons(event):
    user_id = event.sender_id
    text = event.raw_text

    valid_texts = ["📊 Status Sistem", "🌐 Info Interface", "🔄 Restart Network", "♻️ Reboot OpenWrt"]
    if text not in valid_texts:
        return

    if not is_authorized(user_id):
        await event.respond("❌ Akses ditolak.")
        return

    if text == "📊 Status Sistem":
        await event.respond("⏳ Mengambil status via HTTP API...")
        output = send_api_request("status")
        await event.respond(f"📊 **Status Sistem OpenWrt:**\n```\n{output}\n```", buttons=get_main_keyboard())

    elif text == "🌐 Info Interface":
        await event.respond("⏳ Mengambil info interface...")
        output = send_api_request("interface")
        if len(output) > 4000:
            output = output[:4000] + "\n\n...(dipotong)"
        await event.respond(f"🌐 **Interface Info:**\n```\n{output}\n```", buttons=get_main_keyboard())

    elif text == "🔄 Restart Network":
        await event.respond("🔄 Merefresh jaringan via HTTP API...")
        output = send_api_request("network_restart")
        await event.respond(f"✅ Selesai:\n```\n{output}\n```", buttons=get_main_keyboard())

    elif text == "♻️ Reboot OpenWrt":
        await event.respond("⚠️ Perintah reboot dikirim ke router!")
        send_api_request("reboot")

async def main():
    print("Memulai bot Telegram...")
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot Telegram HTTP API sedang berjalan...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
