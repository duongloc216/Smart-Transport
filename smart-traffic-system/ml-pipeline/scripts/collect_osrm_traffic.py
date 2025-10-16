"""
OSRM Traffic Data Collector (FREE - No API Key Required)
Collects traffic data from OSRM (Open Source Routing Machine)

OSRM is completely FREE and open-source:
- No API key required
- No rate limits
- No billing
- Perfect for students and research projects

Note: OSRM doesn't provide real-time traffic, but we can:
1. Calculate baseline travel times
2. Simulate traffic patterns based on time of day
3. Use historical patterns for predictions
"""

import requests
import json
from datetime import datetime, time as dt_time
from typing import List, Dict, Optional, Tuple
import time
import random
from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.database import SessionLocal
from app.models.traffic_flow import TrafficFlowObserved
from app.models.road_segment import RoadSegment


class OSRMTrafficCollector:
    """
    Collect traffic data using OSRM (Open Source Routing Machine)
    
    Features:
    - Completely FREE (no API key needed)
    - Calculates distance and baseline travel time
    - Simulates traffic conditions based on time of day
    - Good enough for academic projects and research
    
    Public OSRM Server: http://router.project-osrm.org
    """
    
    def __init__(self, osrm_server: str = "http://router.project-osrm.org"):
        self.osrm_server = osrm_server
        self.profile = "driving"  # or "car", "bike", "foot"
        
    def get_route(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route information from OSRM
        
        Args:
            origin: (lat, lon) tuple
            destination: (lat, lon) tuple
            
        Returns:
            {
                "distance_meters": float,
                "duration_seconds": float,
                "geometry": dict
            }
        """
        # OSRM uses lon,lat format (not lat,lon like Google)
        url = f"{self.osrm_server}/route/v1/{self.profile}/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
        
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["code"] == "Ok" and len(data["routes"]) > 0:
                route = data["routes"][0]
                
                return {
                    "distance_meters": route["distance"],
                    "duration_seconds": route["duration"],
                    "geometry": route["geometry"]
                }
            else:
                print(f"OSRM returned code: {data.get('code')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting route from OSRM: {e}")
            return None
    
    def simulate_traffic_factor(self, current_time: datetime) -> float:
        """
        Simulate traffic congestion factor based on time of day
        
        Traffic patterns in Ho Chi Minh City:
        - 06:00-09:00: Morning rush hour (1.3-1.8x slower)
        - 09:00-11:00: Normal traffic (1.1-1.2x)
        - 11:00-13:00: Lunch time (1.2-1.4x)
        - 13:00-17:00: Normal (1.0-1.1x)
        - 17:00-20:00: Evening rush hour (1.5-2.0x slower)
        - 20:00-06:00: Light traffic (0.9-1.0x)
        
        Args:
            current_time: Current datetime
            
        Returns:
            Traffic factor (1.0 = normal, >1.0 = slower, <1.0 = faster)
        """
        hour = current_time.hour
        minute = current_time.minute
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend traffic is lighter
        weekend_factor = 0.85 if day_of_week >= 5 else 1.0
        
        # Time-based factors
        if 6 <= hour < 9:  # Morning rush
            base_factor = 1.3 + (hour - 6) * 0.15  # 1.3 -> 1.75
            random_variation = random.uniform(-0.1, 0.2)
        elif 9 <= hour < 11:  # Post-morning
            base_factor = 1.15
            random_variation = random.uniform(-0.05, 0.1)
        elif 11 <= hour < 13:  # Lunch time
            base_factor = 1.3
            random_variation = random.uniform(-0.1, 0.15)
        elif 13 <= hour < 17:  # Afternoon
            base_factor = 1.05
            random_variation = random.uniform(-0.05, 0.1)
        elif 17 <= hour < 20:  # Evening rush
            base_factor = 1.5 + (hour - 17) * 0.15  # 1.5 -> 1.95
            random_variation = random.uniform(-0.1, 0.25)
        else:  # Night/early morning
            base_factor = 0.95
            random_variation = random.uniform(-0.05, 0.05)
        
        final_factor = base_factor * weekend_factor + random_variation
        return max(0.8, min(2.5, final_factor))  # Clamp between 0.8 and 2.5
    
    def calculate_traffic_speed(self, distance_meters: float, 
                                duration_seconds: float, 
                                traffic_factor: float) -> Dict:
        """
        Calculate traffic speed with congestion simulation
        
        Args:
            distance_meters: Route distance in meters
            duration_seconds: Baseline travel time in seconds
            traffic_factor: Congestion factor (1.0 = normal)
            
        Returns:
            {
                "baseline_speed_kmh": float,
                "traffic_speed_kmh": float,
                "duration_in_traffic_seconds": float,
                "congested": bool
            }
        """
        # Baseline speed (no traffic)
        baseline_speed_kmh = (distance_meters / duration_seconds) * 3.6
        
        # Actual speed with traffic
        duration_in_traffic = duration_seconds * traffic_factor
        traffic_speed_kmh = (distance_meters / duration_in_traffic) * 3.6
        
        # Congested if traffic factor > 1.2 (20% slower)
        is_congested = traffic_factor > 1.2
        
        return {
            "baseline_speed_kmh": round(baseline_speed_kmh, 2),
            "traffic_speed_kmh": round(traffic_speed_kmh, 2),
            "duration_in_traffic_seconds": round(duration_in_traffic, 2),
            "congested": is_congested,
            "traffic_factor": round(traffic_factor, 2)
        }
    
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
                
                # Get route from OSRM
                route_data = self.get_route(origin, destination)
                
                if route_data:
                    # Simulate traffic based on current time
                    current_time = datetime.now()
                    traffic_factor = self.simulate_traffic_factor(current_time)
                    
                    # Calculate speeds
                    traffic_info = self.calculate_traffic_speed(
                        route_data["distance_meters"],
                        route_data["duration_seconds"],
                        traffic_factor
                    )
                    
                    # Create TrafficFlowObserved record
                    traffic_record = TrafficFlowObserved(
                        id=f"traffic_{segment.id}_{int(time.time())}",
                        refRoadSegment=segment.id,
                        dateObservedFrom=current_time,
                        dateObservedTo=current_time,
                        averageVehicleSpeed=traffic_info["traffic_speed_kmh"],
                        intensity=None,  # OSRM doesn't provide vehicle count
                        occupancy=None,  # OSRM doesn't provide occupancy
                        congested=traffic_info["congested"],
                        laneDirection="forward",
                        vehicleType="car",
                        location=segment.startPoint,
                        dataProvider="OSRM + Simulated Traffic",
                        source=f"OSRM Route API + Time-based simulation (factor: {traffic_info['traffic_factor']})",
                        dateCreated=current_time,
                        dateModified=current_time
                    )
                    
                    db.add(traffic_record)
                    db.commit()
                    
                    print(f"✅ {segment.roadName}: {traffic_info['traffic_speed_kmh']} km/h "
                          f"(factor: {traffic_info['traffic_factor']}, "
                          f"{'🔴 CONGESTED' if traffic_info['congested'] else '🟢 CLEAR'})")
                    return True
                    
        except Exception as e:
            print(f"❌ Error collecting traffic for segment {segment.id}: {e}")
            db.rollback()
            return False
        
        return False
    
    def collect_all_segments(self, limit: int = 10, delay_seconds: int = 1):
        """
        Collect traffic data for all road segments in database
        
        Args:
            limit: Maximum number of segments to collect
            delay_seconds: Delay between requests (be nice to free server)
        """
        db = SessionLocal()
        
        try:
            # Get segments with status='open'
            segments = db.query(RoadSegment).filter(
                RoadSegment.status == "open"
            ).limit(limit).all()
            
            print(f"📊 Found {len(segments)} segments to collect traffic data")
            print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🌐 Using FREE OSRM server (no API key needed)\n")
            
            success_count = 0
            for i, segment in enumerate(segments, 1):
                print(f"[{i}/{len(segments)}] Processing: {segment.roadName}")
                
                if self.collect_traffic_for_segment(segment, db):
                    success_count += 1
                
                # Small delay to be respectful to free server
                if i < len(segments):
                    time.sleep(delay_seconds)
            
            print(f"\n✅ Successfully collected traffic for {success_count}/{len(segments)} segments")
            
        finally:
            db.close()


def main():
    """
    Main function to run traffic collection with OSRM (FREE)
    
    Usage:
    python collect_osrm_traffic.py
    
    No API key required! 🎉
    """
    print("=" * 60)
    print("🚀 OSRM Traffic Data Collection (100% FREE)")
    print("=" * 60)
    print("✅ No API key required")
    print("✅ No billing or credit card needed")
    print("✅ Perfect for student projects")
    print("✅ Simulates realistic traffic patterns for Ho Chi Minh City")
    print("=" * 60)
    
    collector = OSRMTrafficCollector()
    
    # Collect traffic for all segments
    collector.collect_all_segments(limit=10, delay_seconds=1)
    
    print("\n✅ Traffic data collection completed!")
    print("\n💡 TIP: Run this script every 15 minutes to build a dataset")
    print("   Example: Run 96 times per day for 7 days = 6,720 data points")


if __name__ == "__main__":
    main()
