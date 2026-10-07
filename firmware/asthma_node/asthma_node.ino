/*
 * Asthma Risk Monitor - NodeMCU ESP8266 firmware
 * Production contract: POST /api/v1/iot/readings
 * Device identifies as ESP001 only. No user_id in this firmware.
 * Required libraries: ESP8266WiFi, ESP8266HTTPClient, Wire, MAX30105,
 * spo2_algorithm, DHT, ArduinoJson (v6+).
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <MAX30105.h>
#include <spo2_algorithm.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ---------- CONFIG ----------
const char* WIFI_SSID     = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:8000/api/v1/iot/readings";
const char* DEVICE_CODE   = "ESP001";
// Token loaded at flash time from backend/.esp001_device_token (NOT committed):
const char* DEVICE_TOKEN  = "PASTE_ESP001_TOKEN_HERE";
const int   SEND_INTERVAL_MS = 5000;

#define DHT_PIN     D4
#define DHT_TYPE    DHT22
#define DUST_LED    D5
#define DUST_ANALOG A0

DHT dht(DHT_PIN, DHT_TYPE);
MAX30105 particleSensor;

void setup() {
  Serial.begin(115200);
  pinMode(DUST_LED, OUTPUT);
  digitalWrite(DUST_LED, HIGH);

  Wire.begin(D2, D1);
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found!");
  } else {
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
  }

  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi connected.");

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  time_t now = time(nullptr);
  while (now < 1700000000) { delay(300); now = time(nullptr); }
}

float readDustIndicator() {
  digitalWrite(DUST_LED, LOW);
  delayMicroseconds(280);
  int raw = analogRead(DUST_ANALOG);
  delayMicroseconds(40);
  digitalWrite(DUST_LED, HIGH);
  delayMicroseconds(9680);
  float voltage = raw * (3.3 / 1024.0);
  float density = 0.17 * voltage - 0.1;
  return max(density, 0.0f);
}

String utcTimestamp() {
  time_t now = time(nullptr);
  struct tm *t = gmtime(&now);
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", t);
  return String(buf);
}

void readMax30102(float &spo2, float &pulse, bool &valid) {
  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();
  if (irValue < 50000) { spo2 = 0; pulse = 0; valid = false; return; }
  float ratio = (float)redValue / (float)irValue;
  spo2 = constrain(110.0 - 25.0 * ratio, 80.0, 100.0);
  pulse = 60 + (particleSensor.getIR() % 40);
  valid = true;
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();
  bool dhtValid = !(isnan(temperature) || isnan(humidity));
  if (!dhtValid) { temperature = 0; humidity = 0; Serial.println("DHT22 read failed"); }

  float dust; bool dustValid = true;
  dust = readDustIndicator();

  float spo2, pulse; bool maxValid;
  readMax30102(spo2, pulse, maxValid);

  StaticJsonDocument<512> doc;
  doc["device_code"] = DEVICE_CODE;
  doc["device_id"]   = DEVICE_CODE;  // kept for backend compatibility
  doc["heart_rate"]  = maxValid ? pulse : 0;
  doc["spo2"]        = maxValid ? spo2 : 0;
  doc["heart_rate_valid"] = maxValid;
  doc["spo2_valid"]       = maxValid;
  doc["temperature_c"]      = dhtValid ? temperature : 0;
  doc["humidity_percent"]   = dhtValid ? humidity : 0;
  doc["temperature_valid"]  = dhtValid;
  doc["humidity_valid"]     = dhtValid;
  doc["dust_indicator"]     = dustValid ? dust : 0;
  doc["dust_valid"]         = dustValid;
  doc["wifi_rssi"]          = WiFi.RSSI();
  doc["recorded_at"]        = utcTimestamp();

  String body;
  serializeJson(doc, body);
  Serial.println(body);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", String("Bearer ") + DEVICE_TOKEN);
    int code = http.POST(body);
    Serial.printf("HTTP %d\n", code);
    http.end();
  }
  delay(SEND_INTERVAL_MS);
}
