"""
Traffic Prediction ML Service
Wrapper service for ML models integration with FastAPI
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta

# Add ml-pipeline to Python path
BACKEND_PATH = Path(__file__).parent.parent.parent
ML_PIPELINE_PATH = BACKEND_PATH.parent / "ml-pipeline"

# Add both paths
if str(ML_PIPELINE_PATH) not in sys.path:
    sys.path.insert(0, str(ML_PIPELINE_PATH))
if str(ML_PIPELINE_PATH / "models") not in sys.path:
    sys.path.insert(0, str(ML_PIPELINE_PATH / "models"))

# Try to import TrafficPredictor
try:
    from model_loader import TrafficPredictor
    ML_AVAILABLE = True
except ImportError:
    try:
        from ml_pipeline.models.model_loader import TrafficPredictor
        ML_AVAILABLE = True
    except ImportError:
        print("⚠️  TrafficPredictor not found. ML predictions will use dummy data.")
        TrafficPredictor = None
        ML_AVAILABLE = False


class TrafficPredictionService:
    """
    Service to handle traffic predictions using trained ML models
    """
    
    _instance = None
    _predictor = None
    
    def __new__(cls):
        """Singleton pattern to load models only once"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._predictor = None
        return cls._instance
    
    def __init__(self):
        """Initialize the ML predictor"""
        if self._predictor is None:
            self._load_models()
    
    def _load_models(self):
        """Load trained ML models"""
        if not ML_AVAILABLE or TrafficPredictor is None:
            print("⚠️  TrafficPredictor class not available")
            self._predictor = None
            return
            
        try:
            models_dir = ML_PIPELINE_PATH / "models" / "saved_models"
            
            if not models_dir.exists():
                raise FileNotFoundError(
                    f"Models directory not found: {models_dir}\n"
                    "Please train models first using Google Colab and download them."
                )
            
            print("🔄 Loading ML models...")
            self._predictor = TrafficPredictor(models_dir=str(models_dir))
            print("✅ ML models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            print("⚠️ API will run with dummy predictions until models are loaded.")
            self._predictor = None
    
    def is_ready(self) -> bool:
        """Check if models are loaded and ready"""
        return self._predictor is not None
    
    def predict(
        self,
        features: Dict,
        model_type: str = "ensemble"
    ) -> Dict:
        """
        Make traffic prediction using ML models
        
        Args:
            features: Dictionary of engineered features
            model_type: Type of model to use (ensemble, xgboost, lightgbm)
            
        Returns:
            Prediction results with speed, congestion, confidence
        """
        if not self.is_ready():
            return self._dummy_prediction(features)
        
        try:
            # Use ensemble prediction (XGBoost + LightGBM + Prophet)
            result = self._predictor.predict(features)
            
            return {
                'predicted_speed': result['predicted_speed'],
                'congestion_probability': result['congestion_probability'],
                'congestion_status': self._get_status_text(result['status']),
                'confidence_lower': result['confidence_interval'][0],
                'confidence_upper': result['confidence_interval'][1],
                'model_contributions': result.get('model_contributions', {}),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._dummy_prediction(features)
    
    def predict_future(
        self,
        segment_id: str,
        features: Dict,
        horizon_minutes: int = 60
    ) -> List[Dict]:
        """
        Predict traffic for future time horizons using Prophet
        
        Args:
            segment_id: Road segment ID
            features: Current features
            horizon_minutes: How far to predict (minutes)
            
        Returns:
            List of predictions for future timestamps
        """
        if not self.is_ready():
            return [self._dummy_prediction(features) for _ in range(4)]
        
        try:
            # Prophet forecast
            prophet_result = self._predictor.predict_segment_future(
                segment_id=segment_id,
                current_features=features,
                horizon_hours=horizon_minutes / 60
            )
            
            predictions = []
            base_time = datetime.now()
            
            # Generate predictions for 15-min intervals
            for i, (speed, lower, upper) in enumerate(
                zip(
                    prophet_result['predicted_speeds'],
                    prophet_result['lower_bounds'],
                    prophet_result['upper_bounds']
                )
            ):
                timestamp = base_time + timedelta(minutes=(i+1)*15)
                
                # Estimate congestion from speed
                max_speed = features.get('MaximumAllowedSpeed', 40)
                speed_ratio = speed / max_speed
                
                if speed_ratio > 0.7:
                    congestion_prob = 0.0
                    status = 'FREE_FLOW'
                elif speed_ratio > 0.5:
                    congestion_prob = 0.3
                    status = 'MODERATE'
                else:
                    congestion_prob = 0.8
                    status = 'HEAVY_CONGESTION'
                
                predictions.append({
                    'timestamp': timestamp,
                    'predicted_speed': round(speed, 2),
                    'congestion_probability': congestion_prob,
                    'congestion_status': status,
                    'confidence_lower': round(lower, 2),
                    'confidence_upper': round(upper, 2)
                })
            
            return predictions[:min(4, horizon_minutes // 15)]
            
        except Exception as e:
            print(f"❌ Future prediction error: {e}")
            return [self._dummy_prediction(features) for _ in range(4)]
    
    def _get_status_text(self, status_emoji: str) -> str:
        """Convert emoji status to text"""
        status_map = {
            '🟢 FREE FLOW': 'FREE_FLOW',
            '🟡 MODERATE': 'MODERATE',
            '🔴 HEAVY CONGESTION': 'HEAVY_CONGESTION'
        }
        return status_map.get(status_emoji, 'UNKNOWN')
    
    def _dummy_prediction(self, features: Dict) -> Dict:
        """
        Generate dummy prediction when models not available
        """
        hour = features.get('hour', 12)
        is_rush_hour = features.get('is_rush_hour', 0)
        speed_lag = features.get('speed_lag_1', 25.0)
        
        # Simple rule-based prediction
        if is_rush_hour:
            speed = 15.0
            congestion_prob = 0.9
            status = 'HEAVY_CONGESTION'
        elif hour >= 22 or hour <= 6:
            speed = 35.0
            congestion_prob = 0.1
            status = 'FREE_FLOW'
        else:
            speed = speed_lag
            congestion_prob = 0.3
            status = 'MODERATE'
        
        return {
            'predicted_speed': speed,
            'congestion_probability': congestion_prob,
            'congestion_status': status,
            'confidence_lower': speed - 2.0,
            'confidence_upper': speed + 2.0,
            'timestamp': datetime.now(),
            'warning': 'Using dummy prediction - ML models not loaded'
        }
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        if not self.is_ready():
            return {
                'status': 'not_loaded',
                'models': [],
                'message': 'ML models not loaded. Train and download models first.'
            }
        
        return {
            'status': 'ready',
            'models': [
                {
                    'name': 'XGBoost Classifier',
                    'purpose': 'Congestion classification',
                    'expected_accuracy': '99%'
                },
                {
                    'name': 'LightGBM Regressor',
                    'purpose': 'Speed prediction',
                    'expected_performance': 'MAE: 0.58 km/h, R²: 0.9836'
                },
                {
                    'name': 'Prophet Forecaster',
                    'purpose': 'Time series forecasting',
                    'expected_performance': 'MAPE: 8%'
                }
            ],
            'ensemble_method': 'Weighted average (60% LightGBM + 40% baseline)',
            'training_date': 'October 2025',
            'training_samples': 8650
        }


# Singleton instance
_prediction_service = TrafficPredictionService()


def get_prediction_service() -> TrafficPredictionService:
    """Get the singleton prediction service instance"""
    return _prediction_service
