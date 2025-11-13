# 🎯 DEMO QUICK REFERENCE

## 🚀 START SYSTEM (2 phút)

```powershell
# Terminal 1: Backend
cd backend
python main.py
# Đợi: ✅ ML models loaded successfully!

# Terminal 2: Frontend  
cd frontend
npm run dev
# Mở: http://localhost:5173
```

---

## 🎬 DEMO FLOW (5 phút)

### 1️⃣ Click "📍 Tìm đường" (góc phải)

### 2️⃣ Chọn:
- Origin: `segment_001`
- Destination: `segment_010`
- Time: Để trống

### 3️⃣ Click "🚀 Tìm tuyến đường tối ưu"

### 4️⃣ CHỈ VÀO & GIẢI THÍCH:

#### ✅ Badge "🤖 AI-Predicted"
> "Route dùng AI predictions, không phải current traffic"

#### ✅ Phần "💡 Cách tính toán"
> "Route calculated using AI-predicted traffic at **arrival times**"

#### ✅ Chi tiết segment (KEY!)
```
5  segment_005
   🕐 10:15:23  ⬅️ NHẤN MẠNH!
```
> "Em tới segment_005 lúc 10:15
> 
> Hệ thống predict traffic **lúc 10:15**, không phải hiện tại
>
> Nếu hiện tại kẹt nhưng 10:15 hết kẹt → Vẫn đi qua!"

---

## 💬 KEY MESSAGES

### Câu 1: Vấn đề Google Maps
> "Google Maps tính route dựa trên traffic HIỆN TẠI"

### Câu 2: Giải pháp của em
> "Em dự đoán traffic TƯƠNG LAI khi TỚI từng đoạn đường"

### Câu 3: Ví dụ cụ thể
> "Điểm C đang kẹt, Google gợi ý tránh. Nhưng nếu em tới C sau 15 phút và ML dự đoán lúc đó hết kẹt → Đi qua C vẫn tối ưu!"

### Câu 4: Technical highlight
> "3 ML models (XGBoost 99%, LightGBM R²=0.98, Prophet MAPE 8%) + A* algorithm"

---

## 🆘 BACKUP PLANS

### Nếu frontend lỗi:
→ Demo bằng Swagger UI: http://localhost:8000/api/docs

### Nếu backend lỗi:
→ Show screenshots + giải thích algorithm

### Nếu không có internet:
→ Map sẽ không load, focus vào API responses

---

## ⏱️ TIME MANAGEMENT

- Giới thiệu: 30s
- Demo frontend: 2 phút
- Giải thích arrival_time: 1 phút
- So sánh Google Maps: 1 phút
- Q&A: 30s

**TOTAL: 5 phút**

---

## 🎯 MUST-MENTION POINTS

1. ✅ "arrival_time" ở mỗi segment
2. ✅ "prediction_based: true"
3. ✅ So sánh với Google Maps
4. ✅ 3 ML models với accuracy
5. ✅ Real-world application

---

## 📞 EMERGENCY CONTACTS

- Backend port: 8000
- Frontend port: 5173
- API docs: /api/docs
- Test script: `.\retest.ps1`

---

**IN NGAY RA GIẤY & ĐỂ BÊN LAPTOP!** 📄
