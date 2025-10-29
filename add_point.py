import requests
import json

# Dữ liệu điểm dịch vụ mới chúng ta muốn thêm
diem_moi = {
    "id": "GAS003",
    "ten": "Cây xăng Shell (Mới)",
    "loai": "xang_dau",
    "dia_chi": "555 Đường Đồng Khởi, Quận 1, TP. HCM",
    "vi_do": 10.7795,
    "kinh_do": 106.7025
}

API_URL = "http://127.0.0.1:8000/diem-dich-vu"

print(f"Đang gửi dữ liệu điểm mới tới: {API_URL}")
print("Dữ liệu:")
print(json.dumps(diem_moi, indent=4, ensure_ascii=False))

try:
    # Thực hiện cuộc gọi POST, gửi dữ liệu dưới dạng JSON
    response = requests.post(API_URL, json=diem_moi)

    if response.status_code == 201: # 201 = Created
        print("\n--- THÊM MỚI THÀNH CÔNG ---")
        print("Dữ liệu đã được lưu vào CSDL:")
        print(response.text)
        
    elif response.status_code == 422: # Lỗi validation
        print(f"\n--- LỖI DỮ LIỆU ĐẦU VÀO (422) ---")
        print("Dữ liệu gửi đi không hợp lệ. Chi tiết:")
        print(response.text)
        
    else:
        print(f"\n--- LỖI MÁY CHỦ ---")
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Nội dung lỗi: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n--- LỖI KẾT NỐI ---")
    print("Không thể kết nối tới API. Hãy đảm bảo máy chủ 'uvicorn' đang chạy.")
