import os
import asyncio
import asyncssh
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton

# Muat variabel dari file .env
load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Ambil daftar allowed users
raw_users = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = [int(uid.strip()) for uid in raw_users.split(",") if uid.strip().isdigit()]

# Konfigurasi SSH OpenWrt
OPENWRT_HOST = os.getenv("OPENWRT_HOST", "192.168.1.1")
OPENWRT_PORT = int(os.getenv("OPENWRT_PORT", 22))
OPENWRT_USER = os.getenv("OPENWRT_USER", "root")
OPENWRT_PASS = os.getenv("OPENWRT_PASS", "")

# Inisialisasi Bot Client menggunakan Telethon
bot = TelegramClient("openwrt_remote_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def is_authorized(user_id):
    """Cek apakah user memiliki akses ke bot"""
    if not ALLOWED_USERS:
        return True
    return user_id in ALLOWED_USERS

async def run_ssh_command(cmd):
    """Fungsi helper untuk menjalankan perintah jarak jauh via SSH ke OpenWrt"""
    try:
        async with asyncssh.connect(
            OPENWRT_HOST, 
            port=OPENWRT_PORT, 
            username=OPENWRT_USER, 
            password=OPENWRT_PASS, 
            known_hosts=None
        ) as conn:
            result = await conn.run(cmd, check=False)
            output = result.stdout.strip() or result.stderr.strip()
            return output if output else "Perintah dieksekusi tanpa output."
    except Exception as e:
        return f"Gagal terhubung ke OpenWrt via SSH: {str(e)}"

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
        "👋 **Halo! Selamat datang di OpenWrt Remote Management Bot.**\n"
        "Gunakan tombol di bawah untuk mengontrol router OpenWrt Anda:",
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
        await event.respond("❌ Akses ditolak. Anda bukan pengguna yang diizinkan.")
        return

    if text == "📊 Status Sistem":
        await event.respond("⏳ Mengambil status sistem dari router...")
        uptime = await run_ssh_command("uptime")
        free_mem = await run_ssh_command("free -m")
        response = f"📊 **Status Sistem OpenWrt ({OPENWRT_HOST}):**\n\n`{uptime}`\n\n```\n{free_mem}\n```"
        await event.respond(response, buttons=get_main_keyboard())

    elif text == "🌐 Info Interface":
        await event.respond("⏳ Mengambil informasi interface...")
        net_info = await run_ssh_command("ifconfig")
        if len(net_info) > 4000:
            net_info = net_info[:4000] + "\n\n...(dipotong karena terlalu panjang)"
        await event.respond(f"🌐 **Interface Info:**\n```\n{net_info}\n```", buttons=get_main_keyboard())

    elif text == "🔄 Restart Network":
        await event.respond("🔄 Memuat ulang layanan jaringan via SSH...")
        res = await run_ssh_command("/etc/init.d/network restart")
        await event.respond(f"✅ Selesai:\n```\n{res}\n```", buttons=get_main_keyboard())

    elif text == "♻️ Reboot OpenWrt":
        await event.respond("⚠️ Perintah reboot dikirim. Perangkat OpenWrt akan segera restart!")
        # Menjalankan reboot di background agar koneksi SSH tidak menggantung (hang)
        asyncio.create_task(run_ssh_command("reboot"))

def main():
    print("Bot Remote OpenWrt sedang berjalan...")
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()
