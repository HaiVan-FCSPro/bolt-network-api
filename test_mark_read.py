import datetime
import requests
import json
import sys

# --- CONFIG ---
ALERT_ID_TO_MARK = None # Will be filled later
DEVICE_ID = "BOLT-TEST-001"
API_KEY = "bolt_secret_key_for_testing"
BASE_URL = "http://127.0.0.1:8000"

HEADERS = {
    "X-Device-ID": DEVICE_ID,
    "X-API-Key": API_KEY
}

# --- FUNCTIONS ---
def get_unread_alerts():
    print("\n--- Đang lấy cảnh báo chưa đọc ---")
    try:
        response = requests.get(f"{BASE_URL}/device/alerts", headers=HEADERS)
        response.raise_for_status() # Raise exception for bad status codes
        alerts = response.json()
        print(f"Tìm thấy {len(alerts)} cảnh báo chưa đọc:")
        print(json.dumps(alerts, indent=2))
        return alerts
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy cảnh báo: {e}")
        sys.exit(1) # Exit if we can't get alerts

def mark_alert_read(alert_id):
    print(f"\n--- Đang đánh dấu alert '{alert_id}' là đã đọc ---")
    url = f"{BASE_URL}/device/alerts/{alert_id}/read"
    try:
        response = requests.put(url, headers=HEADERS)
        if response.status_code == 204:
            print("--- THÀNH CÔNG (204) ---")
            print("Đã đánh dấu cảnh báo là đã đọc.")
        elif response.status_code == 404:
            print("--- LỖI (404) ---")
            print("Không tìm thấy cảnh báo này hoặc nó đã được đọc.")
        else:
            print(f"--- LỖI KHÁC ({response.status_code}) ---")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi đánh dấu đã đọc: {e}")

# --- MAIN SCRIPT ---

# 1. Get initial alerts (should be 0 after restart)
initial_alerts = get_unread_alerts()
if initial_alerts:
     print("Cảnh báo: Lẽ ra phải thấy 0 cảnh báo sau khi khởi động lại. Tiếp tục...")

# 2. Trigger low fuel alert
print("\n--- Đang tạo cảnh báo nhiên liệu thấp ---")
try:
     requests.post(f"{BASE_URL}/device/heartbeat", headers={**HEADERS, "Content-Type": "application/json"}, json={
         "timestamp": datetime.datetime.now().isoformat(),
         "location": {"lat": 10.7798, "lon": 106.7020},
         "obd_data": {"fuel_level": 15.0}
     }).raise_for_status()
     print("-> Đã gửi heartbeat nhiên liệu thấp.")
except requests.exceptions.RequestException as e:
     print(f"Lỗi khi tạo cảnh báo nhiên liệu: {e}")
     sys.exit(1)

# 3. Get alerts again to find the new one
alerts_after_fuel = get_unread_alerts()
if not alerts_after_fuel:
     print("Lỗi: Không tìm thấy cảnh báo nhiên liệu thấp vừa tạo!")
     sys.exit(1)

# 4. Pick the first alert ID to mark as read
ALERT_ID_TO_MARK = alerts_after_fuel[0]['alert_id']

# 5. Mark it as read
mark_alert_read(ALERT_ID_TO_MARK)

# 6. Get alerts one last time
final_alerts = get_unread_alerts()
print("\n--- KẾT QUẢ CUỐI CÙNG ---")
if len(final_alerts) == len(alerts_after_fuel) - 1:
     print("✅ Xác minh thành công: Số lượng cảnh báo chưa đọc đã giảm đi 1.")
else:
     print(f"❌ Xác minh thất bại: Lẽ ra phải thấy {len(alerts_after_fuel) - 1} cảnh báo, nhưng thấy {len(final_alerts)}.")
