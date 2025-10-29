import requests
import json

# Tọa độ kiểm tra (gần GAS001 và GAS003)
VI_DO = 10.7798
KINH_DO = 106.7020

# 1. Bán kính nhỏ (1 km): Chỉ nên thấy 2 trạm xăng
# 2. Bán kính lớn (5 km): Sẽ thấy thêm trạm sạc và gara
params = {
    'vi_do': 10.7845,
    'kinh_do': 106.7020,
    'ban_kinh_km': 1.0, # Thử với bán kính 1km
    'loai_diem': 'tram_sac' # Chỉ tìm cây xăng
}

API_URL = "http://127.0.0.1:8000/cac-diem-xung-quanh"

print(f"Đang gọi API tại: {API_URL}")
print(f"Với tham số: {params}\n")

try:
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        print(f"--- GỌI API THÀNH CÔNG (Tìm thấy {len(data)} điểm) ---")
        
        # In kết quả đẹp mắt
        print(json.dumps(data, indent=4, ensure_ascii=False))
        
        print("\n--- TÓM TẮT KẾT QUẢ (Trong 1.0 km) ---")
        for diem in data:
            print(f"- {diem.get('ten')} (Cách: {diem.get('khoang_cach_km')} km)")
            
    else:
        print(f"--- GỌI API THẤT BẠI ---")
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Nội dung lỗi: {response.text}")

except requests.exceptions.ConnectionError:
    print("--- LỖI KẾT NỐI ---")
    print("Không thể kết nối tới API.")
