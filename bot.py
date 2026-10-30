import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, is_authorized, get_main_keyboard
from api_handler import send_api_request

async def start_handler(event):
    if not is_authorized(event.sender_id):
        await event.respond("❌ Maaf, Anda tidak memiliki izin untuk mengakses bot ini.")
        return

    await event.respond(
        "👋 **Selamat datang di OpenWrt Advanced Control Bot!**\n"
        "Silakan pilih menu perintah di bawah ini:",
        buttons=get_main_keyboard()
    )

async def handle_buttons(event):
    user_id = event.sender_id
    text = event.raw_text

    valid_actions = {
        "📊 Status Sistem": ("status", "⏳ Mengambil status sistem..."),
        "🌐 Info Interface": ("interface", "⏳ Mengambil informasi interface..."),
        "👥 Klien WiFi": ("wifi_clients", "⏳ Memindai perangkat klien WiFi yang terhubung..."),
        "💽 Penyimpanan": ("storage", "⏳ Memeriksa kapasitas penyimpanan router..."),
        "🔄 Restart Network": ("network_restart", "⏳ Merefresh layanan jaringan..."),
    }

    if text not in valid_actions and text != "♻️ Reboot OpenWrt":
        return

    if not is_authorized(user_id):
        await event.respond("❌ Akses ditolak.")
        return

    # Handle Khusus untuk Reboot dengan Konfirmasi Ekstra
    if text == "♻️ Reboot OpenWrt":
        await event.respond("⚠️ **Perhatian!** Perangkat OpenWrt akan segera melakukan reboot.", buttons=get_main_keyboard())
        send_api_request("reboot")
        return

    action_key, loading_text = valid_actions[text]
    await event.respond(loading_text, buttons=get_main_keyboard())
    
    output = send_api_request(action_key)
    if len(output) > 4000:
        output = output[:4000] + "\n\n...(dipotong karena terlalu panjang)"
        
    await event.respond(f"📋 **Hasil ({text}):**\n```\n{output}\n```", buttons=get_main_keyboard())

async def main():
    bot = TelegramClient("openwrt_modular_bot", API_ID, API_HASH)
    
    bot.add_event_handler(start_handler, events.NewMessage(pattern="/start"))
    bot.add_event_handler(handle_buttons, events.NewMessage)

    print("🤖 Bot Telegram Modular OpenWrt sedang berjalan...")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
