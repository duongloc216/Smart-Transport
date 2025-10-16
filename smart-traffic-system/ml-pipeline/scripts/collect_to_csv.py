"""
Google Maps Traffic Collector - Save to CSV
For running on cloud VM without database connection
"""

import os
import requests
import json
import csv
from datetime import datetime
import time
from pathlib import Path

class TrafficCollectorCSV:
    """Collect traffic data and save to CSV file"""
    
    def __init__(self, api_key: str, output_dir: str = "./data"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        # 10 road segments in HCMC
        self.segments = [
            {
                "id": "segment_001",
                "name": "Nguyen Hue Street",
                "origin": (10.7741, 106.7008),
                "destination": (10.7769, 106.7011)
            },
            {
                "id": "segment_002",
                "name": "Le Loi Boulevard",
                "origin": (10.7723, 106.6989),
                "destination": (10.7741, 106.7008)
            },
            {
                "id": "segment_003",
                "name": "Vo Van Tan Street",
                "origin": (10.7793, 106.6931),
                "destination": (10.7826, 106.6952)
            },
            {
                "id": "segment_004",
                "name": "Dien Bien Phu Street",
                "origin": (10.7874, 106.6989),
                "destination": (10.7889, 106.7031)
            },
            {
                "id": "segment_005",
                "name": "Cach Mang Thang Tam",
                "origin": (10.778, 106.6651),
                "destination": (10.782, 106.6691)
            },
            {
                "id": "segment_006",
                "name": "Tran Hung Dao Street",
                "origin": (10.7965, 106.6919),
                "destination": (10.8003, 106.6965)
            },
            {
                "id": "segment_007",
                "name": "Nguyen Thi Minh Khai",
                "origin": (10.7754, 106.6938),
                "destination": (10.7789, 106.692)
            },
            {
                "id": "segment_008",
                "name": "Pasteur Street",
                "origin": (10.7755, 106.7023),
                "destination": (10.78, 106.7045)
            },
            {
                "id": "segment_009",
                "name": "Hai Ba Trung Street",
                "origin": (10.7622, 106.6859),
                "destination": (10.7598, 106.681)
            },
            {
                "id": "segment_010",
                "name": "Pham Ngu Lao Street",
                "origin": (10.7878, 106.7124),
                "destination": (10.7915, 106.7158)
            }
        ]
    
    def get_traffic_data(self, origin: tuple, destination: tuple) -> dict:
        """Get traffic data from Google Maps API"""
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
                    distance = element["distance"]["value"]
                    duration = element["duration"]["value"]
                    duration_traffic = element.get("duration_in_traffic", {}).get("value", duration)
                    
                    speed_kmh = (distance / duration_traffic) * 3.6 if duration_traffic > 0 else 0
                    
                    return {
                        "distance_meters": distance,
                        "duration_seconds": duration,
                        "duration_traffic_seconds": duration_traffic,
                        "speed_kmh": round(speed_kmh, 2),
                        "congested": duration_traffic > duration * 1.2,
                        "status": "OK"
                    }
            
            return {"status": data.get("status", "ERROR")}
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def collect_once(self):
        """Collect traffic data for all segments once"""
        timestamp = datetime.now()
        results = []
        
        print(f"\n⏰ Collection at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for i, segment in enumerate(self.segments, 1):
            print(f"[{i}/10] {segment['name']}...", end=" ")
            
            traffic = self.get_traffic_data(segment["origin"], segment["destination"])
            
            if traffic["status"] == "OK":
                record = {
                    "timestamp": timestamp.isoformat(),
                    "segment_id": segment["id"],
                    "segment_name": segment["name"],
                    "distance_meters": traffic["distance_meters"],
                    "duration_seconds": traffic["duration_seconds"],
                    "duration_traffic_seconds": traffic["duration_traffic_seconds"],
                    "speed_kmh": traffic["speed_kmh"],
                    "congested": 1 if traffic["congested"] else 0,
                    "origin_lat": segment["origin"][0],
                    "origin_lon": segment["origin"][1],
                    "destination_lat": segment["destination"][0],
                    "destination_lon": segment["destination"][1]
                }
                results.append(record)
                
                status = "🔴" if traffic["congested"] else "🟢"
                print(f"{status} {traffic['speed_kmh']} km/h")
            else:
                print(f"❌ {traffic.get('error', 'Error')}")
            
            time.sleep(1)  # Small delay between requests
        
        return results
    
    def save_to_csv(self, records: list):
        """Append records to CSV file"""
        csv_file = self.output_dir / "traffic_data.csv"
        
        # Check if file exists to write header
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            if records:
                fieldnames = records[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerows(records)
        
        print(f"💾 Saved {len(records)} records to {csv_file}")


def main():
    """Run single collection"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY not found!")
        return
    
    collector = TrafficCollectorCSV(api_key)
    records = collector.collect_once()
    
    if records:
        collector.save_to_csv(records)
        print(f"✅ Collection completed: {len(records)} records")
    else:
        print("❌ No records collected")


if __name__ == "__main__":
    main()
