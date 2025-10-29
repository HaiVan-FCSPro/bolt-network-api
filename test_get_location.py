import requests
import json

API_URL = "http://127.0.0.1:8000/device/location/last"

# Sử dụng cùng thông tin xác thực với 'test_heartbeat.py'
headers = {
    "X-Device-ID": "BOLT-TEST-001",
    "X-API-Key": "bolt_secret_key_for_testing"
}

print(f"Đang gọi API 'Tìm xe' tại: {API_URL}")
print(f"Headers: {headers}\n")

try:
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("--- THÀNH CÔNG (200) ---")
        print("Đã tìm thấy vị trí cuối cùng của xe:")
        print(json.dumps(data, indent=2))
        
    elif response.status_code == 404:
        print("\n--- KHÔNG TÌM THẤY (404) ---")
        print("Không tìm thấy dữ liệu vị trí. Bạn đã chạy 'test_heartbeat.py' trước chưa?")
        
    elif response.status_code == 401:
        print("\n--- LỖI XÁC THỰC (401) ---")
        print("X-API-Key không hợp lệ.")
        
    else:
        print(f"\n--- LỖI KHÁC ({response.status_code}) ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- LỖI KẾT NỐI ---")
