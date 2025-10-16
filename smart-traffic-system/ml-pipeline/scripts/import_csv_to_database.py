"""
Import Synthetic Traffic Data to SQL Server
"""

import pandas as pd
import pyodbc
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('../backend/.env')

def get_db_connection():
    """Create database connection"""
    server = os.getenv('DB_SERVER', 'localhost\\MSSQLSERVER02')
    database = os.getenv('DB_NAME', 'SmartTrafficDB')
    username = os.getenv('DB_USER', 'locdt')
    password = os.getenv('DB_PASSWORD', 'locdt')
    
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    
    return pyodbc.connect(connection_string)


def import_traffic_data(csv_file):
    """Import traffic data from CSV to SQL Server"""
    
    print("=" * 70)
    print("📥 IMPORT SYNTHETIC TRAFFIC DATA TO SQL SERVER")
    print("=" * 70)
    print()
    
    # Read CSV
    print(f"📂 Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"✅ Loaded {len(df)} records")
    print()
    
    # Connect to database
    print("🔌 Connecting to SQL Server...")
    conn = get_db_connection()
    cursor = conn.cursor()
    print("✅ Connected successfully")
    print()
    
    # Clear existing data (optional)
    print("🗑️  Clearing existing traffic data...")
    cursor.execute("DELETE FROM TrafficFlowObserved")
    conn.commit()
    print("✅ Existing data cleared")
    print()
    
    # Prepare insert query with all columns
    insert_query = """
    INSERT INTO TrafficFlowObserved (
        ID,
        RefRoadSegment,
        DateObservedFrom,
        DateObservedTo,
        AverageVehicleSpeed,
        Intensity,
        Occupancy,
        Congested,
        AverageGapDistance,
        AverageHeadwayTime,
        AverageVehicleLength,
        LaneDirection,
        VehicleType,
        Location,
        DataProvider,
        Source,
        DateCreated,
        DateModified
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Import data in batches
    batch_size = 100
    total_imported = 0
    errors = 0
    
    print(f"📊 Importing data in batches of {batch_size}...")
    print()
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        for idx, row in batch.iterrows():
            try:
                # Create unique ID
                record_id = f"traffic_{row['segment_id']}_{int(pd.Timestamp(row['timestamp']).timestamp())}"
                
                # Parse timestamp
                timestamp = pd.to_datetime(row['timestamp'])
                
                # Calculate additional traffic metrics based on speed and congestion
                speed = float(row['speed_kmh'])
                is_congested = int(row['congested'])
                
                # Intensity: vehicles/hour (estimate based on congestion)
                # High congestion = more vehicles
                if is_congested:
                    intensity = int(random.uniform(800, 1200))  # Heavy traffic
                else:
                    intensity = int(random.uniform(200, 600))   # Normal traffic
                
                # Occupancy: % of road occupied (0-100)
                # Based on speed reduction
                max_speed = 40  # Assumed max speed
                occupancy = max(0, min(100, int((1 - speed / max_speed) * 100)))
                
                # Average gap distance: meters between vehicles
                # Less distance when congested
                if is_congested:
                    gap_distance = round(random.uniform(5, 15), 2)
                else:
                    gap_distance = round(random.uniform(20, 50), 2)
                
                # Average headway time: seconds between vehicles
                # Headway = Gap / Speed
                if speed > 0:
                    headway_time = round((gap_distance / speed) * 3.6, 2)  # Convert to seconds
                else:
                    headway_time = 10.0
                
                # Average vehicle length: meters (typical car ~4.5m)
                vehicle_length = round(random.uniform(4.0, 5.5), 2)
                
                # Create GeoJSON location
                location = f'{{"type":"Point","coordinates":[{row["origin_lon"]},{row["origin_lat"]}]}}'
                
                # Insert record with all calculated values
                cursor.execute(insert_query, (
                    record_id,
                    row['segment_id'],
                    timestamp,
                    timestamp,
                    speed,
                    intensity,
                    occupancy,
                    is_congested,
                    gap_distance,
                    headway_time,
                    vehicle_length,
                    'forward',
                    'car',
                    location,
                    'Synthetic Data Generator',
                    'Generated from realistic patterns',
                    datetime.now(),
                    datetime.now()
                ))
                
                total_imported += 1
                
                # Progress update
                if total_imported % 500 == 0:
                    progress = (total_imported / len(df)) * 100
                    print(f"  ⏳ Progress: {total_imported}/{len(df)} ({progress:.1f}%)")
                
            except Exception as e:
                errors += 1
                if errors < 10:  # Only print first 10 errors
                    print(f"  ❌ Error at row {idx}: {e}")
        
        # Commit batch
        conn.commit()
    
    print()
    print("=" * 70)
    print("📊 IMPORT SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully imported: {total_imported} records")
    print(f"❌ Errors: {errors}")
    print(f"📈 Success rate: {(total_imported / len(df) * 100):.2f}%")
    print("=" * 70)
    print()
    
    # Verify data
    print("🔍 Verifying imported data...")
    cursor.execute("SELECT COUNT(*) FROM TrafficFlowObserved")
    count = cursor.fetchone()[0]
    print(f"✅ Total records in database: {count}")
    print()
    
    # Show sample
    print("📋 Sample data from database:")
    cursor.execute("""
        SELECT TOP 5 
            ID, 
            RefRoadSegment, 
            AverageVehicleSpeed, 
            Congested,
            DateObservedFrom
        FROM TrafficFlowObserved 
        ORDER BY DateObservedFrom DESC
    """)
    
    for row in cursor.fetchall():
        status = "🔴 CONGESTED" if row[3] else "🟢 FLOWING"
        print(f"  {row[1]} | {row[2]:.2f} km/h | {status} | {row[4]}")
    
    print()
    print("✅ Import completed successfully!")
    print()
    print("📊 Next steps:")
    print("  1. Verify data: SELECT * FROM TrafficFlowObserved")
    print("  2. Start ML model training")
    print("  3. Build prediction APIs")
    
    # Close connection
    cursor.close()
    conn.close()


def main():
    """Main function"""
    csv_file = "synthetic_traffic_data.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        print("Please run generate_synthetic_traffic_data.py first.")
        return
    
    try:
        import_traffic_data(csv_file)
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
