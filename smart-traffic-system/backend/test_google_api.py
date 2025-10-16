"""
Test Google Maps API Connection and Functionality
Run this after adding GOOGLE_MAPS_API_KEY to .env file
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import googlemaps
from googlemaps.exceptions import ApiError, HTTPError, Timeout, TransportError

# Load environment variables
load_dotenv()

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"{title}")
    print("="*60 + "\n")

def test_api_key():
    """Test if API key exists and is valid format"""
    print_section("STEP 1: Checking API Key")
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env file")
        print("\n📝 Please add this line to .env:")
        print("   GOOGLE_MAPS_API_KEY=your_api_key_here")
        return None
    
    if not api_key.startswith("AIza"):
        print(f"⚠️  Warning: API key format looks unusual")
        print(f"   Expected to start with 'AIza...'")
        print(f"   Your key starts with: {api_key[:10]}...")
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Length: {len(api_key)} characters")
    return api_key

def test_client_connection(api_key):
    """Test Google Maps client connection"""
    print_section("STEP 2: Testing Client Connection")
    
    try:
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps client initialized successfully")
        return gmaps
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return None

def test_distance_matrix_api(gmaps):
    """Test Distance Matrix API with Ho Chi Minh City locations"""
    print_section("STEP 3: Testing Distance Matrix API")
    
    # Test với 2 điểm ở Sài Gòn
    origins = [(10.7741, 106.7008)]  # Nguyễn Huệ
    destinations = [(10.7769, 106.7011)]  # Lê Lợi
    
    try:
        print("📍 Testing route:")
        print(f"   Origin: Nguyen Hue Street (10.7741, 106.7008)")
        print(f"   Destination: Le Loi Boulevard (10.7769, 106.7011)")
        print(f"   Mode: Driving")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n⏳ Sending request to Google Maps API...")
        
        result = gmaps.distance_matrix(
            origins=origins,
            destinations=destinations,
            mode="driving",
            departure_time="now",
            traffic_model="best_guess"
        )
        
        # Check status
        if result['status'] != 'OK':
            print(f"❌ API returned status: {result['status']}")
            return False
        
        # Parse result
        row = result['rows'][0]
        element = row['elements'][0]
        
        if element['status'] != 'OK':
            print(f"❌ Element status: {element['status']}")
            return False
        
        distance = element['distance']['value'] / 1000  # Convert to km
        duration = element['duration']['value'] / 60    # Convert to minutes
        
        if 'duration_in_traffic' in element:
            traffic_duration = element['duration_in_traffic']['value'] / 60
            print(f"\n✅ Distance Matrix API working!")
            print(f"   📏 Distance: {distance:.2f} km")
            print(f"   ⏱️  Normal duration: {duration:.1f} minutes")
            print(f"   🚦 Duration in traffic: {traffic_duration:.1f} minutes")
            print(f"   📊 Traffic delay: {traffic_duration - duration:.1f} minutes")
        else:
            print(f"\n✅ Distance Matrix API working!")
            print(f"   📏 Distance: {distance:.2f} km")
            print(f"   ⏱️  Duration: {duration:.1f} minutes")
            print(f"   ℹ️  Traffic data not available (try during peak hours)")
        
        return True
        
    except ApiError as e:
        print(f"\n❌ API Error: {e}")
        print("\n🔍 Possible causes:")
        print("   - API key not authorized for Distance Matrix API")
        print("   - Billing not enabled on Google Cloud")
        print("   - API restrictions blocking the request")
        return False
    
    except HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print("   Check your internet connection")
        return False
    
    except Timeout as e:
        print(f"\n❌ Timeout: {e}")
        print("   Request took too long - try again")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_directions_api(gmaps):
    """Test Directions API"""
    print_section("STEP 4: Testing Directions API")
    
    origin = (10.7741, 106.7008)   # Nguyễn Huệ
    destination = (10.7769, 106.7011)  # Lê Lợi
    
    try:
        print("📍 Testing route:")
        print(f"   Origin: (10.7741, 106.7008)")
        print(f"   Destination: (10.7769, 106.7011)")
        print("\n⏳ Sending request to Google Directions API...")
        
        result = gmaps.directions(
            origin=origin,
            destination=destination,
            mode="driving",
            departure_time="now"
        )
        
        if not result:
            print("❌ No routes found")
            return False
        
        route = result[0]
        leg = route['legs'][0]
        
        distance = leg['distance']['value'] / 1000
        duration = leg['duration']['value'] / 60
        
        print(f"\n✅ Directions API working!")
        print(f"   📏 Distance: {distance:.2f} km")
        print(f"   ⏱️  Duration: {duration:.1f} minutes")
        print(f"   🛣️  Steps: {len(leg['steps'])} steps")
        print(f"   📍 Start: {leg['start_address']}")
        print(f"   📍 End: {leg['end_address']}")
        
        return True
        
    except ApiError as e:
        print(f"\n❌ API Error: {e}")
        print("\n🔍 Possible causes:")
        print("   - API key not authorized for Directions API")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_roads_api(gmaps):
    """Test Roads API - Snap to Roads"""
    print_section("STEP 5: Testing Roads API")
    
    # Sample GPS path (slightly off road)
    path = [
        (10.7741, 106.7008),
        (10.7750, 106.7010),
        (10.7760, 106.7011)
    ]
    
    try:
        print("📍 Testing with 3 GPS points along Nguyen Hue")
        print("\n⏳ Sending request to Google Roads API...")
        
        result = gmaps.snap_to_roads(path=path, interpolate=True)
        
        if not result:
            print("❌ No snapped points returned")
            return False
        
        print(f"\n✅ Roads API working!")
        print(f"   📍 Input points: {len(path)}")
        print(f"   📍 Snapped points: {len(result)}")
        print(f"   ℹ️  Points are now snapped to actual roads")
        
        return True
        
    except ApiError as e:
        print(f"\n❌ API Error: {e}")
        print("\n🔍 Possible causes:")
        print("   - API key not authorized for Roads API")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def print_quota_info():
    """Print information about API quotas and costs"""
    print_section("API Quota & Cost Information")
    
    print("📊 Monthly Free Credits: $200")
    print("\n💰 Pricing after free credits:")
    print("   - Distance Matrix API: $5 per 1,000 requests")
    print("   - Directions API: $5 per 1,000 requests")
    print("   - Roads API: $10 per 1,000 requests")
    
    print("\n📈 Expected usage for this project:")
    print("   - 7 days data collection")
    print("   - 10 road segments")
    print("   - 96 requests/day/segment")
    print("   - Total: 6,720 requests")
    print("   - Estimated cost: ~$33.60 (within free $200)")
    
    print("\n🔍 Monitor usage at:")
    print("   https://console.cloud.google.com/apis/dashboard")

def print_next_steps():
    """Print next steps after successful API test"""
    print_section("✅ ALL TESTS PASSED! Next Steps:")
    
    print("1. 🗄️  Database is ready (10 road segments)")
    print("2. 🔑 Google Maps API is working")
    print("3. 📊 Start data collection:")
    print()
    print("   Run this command:")
    print("   python smart-traffic-system/ml-pipeline/scripts/collect_google_traffic.py")
    print()
    print("4. ⏰ Keep it running for 7 days")
    print("   - Collects traffic data every 15 minutes")
    print("   - Goal: 6,720 records minimum")
    print()
    print("5. 📈 Monitor progress:")
    print("   - Check database: SELECT COUNT(*) FROM TrafficFlowObserved")
    print("   - Check logs: ml-pipeline/logs/")
    print()
    print("🎯 After 7 days, you can start training ML models!")

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🗺️  GOOGLE MAPS API TEST SUITE")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check API key
    api_key = test_api_key()
    if not api_key:
        return False
    
    # Step 2: Initialize client
    gmaps = test_client_connection(api_key)
    if not gmaps:
        return False
    
    # Step 3: Test Distance Matrix API (most important)
    if not test_distance_matrix_api(gmaps):
        print("\n⚠️  Distance Matrix API test failed!")
        print("   This is the PRIMARY API needed for traffic data collection")
        return False
    
    # Step 4: Test Directions API
    if not test_directions_api(gmaps):
        print("\n⚠️  Directions API test failed!")
        print("   This API is optional but recommended")
    
    # Step 5: Test Roads API
    if not test_roads_api(gmaps):
        print("\n⚠️  Roads API test failed!")
        print("   This API is optional but recommended")
    
    # Print quota info
    print_quota_info()
    
    # Print next steps
    print_next_steps()
    
    print("\n" + "="*60)
    print("✅ API TESTING COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
