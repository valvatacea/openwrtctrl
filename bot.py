import os
import asyncio
import subprocess
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton

# Muat variabel dari file .env
load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Ambil string ALLOWED_USERS, pisahkan dengan koma, dan ubah menjadi integer list
raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid.strip()) for uid in raw_users.split(",") if uid.strip().isdigit()]

# Inisialisasi Bot Client menggunakan Telethon
bot = TelegramClient("openwrt_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def is_authorized(user_id):
    """Cek apakah user memiliki akses ke bot"""
    if not ALLOWED_USERS:
        return True  # Jika kosong, izinkan semua (opsional, tapi lebih aman dibatasi)
    return user_id in ALLOWED_USERS

def run_command(cmd):
    """Fungsi helper untuk menjalankan perintah shell di OpenWrt"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output if output else "Perintah dieksekusi tanpa output."
    except Exception as e:
        return f"Error mengeksekusi perintah: {str(e)}"

# Tombol Menu Utama
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
        "👋 **Halo! Selamat datang di OpenWrt Management Bot.**\n"
        "Gunakan tombol di bawah untuk mengontrol perangkat OpenWrt Anda:",
        buttons=get_main_keyboard()
    )

@bot.on(events.NewMessage)
async def handle_buttons(event):
    user_id = event.sender_id
    text = event.raw_text

    # Abaikan jika bukan pesan dari tombol menu yang valid
    valid_texts = ["📊 Status Sistem", "🌐 Info Interface", "🔄 Restart Network", "♻️ Reboot OpenWrt"]
    if text not in valid_texts:
        return

    # Validasi akses user
    if not is_authorized(user_id):
        await event.respond("❌ Akses ditolak. Anda bukan pengguna yang diizinkan.")
        return

    if text == "📊 Status Sistem":
        await event.respond("⏳ Mengambil status sistem...")
        uptime = run_command("uptime")
        free_mem = run_command("free -m")
        response = f"📊 **Status Sistem OpenWrt:**\n\n`{uptime}`\n\n```\n{free_mem}\n```"
        await event.respond(response, buttons=get_main_keyboard())

    elif text == "🌐 Info Interface":
        await event.respond("⏳ Mengambil informasi interface...")
        net_info = run_command("ifconfig")
        # Batasi panjang pesan jika terlalu panjang untuk Telegram
        if len(net_info) > 4000:
            net_info = net_info[:4000] + "\n\n...(dipotong karena terlalu panjang)"
        await event.respond(f"🌐 **Interface Info:**\n```\n{net_info}\n```", buttons=get_main_keyboard())

    elif text == "🔄 Restart Network":
        await event.respond("🔄 Memuat ulang layanan jaringan (`/etc/init.d/network restart`)...")
        res = run_command("/etc/init.d/network restart")
        await event.respond(f"✅ Selesai:\n```\n{res}\n```", buttons=get_main_keyboard())

    elif text == "♻️ Reboot OpenWrt":
        await event.respond("⚠️ Perangkat OpenWrt akan segera melakukan reboot!")
        run_command("reboot")

def main():
    print("Bot OpenWrt sedang berjalan...")
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()
