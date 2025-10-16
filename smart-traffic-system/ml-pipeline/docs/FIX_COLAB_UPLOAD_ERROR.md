# ⚠️ Hướng dẫn Fix Lỗi Upload Notebook lên Google Colab

## 🔴 Lỗi gặp phải:
```
Error: Unable to read file.
    at sa.program_ (external_binary_l10n__vi.js:4084:202)
```

---

## ✅ Giải pháp: 3 cách thay thế

### **CÁCH 1: Tạo notebook mới trực tiếp trên Colab (RECOMMENDED)**

1. Mở: https://colab.research.google.com
2. Click **File → New notebook**
3. Copy từng cell code từ file này:
   ```
   e:\CĐTT2\Smart-Transport\...\scripts\train_on_colab_simple.py
   ```
4. Paste vào Colab (tạo cells mới bằng `+ Code`)
5. Run all cells

**Lưu ý:**
- Bỏ dòng đầu tiên: `# 🚀 Simple Training Script...`
- Mỗi section là 1 cell riêng
- Copy từ `!pip install...` trở đi

---

### **CÁCH 2: Upload notebook mới đã fixed**

File mới: `Train_Models_Colab.ipynb` (đã tạo)

**Thử upload lại:**
1. Mở: https://colab.research.google.com
2. Click **File → Upload notebook**
3. Browse → chọn:
   ```
   e:\CĐTT2\Smart-Transport\...\notebooks\Train_Models_Colab.ipynb
   ```
4. Nếu vẫn lỗi → dùng Cách 3

---

### **CÁCH 3: Copy-paste trực tiếp (FASTEST - 2 phút)**

#### **Step 1: Tạo notebook mới**
1. Mở: https://colab.research.google.com
2. **File → New notebook**
3. Đặt tên: "Smart Traffic Training"

#### **Step 2: Enable GPU**
1. **Runtime → Change runtime type**
2. Hardware accelerator: **GPU**
3. Click **Save**

#### **Step 3: Copy code sections**

**Cell 1 - Install:**
```python
!pip install -q xgboost lightgbm prophet scikit-learn pandas numpy matplotlib seaborn plotly joblib
```

**Cell 2 - Import:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, f1_score, classification_report
import xgboost as xgb
import lightgbm as lgb
from prophet import Prophet
import joblib
import time
import os

print("✅ Libraries imported")
```

**Cell 3 - Mount Drive:**
```python
from google.colab import drive
drive.mount('/content/drive')

DATA_PATH = '/content/drive/MyDrive/SmartTraffic/data/traffic_data_for_training.csv'
MODEL_OUTPUT_PATH = '/content/drive/MyDrive/SmartTraffic/models/'

print("✅ Drive mounted")
```

**Cell 4 - Load data:**
```python
print("Loading data...")
df = pd.read_csv(DATA_PATH, parse_dates=['DateObservedFrom', 'DateObservedTo'])
print(f"✅ Loaded {len(df)} records")
print(f"Shape: {df.shape}")
df.head()
```

**Cell 5 - Feature engineering:**
```python
def create_features(df):
    df = df.copy()
    df['hour'] = df['DateObservedFrom'].dt.hour
    df['day_of_week'] = df['DateObservedFrom'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9) | (df['hour'] >= 17) & (df['hour'] <= 19)).astype(int)
    
    df = df.sort_values(['RefRoadSegment', 'DateObservedFrom']).reset_index(drop=True)
    
    df['speed_lag_1'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].shift(1)
    df['speed_lag_2'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].shift(2)
    df['speed_lag_3'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].shift(3)
    df['intensity_lag_1'] = df.groupby('RefRoadSegment')['Intensity'].shift(1)
    
    df['speed_rolling_mean_6'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].rolling(6, min_periods=1).mean().reset_index(0, drop=True)
    df['speed_rolling_mean_12'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].rolling(12, min_periods=1).mean().reset_index(0, drop=True)
    df['speed_rolling_std_6'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].rolling(6, min_periods=1).std().reset_index(0, drop=True)
    df['intensity_rolling_mean_6'] = df.groupby('RefRoadSegment')['Intensity'].rolling(6, min_periods=1).mean().reset_index(0, drop=True)
    
    df['speed_diff'] = df.groupby('RefRoadSegment')['AverageVehicleSpeed'].diff()
    df['intensity_diff'] = df.groupby('RefRoadSegment')['Intensity'].diff()
    df['speed_to_max_ratio'] = df['AverageVehicleSpeed'] / df['MaximumAllowedSpeed']
    
    segment_dummies = pd.get_dummies(df['RefRoadSegment'], prefix='segment')
    df = pd.concat([df, segment_dummies], axis=1)
    df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
    
    return df

df_featured = create_features(df)
print(f"✅ Features created. Shape: {df_featured.shape}")
```

**Cell 6 - Prepare data:**
```python
feature_cols = [
    'Intensity', 'Occupancy', 'TotalLaneNumber', 'MaximumAllowedSpeed',
    'hour', 'day_of_week', 'is_weekend', 'is_rush_hour',
    'speed_lag_1', 'speed_lag_2', 'speed_lag_3', 'intensity_lag_1',
    'speed_rolling_mean_6', 'speed_rolling_mean_12', 'speed_rolling_std_6',
    'intensity_rolling_mean_6', 'speed_diff', 'intensity_diff', 'speed_to_max_ratio'
] + [col for col in df_featured.columns if col.startswith('segment_')]

X = df_featured[feature_cols]
y_speed = df_featured['AverageVehicleSpeed']
y_congestion = df_featured['Congested'].astype(int)

X_train, X_test, y_speed_train, y_speed_test, y_cong_train, y_cong_test = train_test_split(
    X, y_speed, y_congestion, test_size=0.2, random_state=42, shuffle=False
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✅ Train: {len(X_train)} | Test: {len(X_test)} | Features: {len(feature_cols)}")
```

**Cell 7 - Train XGBoost:**
```python
print("Training XGBoost...")
start = time.time()

scale_pos_weight = (y_cong_train == 0).sum() / (y_cong_train == 1).sum()

xgb_model = xgb.XGBClassifier(
    n_estimators=500, max_depth=8, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, scale_pos_weight=scale_pos_weight,
    random_state=42, n_jobs=-1, tree_method='hist'
)

xgb_model.fit(X_train_scaled, y_cong_train)
y_pred = xgb_model.predict(X_test_scaled)

print(f"⏱️  Time: {time.time() - start:.1f}s")
print(f"\n{classification_report(y_cong_test, y_pred)}")
```

**Cell 8 - Train LightGBM:**
```python
print("Training LightGBM...")
start = time.time()

lgb_model = lgb.LGBMRegressor(
    n_estimators=500, max_depth=8, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    random_state=42, n_jobs=-1, verbose=-1
)

lgb_model.fit(X_train_scaled, y_speed_train)
y_speed_pred = lgb_model.predict(X_test_scaled)

mae = mean_absolute_error(y_speed_test, y_speed_pred)
rmse = np.sqrt(mean_squared_error(y_speed_test, y_speed_pred))
r2 = r2_score(y_speed_test, y_speed_pred)

print(f"⏱️  Time: {time.time() - start:.1f}s")
print(f"MAE: {mae:.2f} km/h | RMSE: {rmse:.2f} km/h | R²: {r2:.4f}")
```

**Cell 9 - Train Prophet:**
```python
print("Training Prophet (10 segments)...")
prophet_models = {}
segments = df_featured['RefRoadSegment'].unique()
start = time.time()

for i, segment in enumerate(segments, 1):
    print(f"[{i}/10] {segment}...", end=" ")
    df_seg = df_featured[df_featured['RefRoadSegment'] == segment].copy()
    
    df_prophet = pd.DataFrame({
        'ds': df_seg['DateObservedFrom'],
        'y': df_seg['AverageVehicleSpeed'],
        'intensity': df_seg['Intensity'],
        'is_weekend': df_seg['is_weekend'],
        'is_rush_hour': df_seg['is_rush_hour']
    })
    
    model = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
    model.add_regressor('intensity')
    model.add_regressor('is_weekend')
    model.add_regressor('is_rush_hour')
    model.fit(df_prophet)
    
    prophet_models[segment] = model
    print("✅")

print(f"⏱️  Total: {time.time() - start:.1f}s")
```

**Cell 10 - Save models:**
```python
print("Saving models to Google Drive...")
os.makedirs(MODEL_OUTPUT_PATH, exist_ok=True)

joblib.dump(xgb_model, os.path.join(MODEL_OUTPUT_PATH, 'xgboost_congestion.pkl'))
joblib.dump(lgb_model, os.path.join(MODEL_OUTPUT_PATH, 'lightgbm_speed.pkl'))
joblib.dump(prophet_models, os.path.join(MODEL_OUTPUT_PATH, 'prophet_models.pkl'))
joblib.dump(scaler, os.path.join(MODEL_OUTPUT_PATH, 'scaler.pkl'))
joblib.dump(feature_cols, os.path.join(MODEL_OUTPUT_PATH, 'feature_columns.pkl'))

print("✅ All models saved!")
print(f"Location: {MODEL_OUTPUT_PATH}")
```

---

## ⏱️ Timeline

- Cell 1-2 (Install + Import): ~2 min
- Cell 3-4 (Mount + Load): ~10 sec
- Cell 5-6 (Features + Prepare): ~30 sec
- Cell 7 (XGBoost): ~2-3 min
- Cell 8 (LightGBM): ~1-2 min
- Cell 9 (Prophet): ~10-15 min
- Cell 10 (Save): ~10 sec

**Total: ~18-25 phút**

---

## ✅ Checklist

- [ ] CSV uploaded to `MyDrive/SmartTraffic/data/`
- [ ] Colab notebook created
- [ ] GPU enabled (Runtime → Change runtime type)
- [ ] Drive mounted (allow permissions)
- [ ] All 10 cells executed successfully
- [ ] Models saved to `MyDrive/SmartTraffic/models/`
- [ ] Download 5 .pkl files to local

---

## 🎉 Sau khi hoàn thành

Download 5 files từ Google Drive:
```
MyDrive/SmartTraffic/models/
├── xgboost_congestion.pkl
├── lightgbm_speed.pkl
├── prophet_models.pkl
├── scaler.pkl
└── feature_columns.pkl
```

Copy vào local:
```
e:\CĐTT2\Smart-Transport\...\models\saved_models\
```

Test:
```bash
cd ml-pipeline/models
python model_loader.py
```

Good luck! 🚀
