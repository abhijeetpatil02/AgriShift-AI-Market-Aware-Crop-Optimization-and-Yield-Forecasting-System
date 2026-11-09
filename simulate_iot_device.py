"""
simulate_iot_device.py
Simulates an IoT farm node (e.g. ESP32 + DHT22 + Soil Sensor) sending live data
to the AgriShift Flask server. Use this to test the live IoT mode without physical hardware!
"""

import time
import random
import urllib.request
import json

SERVER_URL = "http://127.0.0.1:5000/api/iot/telemetry"
DEVICE_ID = "AGRI_ESP32_01"

print("=" * 60)
print(f"🌾 AgriShift IoT Device Simulator starting...")
print(f"📡 Target Server: {SERVER_URL}")
print(f"🆔 Simulated Node ID: {DEVICE_ID}")
print("Press Ctrl+C to stop simulation.")
print("=" * 60)

# Base baseline numbers (simulating gentle daytime drift)
base_temp = 27.5
base_humidity = 68.0
base_moisture = 48.0
base_n = 26.0
base_p = 54.0
base_k = 62.0
base_ph = 6.8

packet_count = 0

try:
    while True:
        packet_count += 1
        # Add realistic micro-variations
        current_temp = round(base_temp + random.uniform(-0.8, 0.8), 1)
        current_hum = round(base_humidity + random.uniform(-2.0, 2.0), 1)
        current_moisture = round(base_moisture + random.uniform(-1.5, 1.5), 1)
        current_n = round(base_n + random.uniform(-1.0, 1.0), 1)
        current_p = round(base_p + random.uniform(-1.0, 1.0), 1)
        current_k = round(base_k + random.uniform(-1.5, 1.5), 1)
        current_ph = round(base_ph + random.uniform(-0.1, 0.1), 2)

        payload = {
            "device_id": DEVICE_ID,
            "temperature": current_temp,
            "humidity": current_hum,
            "soil_moisture": current_moisture,
            "nitrogen": current_n,
            "phosphorus": current_p,
            "potassium": current_k,
            "ph": current_ph,
            "rainfall": 0.0
        }

        req = urllib.request.Request(
            SERVER_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'AgriShiftSimulator/1.0'},
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                if res.status in (200, 201):
                    print(f"[{time.strftime('%H:%M:%S')}] Packet #{packet_count} Sent -> Temp: {current_temp}°C, Humidity: {current_hum}%, Moisture: {current_moisture}%, NPK: {current_n}-{current_p}-{current_k}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Failed to send telemetry: {e}. (Ensure app.py is running)")

        time.sleep(10)

except KeyboardInterrupt:
    print("\nSimulator stopped by user.")

