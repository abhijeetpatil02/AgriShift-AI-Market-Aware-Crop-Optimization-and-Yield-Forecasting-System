#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ================= WI-FI & SERVER CONFIGURATION =================

// Your Wi-Fi / Hotspot details (from your Windows screenshot):
const char* ssid = "Abhi Patil";           // Exactly as shown in your Wi-Fi settings
const char* password = "Abhijeet"; // <-- Put the password for "Abhi Patil" here!

// Your laptop's IP address on "Abhi Patil" network (detected via ipconfig):
const char* serverUrl = "http://10.157.100.129:5000/api/iot/telemetry";
const char* deviceId  = "AGRI_ESP32_01";

// ================= PIN CONFIGURATION =================

// DHT11
#define DHT_PIN 19
#define DHT_TYPE DHT11

// GY-68 BMP180
#define SDA_PIN 21
#define SCL_PIN 22

// DS18B20
#define DS18B20_PIN 18

// QYF0900 / Soil Moisture Analog Pins
#define QYF_X_PIN 32
#define QYF_Y_PIN 33
#define QYF_Z_PIN 34

// ================= SENSOR OBJECTS =================

DHT dht(DHT_PIN, DHT_TYPE);

Adafruit_BMP085_Unified bmp =
    Adafruit_BMP085_Unified(10085);

OneWire oneWire(DS18B20_PIN);

DallasTemperature ds18b20(&oneWire);

// BMP180 connection status
bool bmpConnected = false;

// ================= SETUP =================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("================================================");
  Serial.println("  AgriShift ESP32 IoT Sensor Monitoring System  ");
  Serial.println("================================================");

  // Initialize I2C
  Wire.begin(SDA_PIN, SCL_PIN);

  // Initialize DHT11
  dht.begin();

  // Initialize DS18B20
  ds18b20.begin();

  // Initialize ADC
  analogReadResolution(12);

  // Initialize BMP180
  bmpConnected = bmp.begin();

  if (bmpConnected) {
    Serial.println("✅ GY-68 BMP180 Connected");
  }
  else {
    Serial.println("⚠️ GY-68 BMP180 Not Detected");
  }

  Serial.println("✅ DHT11 Initialized");
  Serial.println("✅ DS18B20 Initialized");
  Serial.println("✅ QYF0900 Initialized");

  // Connect to Wi-Fi (Optimized for Windows Mobile Hotspot)
  Serial.println();
  Serial.print("Connecting to Hotspot: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(100);
  WiFi.setAutoReconnect(true);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Connected to Hotspot Successfully!");
    Serial.print("ESP32 Local IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Sending Telemetry to: ");
    Serial.println(serverUrl);
  } else {
    Serial.printf("\n❌ Hotspot Connection Failed! (Status code: %d)\n", WiFi.status());
    Serial.println("💡 FIX: Go to Windows Settings -> Mobile Hotspot -> Edit -> Set Network Band to '2.4 GHz'!");
  }

  Serial.println("------------------------------------------------");
}

// ================= MAIN LOOP =================

void loop() {

  // Check Wi-Fi reconnection if dropped
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting to Wi-Fi...");
    WiFi.disconnect();
    WiFi.reconnect();
    delay(3000);
  }

  // -------- DHT11 --------

  float humidity = dht.readHumidity();

  float dhtTemperature = dht.readTemperature();

  // -------- GY-68 BMP180 --------

  float bmpTemperature = NAN;
  float pressurePa = NAN;

  if (bmpConnected) {

    bmp.getTemperature(&bmpTemperature);

    bmp.getPressure(&pressurePa);

  }

  float pressureHpa = pressurePa / 100.0;

  // -------- DS18B20 --------

  ds18b20.requestTemperatures();

  float dsTemperature =
      ds18b20.getTempCByIndex(0);

  // -------- QYF0900 --------

  int xValue = analogRead(QYF_X_PIN);

  int yValue = analogRead(QYF_Y_PIN);

  int zValue = analogRead(QYF_Z_PIN);

  // ================= DISPLAY TO SERIAL MONITOR =================

  Serial.println();
  Serial.println("========== SENSOR DATA ==========");

  // DHT11

  Serial.println("[DHT11]");

  if (!isnan(humidity) &&
      !isnan(dhtTemperature)) {

    Serial.print("Temperature: ");
    Serial.print(dhtTemperature);
    Serial.println(" C");

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

  }
  else {

    Serial.println("DHT11 Reading Failed");

  }

  // GY-68

  Serial.println("\n[GY-68 BMP180]");

  if (bmpConnected) {

    Serial.print("Temperature: ");
    Serial.print(bmpTemperature);
    Serial.println(" C");

    Serial.print("Pressure: ");
    Serial.print(pressureHpa);
    Serial.println(" hPa");

  }
  else {

    Serial.println("BMP180 Not Connected");

  }

  // DS18B20

  Serial.println("\n[DS18B20]");

  if (dsTemperature != DEVICE_DISCONNECTED_C) {

    Serial.print("Temperature: ");
    Serial.print(dsTemperature);
    Serial.println(" C");

  }
  else {

    Serial.println("DS18B20 Not Connected");

  }

  // QYF0900

  Serial.println("\n[QYF0900]");

  Serial.print("X Axis: ");
  Serial.println(xValue);

  Serial.print("Y Axis: ");
  Serial.println(yValue);

  Serial.print("Z Axis: ");
  Serial.println(zValue);

  // ================= SEND TELEMETRY TO AGRISHIFT API =================

  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Select the best available temperature reading:
    float finalTemperature = 28.0; // fallback
    if (!isnan(dhtTemperature)) {
      finalTemperature = dhtTemperature;
    } else if (dsTemperature != DEVICE_DISCONNECTED_C && dsTemperature > -50 && dsTemperature < 100) {
      finalTemperature = dsTemperature;
    } else if (!isnan(bmpTemperature)) {
      finalTemperature = bmpTemperature;
    }

    // Select humidity reading:
    float finalHumidity = !isnan(humidity) ? humidity : 65.0;

    // Convert analog reading (X Axis) to approximate Soil Moisture % (0 - 100%):
    int soilMoisture = map(xValue, 3500, 1400, 0, 100);
    soilMoisture = constrain(soilMoisture, 0, 100);

    // Build JSON Payload
    String jsonPayload = "{";
    jsonPayload += "\"device_id\":\"" + String(deviceId) + "\",";
    jsonPayload += "\"temperature\":" + String(finalTemperature, 2) + ",";
    jsonPayload += "\"humidity\":" + String(finalHumidity, 2) + ",";
    jsonPayload += "\"soil_moisture\":" + String(soilMoisture);
    jsonPayload += "}";

    Serial.println("\n[AgriShift HTTP Transmission]");
    Serial.print("Payload: ");
    Serial.println(jsonPayload);

    int httpCode = http.POST(jsonPayload);

    if (httpCode > 0) {
      String response = http.getString();
      Serial.printf("✅ Telemetry Sent to AgriShift successfully! HTTP Code: %d\n", httpCode);
    } else {
      Serial.printf("❌ HTTP POST Failed! Error: %s\n", http.errorToString(httpCode).c_str());
      Serial.println("💡 Tip: Verify your PC's IP and check Windows Firewall for port 5000.");
    }

    http.end();
  } else {
    Serial.println("\n⚠️ Cannot send telemetry: Wi-Fi not connected.");
  }

  Serial.println("=================================");

  // Wait 6 seconds between updates
  delay(6000);

}
