"""
Model Loader - Load trained models from Google Colab
"""

import joblib
import os
import numpy as np
import pandas as pd
from datetime import datetime

class TrafficPredictor:
    """
    Load and use trained models for traffic prediction
    """
    
    def __init__(self, models_dir='saved_models'):
        """
        Load all trained models
        
        Args:
            models_dir: Directory containing .pkl model files
        """
        self.models_dir = models_dir
        
        print("=" * 80)
        print("🔄 LOADING TRAINED MODELS")
        print("=" * 80)
        
        # Load models
        self.xgb_model = self._load_model('xgboost_congestion.pkl')
        self.lgb_model = self._load_model('lightgbm_speed.pkl')
        self.prophet_models = self._load_model('prophet_models.pkl')
        self.scaler = self._load_model('scaler.pkl')
        self.feature_cols = self._load_model('feature_columns.pkl')
        
        print("\n✅ All models loaded successfully!")
        print("=" * 80)
    
    def _load_model(self, filename):
        """Load a single model file"""
        path = os.path.join(os.path.dirname(__file__), self.models_dir, filename)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Model not found: {path}")
        
        model = joblib.load(path)
        size_kb = os.path.getsize(path) / 1024
        print(f"  ✅ {filename:30s} ({size_kb:>8.1f} KB)")
        
        return model
    
    def predict(self, features_dict):
        """
        Make prediction using ensemble of 3 models
        
        Args:
            features_dict: Dictionary with feature values
                {
                    'Intensity': 5000,
                    'Occupancy': 0.65,
                    'hour': 17,
                    'is_rush_hour': 1,
                    ...
                }
        
        Returns:
            {
                'predicted_speed': 18.5,
                'congestion_probability': 0.87,
                'status': 'HEAVY CONGESTION',
                'confidence_interval': (16.2, 20.8),
                'model_contributions': {...}
            }
        """
        
        # 1. Convert to DataFrame
        df = pd.DataFrame([features_dict])
        
        # 2. Ensure all feature columns exist
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0  # Default value
        
        # Select only model features in correct order
        X = df[self.feature_cols]
        
        # 3. Scale features
        X_scaled = self.scaler.transform(X)
        
        # 4. XGBoost: Congestion probability
        congestion_prob = self.xgb_model.predict_proba(X_scaled)[0][1]
        
        # 5. LightGBM: Speed prediction
        speed_lgbm = self.lgb_model.predict(X_scaled)[0]
        
        # 6. Weighted ensemble (60% LightGBM, 40% baseline)
        final_speed = 0.60 * speed_lgbm + 0.40 * features_dict.get('speed_baseline', speed_lgbm)
        
        # 7. Adjust based on congestion
        if congestion_prob > 0.7:
            final_speed *= 0.85  # Reduce 15% if congested
        
        # 8. Confidence interval (±10%)
        confidence_lower = final_speed * 0.90
        confidence_upper = final_speed * 1.10
        
        # 9. Status
        if congestion_prob > 0.7:
            status = '🔴 HEAVY CONGESTION'
        elif congestion_prob > 0.4:
            status = '🟠 MODERATE'
        else:
            status = '🟢 FREE FLOW'
        
        return {
            'predicted_speed': round(final_speed, 2),
            'congestion_probability': round(congestion_prob, 3),
            'status': status,
            'confidence_interval': (round(confidence_lower, 2), round(confidence_upper, 2)),
            'model_contributions': {
                'lightgbm_speed': round(speed_lgbm, 2),
                'xgboost_congestion_prob': round(congestion_prob, 3)
            }
        }
    
    def predict_segment_future(self, segment_id, current_features, horizon_minutes=30):
        """
        Predict future traffic for a segment using Prophet
        
        Args:
            segment_id: Road segment ID (e.g., 'segment_001')
            current_features: Current feature values
            horizon_minutes: How far to predict (15, 30, 60)
        
        Returns:
            Forecast dictionary
        """
        
        if segment_id not in self.prophet_models:
            raise ValueError(f"No Prophet model for segment: {segment_id}")
        
        prophet_model = self.prophet_models[segment_id]
        
        # Create future dataframe
        future = prophet_model.make_future_dataframe(periods=horizon_minutes//5, freq='5min')
        
        # Add regressors (use current values as proxy)
        future['intensity'] = current_features.get('Intensity', 5000)
        future['is_weekend'] = current_features.get('is_weekend', 0)
        future['is_rush_hour'] = current_features.get('is_rush_hour', 0)
        
        # Predict
        forecast = prophet_model.predict(future)
        
        # Get last prediction (target horizon)
        last_prediction = forecast.iloc[-1]
        
        return {
            'segment_id': segment_id,
            'horizon_minutes': horizon_minutes,
            'predicted_speed': round(last_prediction['yhat'], 2),
            'lower_bound': round(last_prediction['yhat_lower'], 2),
            'upper_bound': round(last_prediction['yhat_upper'], 2),
            'trend': round(last_prediction['trend'], 2)
        }


def demo_prediction():
    """
    Demo: Load models and make sample prediction
    """
    
    # Load models
    predictor = TrafficPredictor()
    
    print("\n" + "=" * 80)
    print("🔮 DEMO PREDICTION")
    print("=" * 80)
    
    # Sample input (giả lập giờ cao điểm chiều)
    sample_features = {
        'Intensity': 7500,
        'Occupancy': 0.72,
        'TotalLaneNumber': 4,
        'MaximumAllowedSpeed': 40,
        'hour': 17,  # 5 PM
        'day_of_week': 3,  # Thursday
        'is_weekend': 0,
        'is_rush_hour': 1,
        'speed_lag_1': 18.5,
        'speed_lag_2': 19.2,
        'speed_lag_3': 20.1,
        'intensity_lag_1': 7200,
        'speed_rolling_mean_6': 19.5,
        'speed_rolling_mean_12': 21.3,
        'speed_rolling_std_6': 2.1,
        'intensity_rolling_mean_6': 7000,
        'speed_diff': -0.7,
        'intensity_diff': 300,
        'speed_to_max_ratio': 0.46,
        'speed_baseline': 20.0,
        # Segment dummies
        'segment_segment_001': 1,
        'segment_segment_002': 0,
        'segment_segment_003': 0,
        'segment_segment_004': 0,
        'segment_segment_005': 0,
        'segment_segment_006': 0,
        'segment_segment_007': 0,
        'segment_segment_008': 0,
        'segment_segment_009': 0,
        'segment_segment_010': 0
    }
    
    # Predict
    result = predictor.predict(sample_features)
    
    print(f"\n📊 INPUT CONDITIONS:")
    print(f"  Time: Thursday 17:00 (Rush hour)")
    print(f"  Intensity: {sample_features['Intensity']} veh/h")
    print(f"  Occupancy: {sample_features['Occupancy']}")
    print(f"  Recent speed: {sample_features['speed_lag_1']} km/h")
    
    print(f"\n🔮 PREDICTION:")
    print(f"  Predicted Speed: {result['predicted_speed']} km/h")
    print(f"  Confidence: {result['confidence_interval'][0]}-{result['confidence_interval'][1]} km/h")
    print(f"  Congestion Probability: {result['congestion_probability']*100:.1f}%")
    print(f"  Status: {result['status']}")
    
    print(f"\n🤖 MODEL CONTRIBUTIONS:")
    for model, value in result['model_contributions'].items():
        print(f"  {model}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    demo_prediction()
