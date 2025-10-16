"""
Export traffic data from SQL Server to CSV for Google Colab training
"""

import pyodbc
import pandas as pd
from datetime import datetime
import os

# Database connection
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=localhost\\MSSQLSERVER02;'
        'DATABASE=SmartTrafficDB;'
        'UID=locdt;'
        'PWD=locdt'
    )

def export_traffic_data():
    """
    Export all traffic data with road segment info for ML training
    """
    print("=" * 80)
    print("📤 EXPORTING TRAFFIC DATA FOR ML TRAINING")
    print("=" * 80)
    print()
    
    conn = get_db_connection()
    
    # Query: Join TrafficFlowObserved + RoadSegment
    query = """
    SELECT 
        t.ID,
        t.RefRoadSegment,
        t.DateObservedFrom,
        t.DateObservedTo,
        t.AverageVehicleSpeed,
        t.Intensity,
        t.Occupancy,
        t.Congested,
        t.LaneDirection,
        t.VehicleType,
        r.TotalLaneNumber,
        r.MaximumAllowedSpeed,
        r.RoadClass,
        t.DateCreated
    FROM TrafficFlowObserved t
    LEFT JOIN RoadSegment r ON t.RefRoadSegment = r.ID
    ORDER BY t.DateObservedFrom
    """
    
    print("📊 Loading data from database...")
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"✅ Loaded {len(df)} records")
    print()
    
    # Data info
    print("📋 DATA SUMMARY:")
    print(f"  Segments: {df['RefRoadSegment'].nunique()}")
    print(f"  Date range: {df['DateObservedFrom'].min()} → {df['DateObservedFrom'].max()}")
    print(f"  Records: {len(df)}")
    print()
    
    # Check for nulls
    print("🔍 NULL VALUES:")
    null_counts = df.isnull().sum()
    for col, count in null_counts[null_counts > 0].items():
        print(f"  {col}: {count} ({count/len(df)*100:.1f}%)")
    print()
    
    # Save to CSV
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'traffic_data_for_training.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("=" * 80)
    print("✅ EXPORT COMPLETED!")
    print("=" * 80)
    print(f"📁 File saved: {output_file}")
    print(f"📏 File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print()
    print("📋 NEXT STEPS:")
    print("  1. Upload file to Google Drive:")
    print(f"     {output_file}")
    print("  2. Open Google Colab notebook")
    print("  3. Run training cells")
    print("  4. Download trained models")
    print()
    
    return output_file

if __name__ == "__main__":
    export_traffic_data()
