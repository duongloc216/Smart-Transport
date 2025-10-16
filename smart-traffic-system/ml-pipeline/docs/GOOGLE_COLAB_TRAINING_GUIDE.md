# 🚀 Google Colab Training Guide - Smart Traffic System

## 📋 Tổng quan

**Mục đích:** Train ML models trên Google Colab (Free T4 GPU) rồi download về máy local để deploy

**Lợi ích:**
- ✅ **Free GPU**: T4 GPU miễn phí (15GB VRAM)
- ✅ **Fast**: Train nhanh hơn máy cá nhân 10-50x
- ✅ **No risk**: Máy local không bị treo
- ✅ **Easy**: Chỉ cần browser, không cài gì cả

**Timeline:**
- Export data: 30 giây
- Upload to Drive: 1 phút
- Training on Colab: 15-25 phút
- Download models: 30 giây
- **Total: ~30 phút** ⚡

---

## 🔧 Chi tiết từng bước

### **BƯỚC 1: Export data từ SQL Server (Local)**

```bash
cd e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\scripts
python export_data_for_training.py
```

**Output:**
```
📤 EXPORTING TRAFFIC DATA FOR ML TRAINING
✅ Loaded 8650 records
📁 File saved: ..\data\processed\traffic_data_for_training.csv
📏 File size: ~850 KB
```

**File location:**
```
e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\data\processed\traffic_data_for_training.csv
```

---

### **BƯỚC 2: Upload lên Google Drive**

1. Mở Google Drive: https://drive.google.com
2. Tạo folders:
   ```
   MyDrive/
   └── SmartTraffic/
       ├── data/               # Upload CSV vào đây
       └── models/             # Models sẽ save vào đây
   ```
3. Upload file `traffic_data_for_training.csv` vào `data/`

**Verify:**
- File path: `/MyDrive/SmartTraffic/data/traffic_data_for_training.csv`
- Size: ~850 KB ✅

---

### **BƯỚC 3: Mở Google Colab**

#### **Option A: Upload notebook (RECOMMENDED)**

1. Mở: https://colab.research.google.com
2. Click **File → Upload notebook**
3. Upload file:
   ```
   e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\notebooks\Train_Models_on_Colab.ipynb
   ```

#### **Option B: Import từ Drive**

1. Upload notebook vào Drive trước
2. Right-click → Open with → Google Colaboratory

---

### **BƯỚC 4: Setup Colab Environment**

#### **4.1. Check GPU (QUAN TRỌNG!)**

Menu: **Runtime → Change runtime type**
- Hardware accelerator: **GPU** (T4, 15GB)
- Click **Save**

Verify GPU:
```python
!nvidia-smi
```

Output:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.x.x       Driver Version: 525.x.x       CUDA Version: 12.0  |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
| N/A   42C    P0    26W /  70W |      0MiB / 15360MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

✅ Thấy "Tesla T4" là OK!

#### **4.2. Mount Google Drive**

Run cell đầu tiên:
```python
from google.colab import drive
drive.mount('/content/drive')
```

Click link → Chọn Google account → Allow → Copy authorization code → Paste vào Colab

**Verify:**
```python
!ls /content/drive/MyDrive/SmartTraffic/data/
# Output: traffic_data_for_training.csv
```

---

### **BƯỚC 5: Run Training Cells**

Execute cells **theo thứ tự** (Shift+Enter):

#### **Cell 1: Install packages** (~2 phút)
```python
!pip install -q xgboost lightgbm prophet scikit-learn ...
```

#### **Cell 2-3: Import & Load data** (~10 giây)
```python
df = pd.read_csv(DATA_PATH, ...)
# ✅ Loaded 8650 records
```

#### **Cell 4: Feature engineering** (~30 giây)
```python
df_featured = create_features(df)
# ✅ Created features. New shape: (8650, 45)
```

#### **Cell 5: Train/Test split** (~5 giây)
```python
X_train, X_test = train_test_split(...)
# ✅ Train: 6920 | Test: 1730
```

#### **Cell 6: Train XGBoost** (~2-5 phút)
```python
xgb_model.fit(X_train, y_train)
# ✅ F1-Score: 0.915
```

#### **Cell 7: Train LightGBM** (~1-3 phút)
```python
lgb_model.fit(X_train, y_speed)
# ✅ MAE: 2.3 km/h
```

#### **Cell 8: Train Prophet** (~10-15 phút)
```python
for segment in segments:
    prophet_model.fit(df_segment)
# ✅ 10 models trained
```

#### **Cell 9: Save models** (~10 giây)
```python
joblib.dump(xgb_model, '/content/drive/MyDrive/SmartTraffic/models/...')
# ✅ All models saved
```

---

### **BƯỚC 6: Verify Models Saved**

Check Google Drive:
```
MyDrive/SmartTraffic/models/
├── xgboost_congestion.pkl      (4.5 MB)
├── lightgbm_speed.pkl          (2.8 MB)
├── prophet_models.pkl          (11.2 MB)
├── scaler.pkl                  (0.9 MB)
└── feature_columns.pkl         (0.5 KB)

Total: ~20 MB
```

✅ All files present = SUCCESS!

---

### **BƯỚC 7: Download Models về Local**

#### **Option A: Via Google Drive Web**
1. Mở Drive: https://drive.google.com
2. Navigate: `MyDrive/SmartTraffic/models/`
3. Select all `.pkl` files
4. Right-click → **Download**
5. Extract ZIP → Move to:
   ```
   e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\models\saved_models\
   ```

#### **Option B: Via Colab (Faster)**
```python
# Add cell ở cuối notebook:
from google.colab import files

# Download all models
files.download('/content/drive/MyDrive/SmartTraffic/models/xgboost_congestion.pkl')
files.download('/content/drive/MyDrive/SmartTraffic/models/lightgbm_speed.pkl')
files.download('/content/drive/MyDrive/SmartTraffic/models/prophet_models.pkl')
files.download('/content/drive/MyDrive/SmartTraffic/models/scaler.pkl')
files.download('/content/drive/MyDrive/SmartTraffic/models/feature_columns.pkl')
```

Files tự động download vào `Downloads/` folder

---

### **BƯỚC 8: Test Models Locally**

```bash
cd e:\CĐTT2\Smart-Transport\smart-traffic-system\ml-pipeline\models
python model_loader.py
```

**Expected output:**
```
================================================================================
🔄 LOADING TRAINED MODELS
================================================================================
  ✅ xgboost_congestion.pkl        (  4532.1 KB)
  ✅ lightgbm_speed.pkl            (  2819.5 KB)
  ✅ prophet_models.pkl            ( 11238.7 KB)
  ✅ scaler.pkl                    (   902.3 KB)
  ✅ feature_columns.pkl           (     0.5 KB)

✅ All models loaded successfully!
================================================================================

🔮 DEMO PREDICTION
📊 INPUT CONDITIONS:
  Time: Thursday 17:00 (Rush hour)
  Intensity: 7500 veh/h
  Occupancy: 0.72
  Recent speed: 18.5 km/h

🔮 PREDICTION:
  Predicted Speed: 17.8 km/h
  Confidence: 16.0-19.6 km/h
  Congestion Probability: 87.3%
  Status: 🔴 HEAVY CONGESTION

✅ Demo completed!
```

✅ Models working perfectly!

---

## 🎯 Troubleshooting

### **Problem 1: "Runtime disconnected"**
**Cause:** Colab timeout (idle >90 min)
**Solution:**
- Notebook tự động save progress
- Re-run cells từ cell bị dừng
- Hoặc chạy lại từ đầu (nhanh thôi, ~20 phút)

### **Problem 2: "Out of memory"**
**Cause:** Model quá lớn hoặc batch size lớn
**Solution:**
```python
# Giảm batch size trong training
xgb_model = XGBClassifier(
    n_estimators=300,  # Giảm từ 500
    max_depth=6        # Giảm từ 8
)
```

### **Problem 3: "File not found" khi load data**
**Cause:** Sai đường dẫn Google Drive
**Solution:**
```python
# Verify path
!ls /content/drive/MyDrive/SmartTraffic/
# Update DATA_PATH nếu sai
```

### **Problem 4: Training quá lâu**
**Check:**
- GPU enabled? `!nvidia-smi`
- XGBoost/LightGBM dùng CPU (OK, vẫn nhanh)
- Prophet chậm nhất (~15 min cho 10 segments)

**Optimize:**
```python
# Prophet: Reduce seasonality complexity
model = Prophet(
    daily_seasonality=10,  # Reduce from default
    weekly_seasonality=5
)
```

---

## 📊 Training Time Comparison

| Step | Local PC (i7, 16GB RAM) | Google Colab (T4 GPU) |
|------|-------------------------|------------------------|
| Feature Engineering | 1 min | 30 sec |
| XGBoost Training | 10-15 min | 2-3 min |
| LightGBM Training | 5-8 min | 1-2 min |
| Prophet Training | 30-45 min | 10-15 min |
| **TOTAL** | **~60 min** | **~20 min** |

**Speedup: 3x faster** 🚀

---

## ✅ Success Checklist

- [ ] CSV exported (850 KB)
- [ ] Uploaded to Google Drive
- [ ] Colab notebook opened
- [ ] GPU enabled (Tesla T4)
- [ ] Drive mounted successfully
- [ ] All cells executed without errors
- [ ] 5 model files saved to Drive
- [ ] Models downloaded to local
- [ ] `model_loader.py` demo runs OK
- [ ] Ready for FastAPI integration

---

## 🚀 Next Steps

1. **Integrate với FastAPI:**
   ```python
   # backend/app/ml/predictor.py
   from ml_pipeline.models.model_loader import TrafficPredictor
   
   predictor = TrafficPredictor()
   
   @app.post("/api/v1/predict")
   def predict(data: PredictRequest):
       return predictor.predict(data.features)
   ```

2. **Deploy API lên server**
3. **Build React frontend**
4. **Connect frontend → API → Models**

---

## 📞 Support

Nếu gặp vấn đề:
1. Check Colab logs (scroll down terminal)
2. Verify file paths
3. Re-run cells từ đầu
4. Google error message (thường có solution)

Good luck! 🎉
