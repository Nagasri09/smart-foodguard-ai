/*
 Smart FoodGuard AI - ESP32 Wi-Fi ingestion example.
 Install ArduinoJson library. Set credentials and active session ID.
 Sensor values below are placeholders for interface testing only.
 They are NOT validated measurements and do not indicate adulteration.
*/
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* API_URL = "http://192.168.1.10:8000/api/sensors/ingest";
const char* DEVICE_ID = "esp32-demo-01";
const char* DEVICE_KEY = "CHANGE_ME_DEVICE_KEY";
const char* SESSION_ID = "PASTE_ACTIVE_SESSION_ID";
const char* FOOD = "milk";

unsigned long counter = 0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWi-Fi connected. Configure calibrated food-specific sensors before real use.");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", DEVICE_ID);
    http.addHeader("X-Device-Key", DEVICE_KEY);

    StaticJsonDocument<512> doc;
    doc["message_id"] = String(DEVICE_ID) + "-" + String(++counter);
    doc["session_id"] = SESSION_ID;
    doc["food"] = FOOD;
    doc["measured_at"] = "2026-10-31T12:30:00Z"; // Replace with real synchronized UTC timestamp.
    JsonObject m = doc.createNestedObject("measurements");
    m["temperature_c"] = 22.4;       // PLACEHOLDER ONLY
    m["ph"] = 6.7;                   // PLACEHOLDER ONLY
    m["conductivity_us_cm"] = 410.0; // PLACEHOLDER ONLY

    String body; serializeJson(doc, body);
    int code = http.POST(body);
    Serial.printf("HTTP %d: %s\n", code, http.getString().c_str());
    http.end();
  } else {
    Serial.println("Wi-Fi disconnected; no readings sent.");
  }
  delay(5000);
}
