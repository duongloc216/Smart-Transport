# 🗺️ Google Maps API Setup Guide

**Ngày tạo:** October 15, 2025  
**Mục đích:** Hướng dẫn setup Google Maps API để thu thập dữ liệu traffic thực tế

---

## 📋 Tổng quan

Dự án cần **3 APIs** từ Google Maps Platform:
1. **Distance Matrix API** - Tính thời gian di chuyển thực tế giữa các điểm
2. **Roads API** - Snap GPS coordinates lên đường thực tế
3. **Directions API** - Tính route & thời gian dự kiến

**Chi phí dự kiến:** ~$33.6 cho 7 ngày thu thập dữ liệu (trong $200 free credit)

---

## 🚀 Bước 1: Tạo Google Cloud Account

### 1.1. Truy cập Google Cloud Console
```
URL: https://console.cloud.google.com/
```

### 1.2. Đăng nhập
- Sử dụng tài khoản Google cá nhân hoặc tạo mới
- Nếu lần đầu, bạn sẽ thấy màn hình Welcome

### 1.3. Accept Terms of Service
- Đọc và chấp nhận Terms of Service
- Chọn Country/Region: **Vietnam**

### 1.4. Free Trial
- Google cung cấp **$300 credit miễn phí** cho 90 ngày đầu
- Sau đó **$200 credit mỗi tháng** (không tính phí nếu dưới quota)
- ⚠️ **BẮT BUỘC:** Phải thêm credit card (nhưng sẽ không auto-charge)

---

## 🏗️ Bước 2: Tạo Project Mới

### 2.1. Click "Select a project" (góc trên bên trái)

### 2.2. Click "NEW PROJECT"

### 2.3. Điền thông tin project:
```
Project name: Smart-Traffic-System
Project ID: smart-traffic-system-xxxxx (tự động generate)
Organization: No organization
Location: No organization
```

### 2.4. Click "CREATE"
- Đợi ~10-30 giây để project được tạo

### 2.5. Select project vừa tạo
- Click notification bell (góc phải) → Click project name
- Hoặc dùng dropdown "Select a project" → Chọn "Smart-Traffic-System"

✅ **Checkpoint:** Bạn thấy tên project "Smart-Traffic-System" ở góc trên bên trái

---

## 💳 Bước 3: Enable Billing (BẮT BUỘC)

⚠️ **Lưu ý quan trọng:**
- Google Maps APIs yêu cầu billing account
- Credit card chỉ để xác thực, KHÔNG tự động charge
- Bạn có $200 free credit/tháng
- Chỉ tính phí khi vượt $200/tháng

### 3.1. Vào Billing
```
Navigation Menu (☰) → Billing → Link a billing account
```

### 3.2. Create Billing Account
- Click "CREATE BILLING ACCOUNT"

### 3.3. Điền thông tin:
```
Country: Vietnam
Account type: Individual
```

### 3.4. Thêm Payment Method
- Chọn "Add credit or debit card"
- Điền thông tin thẻ:
  - Card number: 16 chữ số
  - Expiration date: MM/YY
  - CVV: 3 chữ số
  - Name on card: Tên trên thẻ
  - Billing address: Địa chỉ của bạn

### 3.5. Click "START MY FREE TRIAL"
- Google sẽ charge $1 để verify (và refund ngay)

### 3.6. Link billing account với project
- Chọn "Smart-Traffic-System" project
- Click "SET ACCOUNT"

✅ **Checkpoint:** Bạn thấy "Billing account linked" notification

---

## 🔑 Bước 4: Enable APIs

### 4.1. Vào APIs & Services
```
Navigation Menu (☰) → APIs & Services → Library
```

### 4.2. Enable Distance Matrix API
1. Tìm kiếm: **"Distance Matrix API"**
2. Click vào result đầu tiên
3. Click **"ENABLE"**
4. Đợi ~5-10 giây

### 4.3. Enable Roads API
1. Click "Library" (trở về)
2. Tìm kiếm: **"Roads API"**
3. Click vào result
4. Click **"ENABLE"**

### 4.4. Enable Directions API
1. Click "Library" (trở về)
2. Tìm kiếm: **"Directions API"**
3. Click vào result
4. Click **"ENABLE"**

✅ **Checkpoint:** Vào "Dashboard" → Thấy 3 APIs được enable

---

## 🔐 Bước 5: Tạo API Key

### 5.1. Vào Credentials
```
Navigation Menu (☰) → APIs & Services → Credentials
```

### 5.2. Create Credentials
- Click **"+ CREATE CREDENTIALS"** (góc trên)
- Chọn **"API key"**

### 5.3. Copy API Key
- Một popup hiện ra với API key
- **QUAN TRỌNG:** Copy API key này (dạng: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
- Click "RESTRICT KEY" (recommended)

### 5.4. Restrict API Key (Bảo mật)

#### Tab "API restrictions":
- Chọn **"Restrict key"**
- Select APIs:
  - ✅ Distance Matrix API
  - ✅ Roads API
  - ✅ Directions API
- Click **"SAVE"**

#### Tab "Application restrictions" (Optional):
- Để "None" nếu test local
- Hoặc chọn "IP addresses" → thêm IP server của bạn

✅ **Checkpoint:** API key được tạo và restricted

---

## ⚙️ Bước 6: Thêm API Key vào Project

### 6.1. Mở file `.env`
```powershell
cd "e:\CĐTT2\Smart-Transport\smart-traffic-system\backend"
notepad .env
```

### 6.2. Thêm dòng này (thay YOUR_API_KEY):
```env
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 6.3. Lưu file (Ctrl+S)

✅ **Checkpoint:** File `.env` có dòng `GOOGLE_MAPS_API_KEY=...`

---

## 🧪 Bước 7: Test API Key

Sau khi bạn hoàn thành các bước trên, báo mình để test API key!

Mình sẽ tạo script test:
```python
# Test Distance Matrix API
# Test Roads API
# Verify quota & billing
```

---

## 📊 Chi phí & Quota Monitoring

### Theo dõi usage:
```
Navigation Menu (☰) → APIs & Services → Dashboard
→ Click vào API → Tab "Quotas & System Limits"
```

### Pricing (October 2025):
| API | Free Quota | Price after quota |
|-----|------------|-------------------|
| Distance Matrix | $200/month credit | $5 per 1,000 requests |
| Roads | $200/month credit | $10 per 1,000 requests |
| Directions | $200/month credit | $5 per 1,000 requests |

### Dự án này cần:
- **7 ngày collection:** 10 segments × 96/day × 7 = 6,720 requests
- **Distance Matrix:** 6,720 × $5/1000 = **$33.6**
- **Tổng:** ~$35 (trong $200 free credit) ✅

### Set Budget Alert:
```
Navigation Menu (☰) → Billing → Budgets & alerts
→ CREATE BUDGET → Set $50 alert
```

---

## ⚠️ Troubleshooting

### Lỗi "This API project is not authorized..."
- **Nguyên nhân:** Billing chưa enable
- **Giải pháp:** Quay lại Bước 3, enable billing

### Lỗi "API key not valid..."
- **Nguyên nhân:** API key sai hoặc bị restrict
- **Giải pháp:** 
  1. Check API key trong `.env` (không có space)
  2. Verify API restrictions (phải enable 3 APIs)

### Lỗi "Quota exceeded"
- **Nguyên nhân:** Vượt free quota
- **Giải pháp:** 
  1. Check Dashboard → Quotas
  2. Wait until next month
  3. Hoặc upgrade billing

---

## ✅ Checklist Hoàn thành

Trước khi tiếp tục, hãy check:

- [ ] **Google Cloud Account created**
- [ ] **Project "Smart-Traffic-System" created**
- [ ] **Billing enabled** (credit card linked)
- [ ] **Distance Matrix API enabled**
- [ ] **Roads API enabled**
- [ ] **Directions API enabled**
- [ ] **API Key created & copied**
- [ ] **API Key restricted** (3 APIs only)
- [ ] **API Key added to `.env`**
- [ ] **Ready to test!** 🚀

---

## 📞 Hỗ trợ

Nếu gặp vấn đề ở bất kỳ bước nào:
1. Chụp screenshot lỗi
2. Cho mình biết bước nào bị stuck
3. Mình sẽ hướng dẫn chi tiết hơn!

---

**Next Step:** Sau khi hoàn thành tất cả các bước, báo mình để test API key và bắt đầu thu thập dữ liệu! 🎉
