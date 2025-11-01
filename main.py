# === main.py v0.14.0 (Seed Location Fix) ===
import math
import datetime
import uuid
from enum import Enum
from fastapi import FastAPI, HTTPException, Query, Depends, Header, status, Path
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, text, Column, String, Float, MetaData, Table, BigInteger, DateTime, func, Boolean, UUID
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings
from passlib.context import CryptContext

# --- 1. SETTINGS ---
class Settings(BaseSettings):
    DATABASE_URL: str
    class Config: env_file = ".env"
settings = Settings()

# --- CONSTANTS ---
LOW_FUEL_THRESHOLD = 20.0
TEST_DEVICE_ID = "BOLT-TEST-001" # Thiết bị mặc định cho mocking

# --- 2. DATABASE ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"]) # Fixed syntax warning

# --- 2a, 2b, 2c. BẢNG DỮ LIỆU (Giữ nguyên) ---
diem_dich_vu_table = Table(
    "diem_dich_vu", metadata,
    Column("id", String, primary_key=True), Column("ten", String, nullable=False),
    Column("loai", String, nullable=False), Column("dia_chi", String),
    Column("vi_do", Float, nullable=False), Column("kinh_do", Float, nullable=False)
)
devices_table = Table(
    "devices", metadata,
    Column("id", String, primary_key=True), Column("api_key_hash", String, nullable=False),
    Column("vehicle_make", String), Column("vehicle_model", String)
)
device_locations_table = Table(
    "device_locations", metadata,
    Column("device_id", String, primary_key=True),
    Column("last_lat", Float, nullable=False), Column("last_lon", Float, nullable=False),
    Column("last_seen", DateTime, nullable=False, default=func.now())
)
obd_logs_table = Table(
    "obd_logs", metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("device_id", String, nullable=False),
    Column("timestamp", DateTime, nullable=False, default=func.now()),
    Column("fuel_level", Float), Column("rpm", BigInteger),
    Column("speed", BigInteger), Column("error_codes", String)
)
user_alerts_table = Table(
    "user_alerts", metadata,
    Column("alert_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("device_id", String, nullable=False),
    Column("timestamp", DateTime, default=func.now()),
    Column("alert_type", String, nullable=False),
    Column("message", String, nullable=False),
    Column("is_read", Boolean, default=False, nullable=False)
)

# DB Dependency (Giữ nguyên)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. PYDANTIC MODELS (Giữ nguyên) ---
class DiemDichVuInputModel(BaseModel): id: str; ten: str; loai: str; dia_chi: Optional[str] = None; vi_do: float; kinh_do: float
class DiemDichVuResponseModel(BaseModel): id: str; ten: str; loai: str; dia_chi: Optional[str] = None; vi_do: float; kinh_do: float; khoang_cach_km: float
class LocationModel(BaseModel): lat: float; lon: float
class OBDDataModel(BaseModel): fuel_level: Optional[float] = None; engine_status: Optional[str] = None; rpm: Optional[int] = None; speed: Optional[int] = None; error_codes: Optional[List[str]] = []
class DeviceHeartbeatModel(BaseModel): timestamp: datetime.datetime; location: LocationModel; obd_data: OBDDataModel
class DeviceLocationResponse(BaseModel): device_id: str; last_lat: float; last_lon: float; last_seen: datetime.datetime
class AlertType(str, Enum): LOW_FUEL = "LOW_FUEL"; ERROR_CODE = "ERROR_CODE"
class UserAlertResponse(BaseModel): alert_id: uuid.UUID; device_id: str; timestamp: datetime.datetime; alert_type: AlertType; message: str; is_read: bool
class MockLocationInput(BaseModel):
    lat: float
    lon: float
    device_id: Optional[str] = TEST_DEVICE_ID
    
    @validator('device_id', pre=True, always=True)
    def check_device_id(cls, v):
        if not v:
            return TEST_DEVICE_ID
        return v


# --- 4. LIFESPAN (ĐÃ SỬA seed_initial_data) ---
def seed_initial_data(db: Session):
    CSDL_MAU = [
      { "id": "GAS001", "ten": "Cây xăng Petrolimex", "loai": "xang_dau", "dia_chi": "123 Đường ABC, Quận 1, TP. HCM", "vi_do": 10.7769, "kinh_do": 106.7009 },
      { "id": "GAS002", "ten": "Cây xăng Comeco", "loai": "xang_dau", "dia_chi": "456 Đường DEF, Quận 3, TP. HCM", "vi_do": 10.7811, "kinh_do": 106.6982 },
      { "id": "EV001", "ten": "Trạm sạc VinFast", "loai": "tram_sac", "dia_chi": "789 Đường GHI, Quận 1, TP. HCM", "vi_do": 10.7852, "kinh_do": 106.6954 },
      { "id": "GARAGE001", "ten": "Garage Auto A+", "loai": "sua_chua", "dia_chi": "101 Đường JKL, Quận 10, TP. HCM", "vi_do": 10.7714, "kinh_do": 106.6682 }
    ]
    stmt_map = text("INSERT INTO diem_dich_vu (id, ten, loai, dia_chi, vi_do, kinh_do) VALUES (:id, :ten, :loai, :dia_chi, :vi_do, :kinh_do) ON CONFLICT (id) DO NOTHING")
    for diem in CSDL_MAU: db.execute(stmt_map, diem)
    
    # --- SEED DEVICES ---
    PLAINTEXT_API_KEY = "bolt_secret_key_for_testing"
    HASHED_API_KEY = pwd_context.hash(PLAINTEXT_API_KEY)
    stmt_device = text("INSERT INTO devices (id, api_key_hash, vehicle_make, vehicle_model) VALUES (:id, :api_key_hash, :vehicle_make, :vehicle_model) ON CONFLICT (id) DO NOTHING")
    # Device TEST
    db.execute(stmt_device, {"id": TEST_DEVICE_ID, "api_key_hash": HASHED_API_KEY, "vehicle_make": "ThinkPad", "vehicle_model": "DevClient"})
    # Device LIVE
    PROD_DEVICE_ID = "BOLT-RPi-001"
    PLAINTEXT_PROD_KEY = "ProdKey_RPi001_!@#"
    HASHED_PROD_KEY = pwd_context.hash(PLAINTEXT_PROD_KEY)
    db.execute(stmt_device, {"id": PROD_DEVICE_ID, "api_key_hash": HASHED_PROD_KEY, "vehicle_make": "Raspberry", "vehicle_model": "Pi 5"})
    
    # --- THÊM VỊ TRÍ MẶC ĐỊNH (FIX LỖI 404 KHI LẤY LẦN ĐẦU) ---
    stmt_location_seed = text("""
    INSERT INTO device_locations (device_id, last_lat, last_lon, last_seen)
    VALUES (:device_id, 0.0, 0.0, NOW())
    ON CONFLICT (device_id) DO NOTHING
    """)
    db.execute(stmt_location_seed, {"device_id": TEST_DEVICE_ID})
    db.execute(stmt_location_seed, {"device_id": PROD_DEVICE_ID})

    db.commit()
    print("Khởi tạo/Seed CSDL Postgres thành công (Phase 1, 2 & Initial Location).")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API đang khởi động... kết nối tới PostgreSQL...")
    try:
        with engine.begin() as conn: metadata.create_all(conn)
        with SessionLocal() as db: seed_initial_data(db)
    except Exception as e: print(f"LỖI NGHIÊM TRỌNG KHI KẾT NỐI/KHỞI TẠO CSDL: {e}")
    yield; print("Máy chủ đang tắt...")

# --- 5. APP (Giữ nguyên) ---
app = FastAPI(
    title="BOLT Network API",
    description="API lõi cho Hệ sinh thái Giao thông Thông minh BOLT",
    version="0.14.0 (Location Seeded)",
    lifespan=lifespan
)

# --- 6. CẤU HÌNH CORS (Giữ nguyên) ---
origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- 7. CÔNG THỨC HAVERSINE (Giữ nguyên) ---
HAVERSINE_SQL = """( 6371 * 2 * ASIN( SQRT(
    SIN((RADIANS(vi_do) - RADIANS(:user_lat)) / 2) ^ 2 +
    COS(RADIANS(:user_lat)) * COS(RADIANS(vi_do)) *
    SIN((RADIANS(kinh_do) - RADIANS(:user_lon)) / 2) ^ 2
)))"""

# --- 8. BẢO MẬT (Giữ nguyên) ---
async def get_current_device(x_device_id: str = Header(...), x_api_key: str = Header(...), db: Session = Depends(get_db)) -> str:
    stmt = text("SELECT api_key_hash FROM devices WHERE id = :device_id")
    result = db.execute(stmt, {"device_id": x_device_id}).fetchone()
    if not result: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device ID not registered")
    stored_hash = result[0]
    if not pwd_context.verify(x_api_key, stored_hash): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_device_id

# --- 9. HÀM LOGIC NỘI BỘ ---
def _tim_diem_gan_nhat_logic(db: Session, vi_do: float, kinh_do: float, loai_diem: Optional[str] = None) -> Optional[dict]:
    params = {"user_lat": vi_do, "user_lon": kinh_do}
    base_query = f"SELECT *, {HAVERSINE_SQL} AS khoang_cach_km FROM diem_dich_vu"
    where_clause = ""
    if loai_diem: where_clause = " WHERE loai = :loai"; params["loai"] = loai_diem
    query = text(f"{base_query} {where_clause} ORDER BY khoang_cach_km ASC LIMIT 1")
    try:
        result = db.execute(query, params).fetchone()
        if not result: return None
        ket_qua = dict(result._mapping); ket_qua['khoang_cach_km'] = round(ket_qua['khoang_cach_km'], 2)
        return ket_qua
    except Exception as e: print(f"--- [LỖI LOGIC] Lỗi khi tìm điểm gần nhất (nội bộ): {e} ---"); return None

# --- 10. AI TRIGGER ---
def _trigger_proactive_alerts(db: Session, device_id: str, payload: DeviceHeartbeatModel):
    vi_tri_xe = payload.location
    stmt_insert_alert = text("INSERT INTO user_alerts (alert_id, device_id, timestamp, alert_type, message, is_read) VALUES (:alert_id, :device_id, :timestamp, :alert_type, :message, false)")
    # Fuel check
    try:
        fuel = payload.obd_data.fuel_level
        if fuel is not None and fuel < LOW_FUEL_THRESHOLD:
            print(f"--- [AI Phân tích] Phát hiện nhiên liệu thấp ({fuel}%) cho {device_id} ---")
            tram_xang = _tim_diem_gan_nhat_logic(db=db, vi_do=vi_tri_xe.lat, kinh_do=vi_tri_xe.lon, loai_diem="xang_dau")
            if tram_xang:
                msg = f"Nhiên liệu thấp ({fuel}%)! Trạm xăng gần nhất: {tram_xang.get('ten')} (cách {tram_xang.get('khoang_cach_km')} km)."
                db.execute(stmt_insert_alert, {"alert_id": uuid.uuid4(), "device_id": device_id, "timestamp": payload.timestamp, "alert_type": AlertType.LOW_FUEL, "message": msg})
                print("--- [AI CẢNH BÁO] Đã lưu cảnh báo Nhiên liệu thấp vào CSDL. ---")
    except Exception as e: print(f"--- [LỖI AI] Lỗi khi xử lý cảnh báo nhiên liệu: {e} ---")
    # Error code check
    try:
        error_codes = payload.obd_data.error_codes
        if error_codes:
            codes_str = ", ".join(error_codes)
            print(f"--- [AI Phân tích] Phát hiện Mã lỗi Động cơ ({codes_str}) cho {device_id} ---")
            gara = _tim_diem_gan_nhat_logic(db=db, vi_do=vi_tri_xe.lat, kinh_do=vi_tri_xe.lon, loai_diem="sua_chua")
            if gara:
                msg = f"Phát hiện Mã lỗi ({codes_str})! Gara gần nhất: {gara.get('ten')} (cách {gara.get('khoang_cach_km')} km)."
                db.execute(stmt_insert_alert, {"alert_id": uuid.uuid4(), "device_id": device_id, "timestamp": payload.timestamp, "alert_type": AlertType.ERROR_CODE, "message": msg})
                print("--- [AI CẢNH BÁO] Đã lưu cảnh báo Mã lỗi vào CSDL. ---")
    except Exception as e: print(f"--- [LỖI AI] Lỗi khi xử lý cảnh báo mã lỗi: {e} ---")

# --- 11. API ENDPOINTS (PHASE 1) ---
@app.post("/diem-dich-vu", status_code=201, response_model=DiemDichVuInputModel)
def them_diem_dich_vu(diem: DiemDichVuInputModel, db: Session = Depends(get_db)):
    stmt = text("INSERT INTO diem_dich_vu (id, ten, loai, dia_chi, vi_do, kinh_do) VALUES (:id, :ten, :loai, :dia_chi, :vi_do, :kinh_do) ON CONFLICT (id) DO UPDATE SET ten = EXCLUDED.ten, loai = EXCLUDED.loai, dia_chi = EXCLUDED.dia_chi, vi_do = EXCLUDED.vi_do, kinh_do = EXCLUDED.kinh_do")
    try: db.execute(stmt, diem.dict()); db.commit()
    except Exception as e: db.rollback(); raise HTTPException(status_code=500, detail=f"Lỗi CSDL: {e}")
    return diem

@app.get("/cac-diem-xung-quanh", response_model=List[DiemDichVuResponseModel])
def lay_cac_diem_xung_quanh(vi_do: float, kinh_do: float, ban_kinh_km: float = Query(5.0), loai_diem: Optional[str] = Query(None), db: Session = Depends(get_db)):
    params = {"user_lat": vi_do, "user_lon": kinh_do, "radius": ban_kinh_km}; inner_query = f"SELECT *, {HAVERSINE_SQL} AS khoang_cach_km FROM diem_dich_vu"; where_clause = ""
    if loai_diem: where_clause = " WHERE loai = :loai"; params["loai"] = loai_diem
    query = text(f"SELECT * FROM ({inner_query} {where_clause}) AS subquery WHERE khoang_cach_km <= :radius ORDER BY khoang_cach_km ASC")
    try: result = db.execute(query, params).fetchall(); ket_qua = [dict(row._mapping) for row in result]; [d.update({'khoang_cach_km': round(d['khoang_cach_km'], 2)}) for d in ket_qua]; return ket_qua
    except Exception as e: raise HTTPException(status_code=500, detail=f"Lỗi truy vấn CSDL: {e}")

@app.get("/tim-diem-gan-nhat", response_model=DiemDichVuResponseModel)
def tim_diem_gan_nhat_api(vi_do: float, kinh_do: float, loai_diem: Optional[str] = None, db: Session = Depends(get_db)):
    diem = _tim_diem_gan_nhat_logic(db, vi_do, kinh_do, loai_diem);
    if not diem: raise HTTPException(status_code=404, detail="Không tìm thấy điểm dịch vụ nào phù hợp.")
    return diem

# --- 12. API ENDPOINTS (PHASE 2 & 3) ---
@app.post("/device/heartbeat", status_code=status.HTTP_202_ACCEPTED)
async def device_heartbeat(payload: DeviceHeartbeatModel, device_id: str = Depends(get_current_device), db: Session = Depends(get_db)):
    stmt_loc = text("INSERT INTO device_locations (device_id, last_lat, last_lon, last_seen) VALUES (:device_id, :lat, :lon, :timestamp) ON CONFLICT (device_id) DO UPDATE SET last_lat = EXCLUDED.last_lat, last_lon = EXCLUDED.last_lon, last_seen = EXCLUDED.last_seen")
    stmt_obd = text("INSERT INTO obd_logs (device_id, timestamp, fuel_level, rpm, speed, error_codes) VALUES (:device_id, :timestamp, :fuel_level, :rpm, :speed, :error_codes)")
    try:
        db.execute(stmt_loc, {"device_id": device_id, "lat": payload.location.lat, "lon": payload.location.lon, "timestamp": payload.timestamp})
        db.execute(stmt_obd, {"device_id": device_id, "timestamp": payload.timestamp, "fuel_level": payload.obd_data.fuel_level, "rpm": payload.obd_data.rpm, "speed": payload.obd_data.speed, "error_codes": ",".join(payload.obd_data.error_codes) if payload.obd_data.error_codes else None})
        _trigger_proactive_alerts(db, device_id, payload) # Trigger AI before commit
        db.commit() # Commit logs and alerts together
    except Exception as e: db.rollback(); raise HTTPException(status_code=500, detail=f"Lỗi CSDL khi ghi log hoặc cảnh báo: {e}")
    return {"status": "accepted"}

@app.get("/device/location/last", response_model=DeviceLocationResponse)
async def get_last_device_location(device_id: str = Depends(get_current_device), db: Session = Depends(get_db)):
    stmt = text("SELECT * FROM device_locations WHERE device_id = :device_id")
    try: result = db.execute(stmt, {"device_id": device_id}).fetchone()
    except Exception as e: raise HTTPException(status_code=500, detail=f"Lỗi truy vấn CSDL: {e}")
    if not result: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dữ liệu vị trí cho thiết bị này.")
    return dict(result._mapping)

@app.get("/device/alerts", response_model=List[UserAlertResponse])
def get_device_alerts(device_id: str = Depends(get_current_device), db: Session = Depends(get_db)):
    stmt = text("SELECT * FROM user_alerts WHERE device_id = :device_id AND is_read = false ORDER BY timestamp DESC")
    try: result = db.execute(stmt, {"device_id": device_id}).fetchall(); return [dict(row._mapping) for row in result]
    except Exception as e: raise HTTPException(status_code=500, detail=f"Lỗi truy vấn CSDL: {e}")

@app.put("/device/alerts/{alert_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_alert_as_read(alert_id: uuid.UUID = Path(...), device_id: str = Depends(get_current_device), db: Session = Depends(get_db)):
    stmt = text("UPDATE user_alerts SET is_read = true WHERE alert_id = :alert_id AND device_id = :device_id AND is_read = false")
    try:
        result = db.execute(stmt, {"alert_id": alert_id, "device_id": device_id}); db.commit()
        if result.rowcount == 0: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy cảnh báo chưa đọc hoặc bạn không có quyền.")
    except Exception as e: db.rollback(); raise HTTPException(status_code=500, detail=f"Lỗi CSDL khi cập nhật cảnh báo: {e}")
    return None

# --- 14. ENDPOINT MỚI: MOCK LOCATION ---
@app.post("/mock/location", status_code=status.HTTP_204_NO_CONTENT)
async def mock_location_update(
    data: MockLocationInput,
    db: Session = Depends(get_db)
):
    """
    (MOCKING TOOL) Cập nhật vị trí cuối cùng cho thiết bị thử nghiệm từ giao diện web/tool.
    """
    stmt_location = text("""
    INSERT INTO device_locations (device_id, last_lat, last_lon, last_seen)
    VALUES (:device_id, :lat, :lon, NOW())
    ON CONFLICT (device_id) DO UPDATE SET
        last_lat = EXCLUDED.last_lat,
        last_lon = EXCLUDED.last_lon,
        last_seen = EXCLUDED.last_seen
    """)
    
    try:
        db.execute(stmt_location, {
            "device_id": data.device_id,
            "lat": data.lat,
            "lon": data.lon
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi CSDL khi ghi vị trí giả lập: {e}")
    
    return None
