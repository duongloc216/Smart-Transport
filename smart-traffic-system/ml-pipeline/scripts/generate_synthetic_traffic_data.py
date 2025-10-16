"""
Generate Synthetic Traffic Data
Tạo dữ liệu giao thông giả với patterns thực tế cho 3 ngày
"""

import random
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class SyntheticTrafficGenerator:
    """Generate realistic synthetic traffic data"""
    
    def __init__(self):
        # 10 road segments in HCMC
        self.segments = [
            {
                "id": "segment_001",
                "name": "Nguyen Hue Street",
                "base_speed": 25,
                "length_km": 0.71
            },
            {
                "id": "segment_002",
                "name": "Le Loi Boulevard",
                "base_speed": 30,
                "length_km": 0.54
            },
            {
                "id": "segment_003",
                "name": "Vo Van Tan Street",
                "base_speed": 28,
                "length_km": 0.91
            },
            {
                "id": "segment_004",
                "name": "Dien Bien Phu Street",
                "base_speed": 35,
                "length_km": 1.62
            },
            {
                "id": "segment_005",
                "name": "Cach Mang Thang Tam",
                "base_speed": 32,
                "length_km": 1.52
            },
            {
                "id": "segment_006",
                "name": "Tran Hung Dao Street",
                "base_speed": 38,
                "length_km": 1.03
            },
            {
                "id": "segment_007",
                "name": "Nguyen Thi Minh Khai",
                "base_speed": 36,
                "length_km": 1.60
            },
            {
                "id": "segment_008",
                "name": "Pasteur Street",
                "base_speed": 22,
                "length_km": 0.72
            },
            {
                "id": "segment_009",
                "name": "Hai Ba Trung Street",
                "base_speed": 33,
                "length_km": 0.84
            },
            {
                "id": "segment_010",
                "name": "Pham Ngu Lao Street",
                "base_speed": 40,
                "length_km": 2.66
            }
        ]
        
        # Traffic patterns based on HCMC reality
        self.traffic_patterns = {
            "weekday_morning_rush": {  # 7:00-9:00
                "speed_multiplier": 0.35,  # Giảm 65% tốc độ
                "congestion_prob": 0.85
            },
            "weekday_evening_rush": {  # 17:00-19:00
                "speed_multiplier": 0.40,
                "congestion_prob": 0.80
            },
            "weekday_midday": {  # 11:00-13:00
                "speed_multiplier": 0.65,
                "congestion_prob": 0.35
            },
            "weekday_normal": {  # Other hours
                "speed_multiplier": 0.75,
                "congestion_prob": 0.20
            },
            "weekend_day": {  # Weekend 8:00-18:00
                "speed_multiplier": 0.85,
                "congestion_prob": 0.15
            },
            "night": {  # 22:00-6:00
                "speed_multiplier": 0.95,
                "congestion_prob": 0.05
            }
        }
    
    def get_traffic_pattern(self, timestamp):
        """Xác định traffic pattern dựa trên thời gian"""
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        if is_weekend:
            if 22 <= hour or hour < 6:
                return "night"
            else:
                return "weekend_day"
        else:  # Weekday
            if 22 <= hour or hour < 6:
                return "night"
            elif 7 <= hour < 9:
                return "weekday_morning_rush"
            elif 17 <= hour < 19:
                return "weekday_evening_rush"
            elif 11 <= hour < 13:
                return "weekday_midday"
            else:
                return "weekday_normal"
    
    def generate_traffic_record(self, segment, timestamp):
        """Generate một traffic record cho segment tại timestamp"""
        pattern_name = self.get_traffic_pattern(timestamp)
        pattern = self.traffic_patterns[pattern_name]
        
        # Calculate speed với noise
        base_speed = segment["base_speed"]
        speed_multiplier = pattern["speed_multiplier"]
        
        # Add random noise (-15% to +10%)
        noise = random.uniform(-0.15, 0.10)
        actual_speed = base_speed * speed_multiplier * (1 + noise)
        actual_speed = max(5, min(actual_speed, base_speed))  # Clamp between 5 and base_speed
        actual_speed = round(actual_speed, 2)
        
        # Calculate duration
        length_km = segment["length_km"]
        duration_hours = length_km / actual_speed
        duration_seconds = int(duration_hours * 3600)
        
        # Base duration (ideal conditions)
        base_duration_seconds = int((length_km / base_speed) * 3600)
        
        # Determine congestion
        congestion_prob = pattern["congestion_prob"]
        is_congested = random.random() < congestion_prob
        
        # Add distance in meters
        distance_meters = int(length_km * 1000)
        
        # Add coordinates (fake but consistent)
        origin_lat = 10.77 + random.uniform(0, 0.02)
        origin_lon = 106.68 + random.uniform(0, 0.03)
        dest_lat = origin_lat + random.uniform(0, 0.01)
        dest_lon = origin_lon + random.uniform(0, 0.01)
        
        return {
            "timestamp": timestamp.isoformat(),
            "segment_id": segment["id"],
            "segment_name": segment["name"],
            "distance_meters": distance_meters,
            "duration_seconds": base_duration_seconds,
            "duration_traffic_seconds": duration_seconds,
            "speed_kmh": actual_speed,
            "congested": 1 if is_congested else 0,
            "origin_lat": round(origin_lat, 6),
            "origin_lon": round(origin_lon, 6),
            "destination_lat": round(dest_lat, 6),
            "destination_lon": round(dest_lon, 6)
        }
    
    def generate_dataset(self, days=3, interval_minutes=5):
        """
        Generate complete dataset for multiple days
        
        Args:
            days: Số ngày data (default: 3)
            interval_minutes: Khoảng cách giữa các lần collection (default: 5 phút)
        
        Returns:
            DataFrame with all traffic records
        """
        print("=" * 70)
        print("🎲 SYNTHETIC TRAFFIC DATA GENERATOR")
        print("=" * 70)
        
        start_time = datetime.now() - timedelta(days=days)
        end_time = datetime.now()
        
        print(f"📅 Time Range: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"⏱️  Interval: {interval_minutes} minutes")
        print(f"🛣️  Segments: {len(self.segments)}")
        
        # Calculate number of timestamps
        total_minutes = days * 24 * 60
        num_timestamps = total_minutes // interval_minutes
        
        print(f"📊 Expected Records: {num_timestamps * len(self.segments)}")
        print(f"    ({len(self.segments)} segments × {num_timestamps} timestamps)")
        print("=" * 70)
        print()
        
        all_records = []
        current_time = start_time
        timestamp_count = 0
        
        while current_time <= end_time:
            timestamp_count += 1
            
            # Generate record for each segment at this timestamp
            for segment in self.segments:
                record = self.generate_traffic_record(segment, current_time)
                all_records.append(record)
            
            # Progress update every 100 timestamps
            if timestamp_count % 100 == 0:
                progress = (timestamp_count / num_timestamps) * 100
                print(f"⏳ Progress: {timestamp_count}/{num_timestamps} timestamps ({progress:.1f}%)")
            
            # Move to next timestamp
            current_time += timedelta(minutes=interval_minutes)
        
        print()
        print("✅ Data generation completed!")
        print(f"📊 Total records: {len(all_records)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        
        # Statistics
        print("\n" + "=" * 70)
        print("📈 DATASET STATISTICS")
        print("=" * 70)
        print(f"Total Records: {len(df)}")
        print(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"\nSpeed Statistics (km/h):")
        print(f"  Mean: {df['speed_kmh'].mean():.2f}")
        print(f"  Min: {df['speed_kmh'].min():.2f}")
        print(f"  Max: {df['speed_kmh'].max():.2f}")
        print(f"  Std: {df['speed_kmh'].std():.2f}")
        print(f"\nCongestion:")
        congestion_count = df['congested'].sum()
        congestion_pct = (congestion_count / len(df)) * 100
        print(f"  Congested: {congestion_count} ({congestion_pct:.1f}%)")
        print(f"  Flowing: {len(df) - congestion_count} ({100 - congestion_pct:.1f}%)")
        print("=" * 70)
        
        return df


def main():
    """Main function"""
    print("\n🚀 Starting Synthetic Traffic Data Generation...\n")
    
    # Create generator
    generator = SyntheticTrafficGenerator()
    
    # Generate 3 days of data, every 5 minutes
    df = generator.generate_dataset(days=3, interval_minutes=5)
    
    # Save to CSV
    output_file = "synthetic_traffic_data.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Data saved to: {output_file}")
    print(f"📁 File size: {len(df)} rows")
    
    # Show sample
    print("\n📋 Sample data (first 5 records):")
    print(df.head().to_string())
    
    print("\n✅ All done! You can now import this CSV into SQL Server.")
    print("\nNext steps:")
    print("  1. Run import script to load into database")
    print("  2. Start ML model training")
    print("  3. Build prediction APIs")


if __name__ == "__main__":
    main()
