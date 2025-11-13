"""
Smart Routing API Endpoints
Handles intelligent route finding with traffic prediction
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.routing import (
    RouteRequest,
    RouteResponse,
    AlternativeRoutesRequest,
    RoadStatusResponse
)
from app.services.routing_service import get_routing_service

router = APIRouter()


@router.post("/find-route", response_model=RouteResponse)
async def find_optimal_route(
    request: RouteRequest,
    db: Session = Depends(get_db)
):
    """
    Tìm đường đi tối ưu từ điểm A đến điểm B
    
    Uses A* algorithm with ML-predicted traffic conditions
    
    Parameters:
    - origin: Origin road segment ID
    - destination: Destination road segment ID
    - departure_time: Departure time (optional, default: now)
    
    Returns:
    - Optimal route with segments, distance, estimated time
    """
    try:
        routing_service = get_routing_service(db)
        
        # Find optimal route
        result = routing_service.find_optimal_route(
            origin=request.origin,
            destination=request.destination,
            departure_time=request.departure_time
        )
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error', 'Route not found'))
        
        # Parse GeoJSON coordinates from database
        from app.models.traffic import RoadSegment
        
        for segment in result['segments']:
            segment_id = segment['segment_id']
            # Fetch segment with coordinates
            db_segment = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
            
            if db_segment:
                try:
                    # Parse GeoJSON startPoint and endPoint
                    if db_segment.startPoint:
                        start_geojson = json.loads(db_segment.startPoint)
                        if 'coordinates' in start_geojson:
                            segment['start_coordinates'] = start_geojson['coordinates']  # [lon, lat]
                    
                    if db_segment.endPoint:
                        end_geojson = json.loads(db_segment.endPoint)
                        if 'coordinates' in end_geojson:
                            segment['end_coordinates'] = end_geojson['coordinates']  # [lon, lat]
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    # If parse fails, skip coordinates
                    print(f"Warning: Could not parse GeoJSON for {segment_id}: {e}")
        
        return {
            "success": True,
            "route": {
                "segments": result['segments'],
                "total_distance": result['total_distance_km'],
                "total_duration": result['estimated_time_min'],
                "traffic_conditions": "ML-predicted"
            },
            "origin": request.origin,
            "destination": request.destination,
            "mode": request.mode or "optimal",
            "departure_time": result.get('departure_time'),
            "estimated_arrival_time": result.get('estimated_arrival_time'),
            "generated_at": datetime.now(),
            "incidents_avoided": result.get('incidents_avoided', 0),
            "prediction_based": result.get('prediction_based', True),
            "explanation": result.get('explanation', '')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alternative-routes", response_model=List[RouteResponse])
async def find_alternative_routes(
    request: AlternativeRoutesRequest,
    db: Session = Depends(get_db)
):
    """
    Tìm nhiều lộ trình thay thế
    
    Parameters:
    - origin: Điểm xuất phát (segment ID)
    - destination: Điểm đích (segment ID)
    - num_alternatives: Số lộ trình thay thế (1-5)
    
    Returns:
    - List of alternative routes sorted by preference
    """
    try:
        routing_service = get_routing_service(db)
        
        # Find alternative routes
        routes = routing_service.find_alternative_routes(
            origin=request.origin,
            destination=request.destination,
            departure_time=request.departure_time,
            num_routes=min(request.num_alternatives or 3, 5)
        )
        
        # Format response
        results = []
        for i, route in enumerate(routes):
            if route['success']:
                results.append({
                    "success": True,
                    "route": {
                        "segments": route['segments'],
                        "total_distance": route['total_distance_km'],
                        "total_duration": route['estimated_time_min'],
                        "traffic_conditions": f"Alternative {i+1}"
                    },
                    "origin": request.origin,
                    "destination": request.destination,
                    "mode": "alternative",
                    "generated_at": datetime.now()
                })
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/road-status/{road_segment_id}", response_model=RoadStatusResponse)
async def get_road_status(
    road_segment_id: str,
    db: Session = Depends(get_db)
):
    """
    Kiểm tra trạng thái đoạn đường
    
    Parameters:
    - road_segment_id: ID đoạn đường
    
    Returns:
    - Road status including traffic, accidents, construction
    """
    try:
        # TODO: Query road status
        return {
            "success": True,
            "road_segment_id": road_segment_id,
            "status": "open",
            "traffic_level": "moderate",
            "has_accident": False,
            "has_construction": False,
            "speed_limit": 50,
            "current_speed": 42,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Road segment not found")


@router.post("/reroute")
async def reroute(
    current_route_id: str,
    current_location: dict,
    db: Session = Depends(get_db)
):
    """
    Tính toán lại lộ trình khi có thay đổi
    
    Parameters:
    - current_route_id: ID lộ trình hiện tại
    - current_location: Vị trí hiện tại
    
    Returns:
    - Updated route from current location
    """
    try:
        # TODO: Implement rerouting
        return {
            "success": True,
            "message": "Route updated successfully",
            "new_route": {},
            "reason": "Traffic conditions changed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
