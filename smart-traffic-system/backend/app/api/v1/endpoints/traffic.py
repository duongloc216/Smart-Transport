"""
Traffic Prediction API Endpoints
Handles AI-powered traffic prediction requests with ML models
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.traffic import (
    TrafficPredictionRequest,
    TrafficPredictionResponse,
    TrafficPrediction,
    CurrentTrafficResponse,
    TrafficHistoryResponse,
    HistoricalTrafficData,
    AllTrafficResponse,
    AllTrafficSegment
)
from app.services.traffic_prediction_service import get_prediction_service
from app.services.feature_engineering_service import FeatureEngineeringService

router = APIRouter()


@router.post("/predict", response_model=TrafficPredictionResponse)
async def predict_traffic(
    request: TrafficPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    🔮 Dự đoán giao thông cho đoạn đường cụ thể sử dụng ML models
    
    **Models**: XGBoost + LightGBM + Prophet Ensemble
    
    **Parameters:**
    - **road_segment_id**: ID đoạn đường (e.g., segment_001 to segment_010)
    - **prediction_horizon**: Thời gian dự đoán (15, 30, 60 phút)
    - **model_type**: Loại model (ensemble, xgboost, lightgbm, prophet)
    
    **Returns:**
    - Predicted speed (km/h)
    - Congestion probability (0-1)
    - Congestion status (FREE_FLOW, MODERATE, HEAVY_CONGESTION)
    - Confidence intervals
    
    **Example:**
    ```json
    {
        "road_segment_id": "segment_001",
        "prediction_horizon": 15,
        "model_type": "ensemble"
    }
    ```
    """
    try:
        # Initialize services
        ml_service = get_prediction_service()
        feature_service = FeatureEngineeringService(db)
        
        # Engineer features
        features = feature_service.engineer_features(
            segment_id=request.road_segment_id,
            target_datetime=datetime.now()
        )
        
        if not features:
            raise HTTPException(
                status_code=404,
                detail=f"Road segment '{request.road_segment_id}' not found"
            )
        
        # Make predictions
        if request.prediction_horizon and request.prediction_horizon > 15:
            # Use Prophet for future predictions
            predictions = ml_service.predict_future(
                segment_id=request.road_segment_id,
                features=features,
                horizon_minutes=request.prediction_horizon
            )
        else:
            # Single prediction for current/next 15 minutes
            result = ml_service.predict(features, model_type=request.ml_model_type or "ensemble")
            predictions = [{
                'timestamp': result['timestamp'],
                'predicted_speed': result['predicted_speed'],
                'congestion_probability': result['congestion_probability'],
                'congestion_status': result['congestion_status'],
                'confidence_lower': result['confidence_lower'],
                'confidence_upper': result['confidence_upper']
            }]
        
        # Format response
        prediction_objects = [
            TrafficPrediction(
                timestamp=p['timestamp'],
                predicted_speed=p['predicted_speed'],
                predicted_intensity=features.get('Intensity'),
                predicted_occupancy=features.get('Occupancy'),
                congestion_probability=p['congestion_probability'],
                congestion_status=p['congestion_status'],
                confidence_lower=p['confidence_lower'],
                confidence_upper=p['confidence_upper']
            )
            for p in predictions
        ]
        
        return TrafficPredictionResponse(
            success=True,
            road_segment_id=request.road_segment_id,
            predictions=prediction_objects,
            ml_model_used=request.ml_model_type or "ensemble",
            generated_at=datetime.now(),
            metadata={
                'features_used': len(features),
                'ml_models_loaded': ml_service.is_ready()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@router.get("/current/{road_segment_id}", response_model=CurrentTrafficResponse)
async def get_current_traffic(
    road_segment_id: str,
    db: Session = Depends(get_db)
):
    """
    📊 Lấy dữ liệu giao thông hiện tại cho đoạn đường (với ML prediction)
    
    **Parameters:**
    - **road_segment_id**: ID đoạn đường (e.g., segment_001)
    
    **Returns:**
    - Current traffic conditions from database
    - ML-powered congestion probability
    - Real-time status
    
    **Example:**
    ```
    GET /api/v1/traffic/current/segment_001
    ```
    """
    try:
        feature_service = FeatureEngineeringService(db)
        ml_service = get_prediction_service()
        
        # Get current status from database
        current = feature_service.get_current_traffic_status(road_segment_id)
        
        if not current:
            raise HTTPException(
                status_code=404,
                detail=f"No traffic data found for segment '{road_segment_id}'"
            )
        
        # Get ML prediction for current status
        congestion_prob = None
        congestion_status = "UNKNOWN"
        
        if ml_service.is_ready():
            try:
                features = feature_service.engineer_features(road_segment_id)
                if features:
                    result = ml_service.predict(features)
                    congestion_prob = result['congestion_probability']
                    congestion_status = result['congestion_status']
            except Exception as e:
                print(f"⚠️ ML prediction failed: {e}")
        
        # Fallback to rule-based status
        if congestion_status == "UNKNOWN":
            if current['congested']:
                congestion_status = "HEAVY_CONGESTION"
                congestion_prob = 0.8
            else:
                congestion_status = "FREE_FLOW"
                congestion_prob = 0.2
        
        return CurrentTrafficResponse(
            success=True,
            road_segment_id=road_segment_id,
            timestamp=current.get('timestamp') or datetime.now(),
            speed=current['speed'],
            intensity=current['intensity'],
            occupancy=current['occupancy'],
            congestion_status=congestion_status,
            congestion_probability=congestion_prob,
            road_name=current.get('road_name'),
            road_class=current.get('road_class')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching current traffic: {str(e)}"
        )


@router.get("/history/{road_segment_id}", response_model=TrafficHistoryResponse)
async def get_traffic_history(
    road_segment_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    limit: int = Query(288, le=1000, description="Max records (default: 288 = 1 day)"),
    db: Session = Depends(get_db)
):
    """
    📈 Lấy lịch sử giao thông của đoạn đường
    
    **Parameters:**
    - **road_segment_id**: ID đoạn đường
    - **start_date**: Ngày bắt đầu (optional, default: 24h ago)
    - **end_date**: Ngày kết thúc (optional, default: now)
    - **limit**: Số lượng records tối đa (default: 288 = 1 ngày với 5-min intervals)
    
    **Returns:**
    - Historical traffic data with timestamps
    
    **Example:**
    ```
    GET /api/v1/traffic/history/segment_001?start_date=2025-10-15T00:00:00
    ```
    """
    try:
        from sqlalchemy import text
        
        # Query historical data
        # Use dateObservedTo / dateObservedFrom when available. If both are NULL
        # fall back to DateObserved. We use COALESCE to filter by the most
        # appropriate timestamp and to order results.
        
        # If user provides date range, use it; otherwise get latest records regardless of date
        if start_date and end_date:
            query_str = f"""
                SELECT TOP {limit}
                    DateObserved,
                    dateObservedFrom,
                    dateObservedTo,
                    AverageVehicleSpeed,
                    Intensity,
                    Occupancy,
                    Congested
                FROM TrafficFlowObserved
                WHERE RefRoadSegment = :segment_id
                  AND COALESCE(dateObservedTo, dateObservedFrom, DateObserved) BETWEEN :start_date AND :end_date
                ORDER BY COALESCE(dateObservedTo, dateObservedFrom, DateObserved) DESC
            """
            result = db.execute(
                text(query_str),
                {
                    'segment_id': road_segment_id,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
        else:
            # No date filter - get latest records
            query_str = f"""
                SELECT TOP {limit}
                    DateObserved,
                    dateObservedFrom,
                    dateObservedTo,
                    AverageVehicleSpeed,
                    Intensity,
                    Occupancy,
                    Congested
                FROM TrafficFlowObserved
                WHERE RefRoadSegment = :segment_id
                ORDER BY COALESCE(dateObservedTo, dateObservedFrom, DateObserved, ID) DESC
            """
            result = db.execute(
                text(query_str),
                {
                    'segment_id': road_segment_id
                }
            )
            # Set dates for response
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)  # Show we got last 30 days of data

        records = result.fetchall()

        if not records:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for segment '{road_segment_id}'"
            )

        # Format data: choose timestamp in order of preference:
        # dateObservedTo -> dateObservedFrom -> DateObserved
        historical_data = []
        for row in records:
            # SQLAlchemy row may use keys in original case, normalize with getattr
            dt_to = getattr(row, 'dateObservedTo', None) or getattr(row, 'dateobservedto', None)
            dt_from = getattr(row, 'dateObservedFrom', None) or getattr(row, 'dateobservedfrom', None)
            dt_obs = getattr(row, 'DateObserved', None) or getattr(row, 'dateobserved', None)

            timestamp = dt_to or dt_from or dt_obs or datetime.now()

            historical_data.append(
                HistoricalTrafficData(
                    timestamp=timestamp,
                    speed=float(row.AverageVehicleSpeed) if row.AverageVehicleSpeed is not None else 0.0,
                    intensity=float(row.Intensity) if row.Intensity is not None else 0.0,
                    occupancy=float(row.Occupancy) if row.Occupancy is not None else 0.0,
                    congested=bool(row.Congested)
                )
            )
        
        return TrafficHistoryResponse(
            success=True,
            road_segment_id=road_segment_id,
            data=historical_data,
            start_date=start_date,
            end_date=end_date,
            total_records=len(historical_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )


@router.get("/realtime/all", response_model=AllTrafficResponse)
async def get_all_realtime_traffic(
    limit: int = Query(100, le=1000, description="Max segments to return"),
    db: Session = Depends(get_db)
):
    """
    🗺️ Lấy dữ liệu giao thông real-time của tất cả đoạn đường (với ML predictions)
    
    **Parameters:**
    - **limit**: Số lượng segments tối đa (default: 100)
    
    **Returns:**
    - List of all segments with current traffic + ML predictions
    - Suitable for map visualization
    
    **Example:**
    ```
    GET /api/v1/traffic/realtime/all?limit=10
    ```
    
    **Use case:** Display all traffic on map with color-coded congestion
    """
    try:
        feature_service = FeatureEngineeringService(db)
        ml_service = get_prediction_service()
        
        # Get all segments current status
        segments = feature_service.get_all_segments_current_status()
        
        if not segments:
            return AllTrafficResponse(
                success=True,
                count=0,
                data=[],
                timestamp=datetime.now()
            )
        
        # Add ML predictions to each segment
        all_traffic = []
        for segment in segments[:limit]:
            congestion_prob = 0.5
            congestion_status = "MODERATE"
            
            # Try to get ML prediction
            if ml_service.is_ready():
                try:
                    features = feature_service.engineer_features(segment['segment_id'])
                    if features:
                        result = ml_service.predict(features)
                        congestion_prob = result['congestion_probability']
                        congestion_status = result['congestion_status']
                except Exception as e:
                    print(f"⚠️ Prediction failed for {segment['segment_id']}: {e}")
            
            # Fallback to rule-based
            if congestion_status == "MODERATE" and segment.get('congested'):
                congestion_status = "HEAVY_CONGESTION"
                congestion_prob = 0.8
            elif congestion_status == "MODERATE" and not segment.get('congested'):
                congestion_status = "FREE_FLOW"
                congestion_prob = 0.2
            
            all_traffic.append(
                AllTrafficSegment(
                    road_segment_id=segment['segment_id'],
                    road_name=segment['road_name'],
                    speed=segment['speed'],
                    intensity=segment['intensity'],
                    occupancy=segment['occupancy'],
                    congestion_status=congestion_status,
                    congestion_probability=congestion_prob,
                    timestamp=segment['timestamp']
                )
            )
        
        return AllTrafficResponse(
            success=True,
            count=len(all_traffic),
            data=all_traffic,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching all traffic: {str(e)}"
        )


@router.get("/models/info")
async def get_models_info():
    """
    🤖 Lấy thông tin về ML models đang được sử dụng
    
    **Returns:**
    - Model status (loaded/not loaded)
    - Model details (XGBoost, LightGBM, Prophet)
    - Training information
    - Performance metrics
    
    **Example:**
    ```
    GET /api/v1/traffic/models/info
    ```
    """
    try:
        ml_service = get_prediction_service()
        model_info = ml_service.get_model_info()
        
        return {
            "success": True,
            "timestamp": datetime.now(),
            **model_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching model info: {str(e)}"
        )
