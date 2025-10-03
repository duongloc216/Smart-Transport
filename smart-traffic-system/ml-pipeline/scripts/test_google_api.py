"""
Test Google Maps API key and connectivity.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env')
load_dotenv(env_path)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def test_api_key_format():
    """Test if API key exists and has correct format."""
    print("\n🔍 Testing API Key Format...")
    
    if not GOOGLE_MAPS_API_KEY:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY not found in .env file")
        print("   Please add: GOOGLE_MAPS_API_KEY=your_key_here")
        return False
    
    if len(GOOGLE_MAPS_API_KEY) < 39:
        print(f"⚠️  WARNING: API key seems too short (length: {len(GOOGLE_MAPS_API_KEY)})")
        print(f"   Expected format: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        return False
    
    if not GOOGLE_MAPS_API_KEY.startswith("AIza"):
        print(f"⚠️  WARNING: API key doesn't start with 'AIza'")
        print(f"   Current: {GOOGLE_MAPS_API_KEY[:10]}...")
    
    print(f"✅ API Key found: {GOOGLE_MAPS_API_KEY[:10]}...{GOOGLE_MAPS_API_KEY[-4:]}")
    return True

def test_distance_matrix_api():
    """Test Distance Matrix API with a simple request."""
    print("\n🌐 Testing Distance Matrix API...")
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": "21.0285,105.8542",  # Hanoi center
        "destinations": "21.0315,105.8571",  # Nearby point
        "departure_time": "now",
        "traffic_model": "best_guess",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"   Response: {data}")
            return False
        
        if data.get("status") == "REQUEST_DENIED":
            print(f"❌ API Request Denied")
            print(f"   Error: {data.get('error_message', 'Unknown error')}")
            print("\n   Possible causes:")
            print("   1. API key not valid")
            print("   2. Distance Matrix API not enabled")
            print("   3. Billing not enabled")
            print("   4. API key restrictions (IP/referrer)")
            return False
        
        if data.get("status") == "OVER_QUERY_LIMIT":
            print(f"❌ Query Limit Exceeded")
            print(f"   You've exceeded your quota for this API")
            return False
        
        if data.get("status") != "OK":
            print(f"❌ API returned status: {data.get('status')}")
            print(f"   Response: {data}")
            return False
        
        # Extract traffic data
        rows = data.get("rows", [])
        if not rows:
            print(f"❌ No data returned")
            return False
        
        elements = rows[0].get("elements", [])
        if not elements:
            print(f"❌ No route elements returned")
            return False
        
        element = elements[0]
        if element.get("status") != "OK":
            print(f"❌ Route status: {element.get('status')}")
            return False
        
        distance = element.get("distance", {}).get("value")  # meters
        duration = element.get("duration", {}).get("value")  # seconds
        duration_traffic = element.get("duration_in_traffic", {}).get("value")  # seconds
        
        if distance and duration_traffic:
            speed_kmh = (distance / duration_traffic) * 3.6
            print(f"✅ Distance Matrix API working!")
            print(f"   Distance: {distance} meters")
            print(f"   Duration (normal): {duration} seconds")
            print(f"   Duration (traffic): {duration_traffic} seconds")
            print(f"   Current speed: {speed_kmh:.1f} km/h")
            
            if duration_traffic > duration * 1.3:
                print(f"   🚦 Traffic detected: {((duration_traffic/duration - 1) * 100):.0f}% slower")
            else:
                print(f"   🟢 Traffic normal")
            
            return True
        else:
            print(f"❌ Missing traffic data in response")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (>10 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_roads_api():
    """Test Roads API with a simple snap request."""
    print("\n🛣️  Testing Roads API...")
    
    url = "https://roads.googleapis.com/v1/snapToRoads"
    params = {
        "path": "21.0285,105.8542|21.0295,105.8552|21.0305,105.8562",
        "interpolate": "true",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"   Response: {data}")
            return False
        
        if "error" in data:
            error_message = data["error"].get("message", "Unknown error")
            print(f"❌ API Error: {error_message}")
            return False
        
        snapped_points = data.get("snappedPoints", [])
        if not snapped_points:
            print(f"⚠️  No snapped points returned (API works but no roads found)")
            return True
        
        print(f"✅ Roads API working!")
        print(f"   Snapped {len(snapped_points)} points to roads")
        print(f"   First point: {snapped_points[0].get('location')}")
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (>10 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_quota_info():
    """Display quota and billing information."""
    print("\n📊 API Quota Information:")
    print("=" * 50)
    print("FREE TIER ($200 credit/month):")
    print("  • Distance Matrix API: $5/1000 requests")
    print("    → 40,000 requests/month FREE")
    print("    → ~1,330 requests/day")
    print()
    print("  • Roads API: $10/1000 requests")
    print("    → 20,000 requests/month FREE")
    print("    → ~660 requests/day")
    print()
    print("RECOMMENDATIONS:")
    print("  • Collect traffic every 15 minutes")
    print("  • Max ~40 road segments for free tier")
    print("  • Monitor usage at console.cloud.google.com")
    print("=" * 50)

def main():
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("🧪 GOOGLE MAPS API TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: API Key format
    results.append(("API Key Format", test_api_key_format()))
    
    if not results[0][1]:
        print("\n❌ FAILED: Fix API key before continuing")
        sys.exit(1)
    
    # Test 2: Distance Matrix API
    results.append(("Distance Matrix API", test_distance_matrix_api()))
    
    # Test 3: Roads API
    results.append(("Roads API", test_roads_api()))
    
    # Display quota info
    test_quota_info()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("   You can now collect real traffic data!")
        print("\n   Next step:")
        print("   python collect_google_traffic.py")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("   Please check the errors above and:")
        print("   1. Verify API key in .env file")
        print("   2. Enable required APIs in Google Cloud Console")
        print("   3. Enable billing (required for Google Maps APIs)")
        print("   4. Check API key restrictions")
    
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
