# 🚀 Quick Start Guide - Smart Traffic System

## 🎯 Get Started in 5 Minutes

### Prerequisites
- ✅ Python 3.10+
- ✅ Node.js 18+
- ✅ SQL Server (hoặc Docker)
- ✅ Git

---

## Option 1: Docker (Fastest) 🐳

### 1. Clone & Navigate
```powershell
git clone https://github.com/duongloc216/Smart-Transport.git
cd Smart-Transport\smart-traffic-system
```

### 2. Configure
```powershell
# Copy environment template
copy .env.example .env

# Edit .env (minimum: set DB_PASSWORD)
notepad .env
```

### 3. Deploy
```powershell
# Run deployment script
.\deploy.ps1

# Or manually:
docker-compose up -d
```

### 4. Access
- **Frontend**: http://localhost
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

✅ **Done! System is running**

---

## Option 2: Manual Setup 🛠️

### Step 1: Database

```powershell
# Option A: Docker SQL Server
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest

# Option B: Local SQL Server
# Install from: https://www.microsoft.com/sql-server/sql-server-downloads

# Create database
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "CREATE DATABASE SmartTrafficDB"

# Run schema
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -d SmartTrafficDB -i "smart-traffic-system\database\schemas\create_all.sql"
```

### Step 2: Backend

```powershell
# Navigate to backend
cd smart-traffic-system\backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure
copy .env.example .env
notepad .env  # Edit with your settings

# Run server
python main.py
```

✅ Backend running at: http://localhost:8000

### Step 3: Frontend

```powershell
# Open new terminal
cd smart-traffic-system\frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

✅ Frontend running at: http://localhost:3000

---

## 🧪 Test the System

### 1. Check Backend Health
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Get Traffic Data
```powershell
curl http://localhost:8000/api/v1/traffic/realtime/all
```

### 3. Predict Traffic
```powershell
curl -X POST http://localhost:8000/api/v1/traffic/predict -H "Content-Type: application/json" -d '{\"road_segment_id\": \"segment_001\", \"prediction_horizon\": 15}'
```

### 4. Find Route
```powershell
curl -X POST http://localhost:8000/api/v1/routing/find-route -H "Content-Type: application/json" -d '{\"origin\": \"segment_001\", \"destination\": \"segment_010\"}'
```

---

## 📊 Access Features

### Frontend Dashboard
1. Open: http://localhost (or http://localhost:3000)
2. View real-time traffic map
3. See traffic statistics
4. Explore road segments

### API Documentation
1. Open: http://localhost:8000/api/docs
2. Browse 14 endpoints
3. Try interactive API calls
4. View schemas

### Database
```powershell
# Connect to database
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -d SmartTrafficDB

# Query traffic data
SELECT TOP 10 * FROM TrafficFlowObserved ORDER BY DateObserved DESC
GO
```

---

## 🔧 Common Issues

### Port Already in Use

**Backend (8000):**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or change port in .env
PORT=8001
```

**Frontend (3000):**
```powershell
# Change port in vite.config.js
server: { port: 3001 }
```

### Database Connection Failed

```powershell
# Check SQL Server is running
docker ps | findstr sqlserver

# Test connection
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd" -Q "SELECT 1"

# Check credentials in .env
DB_SERVER=localhost
DB_PASSWORD=YourStrong@Passw0rd
```

### ML Models Not Found

```powershell
# Check models directory
dir smart-traffic-system\ml-pipeline\models\saved_models

# Should see:
# xgboost_congestion.pkl
# lightgbm_speed.pkl
# prophet_models.pkl
# scaler.pkl
# feature_columns.pkl
```

### Frontend Can't Connect to Backend

```powershell
# Check CORS settings in backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Or use proxy in vite.config.js (already configured)
```

---

## 🎓 Next Steps

### 1. Explore API
- Open http://localhost:8000/api/docs
- Try all 14 endpoints
- View request/response schemas

### 2. Customize Data
```powershell
# Add more road segments
cd smart-traffic-system\ml-pipeline\scripts
python seed_road_segments.py

# Collect traffic data
python collect_osrm_traffic.py
```

### 3. Train Models (Optional)
```powershell
# If you have new data
cd smart-traffic-system\ml-pipeline\notebooks
# Open and run training notebooks
```

### 4. Deploy to Production
```powershell
# Build for production
docker-compose -f docker-compose.yml up -d

# Or deploy to cloud
# See DOCKER_GUIDE.md for cloud deployment
```

---

## 📚 Documentation

- **Main README**: [README.md](README.md)
- **Completion Report**: [COMPLETION_REPORT.md](COMPLETION_REPORT.md)
- **Docker Guide**: [smart-traffic-system/DOCKER_GUIDE.md](smart-traffic-system/DOCKER_GUIDE.md)
- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 💡 Tips

### Development
```powershell
# Watch backend logs
python main.py  # In backend directory

# Watch frontend changes
npm run dev  # Hot reload enabled

# Monitor database
sqlcmd -S localhost -U sa -P "YourStrong@Passw0rd"
```

### Production
```powershell
# Build optimized frontend
npm run build

# Run backend with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# Use Docker (recommended)
docker-compose up -d
```

---

## 🎉 Success!

You now have a fully functional Smart Traffic System running with:
- ✅ Real-time traffic monitoring
- ✅ AI-powered predictions
- ✅ Smart route finding
- ✅ Interactive dashboard

**Enjoy your Smart Traffic System! 🚀**

---

## 📞 Need Help?

- 📖 Check [Documentation](README.md)
- 🐛 Report [Issues](https://github.com/duongloc216/Smart-Transport/issues)
- 💬 Ask questions in Discussions

**Made with ❤️ by Smart Traffic Team**
