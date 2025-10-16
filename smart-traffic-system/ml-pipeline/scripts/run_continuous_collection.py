"""
Continuous Traffic Data Collection
Runs every 15 minutes for 7 days
"""

import time
import schedule
import subprocess
from datetime import datetime, timedelta
import os

# Configuration
COLLECTION_INTERVAL_MINUTES = 15
COLLECTION_DURATION_DAYS = 7
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "collect_traffic_simple.py")

def run_collection():
    """Run traffic collection once"""
    print("\n" + "=" * 70)
    print(f"🔄 Starting collection at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Run the collection script
        result = subprocess.run(
            ["python", SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Collection completed successfully")
            # Print output
            print(result.stdout)
        else:
            print("❌ Collection failed!")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Collection timed out (took more than 5 minutes)")
    except Exception as e:
        print(f"❌ Error running collection: {e}")
    
    print("=" * 70)


def main():
    """Main continuous collection loop"""
    print("=" * 70)
    print("🚗 CONTINUOUS TRAFFIC DATA COLLECTION")
    print("=" * 70)
    print(f"📅 Start Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 End Date: {(datetime.now() + timedelta(days=COLLECTION_DURATION_DAYS)).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Interval: Every {COLLECTION_INTERVAL_MINUTES} minutes")
    print(f"📊 Expected Records: {10 * (24 * 60 // COLLECTION_INTERVAL_MINUTES) * COLLECTION_DURATION_DAYS}")
    print("=" * 70)
    print("\n⚠️  IMPORTANT:")
    print("  - Keep this window open")
    print("  - Keep your computer running")
    print("  - Don't close this program")
    print("  - Press Ctrl+C to stop\n")
    
    # Calculate end time
    end_time = datetime.now() + timedelta(days=COLLECTION_DURATION_DAYS)
    
    # Schedule collection every X minutes
    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(run_collection)
    
    # Run first collection immediately
    print("🚀 Running first collection now...")
    run_collection()
    
    # Keep running until end time
    try:
        while datetime.now() < end_time:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
            # Show progress
            remaining = end_time - datetime.now()
            hours_remaining = remaining.total_seconds() / 3600
            
            if datetime.now().minute % 30 == 0:  # Print every 30 minutes
                print(f"\n⏳ Time remaining: {hours_remaining:.1f} hours")
                print(f"📊 Next collection in: {schedule.idle_seconds() // 60:.0f} minutes")
        
        print("\n" + "=" * 70)
        print("🎉 7-DAY COLLECTION COMPLETED!")
        print("=" * 70)
        print(f"✅ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Next Steps:")
        print("  1. Check database: SELECT COUNT(*) FROM TrafficFlowObserved")
        print("  2. Start ML model training")
        print("  3. Build prediction APIs")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection stopped by user")
        print(f"⏱️  Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 To check collected data:")
        print("  SELECT COUNT(*) FROM TrafficFlowObserved")


if __name__ == "__main__":
    main()
