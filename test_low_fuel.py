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

# Payload với NHIÊN LIỆU THẤP
payload = {
    "timestamp": datetime.datetime.now().isoformat(),
    "location": {
        "lat": 10.7798, # Tọa độ gần các cây xăng Q1
        "lon": 106.7020
    },
    "obd_data": {
        "fuel_level": 15.0, # <-- NHIÊN LIỆU THẤP (Dưới 20)
        "engine_status": "ON",
        "rpm": 900,
        "speed": 15,
        "error_codes": []
    }
}

print(f"Đang gửi Heartbeat (NHIÊN LIỆU THẤP) tới: {API_URL}")

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
