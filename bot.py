import asyncio
from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN, is_authorized, get_main_keyboard
from api_handler import send_api_request

async def start_handler(event):
    if not is_authorized(event.sender_id):
        await event.respond("❌ Maaf, Anda tidak memiliki izin untuk mengakses bot ini.")
        return

    # Terus hantar panel kawalan dengan inline keyboard
    await event.respond(
        "👋 **Selamat datang di OpenWrt Advanced Control Bot!**\n"
        "Silakan gunakan tombol menu di bawah ini:",
        buttons=get_main_keyboard()
    )

async def handle_inline_buttons(event):
    user_id = event.sender_id
    
    if not is_authorized(user_id):
        await event.answer("❌ Akses ditolak.", alert=True)
        return

    action_bytes = event.data
    action_key = action_bytes.decode("utf-8")

    action_labels = {
        "status": "📊 Status Sistem",
        "interface": "🌐 Info Interface",
        "wifi_clients": "👥 Klien WiFi",
        "storage": "💽 Penyimpanan",
        "network_restart": "🔄 Restart Network",
        "reboot": "♻️ Reboot OpenWrt"
    }

    label = action_labels.get(action_key, "Perintah")

    if action_key == "reboot":
        await event.answer("⚠️ Perintah reboot dikirim ke router!", alert=True)
        send_api_request("reboot")
        await event.edit(
            f"⚠️ **Perhatian!** Perangkat OpenWrt sedang melakukan reboot.",
            buttons=get_main_keyboard()
        )
        return

    await event.answer(f"Memproses {label}...")
    
    output = send_api_request(action_key)
    if len(output) > 4000:
        output = output[:4000] + "\n\n...(dipotong karena terlalu panjang)"
        
    await event.edit(
        f"📋 **Hasil ({label}):**\n```\n{output}\n```",
        buttons=get_main_keyboard()
    )

async def main():
    bot = TelegramClient("openwrt_modular_bot", API_ID, API_HASH)
    
    bot.add_event_handler(start_handler, events.NewMessage(pattern="/start"))
    bot.add_event_handler(handle_inline_buttons, events.CallbackQuery)

    print("🤖 Bot Telegram Inline Keyboard OpenWrt sedang berjalan...")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
