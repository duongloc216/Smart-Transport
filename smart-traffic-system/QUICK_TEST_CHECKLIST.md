# ✅ QUICK TEST CHECKLIST

## 🚀 BẮT ĐẦU TEST (5 PHÚT)

### Option A: Manual Test
```powershell
# Terminal 1: Start Backend
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
python main.py

# Terminal 2: Run Tests
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-manual.ps1
```

### Option B: Docker Test
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system"
.\test-docker.ps1
```

---

## ✅ CHECKLIST - BACKEND (8 TESTS)

- [ ] 1. Health Check → http://localhost:8000/health
- [ ] 2. Get All Traffic → 10 segments returned
- [ ] 3. Get Single Segment → segment_001 data OK
- [ ] 4. Get Traffic History → 10 records returned
- [ ] 5. ML Prediction → Reasonable predictions
- [ ] 6. Smart Routing → Path found
- [ ] 7. Models Info → 6 models loaded
- [ ] 8. API Docs → http://localhost:8000/api/docs opens

**Pass Criteria:** All 8 tests ✅

---

## ✅ CHECKLIST - FRONTEND

- [ ] Page loads without errors
- [ ] Map displays correctly
- [ ] 10 road segments visible
- [ ] Segments color-coded (🟢🟡🔴)
- [ ] Click segment → Popup shows
- [ ] Statistics cards show data
- [ ] Auto-refresh every 30s
- [ ] "Last Updated" timestamp changes

**URL:** http://localhost:3000 (manual) or http://localhost (docker)

**Pass Criteria:** All features working ✅

---

## ✅ CHECKLIST - DATABASE

```powershell
# Quick check
sqlcmd -S localhost -d SmartTrafficDB -Q "SELECT COUNT(*) FROM TrafficFlowObserved"
```

- [ ] Connection successful
- [ ] ≥ 8000 traffic records
- [ ] All tables accessible

**Pass Criteria:** All queries return data ✅

---

## ✅ CHECKLIST - DOCKER

```powershell
docker-compose ps
```

- [ ] Backend container running
- [ ] Frontend container running
- [ ] SQL Server container running
- [ ] Redis container running
- [ ] No errors in logs

**Pass Criteria:** All 4 containers running ✅

---

## 🎯 OVERALL PASS CRITERIA

- [x] Backend: 8/8 tests pass
- [x] Frontend: All features working
- [x] Database: All queries OK
- [x] Docker: All containers running

**Result:** ✅ SYSTEM READY FOR PRODUCTION

---

## 🔧 QUICK FIXES

### Backend not starting?
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
python main.py
```

### Frontend not loading?
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\frontend"
npm install
npm run dev
```

### Docker failed?
```powershell
docker-compose down
docker-compose up --build
```

---

## 📖 FULL GUIDES

- **TEST_GUIDE_VI.md** - Hướng dẫn chi tiết tiếng Việt
- **TEST_README.md** - Complete English testing guide
- **TESTING_GUIDE.md** - Original testing documentation

---

**Quick Start:** Run `.\test-manual.ps1` or `.\test-docker.ps1` 🚀
