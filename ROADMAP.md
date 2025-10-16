# 🚦 ROADMAP DỰ ÁN SMART TRAFFIC SYSTEM

## 📋 TỔNG QUAN DỰ ÁN

Dự án **Smart Traffic System** là hệ thống giao thông thông minh sử dụng AI để:
- 🔮 **Dự đoán traffic** (tốc độ, mật độ giao thông) bằng LSTM, XGBoost, Prophet
- 🗺️ **Tìm đường đi tối ưu** tránh kẹt xe dựa trên dự đoán AI
- ⚠️ **Quản lý tai nạn & thi công** để cảnh báo người dùng
- 📊 **Dashboard real-time** hiển thị bản đồ giao thông

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  - Dashboard với Google Maps                                 │
│  - Visualize traffic predictions                             │
│  - Route planning interface                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│              BACKEND (FastAPI + Python)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Traffic    │  │    Smart     │  │  Incidents   │      │
│  │  Prediction  │  │   Routing    │  │   Manager    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                   SQL SERVER DATABASE                        │
│  - TrafficFlowObserved (real-time traffic data)             │
│  - RoadSegment (road network)                               │
│  - RoadAccident (accidents)                                  │
│  - CityWork (construction zones)                             │
│  - Vehicle (vehicle tracking)                                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              ML PIPELINE (TensorFlow + XGBoost)              │
│  - LSTM Model (time series prediction)                       │
│  - XGBoost Model (gradient boosting)                         │
│  - Prophet Model (Facebook time series)                      │
│  - Training scripts & data collection                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ TRẠNG THÁI HIỆN TẠI (ĐÃ HOÀN THÀNH)

### ✅ 1. Cấu trúc dự án
- [x] Backend skeleton với FastAPI
- [x] Database schema (6 tables)
- [x] API endpoints structure
- [x] ML pipeline structure

### ✅ 2. Database Design
- [x] TrafficFlowObserved table ✅
- [x] RoadSegment table ✅
- [x] RoadAccident table ✅
- [x] CityWork table ✅
- [x] Vehicle table ✅
- [x] Road table ✅
- [x] Views & Stored Procedures ✅

### ✅ 3. Backend Foundation
- [x] FastAPI app structure
- [x] Database connection (SQLAlchemy)
- [x] Config management (pydantic-settings)
- [x] API routing structure
- [x] CORS middleware

### ⚠️ 4. API Endpoints (STUB - Chưa implement logic)
- [x] Traffic endpoints (prediction, current, history)
- [x] Routing endpoints (find route, alternatives, reroute)
- [x] Incidents endpoints (accidents, roadworks)

---

## 🎯 CÒN LẠI CẦN LÀM (11 BƯỚC)

## 📍 BƯỚC 1: SETUP MÔI TRƯỜNG PHÁT TRIỂN

### 1.1. Cài đặt Python
```powershell
# Check Python version (cần >= 3.10)
python --version

# Nếu chưa có, download: https://www.python.org/downloads/
```

### 1.2. Cài đặt SQL Server
- Download SQL Server 2019/2022 Express (miễn phí)
- Download SQL Server Management Studio (SSMS)
- Hoặc dùng Docker:
```powershell
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 -d mcr.microsoft.com/mssql/server:2019-latest
```

### 1.3. Create .env file
```powershell
cd smart-traffic-system\backend
cp .env.example .env
# Edit .env với thông tin database của bạn
```

### 1.4. Install Dependencies
```powershell
# Backend dependencies
cd smart-traffic-system\backend
pip install -r requirements.txt

# ML Pipeline dependencies
cd ..\ml-pipeline
pip install -r requirements.txt
```

---

## 📍 BƯỚC 2: SETUP DATABASE

### 2.1. Tạo Database
```sql
-- Mở SSMS và chạy:
CREATE DATABASE SmartTrafficDB;
GO
```

### 2.2. Chạy Schema Script
```powershell
# Option 1: Trong SSMS
# - Open file: smart-traffic-system\database\schemas\create_all.sql
# - Execute (F5)

# Option 2: Command line
sqlcmd -S localhost -U sa -P YourPassword -i "database\schemas\create_all.sql"
```

### 2.3. Verify Tables
```sql
USE SmartTrafficDB;
SELECT name FROM sys.tables;
-- Should show: TrafficFlowObserved, RoadSegment, RoadAccident, CityWork, Vehicle, Road
```

---

## 📍 BƯỚC 3: SETUP GOOGLE MAPS API

### 3.1. Tạo Google Cloud Project
1. Truy cập: https://console.cloud.google.com/
2. Create new project: "Smart Traffic System"
3. Enable APIs:
   - Distance Matrix API ✅
   - Roads API ✅
   - Directions API ✅

### 3.2. Tạo API Key
1. APIs & Services → Credentials
2. Create API Key
3. Restrict key (security):
   - Application restrictions: IP addresses
   - API restrictions: Chọn 3 APIs trên

### 3.3. Update .env
```env
GOOGLE_MAPS_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3.4. Enable Billing
⚠️ **Quan trọng**: Cần thẻ tín dụng, nhưng có $200 free/tháng
- ~40,000 requests/tháng MIỄN PHÍ

### 3.5. Test API
```powershell
cd ml-pipeline\scripts
python test_google_api.py
```

**📖 Chi tiết**: Xem file `ml-pipeline/scripts/GOOGLE_MAPS_SETUP.md`

---

## 📍 BƯỚC 4: THU THẬP DỮ LIỆU TRAFFIC

### 4.1. Define Road Segments
Tạo file `ml-pipeline/data/road_segments.json`:
```json
[
  {
    "id": "segment_001",
    "name": "Nguyen Hue Street",
    "origin": {"lat": 10.7741, "lng": 106.7008},
    "destination": {"lat": 10.7769, "lng": 106.7011}
  },
  {
    "id": "segment_002",
    "name": "Le Loi Boulevard",
    "origin": {"lat": 10.7723, "lng": 106.6989},
    "destination": {"lat": 10.7741, "lng": 106.7008}
  }
]
```

### 4.2. Collect Traffic Data
```powershell
cd ml-pipeline\scripts
python collect_google_traffic.py --segments ../data/road_segments.json --interval 900
# Thu thập mỗi 15 phút (900s)
```

### 4.3. Schedule Data Collection
```powershell
# Windows Task Scheduler hoặc cron job
# Chạy mỗi 15 phút để tích lũy data
```

**Mục tiêu**: Thu thập ít nhất **7 ngày data** trước khi train model

---

## 📍 BƯỚC 5: TẠO PYDANTIC SCHEMAS

### 5.1. Traffic Schemas
Tạo `backend/app/schemas/traffic.py`:
- TrafficPredictionRequest
- TrafficPredictionResponse
- CurrentTrafficResponse
- TrafficHistoryResponse

### 5.2. Routing Schemas
Tạo `backend/app/schemas/routing.py`:
- RouteRequest
- RouteResponse
- RouteSegment
- AlternativeRoutesRequest

### 5.3. Incidents Schemas
Tạo `backend/app/schemas/incidents.py`:
- AccidentResponse
- CityWorkResponse
- IncidentListResponse

---

## 📍 BƯỚC 6: IMPLEMENT TRAFFIC PREDICTION SERVICE

### 6.1. Tạo Service Class
File: `backend/app/services/traffic_prediction_service.py`

**Chức năng**:
- Load pre-trained LSTM/XGBoost models
- Prepare input features (hour, day, weather, historical data)
- Predict future traffic (15min, 30min, 1h, 2h ahead)
- Return predictions với confidence score

### 6.2. Features cho Prediction
- **Temporal**: hour, day_of_week, month, is_weekend, is_holiday
- **Historical**: avg_speed_last_15min, avg_speed_last_1h, avg_speed_same_hour_yesterday
- **External**: weather (temperature, rain), events
- **Road**: road_class, lane_count, speed_limit

### 6.3. Model Ensemble
- LSTM: 60% weight (tốt cho time series)
- XGBoost: 30% weight (tốt cho non-linear patterns)
- Prophet: 10% weight (seasonal trends)

---

## 📍 BƯỚC 7: IMPLEMENT SMART ROUTING SERVICE

### 7.1. Tạo Service Class
File: `backend/app/services/routing_service.py`

**Algorithm**: A* Search với traffic weights

### 7.2. Graph Construction
```python
# Build road network graph
Graph = {
  "node_id": {
    "neighbors": [
      {"node": "next_node", "distance": 1500, "predicted_speed": 42}
    ]
  }
}
```

### 7.3. Cost Function
```python
def calculate_cost(segment):
    base_time = segment.distance / segment.predicted_speed
    
    # Penalties
    if segment.has_accident:
        base_time *= 2.0
    if segment.has_construction:
        base_time *= 1.5
    if segment.predicted_occupancy > 0.8:
        base_time *= 1.3
    
    return base_time
```

### 7.4. Route Modes
- **fastest**: Minimize time (use predictions)
- **shortest**: Minimize distance
- **avoid_traffic**: Prefer low occupancy roads

---

## 📍 BƯỚC 8: IMPLEMENT INCIDENTS SERVICE

### 8.1. Tạo Service Class
File: `backend/app/services/incidents_service.py`

**Chức năng**:
- Query accidents from database
- Query construction zones
- Check if road segment is affected
- Get impact assessment

### 8.2. Real-time Updates
- Integrate với external APIs (nếu có)
- Manual reporting system
- Admin dashboard để update incidents

---

## 📍 BƯỚC 9: TRAIN ML MODELS

### 9.1. Data Preparation
File: `ml-pipeline/scripts/prepare_data.py`

```python
# Load traffic data from database
# Clean & preprocess
# Create features
# Train/test split (80/20)
```

### 9.2. Train LSTM Model
File: `ml-pipeline/scripts/train_lstm.py`

```python
# Model architecture:
# - LSTM(128) → Dropout(0.2)
# - LSTM(64) → Dropout(0.2)
# - Dense(32) → Dense(1)
# 
# Input: [batch, 24 timesteps, 10 features]
# Output: [batch, 1] (predicted speed)
```

### 9.3. Train XGBoost Model
File: `ml-pipeline/scripts/train_xgboost.py`

```python
# Hyperparameters:
# - n_estimators: 500
# - max_depth: 7
# - learning_rate: 0.05
```

### 9.4. Train Prophet Model
File: `ml-pipeline/scripts/train_prophet.py`

```python
# Good for long-term trends
# Captures seasonality (daily, weekly)
```

### 9.5. Model Evaluation
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)
- Target: MAPE < 15%

---

## 📍 BƯỚC 10: TẠO FRONTEND DASHBOARD

### 10.1. Tech Stack
- React + TypeScript
- Google Maps JavaScript API
- Chart.js / Recharts (for graphs)
- Ant Design / Material-UI (UI components)

### 10.2. Main Pages
1. **Dashboard**: Real-time traffic map
2. **Route Planner**: Input origin/destination → Show optimal route
3. **Predictions**: View future traffic predictions
4. **Incidents**: List accidents & construction zones
5. **Analytics**: Historical traffic trends

### 10.3. Key Features
- Real-time traffic heatmap
- Route visualization with alternatives
- Traffic predictions chart (next 2 hours)
- Incident markers on map
- Auto-refresh data (every 30s)

---

## 📍 BƯỚC 11: TESTING & DEPLOYMENT

### 11.1. Testing
```powershell
# Backend tests
cd backend
pytest tests/ -v

# Load testing
locust -f tests/load_test.py
```

### 11.2. Deployment Options

**Option A: Local Server**
- FastAPI: `uvicorn main:app --host 0.0.0.0 --port 8000`
- React: `npm run build` → Nginx

**Option B: Cloud (Azure/AWS)**
- Backend: Azure App Service / AWS EC2
- Database: Azure SQL / AWS RDS
- Frontend: Azure Static Web Apps / AWS S3 + CloudFront

**Option C: Docker**
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  database:
    image: mcr.microsoft.com/mssql/server:2019
    ports: ["1433:1433"]
```

---

## 📊 TIMELINE DỰ KIẾN

| Bước | Nhiệm vụ | Thời gian | Trạng thái |
|------|----------|-----------|------------|
| 1 | Setup môi trường | 1 ngày | ⏳ Chưa bắt đầu |
| 2 | Setup database | 0.5 ngày | ⏳ Chưa bắt đầu |
| 3 | Setup Google Maps API | 0.5 ngày | ⏳ Chưa bắt đầu |
| 4 | Thu thập data (7 ngày) | 7 ngày | ⏳ Chưa bắt đầu |
| 5 | Tạo Pydantic schemas | 1 ngày | ⏳ Chưa bắt đầu |
| 6 | Traffic Prediction Service | 2 ngày | ⏳ Chưa bắt đầu |
| 7 | Smart Routing Service | 2 ngày | ⏳ Chưa bắt đầu |
| 8 | Incidents Service | 1 ngày | ⏳ Chưa bắt đầu |
| 9 | Train ML models | 2 ngày | ⏳ Chưa bắt đầu |
| 10 | Frontend Dashboard | 5 ngày | ⏳ Chưa bắt đầu |
| 11 | Testing & Deployment | 2 ngày | ⏳ Chưa bắt đầu |
| **TỔNG** | | **~24 ngày** | |

---

## 🎯 PRIORITIES

### HIGH PRIORITY (Core Features)
1. ✅ Database setup
2. ✅ Data collection from Google Maps
3. ✅ Traffic Prediction Service
4. ✅ Smart Routing Service
5. ✅ Frontend Dashboard

### MEDIUM PRIORITY (Enhanced Features)
6. Incidents Management
7. ML Model Optimization
8. Real-time data streaming
9. User authentication

### LOW PRIORITY (Nice to Have)
10. Mobile app
11. Advanced analytics
12. Machine learning auto-retraining
13. Integration với traffic cameras

---

## 📚 TÀI LIỆU THAM KHẢO

### Data Models
- FIWARE Data Models: https://github.com/smart-data-models/dataModel.Transportation
- Smart City specs

### ML Frameworks
- TensorFlow LSTM: https://www.tensorflow.org/tutorials/structured_data/time_series
- XGBoost: https://xgboost.readthedocs.io/
- Prophet: https://facebook.github.io/prophet/

### APIs
- Google Maps APIs: https://developers.google.com/maps/documentation
- FastAPI: https://fastapi.tiangolo.com/

---

## 🆘 CẦN TRỢ GIÚP?

### Common Issues
1. **Database connection failed**: Check SQL Server running, credentials correct
2. **Google API error**: Check API key, billing enabled, APIs enabled
3. **Model not loading**: Check file paths in .env
4. **CORS error**: Check CORS_ORIGINS in .env

### Contact & Resources
- GitHub Issues: https://github.com/duongloc216/Smart-Transport/issues
- Stack Overflow: [fastapi], [tensorflow], [sqlalchemy]
- Documentation: Xem README.md trong từng thư mục

---

**🚀 GOOD LUCK! Chúng ta bắt đầu từ Bước 1 nhé!**
