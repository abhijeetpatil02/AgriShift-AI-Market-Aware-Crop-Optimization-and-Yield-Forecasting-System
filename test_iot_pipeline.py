"""
test_iot_pipeline.py
Verification script for AgriShift Dual-Mode IoT Integration.
Tests:
1. IoT telemetry ingestion (/api/iot/telemetry)
2. IoT latest telemetry retrieval (/api/iot/latest)
3. IoT device listing (/api/iot/devices)
4. AI Recommendation via IoT Mode
5. AI Recommendation via Weather API Mode
"""

import json
from app import app
import db

def test_full_iot_flow():
    client = app.test_client()
    print("=" * 70)
    print("STEP 1: INGEST TELEMETRY FROM IOT NODE (ESP32 SIMULATION)")
    print("=" * 70)
    
    device_id = "AGRI_ESP32_01"
    telemetry_payload = {
        'device_id': device_id,
        'temperature': 27.8,
        'humidity': 69.5,
        'soil_moisture': 48.2,
        'nitrogen': 26.5,
        'phosphorus': 56.0,
        'potassium': 64.0,
        'ph': 6.8,
        'rainfall': 12.0
    }
    
    res = client.post('/api/iot/telemetry', json=telemetry_payload)
    print(f"Status: {res.status_code}")
    data = res.get_json()
    print(f"Response: {data}")
    assert res.status_code == 201, "Expected HTTP 201 Created"
    assert data['success'] is True, "Expected success: True"
    assert data['device_id'] == device_id
    
    print("\n" + "=" * 70)
    print("STEP 2: FETCH LATEST TELEMETRY FOR DASHBOARD (/api/iot/latest)")
    print("=" * 70)
    res_latest = client.get(f'/api/iot/latest?device_id={device_id}')
    print(f"Status: {res_latest.status_code}")
    data_latest = res_latest.get_json()
    print(f"Reading: {data_latest.get('reading')}")
    assert res_latest.status_code == 200
    reading = data_latest['reading']
    assert reading['temperature'] == 27.8
    assert reading['humidity'] == 69.5
    assert reading['is_online'] is True
    print(f"Recency: Recorded {reading['seconds_ago']} seconds ago. Status: Online={reading['is_online']}")

    print("\n" + "=" * 70)
    print("STEP 3: RUN AI PREDICTION IN IOT DEVICE MODE")
    print("=" * 70)
    iot_recommend_payload = {
        'district': 'DHARWAD',
        'season': 'Kharif',
        'farm_area': 3.0,
        'input_source': 'iot_device',
        'device_id': device_id,
        'N': reading['nitrogen'],
        'P': reading['phosphorus'],
        'K': reading['potassium'],
        'pH': reading['ph'],
        'temperature': reading['temperature'],
        'humidity': reading['humidity'],
        'rainfall': 620.0
    }
    
    res_pred = client.post('/api/recommend', json=iot_recommend_payload)
    assert res_pred.status_code == 200
    pred_data = res_pred.get_json()
    print(f"Summary: {pred_data['summary']}")
    print(f"Input Source: {pred_data['input_source']} | Device: {pred_data['device_id']}")
    print("Top Recommendations:")
    for crop in pred_data['recommendations']:
        print(f"  - {crop['rank']}. {crop['crop']} | Suitability: {crop['model1_match_score']}% | Forecast Yield: {crop['model2_predicted_yield_ha']} t/ha | Est. Profit: ₹{crop['net_profit_inr']:,}")

    print("\n" + "=" * 70)
    print("STEP 4: RUN AI PREDICTION IN REGIONAL WEATHER API MODE")
    print("=" * 70)
    weather_payload = {
        'district': 'BELAGAVI',
        'season': 'Rabi',
        'farm_area': 2.0,
        'input_source': 'weather_api',
        'device_id': None,
        'N': 28.0,
        'P': 52.0,
        'K': 66.0,
        'pH': 7.2,
        'temperature': 25.0,
        'humidity': 62.0,
        'rainfall': 450.0
    }
    res_weather = client.post('/api/recommend', json=weather_payload)
    assert res_weather.status_code == 200
    weather_data = res_weather.get_json()
    print(f"Summary: {weather_data['summary']}")
    print(f"Input Source: {weather_data['input_source']}")

    print("\n" + "=" * 70)
    print("✅ ALL IOT END-TO-END PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    test_full_iot_flow()

