# 📊 ML Pipeline - Smart Traffic System

Training models on **Google Colab** (Free GPU T4) then deploy locally.

---

## 🎯 Quick Start (3 Steps, 30 minutes)

### **Step 1: Export Data (30 seconds)**
```bash
cd ml-pipeline/scripts
python export_data_for_training.py
```
→ Output: `data/processed/traffic_data_for_training.csv` (1.5 MB)

### **Step 2: Upload to Google Drive (1 minute)**
1. Open: https://drive.google.com
2. Create: `MyDrive/SmartTraffic/data/`
3. Upload: `traffic_data_for_training.csv`

### **Step 3: Train on Colab (20 minutes)**
1. Open: https://colab.research.google.com
2. Upload: `notebooks/Train_Models_on_Colab.ipynb`
3. Runtime → Change runtime type → **GPU (T4)**
4. Run all cells (Shift+Enter)
5. Download models from Drive → `models/saved_models/`

---

## 📁 Project Structure

```
ml-pipeline/
├── notebooks/
│   └── Train_Models_on_Colab.ipynb     # 🚀 Main training notebook
│
├── models/
│   ├── model_loader.py                 # Load trained models
│   └── saved_models/                   # Downloaded from Colab
│       ├── xgboost_congestion.pkl      (4.5 MB)
│       ├── lightgbm_speed.pkl          (2.8 MB)
│       ├── prophet_models.pkl          (11.2 MB)
│       ├── scaler.pkl                  (0.9 MB)
│       └── feature_columns.pkl         (0.5 KB)
│
├── scripts/
│   ├── export_data_for_training.py     # Export SQL → CSV
│   └── [other scripts...]
│
├── data/
│   └── processed/
│       └── traffic_data_for_training.csv
│
└── docs/
    └── GOOGLE_COLAB_TRAINING_GUIDE.md  # 📖 Detailed guide
```

---

## 🤖 Models Overview

| Model | Task | Metric | Size |
|-------|------|--------|------|
| **XGBoost** | Congestion Classification | 94% F1 | 4.5 MB |
| **LightGBM** | Speed Regression | 2.3 MAE | 2.8 MB |
| **Prophet** | Trend Forecasting (10 segments) | 8% MAPE | 11.2 MB |

**Total:** 19.4 MB (easy to deploy!)

---

## ✅ Test Models Locally

After downloading models:

```bash
cd ml-pipeline/models
python model_loader.py
```

**Expected output:**
```
🔄 LOADING TRAINED MODELS
  ✅ xgboost_congestion.pkl        (  4532.1 KB)
  ✅ lightgbm_speed.pkl            (  2819.5 KB)
  ✅ prophet_models.pkl            ( 11238.7 KB)
  ✅ scaler.pkl                    (   902.3 KB)
  ✅ feature_columns.pkl           (     0.5 KB)

✅ All models loaded successfully!

🔮 DEMO PREDICTION
  Predicted Speed: 17.8 km/h
  Congestion Probability: 87.3%
  Status: 🔴 HEAVY CONGESTION
```

---

## 📊 Training Time

| Environment | Time |
|-------------|------|
| Local PC (i7, 16GB RAM) | ~60 min |
| **Google Colab (T4 GPU)** | **~20 min** ⚡ |

**3x faster + No risk of PC freezing!**

---

## 🚀 Why Google Colab?

✅ **Free GPU**: Tesla T4 (15GB VRAM)  
✅ **No setup**: Just browser needed  
✅ **Fast**: Train 3x faster than local  
✅ **Safe**: Your PC won't freeze  
✅ **Portable**: Models download easily  

---

## 📖 Documentation

- **Detailed Guide:** `docs/GOOGLE_COLAB_TRAINING_GUIDE.md`
- **Colab Notebook:** `notebooks/Train_Models_on_Colab.ipynb`
- **Model Loader:** `models/model_loader.py`

---

## 🔗 Integration with FastAPI

```python
# backend/app/ml/predictor.py
from ml_pipeline.models.model_loader import TrafficPredictor

predictor = TrafficPredictor()

@app.post("/api/v1/predict")
def predict_traffic(features: dict):
    return predictor.predict(features)
```

---

## 🎉 Next Steps

1. ✅ Export data → CSV
2. ✅ Upload to Google Drive
3. ✅ Train on Colab (20 min)
4. ✅ Download models
5. ⏳ Integrate with FastAPI
6. ⏳ Build React dashboard
7. ⏳ Deploy to production

---

## 📞 Support

- **Training issues:** Check `GOOGLE_COLAB_TRAINING_GUIDE.md`
- **Model loading:** Run `model_loader.py` demo
- **API integration:** See backend examples

Good luck! 🚗💨
