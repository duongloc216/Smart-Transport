# 🗺️ HƯỚNG DẪN SETUP GOOGLE MAPS API

## Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Đăng nhập với Google Account
3. Click "Select a project" → "New Project"
4. Đặt tên project: **"Smart Traffic System"**
5. Click "Create"

## Bước 2: Enable APIs

### 2.1. Enable Distance Matrix API
1. Trong Google Cloud Console, mở menu bên trái
2. Chọn **"APIs & Services"** → **"Library"**
3. Tìm kiếm **"Distance Matrix API"**
4. Click vào API
5. Click **"Enable"**

### 2.2. Enable Roads API
1. Tìm kiếm **"Roads API"**
2. Click vào API
3. Click **"Enable"**

### 2.3. Enable Directions API (Optional - for advanced routing)
1. Tìm kiếm **"Directions API"**
2. Click **"Enable"**

## Bước 3: Tạo API Key

1. Trong menu bên trái, chọn **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. API key sẽ được tạo tự động
4. **QUAN TRỌNG**: Click vào API key vừa tạo để configure

### 3.1. Restrict API Key (Recommended for security)

**Application restrictions:**
- Chọn "HTTP referrers (web sites)" nếu dùng cho web
- Hoặc "IP addresses" nếu dùng cho server
- Thêm IP của máy bạn (development): `your_ip_address`

**API restrictions:**
- Chọn "Restrict key"
- Chọn APIs:
  - ✅ Distance Matrix API
  - ✅ Roads API
  - ✅ Directions API (optional)

5. Click **"Save"**

## Bước 4: Copy API Key vào Project

1. Copy API key (dạng: `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
2. Mở file `.env` trong thư mục `backend/`
3. Thêm dòng:
   ```env
   GOOGLE_MAPS_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## Bước 5: Enable Billing (QUAN TRỌNG!)

**Lưu ý**: Google Maps API yêu cầu billing account, nhưng có **$200 free credit mỗi tháng**

1. Trong Google Cloud Console, chọn **"Billing"**
2. Click **"Link a billing account"**
3. Thêm thẻ tín dụng (sẽ không bị charge nếu dưới $200/tháng)
4. Confirm

### Chi phí ước tính:

**Distance Matrix API:**
- $5 / 1000 requests
- Free: $200/month = 40,000 requests/month
- **~1,330 requests/day = MIỄN PHÍ**

**Roads API:**
- $10 / 1000 requests  
- Free: $200/month = 20,000 requests/month
- **~660 requests/day = MIỄN PHÍ**

## Bước 6: Test API Key

Chạy script test:

```powershell
cd ml-pipeline\scripts
python test_google_api.py
```

Nếu thành công, bạn sẽ thấy:
```
✅ API Key valid!
✅ Distance Matrix API working!
Current traffic speed: 42.5 km/h
```

## Bước 7: Thu thập Traffic Data

```powershell
# Collect traffic cho 10 road segments
python collect_google_traffic.py
```

## 📊 API Quotas & Limits

### Free Tier ($200 credit/month):
- Distance Matrix: 40,000 requests/month
- Roads API: 20,000 requests/month
- **Total: ~1,330 requests/day MIỄN PHÍ**

### Rate Limits:
- 50 queries per second (QPS)
- 100 elements per request (Distance Matrix)

### Recommendations:
- Collect traffic every 15 minutes: 96 requests/day/segment
- With 10 segments: 960 requests/day ✅ OK
- With 40 segments: 3,840 requests/day ⚠️ Close to limit

## 🔒 Security Best Practices

1. **Restrict API Key** by IP addresses
2. **Enable only necessary APIs**
3. **Set spending limits** in Billing settings:
   - Budget: $50/month
   - Alerts at 50%, 90%, 100%
4. **Monitor usage** in Google Cloud Console
5. **NEVER commit** .env file to git

## ⚠️ Troubleshooting

### Error: "API key not valid"
- Check if API key copied correctly (no spaces)
- Check if APIs are enabled
- Wait 5 minutes after creating key

### Error: "This API project is not authorized"
- Enable required APIs (Distance Matrix, Roads)
- Check API restrictions

### Error: "You must enable Billing"
- Add billing account
- Confirm credit card

### Error: "OVER_QUERY_LIMIT"
- You exceeded free quota
- Wait until next month or add more budget
- Reduce collection frequency

## 📝 Alternative: HERE Maps API

Nếu không muốn dùng Google Maps, có thể dùng HERE Maps:

1. Đăng ký [HERE Developer](https://developer.here.com/)
2. Free tier: 250,000 transactions/month
3. API key setup tương tự
4. Update `.env`: `HERE_MAPS_API_KEY=your_key`
5. Chạy script: `collect_here_traffic.py`

## 💡 Tips

- **Start small**: Test với 5-10 segments trước
- **Monitor costs**: Check billing dashboard weekly
- **Cache data**: Không collect quá thường xuyên (15-30 phút/lần là đủ)
- **Backup plan**: Có HERE Maps API key backup

---

**Done! Bây giờ bạn có thể thu thập real traffic data! 🎉**
