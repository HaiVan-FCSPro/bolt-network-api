import math

def tinh_khoang_cach(lat1, lon1, lat2, lon2):
    """
    Hàm này tính khoảng cách giữa 2 điểm tọa độ (tính bằng km)
    sử dụng công thức Haversine.
    """
    R = 6371  # Bán kính của Trái Đất tính bằng km
    
    # Chuyển đổi độ sang radian
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Chênh lệch kinh độ và vĩ độ
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Áp dụng công thức Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    khoang_cach = R * c
    return khoang_cach

def tim_diem_gan_nhat(vi_do_nguoi_dung, kinh_do_nguoi_dung, danh_sach_diem, loai_diem=None):
    """
    Tìm điểm dịch vụ gần nhất từ vị trí người dùng.
    Có thể lọc theo loại điểm dịch vụ (ví dụ: 'xang_dau').
    """
    diem_gan_nhat = None
    khoang_cach_ngan_nhat = float('inf')

    # Lọc danh sách nếu người dùng chỉ định loại điểm
    danh_sach_can_quet = danh_sach_diem
    if loai_diem:
        danh_sach_can_quet = [diem for diem in danh_sach_diem if diem['loai'] == loai_diem]

    if not danh_sach_can_quet:
        return "Không tìm thấy điểm dịch vụ nào phù hợp."

    # Duyệt qua từng điểm để tìm điểm gần nhất
    for diem in danh_sach_can_quet:
        khoang_cach = tinh_khoang_cach(vi_do_nguoi_dung, kinh_do_nguoi_dung, diem['vi_do'], diem['kinh_do'])
        if khoang_cach < khoang_cach_ngan_nhat:
            khoang_cach_ngan_nhat = khoang_cach
            diem_gan_nhat = diem
            
    # Thêm thông tin khoảng cách vào kết quả trả về
    diem_gan_nhat['khoang_cach_km'] = round(khoang_cach_ngan_nhat, 2)
    
    return diem_gan_nhat

# --- VÍ DỤ SỬ DỤNG ---

# 1. Cơ sở dữ liệu mẫu của chúng ta
CSDL_diem_dich_vu = [
  { "id": "GAS001", "ten": "Cây xăng Petrolimex", "loai": "xang_dau", "vi_do": 10.7769, "kinh_do": 106.7009 },
  { "id": "GAS002", "ten": "Cây xăng Comeco", "loai": "xang_dau", "vi_do": 10.7811, "kinh_do": 106.6982 },
  { "id": "EV001", "ten": "Trạm sạc VinFast", "loai": "tram_sac", "vi_do": 10.7852, "kinh_do": 106.6954 },
  { "id": "GARAGE001", "ten": "Garage Auto A+", "loai": "sua_chua", "vi_do": 10.7714, "kinh_do": 106.6682 }
]

# 2. Giả sử vị trí hiện tại của người dùng
vi_tri_hien_tai_lat = 10.7800
vi_tri_hien_tai_lon = 106.6990

# 3. Tìm cây xăng gần nhất
cay_xang_gan_nhat = tim_diem_gan_nhat(vi_tri_hien_tai_lat, vi_tri_hien_tai_lon, CSDL_diem_dich_vu, loai_diem="xang_dau")
print(f"Cây xăng gần nhất là: {cay_xang_gan_nhat['ten']}")
print(f"Khoảng cách: {cay_xang_gan_nhat['khoang_cach_km']} km")
print("-" * 20)

# 4. Tìm trạm sạc gần nhất
tram_sac_gan_nhat = tim_diem_gan_nhat(vi_tri_hien_tai_lat, vi_tri_hien_tai_lon, CSDL_diem_dich_vu, loai_diem="tram_sac")
print(f"Trạm sạc gần nhất là: {tram_sac_gan_nhat['ten']}")
print(f"Khoảng cách: {tram_sac_gan_nhat['khoang_cach_km']} km")
