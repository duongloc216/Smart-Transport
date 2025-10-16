# 🚀 Simple Training Script (Alternative to Notebook)

"""
Nếu Google Colab notebook không upload được, dùng script này.
Copy toàn bộ code này vào 1 cell mới trên Colab và chạy.
"""

# ============================================================================
# STEP 1: INSTALL & IMPORT
# ============================================================================
print("Step 1: Installing packages...")
!pip install -q xgboost lightgbm prophet scikit-learn pandas numpy matplotlib seaborn plotly joblib

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

print("✅ Packages installed")

# ============================================================================
# STEP 2: MOUNT DRIVE & LOAD DATA
# ============================================================================
print("\nStep 2: Mounting Google Drive...")
from google.colab import drive
drive.mount('/content/drive')

DATA_PATH = '/content/drive/MyDrive/SmartTraffic/data/traffic_data_for_training.csv'
MODEL_OUTPUT_PATH = '/content/drive/MyDrive/SmartTraffic/models/'

print("Loading data...")
df = pd.read_csv(DATA_PATH, parse_dates=['DateObservedFrom', 'DateObservedTo'])
print(f"✅ Loaded {len(df)} records")

# ============================================================================
# STEP 3: FEATURE ENGINEERING
# ============================================================================
print("\nStep 3: Feature engineering...")

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

# ============================================================================
# STEP 4: PREPARE DATA
# ============================================================================
print("\nStep 4: Preparing train/test split...")

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

# ============================================================================
# STEP 5A: TRAIN XGBOOST
# ============================================================================
print("\n" + "="*80)
print("Step 5A: Training XGBoost...")
print("="*80)

start = time.time()
scale_pos_weight = (y_cong_train == 0).sum() / (y_cong_train == 1).sum()

xgb_model = xgb.XGBClassifier(
    n_estimators=500, max_depth=8, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8, scale_pos_weight=scale_pos_weight,
    random_state=42, n_jobs=-1, tree_method='hist'
)

xgb_model.fit(X_train_scaled, y_cong_train)
y_pred = xgb_model.predict(X_test_scaled)

print(f"⏱️  Training time: {time.time() - start:.1f}s")
print(f"\n{classification_report(y_cong_test, y_pred)}")

# ============================================================================
# STEP 5B: TRAIN LIGHTGBM
# ============================================================================
print("\n" + "="*80)
print("Step 5B: Training LightGBM...")
print("="*80)

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

print(f"⏱️  Training time: {time.time() - start:.1f}s")
print(f"MAE: {mae:.2f} km/h | RMSE: {rmse:.2f} km/h | R²: {r2:.4f}")

# ============================================================================
# STEP 5C: TRAIN PROPHET
# ============================================================================
print("\n" + "="*80)
print("Step 5C: Training Prophet (10 segments)...")
print("="*80)

prophet_models = {}
segments = df_featured['RefRoadSegment'].unique()
start = time.time()

for i, segment in enumerate(segments, 1):
    print(f"[{i}/10] Training {segment}...", end=" ")
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

print(f"⏱️  Total time: {time.time() - start:.1f}s")

# ============================================================================
# STEP 6: SAVE MODELS
# ============================================================================
print("\n" + "="*80)
print("Step 6: Saving models to Google Drive...")
print("="*80)

os.makedirs(MODEL_OUTPUT_PATH, exist_ok=True)

joblib.dump(xgb_model, os.path.join(MODEL_OUTPUT_PATH, 'xgboost_congestion.pkl'))
print("✅ XGBoost saved")

joblib.dump(lgb_model, os.path.join(MODEL_OUTPUT_PATH, 'lightgbm_speed.pkl'))
print("✅ LightGBM saved")

joblib.dump(prophet_models, os.path.join(MODEL_OUTPUT_PATH, 'prophet_models.pkl'))
print("✅ Prophet saved")

joblib.dump(scaler, os.path.join(MODEL_OUTPUT_PATH, 'scaler.pkl'))
print("✅ Scaler saved")

joblib.dump(feature_cols, os.path.join(MODEL_OUTPUT_PATH, 'feature_columns.pkl'))
print("✅ Features saved")

# ============================================================================
# STEP 7: SUMMARY
# ============================================================================
print("\n" + "="*80)
print("🎉 TRAINING COMPLETED!")
print("="*80)
print(f"\nXGBoost F1-Score: {f1_score(y_cong_test, y_pred):.3f}")
print(f"LightGBM MAE: {mae:.2f} km/h")
print(f"Prophet: {len(prophet_models)} models trained")
print(f"\n📁 Models saved to: {MODEL_OUTPUT_PATH}")
print("\nNext: Download models from Google Drive to local machine")
print("Location: MyDrive/SmartTraffic/models/")
