# 🧪 HƯỚNG DẪN TEST CHI TIẾT - HỆ THỐNG GIAO THÔNG THÔNG MINH

## 🎯 TÓM TẮT

Thông báo bạn nhận được là **VS Code gợi ý cài extension "Container Tools"** để quản lý Docker dễ hơn.

**👉 Nên click "Install"** để có trải nghiệm tốt nhất!

---

## 📋 2 CÁCH TEST HỆ THỐNG

### 🔧 Cách 1: Manual Testing (Khuyến nghị cho việc tinh chỉnh)
- Test từng component riêng lẻ
- Dễ debug và modify
- Phù hợp để tinh chỉnh parameters

### 🐳 Cách 2: Docker Testing (Khuyến nghị cho production)
- Test toàn bộ stack cùng lúc
- Giống môi trường thực tế
- Deploy nhanh

---

## ✅ CÁCH 1: MANUAL TESTING (CHI TIẾT)

### Bước 1: Khởi động Backend

**Mở Terminal mới (Ctrl + Shift + `):**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
python main.py
```

**Đợi đến khi thấy:**
```
✅ ML models loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

⚠️ **LƯU Ý**: Giữ terminal này mở, KHÔNG TẮT!

---

### Bước 2: Chạy Script Test Tự Động

**Mở Terminal mới thứ 2:**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-manual.ps1
```

**Script sẽ tự động test 8 use cases:**

#### ✅ Test 1: Health Check
Kiểm tra backend có chạy không
```
Expected: {"status": "healthy", "timestamp": ..., "version": "1.0.0"}
```

#### ✅ Test 2: Lấy Toàn Bộ Traffic Data
Lấy traffic của tất cả 10 đoạn đường
```
Expected: 10 segments với speed, intensity, congestion_status
```

#### ✅ Test 3: Lấy Traffic 1 Đoạn Đường
Lấy traffic của segment_001 (Võ Văn Ngân Section 1)
```
Expected: Speed, Intensity, Congestion Status
```

#### ✅ Test 4: Lấy Lịch Sử Traffic
Lấy 5 records gần nhất của segment_001
```
Expected: 5 records với timestamp, speed, intensity
```

#### ✅ Test 5: Dự Đoán Traffic (ML)
Dự đoán traffic 15 phút tới bằng ensemble model
```
Expected: predicted_speed, congestion_probability, confidence
```

#### ✅ Test 6: Tìm Đường Thông Minh
Tìm đường tối ưu từ segment_001 → segment_010
```
Expected: Route với total_distance, total_duration, segments
```

#### ✅ Test 7: Thông Tin ML Models
Kiểm tra các models đã load chưa
```
Expected: 6 models (XGBoost, LightGBM, Prophet, Scaler, Features)
```

#### ✅ Test 8: Mở API Documentation
Tự động mở Swagger UI trong browser
```
URL: http://localhost:8000/api/docs
```

---

### Bước 3: Test Thủ Công (Tùy Chỉnh)

#### 📌 Test Case A: Lấy traffic đoạn đường khác

**Test segment_002:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_002" | Select-Object -ExpandProperty Content
```

**Test segment_005:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_005" | Select-Object -ExpandProperty Content
```

**Test tất cả segments:**
```powershell
# Loop qua tất cả 10 segments
for ($i=1; $i -le 10; $i++) {
    $segmentId = "segment_{0:D3}" -f $i
    Write-Host "Testing $segmentId..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/$segmentId" | Select-Object -ExpandProperty Content
    Write-Host ""
}
```

---

#### 📌 Test Case B: Dự đoán với thời gian khác nhau

**Dự đoán 30 phút:**
```powershell
$body = @{
    road_segment_id = "segment_001"
    prediction_horizon = 30
    model_type = "ensemble"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Dự đoán 60 phút:**
```powershell
$body = @{
    road_segment_id = "segment_001"
    prediction_horizon = 60
    model_type = "ensemble"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**So sánh các models:**

**XGBoost only:**
```powershell
$body = @{
    road_segment_id = "segment_001"
    prediction_horizon = 15
    model_type = "xgboost"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json"
```

**LightGBM only:**
```powershell
$body = @{
    road_segment_id = "segment_001"
    prediction_horizon = 15
    model_type = "lightgbm"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json"
```

---

#### 📌 Test Case C: Tìm đường giữa các điểm khác nhau

**Route 1: segment_002 → segment_008**
```powershell
$body = @{
    origin = "segment_002"
    destination = "segment_008"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Route 2: segment_003 → segment_009**
```powershell
$body = @{
    origin = "segment_003"
    destination = "segment_009"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**Route 3: Lấy nhiều routes thay thế**
```powershell
$body = @{
    origin = "segment_001"
    destination = "segment_010"
    max_routes = 3
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/alternative-routes" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

---

#### 📌 Test Case D: Kiểm tra Incidents

**Lấy active accidents:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/incidents/accidents/active" | Select-Object -ExpandProperty Content
```

**Lấy active construction zones:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/incidents/construction/active" | Select-Object -ExpandProperty Content
```

**Lấy tất cả incidents:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/incidents/all" | Select-Object -ExpandProperty Content
```

---

#### 📌 Test Case E: Lấy lịch sử với số lượng khác nhau

**Lấy 20 records:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/history/segment_001?limit=20" | Select-Object -ExpandProperty Content
```

**Lấy 50 records:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/history/segment_001?limit=50" | Select-Object -ExpandProperty Content
```

---

## 🐳 CÁCH 2: DOCKER TESTING (ĐƠN GIẢN)

### Bước 1: Chạy Docker Test Script

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-docker.ps1
```

**Script sẽ:**
1. ✅ Kiểm tra Docker đã cài chưa
2. ✅ Tạo file .env
3. ✅ Stop containers cũ
4. ✅ Build images mới (5-10 phút lần đầu)
5. ✅ Start tất cả services
6. ✅ Test backend
7. ✅ Test frontend
8. ✅ Hiển thị status

### Bước 2: Truy Cập Các Services

**Frontend Dashboard:**
```
http://localhost
```

**Backend API:**
```
http://localhost:8000
```

**API Documentation:**
```
http://localhost:8000/api/docs
```

### Bước 3: Xem Logs

**Backend logs:**
```powershell
docker-compose logs backend -f
```

**Frontend logs:**
```powershell
docker-compose logs frontend -f
```

**All logs:**
```powershell
docker-compose logs -f
```

**Stop xem logs:** `Ctrl + C`

### Bước 4: Quản Lý Containers

**Xem status:**
```powershell
docker-compose ps
```

**Restart services:**
```powershell
docker-compose restart
```

**Stop tất cả:**
```powershell
docker-compose down
```

**Xóa hết (kể cả volumes):**
```powershell
docker-compose down -v
```

---

## 🌐 TEST FRONTEND

### Khởi động Frontend (Manual - không dùng Docker)

**Terminal 3:**
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\frontend"
npm install
npm run dev
```

**Truy cập:** http://localhost:3000

### Checklist Frontend

#### ✅ 1. Map Hiển Thị
- [ ] Map loads successfully
- [ ] Tất cả 10 đoạn đường hiển thị
- [ ] Màu sắc đúng:
  - 🟢 Xanh = Free Flow (speed > 35 km/h)
  - 🟡 Vàng = Moderate (20-35 km/h)
  - 🔴 Đỏ = Congested (< 20 km/h)

#### ✅ 2. Tương Tác
- [ ] Click vào segment → popup hiện
- [ ] Popup hiển thị:
  - Road name
  - Speed (km/h)
  - Intensity (vehicles/hour)
  - Congestion Status
  - Congestion Probability (%)

#### ✅ 3. Statistics Cards
- [ ] **Total Segments**: Hiển thị "10"
- [ ] **Congested**: Số đoạn đường tắc
- [ ] **Moderate**: Số đoạn đường khá
- [ ] **Free Flow**: Số đoạn đường thông thoáng
- [ ] **Average Speed**: Tốc độ trung bình
- [ ] **Total Intensity**: Tổng lưu lượng

#### ✅ 4. Auto-Refresh
- [ ] Data refresh mỗi 30 giây
- [ ] "Last Updated" timestamp thay đổi
- [ ] Màu segments update theo traffic mới

#### ✅ 5. Responsive Design
- [ ] Hoạt động tốt trên màn hình nhỏ
- [ ] Hoạt động tốt trên màn hình lớn
- [ ] Cards hiển thị đúng grid layout

---

## 💾 TEST DATABASE

### Kiểm tra Database

**Test 1: Đếm traffic records**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT COUNT(*) as TotalRecords FROM TrafficFlowObserved"
```
**Expected:** ≥ 8000 records

**Test 2: Xem road segments**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT SegmentId, SegmentName, MaxSpeed, Length FROM RoadSegment"
```
**Expected:** 10 segments

**Test 3: Traffic gần nhất**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT TOP 10 RefRoadSegment, AverageVehicleSpeed, Intensity, DateObserved FROM TrafficFlowObserved ORDER BY DateObserved DESC"
```
**Expected:** 10 records mới nhất

**Test 4: Active accidents**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT * FROM vw_ActiveAccidents"
```

**Test 5: Active construction**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT * FROM vw_ActiveConstructionZones"
```

**Test 6: Traffic statistics**
```powershell
sqlcmd -S localhost -d SmartTrafficDB -Q "EXEC sp_GetTrafficStatistics"
```

---

## 🔧 TROUBLESHOOTING

### ❌ Lỗi 1: Backend không khởi động được

**Triệu chứng:**
```
can't open file 'main.py': [Errno 2] No such file or directory
```

**Nguyên nhân:** Đường dẫn sai

**Giải pháp:**
```powershell
# Đảm bảo đúng thư mục
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"

# Kiểm tra file có tồn tại
ls main.py

# Khởi động
python main.py
```

---

### ❌ Lỗi 2: ML Models không load được

**Triệu chứng:**
```
FileNotFoundError: ../ml-pipeline/models/saved_models/xgboost_congestion.pkl
```

**Giải pháp:**
```powershell
# Kiểm tra models có tồn tại
dir "e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\models\saved_models"

# Phải thấy 5 files:
# - xgboost_congestion.pkl (393 KB)
# - lightgbm_speed.pkl (1406 KB)
# - prophet_models.pkl (1096 KB)
# - scaler.pkl (2 KB)
# - feature_columns.pkl (0.5 KB)
```

**Nếu thiếu models:** Chạy lại training notebooks trong `ml-pipeline/notebooks`

---

### ❌ Lỗi 3: Database connection failed

**Triệu chứng:**
```
ODBC connection error
Unable to connect to SQL Server
```

**Giải pháp:**
```powershell
# Test SQL Server
sqlcmd -S localhost -Q "SELECT @@VERSION"

# Nếu lỗi, kiểm tra service:
# 1. Win + R → services.msc
# 2. Tìm "SQL Server (MSSQLSERVER)"
# 3. Status phải là "Running"
# 4. Nếu stopped → Right click → Start
```

---

### ❌ Lỗi 4: Frontend CORS error

**Triệu chứng:**
```
Access to fetch blocked by CORS policy
```

**Giải pháp:**
Kiểm tra file `.env` có:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
```

Restart backend sau khi sửa .env

---

### ❌ Lỗi 5: Docker build fails

**Triệu chứng:**
```
ERROR: Service 'backend' failed to build
```

**Giải pháp:**
```powershell
# Clear Docker cache
docker-compose down
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

### ❌ Lỗi 6: Frontend không kết nối backend

**Triệu chứng:**
Frontend loads nhưng không có data

**Giải pháp:**
```powershell
# Check backend có chạy không
Invoke-WebRequest -Uri "http://localhost:8000/health"

# Check proxy config trong vite.config.js
cat "e:\CĐTT2\Smart-Transport\smart-traffic-system\frontend\vite.config.js"

# Phải có:
# server: {
#   proxy: {
#     '/api': 'http://localhost:8000'
#   }
# }
```

---

## ✅ TIÊU CHÍ ĐÁNH GIÁ

### Backend Tests Pass Khi:
- [x] Health endpoint trả về `{"status": "healthy"}`
- [x] Tất cả 14 API endpoints hoạt động
- [x] 6 ML models load thành công
- [x] Predictions trả về giá trị hợp lý (speed: 5-60 km/h)
- [x] Routing tìm được đường đi
- [x] Response time < 500ms

### Frontend Tests Pass Khi:
- [x] Page load không lỗi
- [x] Map hiển thị đúng
- [x] 10 segments visible
- [x] Statistics cards có data
- [x] Auto-refresh hoạt động
- [x] Popups hiện khi click

### Database Tests Pass Khi:
- [x] Connection thành công
- [x] ≥ 1000 traffic records
- [x] Tất cả tables truy cập được
- [x] Views trả về data

### Docker Tests Pass Khi:
- [x] 4 containers đang chạy
- [x] Backend health check pass
- [x] Frontend accessible
- [x] Không có errors trong logs

---

## 📊 PERFORMANCE BENCHMARKS

### Expected Performance:
- **API Response Time**: < 200ms (95th percentile)
- **ML Prediction Time**: < 500ms
- **Route Finding Time**: < 1s
- **Frontend Load Time**: < 2s
- **Database Query Time**: < 100ms

### Đo Performance:

```powershell
# Đo API response time
Measure-Command { 
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/segment_001" 
}

# Đo prediction time
Measure-Command {
    $body = @{road_segment_id="segment_001"; prediction_horizon=15} | ConvertTo-Json
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/predict" -Method POST -Body $body -ContentType "application/json"
}

# Đo routing time
Measure-Command {
    $body = @{origin="segment_001"; destination="segment_010"} | ConvertTo-Json
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/routing/find-route" -Method POST -Body $body -ContentType "application/json"
}
```

---

## 📝 TEMPLATE GHI KẾT QUẢ TEST

### Manual Test Results

```markdown
# Kết Quả Test - [Ngày/Tháng/Năm]

## Môi Trường
- OS: Windows 10/11
- Python: 3.10
- Docker: [version]
- SQL Server: 2022

## Backend Tests
| Test | Endpoint | Kết Quả | Thời Gian | Ghi Chú |
|------|----------|---------|-----------|---------|
| 1 | Health Check | ✅ | 15ms | Pass |
| 2 | All Traffic | ✅ | 120ms | 10 segments |
| 3 | Single Traffic | ✅ | 45ms | OK |
| 4 | History | ✅ | 80ms | 10 records |
| 5 | ML Prediction | ✅ | 380ms | Ensemble |
| 6 | Smart Routing | ✅ | 650ms | Tìm được đường |
| 7 | Models Info | ✅ | 25ms | 6 models |

## Frontend Tests
| Tính Năng | Kết Quả | Ghi Chú |
|-----------|---------|---------|
| Map Display | ✅ | Tất cả segments hiển thị |
| Interactivity | ✅ | Popups OK |
| Statistics | ✅ | Cards có data |
| Auto-Refresh | ✅ | 30s OK |

## Database Tests
| Test | Kết Quả | Ghi Chú |
|------|---------|---------|
| Connection | ✅ | OK |
| Record Count | ✅ | 8650 records |
| Queries | ✅ | < 100ms |

## Docker Tests
| Service | Kết Quả | Ghi Chú |
|---------|---------|---------|
| Backend | ✅ | Running |
| Frontend | ✅ | Running |
| Database | ✅ | Running |
| Redis | ✅ | Running |

## Tổng Kết
✅ TẤT CẢ TESTS PASS
❌ Không có lỗi phát hiện
⚠️ Cần cải thiện: [nếu có]
```

---

## 🎓 ADVANCED TESTING

### Load Testing với Apache Bench

```powershell
# Cài Apache Bench (nếu chưa có)
# Download từ: https://www.apachelounge.com/download/

# Test với 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/api/v1/traffic/current/segment_001

# Test POST endpoint
ab -n 50 -c 5 -p request.json -T application/json http://localhost:8000/api/v1/traffic/predict
```

### Python Integration Test

Tạo file `integration_test.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000"

def test_full_workflow():
    print("🧪 Starting Integration Tests...")
    
    # Test 1: Health
    print("\n[1/5] Testing Health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()['status'] == 'healthy'
    print("   ✅ Health check passed")
    
    # Test 2: Get Traffic
    print("\n[2/5] Testing Get Traffic...")
    r = requests.get(f"{BASE_URL}/api/v1/traffic/current/segment_001")
    assert r.status_code == 200
    data = r.json()
    assert data['speed'] > 0
    assert data['intensity'] > 0
    print(f"   ✅ Traffic data: Speed={data['speed']} km/h")
    
    # Test 3: ML Prediction
    print("\n[3/5] Testing ML Prediction...")
    payload = {
        "road_segment_id": "segment_001",
        "prediction_horizon": 15,
        "model_type": "ensemble"
    }
    r = requests.post(f"{BASE_URL}/api/v1/traffic/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data['predictions']) > 0
    print(f"   ✅ Prediction: Speed={data['predictions'][0]['predicted_speed']:.1f} km/h")
    
    # Test 4: Smart Routing
    print("\n[4/5] Testing Smart Routing...")
    payload = {
        "origin": "segment_001",
        "destination": "segment_010"
    }
    start = time.time()
    r = requests.post(f"{BASE_URL}/api/v1/routing/find-route", json=payload)
    duration = time.time() - start
    assert r.status_code == 200
    data = r.json()
    assert data['route']['total_distance'] > 0
    print(f"   ✅ Route found: {data['route']['total_distance']:.1f} km in {duration*1000:.0f}ms")
    
    # Test 5: Models Info
    print("\n[5/5] Testing Models Info...")
    r = requests.get(f"{BASE_URL}/api/v1/traffic/models/info")
    assert r.status_code == 200
    data = r.json()
    assert data['models_loaded'] == True
    assert data['total_models'] >= 3
    print(f"   ✅ Models loaded: {data['total_models']}")
    
    print("\n" + "="*50)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*50)

if __name__ == "__main__":
    test_full_workflow()
```

Chạy:
```powershell
python integration_test.py
```

---

## 🎯 TIẾP THEO SAU KHI TEST

### ✅ Nếu Tất Cả Tests PASS:

1. **Deploy Production**
   ```powershell
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Setup Monitoring**
   - Cài Prometheus + Grafana
   - Add health check endpoints
   - Setup alerts

3. **Optimize Performance**
   - Add Redis caching
   - Database indexing
   - CDN cho frontend

4. **Documentation**
   - User manual
   - API guide
   - Deployment guide

### ❌ Nếu Có Tests FAIL:

1. **Check Logs**
   ```powershell
   # Backend
   docker-compose logs backend
   
   # Frontend
   docker-compose logs frontend
   ```

2. **Review Errors**
   - Đọc error messages kỹ
   - Tham khảo Troubleshooting section
   - Google error messages

3. **Fix & Retest**
   - Sửa lỗi
   - Restart services
   - Run tests lại

4. **Report Issues**
   - Document lỗi
   - Steps to reproduce
   - Screenshots nếu cần

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề không giải quyết được:

1. **Check Documentation:**
   - TEST_README.md (file này)
   - TESTING_GUIDE.md
   - DOCKER_GUIDE.md
   - QUICK_START.md

2. **Review Logs:**
   - Backend logs
   - Frontend logs
   - Database logs
   - Docker logs

3. **Common Issues:**
   - Path có ký tự tiếng Việt
   - Port đã được dùng
   - Services chưa start
   - Network issues

---

## ✨ TIPS & TRICKS

### Tip 1: Test Nhanh Một Endpoint
```powershell
# Thay vì gõ dài dòng, tạo function:
function Test-Traffic {
    param($segmentId)
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/$segmentId" | ConvertFrom-Json | Format-List
}

# Sử dụng:
Test-Traffic -segmentId "segment_001"
```

### Tip 2: Monitor Logs Real-time
```powershell
# Split terminal và xem logs liên tục
docker-compose logs -f backend | Select-String "ERROR|WARNING"
```

### Tip 3: Quick Restart
```powershell
# Restart nhanh một service
docker-compose restart backend
```

### Tip 4: Check All Endpoints
```powershell
# Test tất cả traffic endpoints
$segments = 1..10 | ForEach-Object { "segment_{0:D3}" -f $_ }
foreach ($seg in $segments) {
    Write-Host "Testing $seg..." -ForegroundColor Yellow
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/traffic/current/$seg"
        Write-Host "  ✅ OK" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ FAILED" -ForegroundColor Red
    }
}
```

---

**🎉 CHÚC BẠN TEST THÀNH CÔNG! 🎉**

Created by: Smart Traffic Team  
Last Updated: 12/11/2025  
Version: 1.0
