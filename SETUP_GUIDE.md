# 🚀 HƯỚNG DẪN SETUP CHI TIẾT - SMART TRAFFIC SYSTEM

## ✅ BƯỚC 1: SETUP MÔI TRƯỜNG (ĐÃ HOÀN THÀNH)

### ✓ Python 3.10.11 - Ready!
### ✓ File .env đã được tạo

---

## 📝 BƯỚC 2: CẤU HÌNH DATABASE

### 2.1. Cài đặt SQL Server

#### Option A: SQL Server Express (Recommended cho Windows)
1. Download SQL Server 2022 Express:
   ```
   https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   ```
2. Download SQL Server Management Studio (SSMS):
   ```
   https://aka.ms/ssmsfullsetup
   ```
3. Cài đặt với các options:
   - Mixed Mode Authentication
   - Password cho `sa` user: **YourStrong@Passw0rd**
   - Default instance name: **MSSQLSERVER**

#### Option B: Docker (Nhanh hơn)
```powershell
# Pull SQL Server image
docker pull mcr.microsoft.com/mssql/server:2019-latest

# Run SQL Server container
docker run -e "ACCEPT_EULA=Y" `
  -e "SA_PASSWORD=YourStrong@Passw0rd" `
  -p 1433:1433 `
  --name sql-server-smart-traffic `
  -d mcr.microsoft.com/mssql/server:2019-latest

# Check if running
docker ps
```

### 2.2. Kiểm tra kết nối

#### Sử dụng SSMS:
1. Mở SQL Server Management Studio
2. Connect với:
   - Server name: `localhost` hoặc `localhost,1433`
   - Authentication: SQL Server Authentication
   - Login: `sa`
   - Password: `YourStrong@Passw0rd`

#### Hoặc dùng sqlcmd:
```powershell
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "SELECT @@VERSION"
```

### 2.3. Cập nhật file .env

Mở file `smart-traffic-system\backend\.env` và cập nhật:

```env
# Database Configuration (SQL Server)
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=SmartTrafficDB
DB_USER=sa
DB_PASSWORD=YourStrong@Passw0rd
DB_TRUSTED_CONNECTION=no
```

### 2.4. Tạo Database

#### Option A: Sử dụng SSMS
1. Mở SSMS
2. New Query
3. Copy toàn bộ nội dung từ `smart-traffic-system\database\schemas\create_all.sql`
4. Execute (F5)

#### Option B: Command line
```powershell
cd "e:\CĐTT2\Smart-Transport"
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -i "smart-traffic-system\database\schemas\create_all.sql"
```

### 2.5. Verify Database

```sql
-- Kiểm tra database đã được tạo
SELECT name FROM sys.databases WHERE name = 'SmartTrafficDB';

-- Switch to database
USE SmartTrafficDB;

-- Kiểm tra tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;

-- Expected output:
-- TrafficFlowObserved
-- Vehicle
-- Road
-- RoadSegment
-- RoadAccident
-- CityWork
```

---

## 📦 BƯỚC 3: CÀI ĐẶT DEPENDENCIES

### 3.1. Backend Dependencies

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"

# Tạo virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages**:
- fastapi==0.109.0
- uvicorn==0.27.0
- sqlalchemy==2.0.25
- pydantic==2.5.3
- pyodbc==5.0.1
- pandas, numpy, redis, etc.

### 3.2. ML Pipeline Dependencies

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline"

# Install ML dependencies
pip install -r requirements.txt

# Verify TensorFlow
python -c "import tensorflow as tf; print(tf.__version__)"
# Expected: 2.15.0

# Verify XGBoost
python -c "import xgboost; print(xgboost.__version__)"
# Expected: 2.0.3
```

### 3.3. Install ODBC Driver (Nếu chưa có)

SQL Server cần ODBC Driver để kết nối:

```powershell
# Download ODBC Driver 17 for SQL Server
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Check available drivers
python -c "import pyodbc; print(pyodbc.drivers())"
# Should include: 'ODBC Driver 17 for SQL Server'
```

---

## 🗺️ BƯỚC 4: SETUP GOOGLE MAPS API

### 4.1. Tạo Google Cloud Project

1. **Truy cập Google Cloud Console**:
   ```
   https://console.cloud.google.com/
   ```

2. **Create New Project**:
   - Click "Select a project" (top bar)
   - Click "New Project"
   - Project name: `Smart Traffic System`
   - Click "Create"

3. **Enable Billing** (REQUIRED):
   - Menu → Billing → Link a billing account
   - Add credit card (sẽ không bị charge nếu dưới $200/tháng)
   - Google cung cấp **$200 free credit mỗi tháng**

### 4.2. Enable Required APIs

1. **Distance Matrix API**:
   - Menu → APIs & Services → Library
   - Search: "Distance Matrix API"
   - Click → Enable
   - **Used for**: Get real-time traffic between points

2. **Roads API**:
   - Search: "Roads API"
   - Enable
   - **Used for**: Snap coordinates to roads, get speed limits

3. **Directions API** (Optional):
   - Search: "Directions API"
   - Enable
   - **Used for**: Advanced routing

### 4.3. Tạo API Key

1. **Create Credentials**:
   - Menu → APIs & Services → Credentials
   - Click "+ CREATE CREDENTIALS"
   - Select "API key"
   - API key will be generated: `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **Restrict API Key** (IMPORTANT for security):
   - Click on the API key just created
   - Application restrictions:
     - Select "IP addresses"
     - Add your server IP (development: your public IP)
   - API restrictions:
     - Select "Restrict key"
     - Select:
       - ✅ Distance Matrix API
       - ✅ Roads API
       - ✅ Directions API
   - Click "Save"

### 4.4. Update .env File

```env
# External APIs
GOOGLE_MAPS_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4.5. Test API Key

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\scripts"
python test_google_api.py
```

**Expected output**:
```
✅ API Key valid!
✅ Distance Matrix API working!
Distance: 1234 meters
Duration: 180 seconds
Current traffic speed: 42.5 km/h
```

### 4.6. Cost Estimation

**Free tier**: $200 credit/month = ~40,000 requests/month

**Example usage**:
- 10 road segments
- Collect every 15 minutes = 96 requests/day/segment
- Total: 960 requests/day
- Monthly: ~28,800 requests ✅ **STILL FREE**

**⚠️ Recommendations**:
- Set budget alerts in Google Cloud Console
- Collect data every 15-30 minutes (not more frequent)
- Start with 5-10 segments, scale up later

---

## 🧪 BƯỚC 5: TEST BACKEND

### 5.1. Test Database Connection

Tạo file test: `smart-traffic-system\backend\test_db.py`

```python
from app.core.database import engine, get_db
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT @@VERSION"))
            print("✅ Database connected!")
            print(f"SQL Server version: {result.fetchone()[0][:50]}...")
            
            # Test tables
            result = connection.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """))
            tables = [row[0] for row in result]
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

Chạy test:
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
python test_db.py
```

### 5.2. Start Backend Server

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"

# Activate venv nếu chưa activate
.\venv\Scripts\Activate.ps1

# Start server
python main.py

# Hoặc dùng uvicorn trực tiếp
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5.3. Test API Endpoints

Mở browser hoặc Postman:

1. **API Docs**: http://localhost:8000/api/docs
2. **Root**: http://localhost:8000/
3. **Health Check**: http://localhost:8000/health

**Expected responses**:
```json
// GET http://localhost:8000/
{
  "message": "Welcome to Smart Traffic System API",
  "version": "1.0.0",
  "docs": "/api/docs",
  "status": "operational"
}

// GET http://localhost:8000/health
{
  "status": "healthy",
  "timestamp": 1729012345.67,
  "version": "1.0.0"
}
```

---

## 📊 BƯỚC 6: THU THẬP DỮ LIỆU (7 NGÀY)

### 6.1. Tạo Road Segments Configuration

Tạo file: `smart-traffic-system\ml-pipeline\data\road_segments.json`

```json
[
  {
    "id": "segment_001",
    "name": "Nguyen Hue Street",
    "description": "Main boulevard in District 1",
    "origin": {
      "lat": 10.7741,
      "lng": 106.7008
    },
    "destination": {
      "lat": 10.7769,
      "lng": 106.7011
    },
    "road_class": "primary",
    "speed_limit": 40
  },
  {
    "id": "segment_002",
    "name": "Le Loi Boulevard",
    "description": "Central shopping district",
    "origin": {
      "lat": 10.7723,
      "lng": 106.6989
    },
    "destination": {
      "lat": 10.7741,
      "lng": 106.7008
    },
    "road_class": "primary",
    "speed_limit": 50
  },
  {
    "id": "segment_003",
    "name": "Vo Van Tan Street",
    "description": "District 3 arterial road",
    "origin": {
      "lat": 10.7793,
      "lng": 106.6931
    },
    "destination": {
      "lat": 10.7826,
      "lng": 106.6952
    },
    "road_class": "secondary",
    "speed_limit": 50
  }
]
```

**💡 Tips for selecting segments**:
- Choose main roads with high traffic
- Cover different areas of the city
- Include different road types (highways, arterials, collectors)
- Start with 5-10 segments for testing

### 6.2. Run Data Collection Script

```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\scripts"

# Collect traffic data every 15 minutes
python collect_google_traffic.py --segments ../data/road_segments.json --interval 900

# Options:
#   --segments: Path to road segments JSON
#   --interval: Collection interval in seconds (900 = 15 min)
#   --max-runs: Maximum number of collections (default: infinite)
```

### 6.3. Schedule Automatic Collection

#### Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Smart Traffic Data Collection"
4. Trigger: Daily at 00:00
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `collect_google_traffic.py --segments ../data/road_segments.json --interval 900`
   - Start in: `e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\scripts`

#### Or use Python script with schedule:
```python
# collector_daemon.py
import schedule
import time
import subprocess

def collect_traffic():
    subprocess.run(['python', 'collect_google_traffic.py', 
                   '--segments', '../data/road_segments.json'])

# Run every 15 minutes
schedule.every(15).minutes.do(collect_traffic)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 6.4. Monitor Data Collection

```powershell
# Check database for collected data
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -d SmartTrafficDB -Q "
SELECT COUNT(*) as TotalRecords, 
       MIN(dateObservedFrom) as FirstRecord,
       MAX(dateObservedFrom) as LastRecord
FROM TrafficFlowObserved
"
```

**Goal**: Collect at least **7 days** of data before training models
- More data = better predictions
- Aim for 672 data points per segment (7 days × 96 per day)

---

## ✅ CHECKLIST - ĐÃ HOÀN THÀNH?

### Bước 1: Môi trường
- [x] Python 3.10+ installed
- [x] Virtual environment created
- [x] .env file created

### Bước 2: Database
- [ ] SQL Server installed
- [ ] Database SmartTrafficDB created
- [ ] All tables created (6 tables)
- [ ] Connection tested successfully

### Bước 3: Dependencies
- [ ] Backend packages installed
- [ ] ML pipeline packages installed
- [ ] ODBC Driver installed

### Bước 4: Google Maps API
- [ ] Google Cloud Project created
- [ ] Billing enabled
- [ ] APIs enabled (Distance Matrix, Roads, Directions)
- [ ] API Key created and restricted
- [ ] API Key added to .env
- [ ] API tested successfully

### Bước 5: Backend Test
- [ ] Database connection working
- [ ] Backend server starts successfully
- [ ] API docs accessible (http://localhost:8000/api/docs)
- [ ] Health check endpoint working

### Bước 6: Data Collection
- [ ] Road segments JSON created
- [ ] Collection script tested
- [ ] Scheduled task configured
- [ ] Data flowing into database

---

## 🆘 TROUBLESHOOTING

### Issue: Cannot connect to SQL Server
**Solution**:
```powershell
# Check if SQL Server is running
Get-Service | Where-Object {$_.Name -like '*SQL*'}

# Start SQL Server
Start-Service MSSQLSERVER

# Check firewall
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433
```

### Issue: ODBC Driver not found
**Solution**:
```powershell
# List available drivers
python -c "import pyodbc; print(pyodbc.drivers())"

# Download ODBC Driver 17
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### Issue: Google Maps API quota exceeded
**Solution**:
- Check usage: https://console.cloud.google.com/apis/dashboard
- Reduce collection frequency (from 15min to 30min)
- Reduce number of segments
- Wait until next month for quota reset

### Issue: ImportError in Python
**Solution**:
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install individually
pip install fastapi uvicorn sqlalchemy pyodbc pandas
```

---

## 📞 NEXT STEPS

Sau khi hoàn thành setup (Bước 1-6), bạn sẽ có:
- ✅ Backend API đang chạy
- ✅ Database đã setup với schema hoàn chỉnh
- ✅ Data đang được thu thập mỗi 15 phút

**Tiếp theo** (sau 7 ngày thu thập data):
1. **Implement Pydantic Schemas** (Bước 7)
2. **Implement Services** (Bước 8-10)
3. **Train ML Models** (Bước 11)
4. **Build Frontend** (Bước 12)

---

**🎉 Bắt đầu từ Bước 2: Setup Database ngay bây giờ!**
