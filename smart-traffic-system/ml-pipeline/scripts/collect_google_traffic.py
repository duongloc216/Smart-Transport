"""
Google Maps Traffic Data Collector
Collects real-time traffic data from Google Maps Roads API and Traffic API
"""

import os
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import time
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.traffic_flow import TrafficFlowObserved
from app.models.road_segment import RoadSegment


class GoogleMapsTrafficCollector:
    """
    Collect traffic data from Google Maps APIs
    
    Required APIs:
    1. Roads API - Get road information
    2. Distance Matrix API - Get travel times (used to calculate traffic speed)
    
    Setup:
    1. Go to https://console.cloud.google.com/
    2. Enable "Roads API" and "Distance Matrix API"
    3. Create API Key
    4. Add key to .env file: GOOGLE_MAPS_API_KEY=your_key_here
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url_roads = "https://roads.googleapis.com/v1"
        self.base_url_maps = "https://maps.googleapis.com/maps/api"
        
    def snap_to_roads(self, coordinates: List[tuple]) -> Dict:
        """
        Snap GPS coordinates to roads
        
        Args:
            coordinates: List of (lat, lon) tuples
            
        Returns:
            Snapped road data with placeIds
        """
        # Format coordinates for API
        path = "|".join([f"{lat},{lon}" for lat, lon in coordinates])
        
        url = f"{self.base_url_roads}/snapToRoads"
        params = {
            "path": path,
            "interpolate": "true",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error snapping to roads: {e}")
            return {}
    
    def get_traffic_speed(self, origin: tuple, destination: tuple) -> Optional[Dict]:
        """
        Get current traffic speed between two points using Distance Matrix API
        
        Args:
            origin: (lat, lon) tuple
            destination: (lat, lon) tuple
            
        Returns:
            {
                "duration": seconds,
                "duration_in_traffic": seconds,
                "distance": meters,
                "average_speed": km/h
            }
        """
        url = f"{self.base_url_maps}/distancematrix/json"
        params = {
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{destination[0]},{destination[1]}",
            "departure_time": "now",  # Get real-time traffic
            "traffic_model": "best_guess",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK":
                element = data["rows"][0]["elements"][0]
                
                if element["status"] == "OK":
                    distance_meters = element["distance"]["value"]
                    duration_traffic_seconds = element.get("duration_in_traffic", {}).get("value", 
                                                           element["duration"]["value"])
                    
                    # Calculate speed: distance (m) / time (s) * 3.6 = km/h
                    average_speed_kmh = (distance_meters / duration_traffic_seconds) * 3.6
                    
                    return {
                        "distance_meters": distance_meters,
                        "duration_seconds": element["duration"]["value"],
                        "duration_in_traffic_seconds": duration_traffic_seconds,
                        "average_speed_kmh": round(average_speed_kmh, 2)
                    }
            
            print(f"API returned status: {data.get('status')}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting traffic speed: {e}")
            return None
    
    def collect_traffic_for_segment(self, segment: RoadSegment, db: Session) -> bool:
        """
        Collect traffic data for a specific road segment
        
        Args:
            segment: RoadSegment model instance
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse GeoJSON to get coordinates
            location_data = json.loads(segment.location)
            
            if location_data["type"] == "LineString":
                coordinates = location_data["coordinates"]
                
                # Get start and end points
                origin = (coordinates[0][1], coordinates[0][0])  # (lat, lon)
                destination = (coordinates[-1][1], coordinates[-1][0])
                
                # Get traffic speed
                traffic_data = self.get_traffic_speed(origin, destination)
                
                if traffic_data:
                    # Create TrafficFlowObserved record
                    traffic_record = TrafficFlowObserved(
                        id=f"traffic_{segment.id}_{int(time.time())}",
                        refRoadSegment=segment.id,
                        dateObservedFrom=datetime.now(),
                        dateObservedTo=datetime.now(),
                        averageVehicleSpeed=traffic_data["average_speed_kmh"],
                        intensity=None,  # Google API doesn't provide this
                        occupancy=None,  # Google API doesn't provide this
                        congested=traffic_data["duration_in_traffic_seconds"] > traffic_data["duration_seconds"] * 1.3,
                        laneDirection="forward",
                        vehicleType="car",
                        location=segment.startPoint,  # Use start point
                        dataProvider="Google Maps API",
                        source="Distance Matrix API",
                        dateCreated=datetime.now(),
                        dateModified=datetime.now()
                    )
                    
                    db.add(traffic_record)
                    db.commit()
                    
                    print(f"✅ Collected traffic for {segment.roadName}: {traffic_data['average_speed_kmh']} km/h")
                    return True
                    
        except Exception as e:
            print(f"❌ Error collecting traffic for segment {segment.id}: {e}")
            db.rollback()
            return False
        
        return False
    
    def collect_all_segments(self, limit: int = 10, delay_seconds: int = 2):
        """
        Collect traffic data for all road segments in database
        
        Args:
            limit: Maximum number of segments to collect (to avoid API quota)
            delay_seconds: Delay between requests (to respect rate limits)
        """
        db = SessionLocal()
        
        try:
            # Get segments with status='open'
            segments = db.query(RoadSegment).filter(
                RoadSegment.status == "open"
            ).limit(limit).all()
            
            print(f"📊 Found {len(segments)} segments to collect traffic data")
            
            success_count = 0
            for i, segment in enumerate(segments, 1):
                print(f"\n[{i}/{len(segments)}] Processing: {segment.roadName}")
                
                if self.collect_traffic_for_segment(segment, db):
                    success_count += 1
                
                # Delay to respect API rate limits
                if i < len(segments):
                    time.sleep(delay_seconds)
            
            print(f"\n✅ Successfully collected traffic for {success_count}/{len(segments)} segments")
            
        finally:
            db.close()


def main():
    """
    Main function to run traffic collection
    
    Usage:
    python collect_google_traffic.py
    """
    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please add it to your .env file:")
        print("GOOGLE_MAPS_API_KEY=your_api_key_here")
        return
    
    print("🚀 Starting Google Maps Traffic Data Collection")
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")  # Show partial key for verification
    
    collector = GoogleMapsTrafficCollector(api_key)
    
    # Collect traffic for up to 10 segments (adjust based on your API quota)
    collector.collect_all_segments(limit=10, delay_seconds=2)
    
    print("\n✅ Traffic data collection completed!")


if __name__ == "__main__":
    main()
