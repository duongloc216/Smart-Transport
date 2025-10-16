"""
Traffic Prediction Schemas
Request/Response models for traffic prediction API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TrafficPredictionRequest(BaseModel):
    """Request schema for traffic prediction"""
    road_segment_id: str = Field(..., description="Road segment ID (e.g., segment_001)")
    prediction_horizon: Optional[int] = Field(15, description="Prediction horizon in minutes (15, 30, 60)")
    ml_model_type: Optional[str] = Field("ensemble", description="Model type: ensemble, xgboost, lightgbm, prophet", alias="model_type")
    
    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "road_segment_id": "segment_001",
                "prediction_horizon": 15,
                "model_type": "ensemble"
            }
        }
    }


class TrafficPrediction(BaseModel):
    """Single traffic prediction"""
    timestamp: datetime
    predicted_speed: float = Field(..., description="Predicted speed in km/h")
    predicted_intensity: Optional[float] = Field(None, description="Predicted intensity in veh/h")
    predicted_occupancy: Optional[float] = Field(None, description="Predicted occupancy ratio")
    congestion_probability: float = Field(..., description="Congestion probability (0-1)")
    congestion_status: str = Field(..., description="Status: FREE_FLOW, MODERATE, HEAVY_CONGESTION")
    confidence_lower: float = Field(..., description="Lower bound of confidence interval")
    confidence_upper: float = Field(..., description="Upper bound of confidence interval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-10-16T17:30:00",
                "predicted_speed": 15.25,
                "predicted_intensity": 8500.0,
                "predicted_occupancy": 0.78,
                "congestion_probability": 1.0,
                "congestion_status": "HEAVY_CONGESTION",
                "confidence_lower": 13.72,
                "confidence_upper": 16.77
            }
        }


class TrafficPredictionResponse(BaseModel):
    """Response schema for traffic prediction"""
    success: bool = True
    road_segment_id: str
    predictions: List[TrafficPrediction]
    ml_model_used: str = Field(..., alias="model_used")
    generated_at: datetime
    metadata: Optional[dict] = None
    
    model_config = {
        "protected_namespaces": (),
        "json_schema_extra": {
            "example": {
                "success": True,
                "road_segment_id": "segment_001",
                "predictions": [
                    {
                        "timestamp": "2025-10-16T17:30:00",
                        "predicted_speed": 15.25,
                        "congestion_probability": 1.0,
                        "congestion_status": "HEAVY_CONGESTION",
                        "confidence_lower": 13.72,
                        "confidence_upper": 16.77
                    }
                ],
                "model_used": "ensemble",
                "generated_at": "2025-10-16T17:15:00"
            }
        }
    }


class CurrentTrafficResponse(BaseModel):
    """Response schema for current traffic status"""
    success: bool = True
    road_segment_id: str
    timestamp: datetime
    speed: float = Field(..., description="Current speed in km/h")
    intensity: float = Field(..., description="Current intensity in veh/h")
    occupancy: float = Field(..., description="Current occupancy ratio")
    congestion_status: str = Field(..., description="Status: FREE_FLOW, MODERATE, HEAVY_CONGESTION")
    congestion_probability: Optional[float] = Field(None, description="Congestion probability from ML")
    road_name: Optional[str] = None
    road_class: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "road_segment_id": "segment_001",
                "timestamp": "2025-10-16T17:30:00",
                "speed": 15.25,
                "intensity": 8500.0,
                "occupancy": 0.78,
                "congestion_status": "HEAVY_CONGESTION",
                "congestion_probability": 1.0,
                "road_name": "Võ Văn Kiệt",
                "road_class": "Primary"
            }
        }


class HistoricalTrafficData(BaseModel):
    """Historical traffic data point"""
    timestamp: datetime
    speed: float
    intensity: float
    occupancy: float
    congested: bool


class TrafficHistoryResponse(BaseModel):
    """Response schema for traffic history"""
    success: bool = True
    road_segment_id: str
    data: List[HistoricalTrafficData]
    start_date: datetime
    end_date: datetime
    total_records: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "road_segment_id": "segment_001",
                "data": [
                    {
                        "timestamp": "2025-10-16T17:00:00",
                        "speed": 15.5,
                        "intensity": 8400.0,
                        "occupancy": 0.76,
                        "congested": True
                    }
                ],
                "start_date": "2025-10-16T00:00:00",
                "end_date": "2025-10-16T23:59:59",
                "total_records": 288
            }
        }


class AllTrafficSegment(BaseModel):
    """Traffic data for single segment"""
    road_segment_id: str
    road_name: str
    speed: float
    intensity: float
    occupancy: float
    congestion_status: str
    congestion_probability: float
    timestamp: datetime


class AllTrafficResponse(BaseModel):
    """Response schema for all traffic segments"""
    success: bool = True
    count: int
    data: List[AllTrafficSegment]
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "count": 10,
                "data": [
                    {
                        "road_segment_id": "segment_001",
                        "road_name": "Võ Văn Kiệt",
                        "speed": 15.25,
                        "intensity": 8500.0,
                        "occupancy": 0.78,
                        "congestion_status": "HEAVY_CONGESTION",
                        "congestion_probability": 1.0,
                        "timestamp": "2025-10-16T17:30:00"
                    }
                ],
                "timestamp": "2025-10-16T17:30:00"
            }
        }
