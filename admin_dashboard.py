import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time

import streamlit as st # Đảm bảo import streamlit ở đầu file

# --- CẤU HÌNH LIVE PRODUCTION (v2.1 - CLOUD READY) ---
# Đọc thông tin xác thực từ Trình quản lý Secrets của Streamlit
try:
    DEVICE_ID = st.secrets["DEVICE_ID"]
    API_KEY = st.secrets["API_KEY"]
    API_BASE_URL = st.secrets["API_BASE_URL"]
except KeyError:
    st.error("Lỗi: Không thể tải cấu hình secrets. Vui lòng thêm secrets vào Streamlit Cloud.")
    st.stop()

# Endpoints API Live (Xây dựng từ secrets)
LOCATION_URL = f"{API_BASE_URL}/device/location/last"
ALERTS_URL = f"{API_BASE_URL}/device/alerts"
# --- CÁC HÀM GỌI API ---

@st.cache_data(ttl=60) # Cache dữ liệu trong 60 giây
def get_live_data():
    """
    Gọi cả hai endpoint Location và Alerts để lấy dữ liệu mới nhất.
    """
    headers = {
        "X-Device-ID": DEVICE_ID,
        "X-API-Key": API_KEY
    }
    
    location_data = None
    alerts_data = []
    
    try:
        # Lấy Vị trí
        response_loc = requests.get(LOCATION_URL, headers=headers, timeout=10)
        if response_loc.status_code == 200:
            location_data = response_loc.json()
        
        # Lấy Cảnh báo
        response_alerts = requests.get(ALERTS_URL, headers=headers, timeout=10)
        if response_alerts.status_code == 200:
            # Sắp xếp cảnh báo, mới nhất lên đầu
            alerts_data = sorted(response_alerts.json(), key=lambda x: x['timestamp'], reverse=True)
            
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối API: {e}")
        
    return location_data, alerts_data

def mark_alert_as_read(alert_id: str):
    """
    (P1) GỌI API 'PUT /device/alerts/{alert_id}/read'
    """
    mark_url = f"{API_BASE_URL}/device/alerts/{alert_id}/read"
    headers = {
        "X-Device-ID": DEVICE_ID,
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.put(mark_url, headers=headers, timeout=10)
        
        if response.status_code == 204:
            st.success(f"Đã đánh dấu cảnh báo {alert_id} là đã đọc!")
            # XÓA CACHE VÀ TẢI LẠI TRANG
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(f"Lỗi {response.status_code} khi đánh dấu đã đọc: {response.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối khi đánh dấu đã đọc: {e}")


# --- XÂY DỰNG GIAO DIỆN (UI v2.0) ---

# Cấu hình trang: Sử dụng bố cục rộng (wide layout)
st.set_page_config(layout="wide")

# Tiêu đề chính
st.title(f"📊 Bảng điều khiển BOLT Network (Device: {DEVICE_ID})")

# Nút Tải lại (Refresh)
if st.button("Tải lại Dữ liệu (Refresh)"):
    # Xóa cache và chạy lại script
    st.cache_data.clear()
    st.rerun()

# Tải dữ liệu
location, alerts = get_live_data()

# Chia giao diện thành 2 cột chính
col1, col2 = st.columns([2, 3]) # Cột 1 rộng 2 phần, cột 2 rộng 3 phần

# --- CỘT 1: BẢN ĐỒ VỊ TRÍ ---
with col1:
    st.header("📍 Vị trí Thiết bị (Live)")
    
    if location:
        last_seen_dt = datetime.fromisoformat(location['last_seen'])
        st.subheader(f"Cập nhật lần cuối: {last_seen_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        lat = location['last_lat']
        lon = location['last_lon']
        
        m = folium.Map(location=[lat, lon], zoom_start=15)
        
        folium.Marker(
            [lat, lon],
            popup=f"<b>{DEVICE_ID}</b><br>Lat: {lat}<br>Lon: {lon}",
            tooltip=f"Last Seen: {last_seen_dt.strftime('%H:%M:%S')}"
        ).add_to(m)
        
        # (P2) FIX: Thay thế 'use_container_width' bằng 'width'
        st_folium(m, width='stretch', height=450)

    else:
        st.error("Không thể tải dữ liệu vị trí.")

# --- CỘT 2: DANH SÁCH CẢNH BÁO (TƯƠNG TÁC) ---
with col2:
    st.header(f"🔔 Cảnh báo Chưa đọc ({len(alerts)})")

    if alerts:
        # (P1) Tạo tiêu đề cho danh sách
        hdr_cols = st.columns([0.25, 0.15, 0.45, 0.15])
        hdr_cols[0].markdown("**Thời gian**")
        hdr_cols[1].markdown("**Loại**")
        hdr_cols[2].markdown("**Nội dung**")
        hdr_cols[3].markdown("**Hành động**")
        st.divider()

        # (P2) FIX: Loại bỏ Pandas, tránh SettingWithCopyWarning
        for alert in alerts:
            alert_id = alert['alert_id']
            
            # Định dạng timestamp bằng Python (thay vì Pandas)
            dt_obj = datetime.fromisoformat(alert['timestamp'])
            timestamp_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            # Tạo các cột cho mỗi hàng cảnh báo
            row_cols = st.columns([0.25, 0.15, 0.45, 0.15])
            
            row_cols[0].text(timestamp_str)
            row_cols[1].text(alert['alert_type'])
            row_cols[2].text(alert['message'])
            
            # (P1) Nút "Đánh dấu Đã đọc"
            if row_cols[3].button("Đọc", key=alert_id, help=f"Đánh dấu cảnh báo {alert_id} là đã đọc"):
                # Khi nhấn nút, gọi hàm xử lý
                mark_alert_as_read(alert_id)
            
            st.divider()

    elif location: # Nếu kết nối thành công nhưng không có cảnh báo
        st.success("Tốt! Không có cảnh báo nào chưa đọc.")
    else:
        st.error("Không thể tải dữ liệu cảnh báo.")
