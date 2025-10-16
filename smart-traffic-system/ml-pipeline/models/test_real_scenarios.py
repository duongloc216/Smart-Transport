"""
Test models với các scenarios thực tế
"""

from model_loader import TrafficPredictor
import pandas as pd

def test_scenarios():
    """
    Test models với 5 scenarios thực tế HCMC
    """
    
    predictor = TrafficPredictor()
    
    print("=" * 80)
    print("🧪 TESTING REAL-WORLD SCENARIOS")
    print("=" * 80)
    
    # Định nghĩa base features cho segment_001
    base_features = {
        'TotalLaneNumber': 4,
        'MaximumAllowedSpeed': 40,
        'day_of_week': 3,  # Thursday
        'speed_baseline': 25.0,
        # Segment encoding (segment_001 active)
        'segment_segment_001': 1,
        'segment_segment_002': 0,
        'segment_segment_003': 0,
        'segment_segment_004': 0,
        'segment_segment_005': 0,
        'segment_segment_006': 0,
        'segment_segment_007': 0,
        'segment_segment_008': 0,
        'segment_segment_009': 0,
        'segment_segment_010': 0
    }
    
    scenarios = [
        {
            'name': '🌅 Rush Hour Sáng (7:30 AM)',
            'features': {
                **base_features,
                'hour': 7,
                'is_rush_hour': 1,
                'is_weekend': 0,
                'Intensity': 8500,
                'Occupancy': 0.78,
                'speed_lag_1': 12.5,
                'speed_lag_2': 13.2,
                'speed_lag_3': 14.8,
                'intensity_lag_1': 8200,
                'speed_rolling_mean_6': 13.5,
                'speed_rolling_mean_12': 15.2,
                'speed_rolling_std_6': 2.3,
                'intensity_rolling_mean_6': 8000,
                'speed_diff': -1.5,
                'intensity_diff': 500,
                'speed_to_max_ratio': 0.31
            },
            'expected': 'Kẹt xe nặng, tốc độ ~12-15 km/h'
        },
        {
            'name': '🌆 Rush Hour Chiều (17:30 PM)',
            'features': {
                **base_features,
                'hour': 17,
                'is_rush_hour': 1,
                'is_weekend': 0,
                'Intensity': 9200,
                'Occupancy': 0.82,
                'speed_lag_1': 10.2,
                'speed_lag_2': 11.5,
                'speed_lag_3': 12.1,
                'intensity_lag_1': 9000,
                'speed_rolling_mean_6': 11.3,
                'speed_rolling_mean_12': 13.8,
                'speed_rolling_std_6': 1.8,
                'intensity_rolling_mean_6': 8800,
                'speed_diff': -1.3,
                'intensity_diff': 600,
                'speed_to_max_ratio': 0.26
            },
            'expected': 'Kẹt xe CỰC NẶNG, tốc độ ~10-12 km/h'
        },
        {
            'name': '☀️ Giờ Hành Chính (10:00 AM)',
            'features': {
                **base_features,
                'hour': 10,
                'is_rush_hour': 0,
                'is_weekend': 0,
                'Intensity': 5500,
                'Occupancy': 0.52,
                'speed_lag_1': 28.5,
                'speed_lag_2': 27.8,
                'speed_lag_3': 29.2,
                'intensity_lag_1': 5300,
                'speed_rolling_mean_6': 28.5,
                'speed_rolling_mean_12': 27.8,
                'speed_rolling_std_6': 1.2,
                'intensity_rolling_mean_6': 5400,
                'speed_diff': 0.7,
                'intensity_diff': 100,
                'speed_to_max_ratio': 0.71
            },
            'expected': 'Thông thoáng, tốc độ ~28-32 km/h'
        },
        {
            'name': '🌙 Đêm Khuya (23:00 PM)',
            'features': {
                **base_features,
                'hour': 23,
                'is_rush_hour': 0,
                'is_weekend': 0,
                'Intensity': 2800,
                'Occupancy': 0.28,
                'speed_lag_1': 36.5,
                'speed_lag_2': 37.2,
                'speed_lag_3': 35.8,
                'intensity_lag_1': 2900,
                'speed_rolling_mean_6': 36.5,
                'speed_rolling_mean_12': 36.1,
                'speed_rolling_std_6': 0.8,
                'intensity_rolling_mean_6': 2850,
                'speed_diff': -0.7,
                'intensity_diff': -100,
                'speed_to_max_ratio': 0.91
            },
            'expected': 'Rất thông thoáng, tốc độ ~35-38 km/h'
        },
        {
            'name': '🎉 Cuối Tuần (Saturday 14:00)',
            'features': {
                **base_features,
                'hour': 14,
                'is_rush_hour': 0,
                'is_weekend': 1,
                'day_of_week': 5,  # Saturday
                'Intensity': 4200,
                'Occupancy': 0.42,
                'speed_lag_1': 32.5,
                'speed_lag_2': 31.8,
                'speed_lag_3': 33.1,
                'intensity_lag_1': 4100,
                'speed_rolling_mean_6': 32.5,
                'speed_rolling_mean_12': 32.1,
                'speed_rolling_std_6': 1.5,
                'intensity_rolling_mean_6': 4150,
                'speed_diff': 0.7,
                'intensity_diff': 50,
                'speed_to_max_ratio': 0.81
            },
            'expected': 'Tốt hơn ngày thường, tốc độ ~30-34 km/h'
        }
    ]
    
    # Test từng scenario
    results = []
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/5: {scenario['name']}")
        print(f"{'='*80}")
        
        # Predict
        result = predictor.predict(scenario['features'])
        
        # Display
        print(f"\n📊 INPUT:")
        print(f"  Hour: {scenario['features']['hour']}:00")
        print(f"  Intensity: {scenario['features']['Intensity']:,} veh/h")
        print(f"  Occupancy: {scenario['features']['Occupancy']:.2f}")
        print(f"  Recent speed: {scenario['features']['speed_lag_1']:.1f} km/h")
        print(f"  Weekend: {'Yes' if scenario['features']['is_weekend'] else 'No'}")
        print(f"  Rush hour: {'Yes' if scenario['features']['is_rush_hour'] else 'No'}")
        
        print(f"\n🔮 PREDICTION:")
        print(f"  Speed: {result['predicted_speed']} km/h")
        print(f"  Confidence: {result['confidence_interval'][0]}-{result['confidence_interval'][1]} km/h")
        print(f"  Congestion: {result['congestion_probability']*100:.1f}%")
        print(f"  Status: {result['status']}")
        
        print(f"\n✅ EXPECTED:")
        print(f"  {scenario['expected']}")
        
        # Validate
        is_correct = validate_prediction(scenario, result)
        print(f"\n{'✅ PASS' if is_correct else '❌ FAIL'}")
        
        results.append({
            'scenario': scenario['name'],
            'predicted_speed': result['predicted_speed'],
            'congestion_prob': result['congestion_probability'],
            'status': result['status'],
            'pass': is_correct
        })
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))
    
    pass_rate = df_results['pass'].sum() / len(df_results) * 100
    print(f"\n✅ Pass Rate: {pass_rate:.0f}%")
    
    if pass_rate >= 80:
        print("🎉 MODELS WORK CORRECTLY! Ready for production.")
    else:
        print("⚠️ Some scenarios failed. Need investigation.")


def validate_prediction(scenario, result):
    """
    Validate if prediction matches expected behavior
    """
    hour = scenario['features']['hour']
    is_rush_hour = scenario['features']['is_rush_hour']
    intensity = scenario['features']['Intensity']
    predicted_speed = result['predicted_speed']
    congestion_prob = result['congestion_probability']
    
    # Rules based on HCMC traffic patterns
    if is_rush_hour == 1:
        # Rush hour: expect slow speed + high congestion
        return predicted_speed < 20 and congestion_prob > 0.6
    
    elif hour >= 22 or hour <= 6:
        # Night: expect high speed + low congestion
        return predicted_speed > 30 and congestion_prob < 0.3
    
    elif intensity > 7000:
        # High intensity: expect congestion
        return congestion_prob > 0.5
    
    else:
        # Normal hours: moderate speed
        return 20 <= predicted_speed <= 35
    

if __name__ == "__main__":
    test_scenarios()
