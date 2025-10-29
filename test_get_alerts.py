import requests
import json

API_URL = "http://127.0.0.1:8000/device/alerts"

# Sử dụng cùng thông tin xác thực
headers = {
    "X-Device-ID": "BOLT-TEST-001",
    "X-API-Key": "bolt_secret_key_for_testing"
}

print(f"Đang gọi API 'Lấy Cảnh báo' tại: {API_URL}")
print(f"Headers: {headers}\n")

try:
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"--- THÀNH CÔNG (200) ---")
        print(f"Tìm thấy {len(data)} cảnh báo mới chưa đọc:")
        print(json.dumps(data, indent=2))
        
    elif response.status_code == 401:
        print("\n--- LỖI XÁC THỰC (401) ---")
        print("X-API-Key không hợp lệ.")
        
    else:
        print(f"\n--- LỖI KHÁC ({response.status_code}) ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- LỖI KẾT NỐI ---")
