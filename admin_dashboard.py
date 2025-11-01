# === admin_dashboard.py v3.0 (Fleet Management) ===
import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time

# --- CẤU HÌNH v3.0 (ADMIN) ---
# Đọc thông tin xác thực ADMIN từ Trình quản lý Secrets của Streamlit
try:
    ADMIN_API_KEY = st.secrets["ADMIN_API_KEY"]
    API_BASE_URL = st.secrets["API_BASE_URL"]
except KeyError:
    st.error("Lỗi: Không thể tải ADMIN_API_KEY / API_BASE_URL. Vui lòng thêm secrets vào Streamlit Cloud.")
    st.stop()

# Xây dựng các endpoint Admin
ADMIN_DEVICES_URL = f"{API_BASE_URL}/admin/devices"
# Các URL (vị trí, cảnh báo) sẽ được xây dựng động sau khi chọn thiết bị

# --- CÁC HÀM GỌI API (v3.0) ---

def get_admin_headers():
    """Tạo header xác thực Admin."""
    return {
        "X-Admin-Api-Key": ADMIN_API_KEY
    }

@st.cache_data(ttl=60) # Cache danh sách thiết bị trong 60s
def get_fleet_list():
    """
    (BƯỚC A) Tải Hạm đội: Gọi GET /admin/devices
    """
    try:
        response = requests.get(ADMIN_DEVICES_URL, headers=get_admin_headers(), timeout=10)
        if response.status_code == 200:
            devices = response.json()
            # Trả về danh sách các (tên hiển thị, id)
            return [(f"{d['id']} ({d.get('vehicle_model', 'N/A')})", d['id']) for d in devices]
        else:
            st.error(f"Lỗi tải Hạm đội (API {response.status_code}): {response.text}")
            return []
    except Exception as e:
        st.error(f"Lỗi kết nối khi tải Hạm đội: {e}")
        return []

@st.cache_data(ttl=15) # Cache dữ liệu thiết bị trong 15s
def get_device_data(device_id: str):
    """
    (BƯỚC C) Tải Dữ liệu Động cho thiết bị đã chọn.
    """
    if not device_id:
        return None, []
        
    location_url = f"{API_BASE_URL}/admin/devices/{device_id}/location"
    alerts_url = f"{API_BASE_URL}/admin/devices/{device_id}/alerts"
    
    location_data = None
    alerts_data = []
    
    try:
        # Lấy Vị trí
        response_loc = requests.get(location_url, headers=get_admin_headers(), timeout=10)
        if response_loc.status_code == 200:
            location_data = response_loc.json()
        elif response_loc.status_code == 404:
             st.warning(f"Thiết bị '{device_id}' chưa có dữ liệu vị trí.")
        else:
            st.error(f"Lỗi tải Vị trí (API {response_loc.status_code}): {response_loc.text}")

        # Lấy Cảnh báo
        response_alerts = requests.get(alerts_url, headers=get_admin_headers(), timeout=10)
        if response_alerts.status_code == 200:
            alerts_data = sorted(response_alerts.json(), key=lambda x: x['timestamp'], reverse=True)
        else:
            st.error(f"Lỗi tải Cảnh báo (API {response_alerts.status_code}): {response_alerts.text}")
            
    except Exception as e:
        st.error(f"Lỗi kết nối API khi tải dữ liệu thiết bị: {e}")
        
    return location_data, alerts_data

def mark_alert_as_read(alert_id: str):
    """
    Gọi API 'PUT /admin/alerts/{alert_id}/read' (Endpoint Admin mới)
    """
    mark_url = f"{API_BASE_URL}/admin/alerts/{alert_id}/read"
    
    try:
        response = requests.put(mark_url, headers=get_admin_headers(), timeout=10)
        
        if response.status_code == 204:
            st.success(f"Đã đánh dấu cảnh báo là đã đọc!")
            # XÓA CACHE VÀ TẢI LẠI TRANG
            st.cache_data.clear() # Xóa toàn bộ cache
            st.rerun()
        else:
            st.error(f"Lỗi {response.status_code} khi đánh dấu đã đọc: {response.text}")
            
    except Exception as e:
        st.error(f"Lỗi kết nối khi đánh dấu đã đọc: {e}")

# --- XÂY DỰNG GIAO DIỆN (UI v3.0) ---

st.set_page_config(layout="wide")
st.title("🛰️ Bảng điều khiển Quản lý Hạm đội BOLT")

# --- (BƯỚC A & B) Tải Hạm đội & Selectbox ---
fleet_list = get_fleet_list()

if not fleet_list:
    st.error("Không thể tải danh sách Hạm đội từ API. Vui lòng kiểm tra ADMIN_API_KEY và API Server.")
    st.stop()

# Tạo selectbox
# format_func giúp selectbox chỉ hiển thị tên (index 0), nhưng trả về ID (index 1)
selected_device_tuple = st.selectbox(
    "Chọn Thiết bị Giám sát:",
    fleet_list,
    format_func=lambda x: x[0] # Hiển thị "BOLT-RPi-001 (Pi 5)"
)

# Lấy ID của thiết bị đã chọn
selected_device_id = selected_device_tuple[1] if selected_device_tuple else None

st.divider()

if st.button("Tải lại Dữ liệu (Refresh)"):
    st.cache_data.clear()
    st.rerun()

# --- (BƯỚC C) Tải Dữ liệu Động ---
location, alerts = get_device_data(selected_device_id)

col1, col2 = st.columns([2, 3])

# --- CỘT 1: BẢN ĐỒ VỊ TRÍ ---
with col1:
    st.header(f"📍 Vị trí Thiết bị (Live)")
    
    if location:
        last_seen_dt = datetime.fromisoformat(location['last_seen'])
        st.subheader(f"Cập nhật lần cuối: {last_seen_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        lat = location['last_lat']
        lon = location['last_lon']
        
        m = folium.Map(location=[lat, lon], zoom_start=15)
        folium.Marker(
            [lat, lon],
            popup=f"<b>{selected_device_id}</b><br>Lat: {lat}<br>Lon: {lon}",
            tooltip=f"Last Seen: {last_seen_dt.strftime('%H:%M:%S')}"
        ).add_to(m)
        
        st_folium(m, width='stretch', height=450)
    else:
        st.info("Chưa có dữ liệu vị trí cho thiết bị này.")

# --- CỘT 2: DANH SÁCH CẢNH BÁO (TƯƠNG TÁC) ---
with col2:
    st.header(f"🔔 Cảnh báo Chưa đọc ({len(alerts)})")

    if alerts:
        hdr_cols = st.columns([0.25, 0.15, 0.45, 0.15])
        hdr_cols[0].markdown("**Thời gian**")
        hdr_cols[1].markdown("**Loại**")
        hdr_cols[2].markdown("**Nội dung**")
        hdr_cols[3].markdown("**Hành động**")
        st.divider()

        for alert in alerts:
            alert_id = alert['alert_id']
            dt_obj = datetime.fromisoformat(alert['timestamp'])
            timestamp_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            row_cols = st.columns([0.25, 0.15, 0.45, 0.15])
            
            row_cols[0].text(timestamp_str)
            row_cols[1].text(alert['alert_type'])
            row_cols[2].text(alert['message'])
            
            if row_cols[3].button("Đọc", key=alert_id, help=f"Đánh dấu cảnh báo {alert_id} là đã đọc"):
                mark_alert_as_read(alert_id)
            
            st.divider()

    elif location:
        st.success("Tốt! Không có cảnh báo nào chưa đọc.")
    else:
        st.info("Chưa có dữ liệu cảnh báo cho thiết bị này.")
