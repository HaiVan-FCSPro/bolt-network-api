# 🌐 BOLT Network API (Backend)

The backbone service for the **BOLT Intelligent HUD System**. This API handles V2X communication, data synchronization, and cloud processing.

## 🚀 Overview
While the [BOLT HUD Client](https://github.com/HaiVan-FCSPro/bolt-hud-smartcity) handles real-time interaction in the car, this **Network API** serves as the cloud brain, enabling:
* **Data Sync:** Storage for trip logs and proactive alerts.
* **Fleet Management:** Real-time location tracking endpoints.
* **V2X Integration:** Ready-to-use endpoints for Smart City infrastructure connection.

## 🛠️ Tech Stack
* **Framework:** FastAPI (Python) - High performance, easy to allow async requests.
* **Database:** PostgreSQL (Scalable relational storage).
* **Deployment:** Docker / Render.

## 🔌 API Endpoints (Draft)
* `GET /status`: Check server health.
* `POST /telemetry`: Receive real-time speed/fuel data from HUD.
* `GET /alerts`: Fetch recent hazard warnings.

---
*Part of the BOLT Ecosystem - Developed by FCS-Pro Team.*
