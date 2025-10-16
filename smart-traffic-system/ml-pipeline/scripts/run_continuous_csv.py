"""
Continuous Traffic Collection - 3 days, every 5 minutes
Save to CSV file for later import
"""

import time
import schedule
import subprocess
from datetime import datetime, timedelta
import os

# Configuration
COLLECTION_INTERVAL_MINUTES = 5
COLLECTION_DURATION_DAYS = 3
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "collect_to_csv.py")

def run_collection():
    """Run traffic collection once"""
    print("\n" + "=" * 70)
    print(f"🔄 Collection at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ["python3", SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Collection failed!")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Collection timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main continuous collection loop"""
    print("=" * 70)
    print("🚗 CONTINUOUS TRAFFIC DATA COLLECTION (CSV)")
    print("=" * 70)
    print(f"📅 Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    end_time = datetime.now() + timedelta(days=COLLECTION_DURATION_DAYS)
    print(f"📅 End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Interval: Every {COLLECTION_INTERVAL_MINUTES} minutes")
    
    # Calculate expected records
    intervals_per_day = (24 * 60) // COLLECTION_INTERVAL_MINUTES
    total_records = 10 * intervals_per_day * COLLECTION_DURATION_DAYS
    print(f"📊 Expected: {total_records} records ({10} segments × {intervals_per_day}/day × {COLLECTION_DURATION_DAYS} days)")
    print("=" * 70)
    
    print("\n⚠️  IMPORTANT:")
    print("  - Keep this terminal open")
    print("  - Don't close the VM connection")
    print("  - Press Ctrl+C to stop")
    print("  - Data saved to: ./data/traffic_data.csv")
    print()
    
    # Schedule collection
    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(run_collection)
    
    # Run first collection immediately
    print("🚀 Running first collection now...")
    run_collection()
    
    collection_count = 1
    
    # Keep running until end time
    try:
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
            
            # Print progress every hour
            if datetime.now().minute == 0:
                remaining = end_time - datetime.now()
                hours_remaining = remaining.total_seconds() / 3600
                print(f"\n📊 Progress: {collection_count} collections | {hours_remaining:.1f} hours remaining")
        
        print("\n" + "=" * 70)
        print("🎉 3-DAY COLLECTION COMPLETED!")
        print("=" * 70)
        print(f"✅ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Data file: ./data/traffic_data.csv")
        print("\n📋 Next Steps:")
        print("  1. Download CSV: Use 'DOWNLOAD FILE' button in SSH window")
        print("  2. Import to SQL Server using provided script")
        print("  3. Start ML model training")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection stopped by user")
        print(f"⏱️  Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Completed: {collection_count} collections")
        print(f"📁 Partial data saved in: ./data/traffic_data.csv")


if __name__ == "__main__":
    main()
