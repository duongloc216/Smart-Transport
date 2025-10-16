"""
Update Traffic Data with Intensity and Occupancy
Tính toán và cập nhật intensity + occupancy vào database
"""

import pyodbc
import random
from datetime import datetime

def get_db_connection():
    """Create database connection"""
    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\MSSQLSERVER02;"
        "DATABASE=SmartTrafficDB;"
        "UID=locdt;"
        "PWD=locdt"
    )
    return pyodbc.connect(connection_string)


def calculate_intensity_occupancy(speed, max_speed, total_lanes, is_congested):
    """
    Tính intensity và occupancy dựa trên speed
    
    Công thức:
    - Intensity (xe/giờ): Số lượng xe đi qua mỗi giờ
    - Occupancy (%): Tỷ lệ đường đang được sử dụng
    
    Args:
        speed: Tốc độ thực tế (km/h)
        max_speed: Tốc độ tối đa (km/h)
        total_lanes: Số làn đường
        is_congested: Có tắc đường không
    
    Returns:
        (intensity, occupancy)
    """
    
    # Capacity per lane (vehicles/hour) - Based on traffic engineering standards
    # Highway: 2000-2400 veh/h/lane
    # Urban roads: 1500-1800 veh/h/lane
    base_capacity_per_lane = 1800  # vehicles/hour/lane
    
    # Total road capacity
    total_capacity = base_capacity_per_lane * total_lanes
    
    # Calculate speed ratio
    speed_ratio = speed / max_speed if max_speed > 0 else 0.5
    speed_ratio = max(0.1, min(1.0, speed_ratio))  # Clamp between 0.1 and 1.0
    
    # Intensity calculation
    # Logic: Khi tốc độ giảm → intensity tăng (nhiều xe hơn)
    if is_congested:
        # Congested: High intensity (70-95% capacity)
        intensity_ratio = 0.7 + (1.0 - speed_ratio) * 0.25
    else:
        # Free flow: Medium intensity (30-70% capacity)
        intensity_ratio = 0.3 + speed_ratio * 0.4
    
    # Add some random variation (-10% to +10%)
    variation = random.uniform(-0.1, 0.1)
    intensity_ratio = max(0.2, min(1.0, intensity_ratio + variation))
    
    intensity = int(total_capacity * intensity_ratio)
    
    # Occupancy calculation (0-1 ratio) for DECIMAL(5,4)
    # Occupancy = actual intensity / capacity
    occupancy = intensity / total_capacity
    
    # Add realism: occupancy typically 0.20-0.85 in practice
    occupancy = max(0.15, min(0.85, occupancy))
    
    return intensity, round(occupancy, 4)


def update_traffic_data():
    """Update all traffic records with intensity and occupancy"""
    
    print("=" * 80)
    print("📊 UPDATE TRAFFIC DATA WITH INTENSITY & OCCUPANCY")
    print("=" * 80)
    print()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get road segment info (for lanes and max speed)
    print("📂 Loading road segment information...")
    cursor.execute("""
        SELECT ID, TotalLaneNumber, MaximumAllowedSpeed
        FROM RoadSegment
    """)
    
    segments_info = {}
    for row in cursor.fetchall():
        segments_info[row[0]] = {
            'lanes': row[1] if row[1] else 4,  # Default 4 lanes
            'max_speed': float(row[2]) if row[2] else 40.0  # Default 40 km/h
        }
    
    print(f"✅ Loaded {len(segments_info)} road segments")
    print()
    
    # Get all traffic records
    print("📊 Loading traffic records...")
    cursor.execute("""
        SELECT 
            ID,
            RefRoadSegment,
            AverageVehicleSpeed,
            Congested
        FROM TrafficFlowObserved
        WHERE Intensity IS NULL
    """)
    
    records = cursor.fetchall()
    total_records = len(records)
    
    print(f"✅ Found {total_records} records to update")
    print()
    
    if total_records == 0:
        print("⚠️  No records need updating")
        conn.close()
        return
    
    # Update records in batches
    print("🔄 Updating records with intensity and occupancy...")
    print()
    
    update_query = """
        UPDATE TrafficFlowObserved
        SET 
            Intensity = ?,
            Occupancy = ?,
            DateModified = ?
        WHERE ID = ?
    """
    
    updated_count = 0
    batch_size = 100
    
    for i, record in enumerate(records):
        record_id = record[0]
        segment_id = record[1]
        speed = float(record[2]) if record[2] else 20.0
        is_congested = bool(record[3])
        
        # Get segment info
        segment_info = segments_info.get(segment_id, {'lanes': 4, 'max_speed': 40.0})
        
        # Calculate intensity and occupancy
        intensity, occupancy = calculate_intensity_occupancy(
            speed,
            segment_info['max_speed'],
            segment_info['lanes'],
            is_congested
        )
        
        # Update record
        try:
            cursor.execute(update_query, (
                intensity,
                occupancy,
                datetime.now(),
                record_id
            ))
            updated_count += 1
            
            # Progress update
            if (i + 1) % 500 == 0:
                progress = ((i + 1) / total_records) * 100
                print(f"  ⏳ Progress: {i + 1}/{total_records} ({progress:.1f}%)")
                conn.commit()  # Commit batch
                
        except Exception as e:
            print(f"  ❌ Error updating {record_id}: {e}")
    
    # Final commit
    conn.commit()
    
    print()
    print("=" * 80)
    print("📊 UPDATE SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully updated: {updated_count} records")
    print(f"📈 Success rate: {(updated_count / total_records * 100):.2f}%")
    print("=" * 80)
    print()
    
    # Verify and show statistics
    print("🔍 Verifying updated data...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(Intensity) as avg_intensity,
            MIN(Intensity) as min_intensity,
            MAX(Intensity) as max_intensity,
            AVG(Occupancy) as avg_occupancy,
            MIN(Occupancy) as min_occupancy,
            MAX(Occupancy) as max_occupancy
        FROM TrafficFlowObserved
        WHERE Intensity IS NOT NULL
    """)
    
    stats = cursor.fetchone()
    
    print()
    print("📈 UPDATED DATA STATISTICS:")
    print(f"  Total Records: {stats[0]}")
    print(f"\n  Intensity (vehicles/hour):")
    print(f"    Average: {stats[1]:.0f}")
    print(f"    Range: {stats[2]:.0f} - {stats[3]:.0f}")
    print(f"\n  Occupancy (%):")
    print(f"    Average: {stats[4]:.2f}%")
    print(f"    Range: {stats[5]:.2f}% - {stats[6]:.2f}%")
    print()
    
    # Show sample records
    print("📋 Sample updated records:")
    cursor.execute("""
        SELECT TOP 5
            RefRoadSegment,
            AverageVehicleSpeed,
            Intensity,
            Occupancy,
            Congested
        FROM TrafficFlowObserved
        ORDER BY DateModified DESC
    """)
    
    for row in cursor.fetchall():
        status = "🔴 CONGESTED" if row[4] else "🟢 FLOWING"
        print(f"  {row[0]} | {row[1]:.1f} km/h | {row[2]} veh/h | {row[3]:.1f}% | {status}")
    
    print()
    print("✅ Update completed successfully!")
    print()
    print("📊 Next steps:")
    print("  1. Verify data: SELECT * FROM TrafficFlowObserved")
    print("  2. Start ML model training")
    print("  3. Build prediction APIs")
    
    conn.close()


def main():
    """Main function"""
    try:
        update_traffic_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
