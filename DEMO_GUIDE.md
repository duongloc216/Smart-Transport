# 🎬 HƯỚNG DẪN DEMO PREDICTIVE ROUTING

## 📋 CHUẨN BỊ

### 1. Start Backend
```powershell
cd e:\CĐTT2\Smart-Transport\smart-traffic-system\backend
python main.py
```
Đợi thấy: `✅ ML models loaded successfully!`

### 2. Start Frontend
```powershell
cd e:\CĐTT2\Smart-Transport\smart-traffic-system\frontend
npm run dev
```
Mở: http://localhost:5173

---

## 🎯 OPTION 1: DEMO BẰNG FRONTEND (VISUAL - KHUYẾN NGHỊ) ⭐

### Bước 1: Mở Dashboard
- Truy cập: http://localhost:5173
- Giao diện hiển thị dashboard với map và stats

### Bước 2: Click nút "📍 Tìm đường"
- Ở góc trên bên phải
- Sẽ mở modal "AI-Powered Route Planning"

### Bước 3: Nhập thông tin
1. **Điểm xuất phát**: Chọn `segment_001`
2. **Điểm đến**: Chọn `segment_010`
3. **Thời gian xuất phát**: Để trống (xuất phát ngay)
   - Hoặc chọn thời gian tương lai (vd: 2 giờ sau)

### Bước 4: Click "🚀 Tìm tuyến đường tối ưu"

### Bước 5: Giải thích kết quả cho thầy 👨‍🏫

**CHỈ VÀO CÁC THÔNG TIN:**

#### A. Badge "🤖 AI-Predicted"
> "Thưa thầy, badge này chứng tỏ route được tính bằng AI predictions, không phải current traffic"

#### B. Thống kê tổng quan
- **📏 Tổng quãng đường**: X km
- **⏱️ Thời gian dự kiến**: Y phút
- **🚦 Số đoạn đường**: 10 segments

#### C. Thời gian xuất phát & đến
> "Hệ thống tính được:
> - Xuất phát: 10:00
> - Tới nơi: 10:32"

#### D. 💡 Cách tính toán (KEY POINT!)
Đọc phần "Cách tính toán":
> "Route calculated using AI-predicted traffic at arrival times for each segment"

**Giải thích:**
> "Thầy thấy câu này không? Đây là điểm khác biệt với Google Maps:
> - Google Maps: Tính cost dựa trên traffic HIỆN TẠI
> - Hệ thống em: Tính cost dựa trên traffic DỰ ĐOÁN khi em TỚI đoạn đường đó"

#### E. Chi tiết tuyến đường (DEMO CHÍNH!) ⭐⭐⭐

Scroll xuống phần "📍 Chi tiết tuyến đường"

**CHỈ VÀO MỖI SEGMENT:**

Segment thứ 1:
```
1  segment_001
   🕐 10:00:00
   📏 1.5 km  ⚡ Max: 60 km/h
```
> "Em xuất phát từ segment_001 lúc 10:00"

Segment thứ 5:
```
5  segment_005
   🕐 10:15:23  ⬅️ CHỈ VÀO ĐÂY!
   📏 1.5 km  ⚡ Max: 60 km/h
```
> "Thầy chú ý! Em sẽ tới segment_005 lúc 10:15
>
> Nếu segment_005 HIỆN TẠI đang kẹt xe, Google Maps sẽ gợi ý tránh.
>
> NHƯNG hệ thống em dự đoán lúc 10:15 (15 phút sau), segment_005 đã HẾT KẸT!
>
> → AI predict traffic lúc 10:15, không phải lúc 10:00
> → Route qua segment_005 vẫn tối ưu!"

Segment cuối:
```
10  segment_010
    🕐 10:32:15
    📏 0 km (đích đến)
```
> "Và em tới đích lúc 10:32, tổng 32 phút"

---

## 🎯 OPTION 2: DEMO BẰNG SWAGGER UI (CHI TIẾT HƠN)

### Bước 1: Mở API Docs
```
http://localhost:8000/api/docs
```

### Bước 2: Demo Current Traffic (để so sánh)
1. Tìm **GET /api/v1/traffic/current/{segment_id}**
2. "Try it out" → `segment_id = segment_005`
3. Execute

**Nói:**
> "Đây là traffic HIỆN TẠI của segment_005:
> - Speed: X km/h (giả sử đang chậm)
> - Status: CONGESTED (đang kẹt)"

### Bước 3: Demo Prediction (Traffic tương lai)
1. Tìm **POST /api/v1/traffic/predict**
2. "Try it out"
3. Body:
```json
{
  "road_segment_id": "segment_005",
  "prediction_horizon": 15,
  "model_type": "ensemble"
}
```
4. Execute

**Nói:**
> "ML dự đoán traffic sau 15 phút:
> - Predicted speed: Y km/h (cao hơn hiện tại)
> - Congestion probability: Z% (thấp hơn)
> → 15 phút sau đã hết kẹt!"

### Bước 4: Demo Predictive Routing
1. Tìm **POST /api/v1/routing/find-route**
2. "Try it out"
3. Body:
```json
{
  "origin": "segment_001",
  "destination": "segment_010",
  "departure_time": "2025-11-13T10:00:00",
  "mode": "optimal"
}
```
4. Execute

**Scroll response, CHỈ VÀO:**

```json
{
  "prediction_based": true,  // ⬅️ Dùng AI
  "explanation": "Route calculated using AI-predicted traffic at arrival times for each segment",
  
  "segments": [
    {
      "segment_id": "segment_005",
      "arrival_time": "2025-11-13T10:15:23",  // ⬅️ CHỈ VÀO!
      "name": "Vo Van Ngan - Section 5",
      "distance_km": 1.5
    }
  ],
  
  "departure_time": "2025-11-13T10:00:00",
  "estimated_arrival_time": "2025-11-13T10:32:15"
}
```

**Script:**
> "Thầy thấy không:
> 1. **arrival_time**: 10:15:23 - Thời gian em tới segment_005
> 2. Khi tính cost, hệ thống dùng **predicted traffic lúc 10:15**, không phải lúc 10:00
> 3. **prediction_based: true** - Confirm dùng AI predictions
>
> Đây là breakthrough của em: TIME-AWARE PREDICTIVE ROUTING!"

---

## 💡 CÂU HỎI THẦY CÓ THỂ HỎI

### Q1: "Làm sao biết prediction đúng?"
**A:** 
> "Thưa thầy, em đã evaluate models:
> - XGBoost: 99% accuracy
> - LightGBM: R² = 0.98, MAE = 0.58 km/h
> - Prophet: MAPE = 8%
>
> Có thể demo phần Models Info để thầy xem"

### Q2: "Nếu prediction sai thì sao?"
**A:**
> "Hệ thống em có confidence intervals và fallback:
> - Nếu ML không available → Dùng historical average
> - Có thể tính multiple alternative routes
> - Real-time updates mỗi 30 giây để adjust"

### Q3: "So sánh với Google Maps?"
**A:**
> "Thưa thầy:
> 
> **Google Maps:**
> - Tính route dựa trên traffic HIỆN TẠI
> - Không biết traffic sẽ thay đổi như thế nào
>
> **Hệ thống em:**
> - Tính route dựa trên traffic DỰ ĐOÁN TƯƠNG LAI
> - Predict traffic tại thời điểm TỚI từng segment
> - Tránh được trường hợp: 'Kẹt xe hiện tại nhưng tới nơi đã hết kẹt'"

### Q4: "Áp dụng thực tế như thế nào?"
**A:**
> "Có thể tích hợp vào:
> - Navigation apps (thay thế Google Maps)
> - Smart city systems
> - Logistics & delivery optimization
> - Public transportation planning"

---

## 🎯 TIPS DEMO THÀNH CÔNG

### DO's ✅
1. **Demo Frontend trước** (visual, dễ hiểu)
2. **Nhấn mạnh arrival_time** ở mỗi segment
3. **So sánh current vs predicted traffic** cho 1 segment
4. **Giải thích "prediction_based: true"**
5. **Show confidence với accuracy metrics**

### DON'Ts ❌
1. Không nói quá nhiều technical terms
2. Không skip phần "arrival_time" (đây là KEY!)
3. Không quên giải thích "tại sao khác Google Maps"
4. Không demo khi backend chưa chạy

---

## 📊 DEMO SCRIPT MẪU (30 GIÂY)

> "Thưa thầy, em xin demo tính năng Predictive Routing:
>
> [Click nút Tìm đường]
>
> Em chọn đi từ segment_001 đến segment_010, xuất phát lúc 10:00
>
> [Click Tìm tuyến đường tối ưu]
>
> Hệ thống tìm được route 13.5 km, 32 phút. 
>
> [CHỈ VÀO BADGE AI-PREDICTED]
>
> Badge này chứng tỏ route dùng AI predictions.
>
> [SCROLL XUỐNG CHI TIẾT]
>
> Thầy chú ý segment_005 - em sẽ tới đây lúc 10:15.
>
> Khi tính cost của segment này, hệ thống KHÔNG dùng traffic hiện tại,
> mà dùng PREDICTED traffic lúc 10:15!
>
> Nếu segment_005 hiện tại kẹt xe nhưng ML dự đoán 10:15 hết kẹt
> → Route vẫn đi qua đây vì tối ưu hơn!
>
> Đây là điểm khác biệt với Google Maps: TIME-AWARE PREDICTIVE ROUTING!"

---

## 🚀 CHUẨN BỊ TRƯỚC BUỔI DEMO

1. ✅ Test lại toàn bộ: `.\retest.ps1` → Phải 6/6 PASS
2. ✅ Kiểm tra frontend load được dữ liệu
3. ✅ Chuẩn bị backup plan: Swagger UI nếu frontend lỗi
4. ✅ Screenshot kết quả để backup
5. ✅ Học thuộc script 30 giây
6. ✅ Chuẩn bị trả lời 4 câu hỏi phổ biến

---

**CHÚC BẠN DEMO THÀNH CÔNG!** 🎉👨‍🎓
