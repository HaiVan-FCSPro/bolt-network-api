import requests
import json

API_URL = "http://127.0.0.1:8000/tim-diem-gan-nhat"

params = {
    'vi_do': 10.7798,
    'kinh_do': 106.7020,
    'loai_diem': 'xang_dau'
}

print(f"Đang gọi API tại: {API_URL}...")
print(f"Với tham số: {params}\n")

try:
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        print("--- GỌI API THÀNH CÔNG ---")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("\n--- TÓM TẮT KẾT QUẢ ---")
        print(f"Đã tìm thấy: {data.get('ten')}")
        print(f"Khoảng cách: {data.get('khoang_cach_km')} km")
    else:
        print(f"--- GỌI API THẤT BẠI ---")
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Nội dung lỗi: {response.text}")

except requests.exceptions.ConnectionError:
    print("--- LỖI KẾT NỐI ---")
    print("Không thể kết nối tới API. Hãy đảm bảo máy chủ 'uvicorn' đang chạy trong Terminal 1.")
