"""
Test ML-integrated Traffic API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/traffic"


def test_models_info():
    """Test model info endpoint"""
    print("="*80)
    print("🤖 TEST 1: Model Info")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/models/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, default=str))
    print()


def test_current_traffic():
    """Test current traffic endpoint"""
    print("="*80)
    print("📊 TEST 2: Current Traffic")
    print("="*80)
    
    segment_id = "segment_001"
    response = requests.get(f"{BASE_URL}/current/{segment_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Segment: {data['road_segment_id']}")
        print(f"Road Name: {data.get('road_name', 'N/A')}")
        print(f"Speed: {data['speed']} km/h")
        print(f"Intensity: {data['intensity']} veh/h")
        print(f"Occupancy: {data['occupancy']:.2f}")
        print(f"Status: {data['congestion_status']}")
        print(f"Congestion Probability: {data.get('congestion_probability', 'N/A')}")
    else:
        print(f"Error: {response.text}")
    print()


def test_predict_traffic():
    """Test ML prediction endpoint"""
    print("="*80)
    print("🔮 TEST 3: ML Prediction")
    print("="*80)
    
    payload = {
        "road_segment_id": "segment_001",
        "prediction_horizon": 15,
        "model_type": "ensemble"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Segment: {data['road_segment_id']}")
        print(f"Model Used: {data['model_used']}")
        print(f"ML Loaded: {data['metadata']['ml_models_loaded']}")
        print(f"\nPredictions:")
        
        for pred in data['predictions']:
            print(f"  Time: {pred['timestamp']}")
            print(f"  Speed: {pred['predicted_speed']} km/h")
            print(f"  Status: {pred['congestion_status']}")
            print(f"  Congestion Prob: {pred['congestion_probability']*100:.1f}%")
            print(f"  Confidence: [{pred['confidence_lower']:.2f}, {pred['confidence_upper']:.2f}] km/h")
            print()
    else:
        print(f"Error: {response.text}")
    print()


def test_predict_future():
    """Test future prediction (Prophet)"""
    print("="*80)
    print("📈 TEST 4: Future Prediction (Prophet)")
    print("="*80)
    
    payload = {
        "road_segment_id": "segment_001",
        "prediction_horizon": 60,  # 60 minutes ahead
        "model_type": "ensemble"
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Segment: {data['road_segment_id']}")
        print(f"Number of Predictions: {len(data['predictions'])}")
        print(f"\nFuture Traffic:")
        
        for i, pred in enumerate(data['predictions'], 1):
            print(f"\n  [{i}] {pred['timestamp']}")
            print(f"      Speed: {pred['predicted_speed']} km/h")
            print(f"      Status: {pred['congestion_status']}")
            print(f"      Congestion: {pred['congestion_probability']*100:.1f}%")
    else:
        print(f"Error: {response.text}")
    print()


def test_all_traffic():
    """Test all traffic segments"""
    print("="*80)
    print("🗺️ TEST 5: All Traffic Segments")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/realtime/all?limit=10")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Segments: {data['count']}")
        print(f"Timestamp: {data['timestamp']}")
        print(f"\nSegments:")
        
        for seg in data['data'][:5]:  # Show first 5
            status_emoji = {
                'FREE_FLOW': '🟢',
                'MODERATE': '🟡',
                'HEAVY_CONGESTION': '🔴'
            }.get(seg['congestion_status'], '⚪')
            
            print(f"\n  {status_emoji} {seg['road_segment_id']} - {seg['road_name']}")
            print(f"     Speed: {seg['speed']:.1f} km/h | Intensity: {seg['intensity']:.0f} veh/h")
            print(f"     Status: {seg['congestion_status']} ({seg['congestion_probability']*100:.0f}%)")
    else:
        print(f"Error: {response.text}")
    print()


def test_history():
    """Test traffic history"""
    print("="*80)
    print("📊 TEST 6: Traffic History")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/history/segment_001?limit=10")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Segment: {data['road_segment_id']}")
        print(f"Total Records: {data['total_records']}")
        print(f"Date Range: {data['start_date']} to {data['end_date']}")
        print(f"\nRecent History:")
        
        for record in data['data'][:5]:  # Show first 5
            congested = "🔴 CONGESTED" if record['congested'] else "🟢 FLOWING"
            print(f"  {record['timestamp']} | {record['speed']:.1f} km/h | {congested}")
    else:
        print(f"Error: {response.text}")
    print()


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 TESTING ML-INTEGRATED TRAFFIC API")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print("="*80 + "\n")
    
    try:
        # Test 1: Model Info
        test_models_info()
        
        # Test 2: Current Traffic
        test_current_traffic()
        
        # Test 3: ML Prediction
        test_predict_traffic()
        
        # Test 4: Future Prediction
        test_predict_future()
        
        # Test 5: All Traffic
        test_all_traffic()
        
        # Test 6: History
        test_history()
        
        print("="*80)
        print("✅ ALL TESTS COMPLETED!")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure FastAPI server is running:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
