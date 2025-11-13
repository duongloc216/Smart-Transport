"""
Routing Schemas
Pydantic models for routing API requests/responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class RouteSegment(BaseModel):
    """Individual segment in a route"""
    segment_id: str = Field(..., description="Road segment ID")
    name: str = Field(..., description="Road name")
    distance_km: float = Field(..., description="Distance in kilometers")
    max_speed: float = Field(..., description="Maximum allowed speed")
    has_incident: bool = Field(False, description="Has active incident")
    incidents: List[Dict[str, Any]] = Field(default_factory=list, description="Active incidents")
    start_coordinates: Optional[List[float]] = Field(None, description="Start point [lon, lat]")
    end_coordinates: Optional[List[float]] = Field(None, description="End point [lon, lat]")


class RouteInfo(BaseModel):
    """Route information"""
    segments: List[RouteSegment] = Field(..., description="Route segments")
    total_distance: float = Field(..., description="Total distance in km")
    total_duration: float = Field(..., description="Total duration in minutes")
    traffic_conditions: str = Field(..., description="Overall traffic conditions")


class RouteRequest(BaseModel):
    """Request schema for route finding"""
    origin: str = Field(..., description="Origin segment ID", example="segment_001")
    destination: str = Field(..., description="Destination segment ID", example="segment_010")
    departure_time: Optional[datetime] = Field(None, description="Departure time (default: now)")
    mode: Optional[str] = Field("optimal", description="Route mode: optimal, fastest, shortest")


class RouteResponse(BaseModel):
    """Response schema for route finding"""
    success: bool = Field(True, description="Request success status")
    route: RouteInfo = Field(..., description="Route information")
    origin: str = Field(..., description="Origin segment ID")
    destination: str = Field(..., description="Destination segment ID")
    mode: str = Field(..., description="Route mode used")
    departure_time: Optional[str] = Field(None, description="Departure time in ISO format")
    estimated_arrival_time: Optional[str] = Field(None, description="Estimated arrival time in ISO format")
    generated_at: datetime = Field(..., description="Response generation time")
    incidents_avoided: Optional[int] = Field(0, description="Number of incidents avoided")
    prediction_based: Optional[bool] = Field(True, description="Whether route uses ML predictions")
    explanation: Optional[str] = Field(None, description="Explanation of routing decision")


class AlternativeRoutesRequest(BaseModel):
    """Request for alternative routes"""
    origin: str = Field(..., description="Origin segment ID")
    destination: str = Field(..., description="Destination segment ID")
    departure_time: Optional[datetime] = Field(None, description="Departure time")
    num_alternatives: Optional[int] = Field(3, ge=1, le=5, description="Number of alternative routes (1-5)")


class RoadStatusResponse(BaseModel):
    """Response for road status"""
    success: bool = Field(True, description="Request success status")
    road_segment_id: str = Field(..., description="Road segment ID")
    status: str = Field(..., description="Road status: open, closed, restricted")
    traffic_level: str = Field(..., description="Traffic level: light, moderate, heavy")
    has_accident: bool = Field(False, description="Has active accident")
    has_construction: bool = Field(False, description="Has active construction")
    speed_limit: float = Field(..., description="Speed limit in km/h")
    current_speed: float = Field(..., description="Current average speed")
    timestamp: datetime = Field(..., description="Status timestamp")
