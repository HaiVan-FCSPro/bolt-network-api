import requests
import json
import datetime

API_URL = "http://127.0.0.1:8000/device/heartbeat"

# Thông tin xác thực (giống hệt)
headers = {
    "Content-Type": "application/json",
    "X-Device-ID": "BOLT-TEST-001",
    "X-API-Key": "bolt_secret_key_for_testing"
}

# Payload với MÃ LỖI ĐỘNG CƠ
payload = {
    "timestamp": datetime.datetime.now().isoformat(),
    "location": {
        "lat": 10.7720, # Tọa độ gần Gara (GARAGE001)
        "lon": 106.6690
    },
    "obd_data": {
        "fuel_level": 75.0, # <-- Nhiên liệu TỐT
        "engine_status": "ON",
        "rpm": 1500,
        "speed": 60,
        "error_codes": ["P0420", "P0301"] # <-- MÃ LỖI
    }
}

print(f"Đang gửi Heartbeat (MÃ LỖI) tới: {API_URL}")

try:
    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 202: # 202 Accepted
        print("\n--- THÀNH CÔNG (202) ---")
        print("Máy chủ đã chấp nhận Heartbeat.")
        print("Hãy kiểm tra log của Terminal 1 để xem Cảnh báo AI.")
    else:
        print(f"\n--- LỖI ({response.status_code}) ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- LỖI KẾT NỐI ---")
