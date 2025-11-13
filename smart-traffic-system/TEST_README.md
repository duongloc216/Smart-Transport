# 🧪 Hướng Dẫn Test Hệ Thống - SMART TRAFFIC SYSTEM

## 📋 Tổng Quan

Có **2 cách** để test hệ thống:
1. **Manual Mode** - Test từng component riêng lẻ (Recommended cho development)
2. **Docker Mode** - Test toàn bộ stack cùng lúc (Recommended cho production)

---

## 🎯 OPTION 1: Manual Testing (Chi Tiết Nhất)

### Bước 1: Start Backend

**Terminal 1 - Backend:**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
python main.py
```

**Chờ đến khi thấy:**
```
✅ ML models loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Bước 2: Run Test Script

**Terminal 2 - Testing:**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-manual.ps1
```

Script sẽ tự động test 8 use cases:
- ✅ Health Check
- ✅ Get All Traffic Data
- ✅ Get Single Segment Traffic
- ✅ Get Traffic History
- ✅ ML Prediction
- ✅ Smart Routing
- ✅ ML Models Info
- ✅ Open API Documentation

### Bước 3: Manual Tests (Tùy chỉnh)

#### Test Case 1: Lấy traffic cho segment khác
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_005" | Select-Object -ExpandProperty Content
```

#### Test Case 2: Predict cho 30 phút
```powershell
$body = @{
    road_segment_id = "segment_001"
    prediction_horizon = 30
    model_type = "ensemble"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

#### Test Case 3: Tìm route khác
```powershell
$body = @{
    origin = "segment_003"
    destination = "segment_007"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

#### Test Case 4: Lấy alternative routes
```powershell
$body = @{
    origin = "segment_001"
    destination = "segment_010"
    max_routes = 3
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/alternative-routes" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

#### Test Case 5: Kiểm tra incidents
```powershell
# Get active accidents
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/incidents/accidents/active" | Select-Object -ExpandProperty Content

# Get construction zones
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/incidents/construction/active" | Select-Object -ExpandProperty Content
```

---

## 🐳 OPTION 2: Docker Testing (Production-like)

### Bước 1: Run Docker Test Script

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-docker.ps1
```

Script sẽ:
1. ✅ Check Docker installation
2. ✅ Navigate to project
3. ✅ Create .env file
4. ✅ Stop existing containers
5. ✅ Build and start all services
6. ✅ Test backend health
7. ✅ Test frontend
8. ✅ Show container status

### Bước 2: Access Services

- **Frontend Dashboard**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

### Bước 3: View Logs

```powershell
# Backend logs
docker-compose logs backend -f

# Frontend logs
docker-compose logs frontend -f

# All logs
docker-compose logs -f

# Stop following logs: Ctrl + C
```

### Bước 4: Stop Docker

```powershell
docker-compose down
```

---

## 🌐 Frontend Testing

### Manual Start Frontend (Nếu không dùng Docker)

**Terminal 3 - Frontend:**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\frontend"
npm install
npm run dev
```

**Access**: http://localhost:3000

### Frontend Test Cases

1. **Map Display**
   - ✅ Map hiển thị đúng
   - ✅ 10 road segments visible
   - ✅ Color-coded by congestion (Green/Yellow/Red)

2. **Interactivity**
   - ✅ Click vào segment → Popup hiện thông tin
   - ✅ Popup shows: Road name, Speed, Intensity, Status, Congestion %

3. **Statistics Cards**
   - ✅ Total Segments = 10
   - ✅ Congested count
   - ✅ Moderate count
   - ✅ Free Flow count
   - ✅ Average Speed
   - ✅ Total Intensity

4. **Auto-Refresh**
   - ✅ Data tự động refresh mỗi 30 giây
   - ✅ "Last Updated" timestamp thay đổi

---

## 📊 Database Testing

### Test Database Queries

```powershell
# Test 1: Count traffic records
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT COUNT(*) as TotalRecords FROM TrafficFlowObserved"

# Test 2: Check road segments
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT * FROM RoadSegment"

# Test 3: Get latest traffic
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT TOP 10 RefRoadSegment, AverageVehicleSpeed, Intensity, DateObserved FROM TrafficFlowObserved ORDER BY DateObserved DESC"

# Test 4: Check active accidents
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT * FROM vw_ActiveAccidents"

# Test 5: Check construction zones
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT * FROM vw_ActiveConstructionZones"
```

---

## 🔧 Troubleshooting

### Problem 1: Backend không start được

**Triệu chứng:**
```
can't open file 'main.py'
```

**Giải pháp:**
```powershell
# Ensure đúng directory
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
Get-Location  # Should show: E:\CĐTT2\Smart-Transport\smart-traffic-system\backend
python main.py
```

### Problem 2: ML Models không load

**Triệu chứng:**
```
FileNotFoundError: Model file not found
```

**Giải pháp:**
```powershell
# Check models exist
dir "e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\models\saved_models"

# Should see:
# - xgboost_congestion.pkl
# - lightgbm_speed.pkl
# - prophet_models.pkl
# - scaler.pkl
# - feature_columns.pkl
```

### Problem 3: Database connection failed

**Triệu chứng:**
```
Unable to connect to SQL Server
```

**Giải pháp:**
```powershell
# Test SQL Server
sqlcmd -S localhost -Q "SELECT @@VERSION"

# If fails, start SQL Server service:
# 1. Win + R → services.msc
# 2. Find "SQL Server (MSSQLSERVER)"
# 3. Right click → Start
```

### Problem 4: Frontend CORS error

**Triệu chứng:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS
```

**Giải pháp:**
Kiểm tra file `.env`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
```

### Problem 5: Docker build fails

**Triệu chứng:**
```
ERROR: Service 'backend' failed to build
```

**Giải pháp:**
```powershell
# Clear Docker cache
docker-compose down
docker system prune -a

# Rebuild
docker-compose up --build
```

---

## ✅ Test Success Criteria

### Backend Tests Pass If:
- [x] Health endpoint returns `{"status": "healthy"}`
- [x] All 14 API endpoints respond
- [x] ML models load without errors
- [x] Predictions return reasonable values (speed: 5-60 km/h)
- [x] Routing finds paths successfully
- [x] Response time < 500ms

### Frontend Tests Pass If:
- [x] Page loads without errors
- [x] Map displays correctly
- [x] All 10 segments visible
- [x] Statistics cards show data
- [x] Auto-refresh works
- [x] Popups show on click

### Database Tests Pass If:
- [x] Connection successful
- [x] ≥ 1000 traffic records exist
- [x] All tables accessible
- [x] Views return data

### Docker Tests Pass If:
- [x] All 4 containers running
- [x] Backend health check passes
- [x] Frontend accessible
- [x] No errors in logs

---

## 📈 Performance Benchmarks

Expected Performance:
- **API Response Time**: < 200ms (95th percentile)
- **ML Prediction Time**: < 500ms
- **Route Finding Time**: < 1s
- **Frontend Load Time**: < 2s
- **Database Query Time**: < 100ms

Test với:
```powershell
# Measure API response time
Measure-Command { Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_001" }
```

---

## 📝 Test Results Template

```markdown
# Test Results - [Date]

## Environment
- OS: Windows 10/11
- Python: 3.10
- Docker: [version]
- SQL Server: 2022

## Manual Tests
| Test | Endpoint | Status | Response Time | Notes |
|------|----------|--------|---------------|-------|
| 1 | Health Check | ✅ | 15ms | Pass |
| 2 | All Traffic | ✅ | 120ms | 10 segments returned |
| 3 | Single Traffic | ✅ | 45ms | segment_001 OK |
| 4 | Traffic History | ✅ | 80ms | 10 records |
| 5 | ML Prediction | ✅ | 380ms | Ensemble model |
| 6 | Smart Routing | ✅ | 650ms | Path found |
| 7 | Models Info | ✅ | 25ms | 6 models loaded |

## Frontend Tests
| Feature | Status | Notes |
|---------|--------|-------|
| Map Display | ✅ | All segments visible |
| Interactivity | ✅ | Popups work |
| Statistics | ✅ | All cards show data |
| Auto-Refresh | ✅ | 30s interval OK |

## Overall Result
✅ ALL TESTS PASSED
```

---

## 🎓 Advanced Testing

### Load Testing
```powershell
# Install Apache Bench (if needed)
# Then run:
ab -n 100 -c 10 http://localhost:8000/api/v1/traffic/current/segment_001
```

### API Testing with Postman
1. Import API docs từ: http://localhost:8000/api/openapi.json
2. Create collection từ OpenAPI spec
3. Run all endpoints

### Python Integration Test
```python
import requests

# Test full workflow
def test_traffic_system():
    base_url = "http://localhost:8000"
    
    # 1. Health check
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    
    # 2. Get traffic
    response = requests.get(f"{base_url}/api/v1/traffic/current/segment_001")
    assert response.status_code == 200
    traffic = response.json()
    assert traffic['speed'] > 0
    
    # 3. Predict
    response = requests.post(
        f"{base_url}/api/v1/traffic/predict",
        json={"road_segment_id": "segment_001", "prediction_horizon": 15}
    )
    assert response.status_code == 200
    
    # 4. Route
    response = requests.post(
        f"{base_url}/api/v1/routing/find-route",
        json={"origin": "segment_001", "destination": "segment_010"}
    )
    assert response.status_code == 200
    
    print("✅ All integration tests passed!")

if __name__ == "__main__":
    test_traffic_system()
```

---

## 🎯 Next Steps After Testing

1. **Nếu tất cả tests PASS**:
   - ✅ System ready for deployment
   - ✅ Move to production environment
   - ✅ Setup monitoring and logging

2. **Nếu có tests FAIL**:
   - ❌ Check error logs
   - ❌ Review troubleshooting section
   - ❌ Fix issues and re-test

3. **Optimization**:
   - 🔧 Tune ML model parameters
   - 🔧 Optimize database queries
   - 🔧 Add caching for frequent requests
   - 🔧 Implement rate limiting

---

**Happy Testing! 🧪🚀**

Created by: Smart Traffic Team  
Last Updated: 12/11/2025
