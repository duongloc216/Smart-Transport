"""
Simple Google Maps Traffic Data Collector
Standalone script - no backend dependencies needed
"""

import os
import sys
import requests
import json
from datetime import datetime
import time
import pyodbc
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '../../backend/.env')
load_dotenv(env_path)

class SimpleTrafficCollector:
    """Collect traffic data from Google Maps and store in SQL Server"""
    
    def __init__(self, api_key: str, db_connection_string: str):
        self.api_key = api_key
        self.db_connection_string = db_connection_string
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    def get_db_connection(self):
        """Create database connection"""
        return pyodbc.connect(self.db_connection_string)
    
    def get_traffic_data(self, origin: tuple, destination: tuple) -> dict:
        """
        Get traffic data between two points
        
        Args:
            origin: (lat, lon)
            destination: (lat, lon)
            
        Returns:
            Traffic data dictionary
        """
        url = f"{self.base_url}/distancematrix/json"
        params = {
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{destination[0]},{destination[1]}",
            "departure_time": "now",
            "traffic_model": "best_guess",
            "mode": "driving",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK":
                element = data["rows"][0]["elements"][0]
                
                if element["status"] == "OK":
                    distance = element["distance"]["value"]  # meters
                    duration = element["duration"]["value"]  # seconds
                    duration_traffic = element.get("duration_in_traffic", {}).get("value", duration)
                    
                    # Calculate average speed in km/h
                    speed_kmh = (distance / duration_traffic) * 3.6 if duration_traffic > 0 else 0
                    
                    return {
                        "distance_meters": distance,
                        "duration_seconds": duration,
                        "duration_traffic_seconds": duration_traffic,
                        "speed_kmh": round(speed_kmh, 2),
                        "congested": duration_traffic > duration * 1.2,
                        "status": "OK"
                    }
            
            return {"status": data.get("status", "ERROR"), "error": data.get("error_message", "Unknown error")}
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def get_road_segments(self):
        """Get all road segments from database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            ID,
            Name,
            Location,
            StartPoint,
            EndPoint,
            TotalLaneNumber,
            MaximumAllowedSpeed
        FROM RoadSegment
        WHERE Status = 'open'
        """
        
        cursor.execute(query)
        segments = []
        
        for row in cursor.fetchall():
            segments.append({
                "id": row.ID,
                "name": row.Name,
                "location": row.Location,
                "start_point": row.StartPoint,
                "end_point": row.EndPoint,
                "lanes": row.TotalLaneNumber,
                "speed_limit": row.MaximumAllowedSpeed
            })
        
        cursor.close()
        conn.close()
        
        return segments
    
    def save_traffic_record(self, segment_id: str, segment_name: str, traffic_data: dict, 
                           start_point: str, end_point: str):
        """Save traffic observation to database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        record_id = f"traffic_{segment_id}_{int(time.time())}"
        
        query = """
        INSERT INTO TrafficFlowObserved (
            ID,
            RefRoadSegment,
            DateObservedFrom,
            DateObservedTo,
            AverageVehicleSpeed,
            Congested,
            LaneDirection,
            VehicleType,
            Location,
            DataProvider,
            Source,
            DateCreated,
            DateModified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor.execute(query, (
                record_id,
                segment_id,
                now,
                now,
                traffic_data["speed_kmh"],
                1 if traffic_data["congested"] else 0,
                "forward",
                "car",
                start_point,
                "Google Maps API",
                "Distance Matrix API",
                now,
                now
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"  ❌ Database error: {e}")
            cursor.close()
            conn.close()
            return False
    
    def collect_all_segments(self, delay_seconds: int = 3):
        """Collect traffic for all segments"""
        print("=" * 60)
        print("🚗 GOOGLE MAPS TRAFFIC DATA COLLECTOR")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Get segments
        print("📊 Loading road segments from database...")
        segments = self.get_road_segments()
        print(f"✅ Found {len(segments)} road segments\n")
        
        if not segments:
            print("❌ No road segments found in database!")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, segment in enumerate(segments, 1):
            print(f"[{i}/{len(segments)}] 🛣️  {segment['name']}")
            
            try:
                # Parse coordinates from GeoJSON
                location_data = json.loads(segment["location"])
                
                if location_data["type"] == "LineString":
                    coords = location_data["coordinates"]
                    origin = (coords[0][1], coords[0][0])  # (lat, lon)
                    destination = (coords[-1][1], coords[-1][0])
                    
                    print(f"  📍 From: {origin}")
                    print(f"  📍 To: {destination}")
                    
                    # Get traffic data
                    traffic = self.get_traffic_data(origin, destination)
                    
                    if traffic["status"] == "OK":
                        print(f"  ✅ Speed: {traffic['speed_kmh']} km/h")
                        print(f"  ⏱️  Duration: {traffic['duration_traffic_seconds']}s")
                        print(f"  {'🔴 CONGESTED' if traffic['congested'] else '🟢 FLOWING'}")
                        
                        # Save to database
                        if self.save_traffic_record(
                            segment["id"], 
                            segment["name"],
                            traffic,
                            segment["start_point"],
                            segment["end_point"]
                        ):
                            print(f"  💾 Saved to database")
                            success_count += 1
                        else:
                            fail_count += 1
                    else:
                        print(f"  ❌ API Error: {traffic.get('error', 'Unknown')}")
                        fail_count += 1
                        
            except Exception as e:
                print(f"  ❌ Error: {e}")
                fail_count += 1
            
            print()  # Blank line
            
            # Delay between requests
            if i < len(segments):
                time.sleep(delay_seconds)
        
        # Summary
        print("=" * 60)
        print("📊 COLLECTION SUMMARY")
        print("=" * 60)
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📈 Total: {len(segments)}")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def main():
    """Main function"""
    # Get configuration from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    db_server = os.getenv("DB_SERVER")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY not found!")
        print("Please check your .env file")
        return
    
    # Build connection string
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={db_server};"
        f"DATABASE={db_name};"
        f"UID={db_user};"
        f"PWD={db_password}"
    )
    
    # Create collector
    collector = SimpleTrafficCollector(api_key, connection_string)
    
    # Run collection
    collector.collect_all_segments(delay_seconds=3)


if __name__ == "__main__":
    main()
