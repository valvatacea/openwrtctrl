import requests
from config import OPENWRT_API_URL

def send_api_request(action):
    try:
        response = requests.get(OPENWRT_API_URL, params={"action": action}, timeout=12)
        if response.status_code == 200:
            data = response.json()
            return data.get("output", "Tidak ada output.")
        else:
            return f"Error HTTP Status: {response.status_code}"
    except Exception as e:
        return f"Gagal terhubung ke HTTP API OpenWrt: {str(e)}"
