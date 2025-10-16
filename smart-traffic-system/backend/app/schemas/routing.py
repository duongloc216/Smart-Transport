"""
Routing Schemas - Stub for now
TODO: Implement full routing schemas later
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RouteRequest(BaseModel):
    """Request schema for route finding"""
    origin: str
    destination: str
    departure_time: Optional[datetime] = None


class RouteResponse(BaseModel):
    """Response schema for route finding"""
    success: bool = True
    origin: str
    destination: str
    routes: List[dict] = []
    generated_at: datetime


class AlternativeRoutesRequest(BaseModel):
    """Request for alternative routes"""
    origin: str
    destination: str
    max_alternatives: Optional[int] = 3


class RoadStatusResponse(BaseModel):
    """Response for road status"""
    success: bool = True
    road_id: str
    status: str
    timestamp: datetime
