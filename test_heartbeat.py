import requests
import json
import datetime

API_URL = "http://127.0.0.1:8000/device/heartbeat"

# 1. Thông tin xác thực
headers = {
    "Content-Type": "application/json",
    "X-Device-ID": "BOLT-TEST-001",
    "X-API-Key": "bolt_secret_key_for_testing" # <-- Chìa khóa bí mật
}

# 2. Dữ liệu Payload mẫu
payload = {
    "timestamp": datetime.datetime.now().isoformat(),
    "location": {
        "lat": 10.87198,
        "lon": 106.75765
    },
    "obd_data": {
        "fuel_level": 78.2,
        "engine_status": "ON",
        "rpm": 900,
        "speed": 15,
        "error_codes": ["P0420"]
    }
}

print(f"Đang gửi Heartbeat tới: {API_URL}")
print(f"Headers: {headers}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(API_URL, json=payload, headers=headers)

    # 3. Kiểm tra kết quả
    if response.status_code == 202: # 202 Accepted
        print("\n--- THÀNH CÔNG (202) ---")
        print("Máy chủ đã chấp nhận Heartbeat.")
        
    elif response.status_code == 401:
        print("\n--- LỖI XÁC THỰC (401) ---")
        print("X-API-Key không hợp lệ hoặc bị thiếu.")
        
    elif response.status_code == 404:
        print("\n--- LỖI XÁC THỰC (404) ---")
        print("X-Device-ID không tồn tại.")
        
    elif response.status_code == 422:
        print("\n--- LỖI DỮ LIỆU (422) ---")
        print(f"Payload gửi đi không hợp lệ: {response.text}")
        
    else:
        print(f"\n--- LỖI KHÁC ({response.status_code}) ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- LỖI KẾT NỐI ---")
