/*
 * Asthma Risk Monitor - NodeMCU ESP8266 firmware
 * Sensors: MAX30102 (SpO2/Pulse, I2C), DHT22 (Temp/Humidity), GP2Y1010AU0F (dust, analog)
 * Sends JSON via HTTP POST to the backend /api/ingest endpoint.
 *
 * Required libraries (Arduino Library Manager):
 *   - Adafruit MAX3010x
 *   - DHT sensor library (Adafruit)
 *   - Adafruit Unified Sensor
 *   - ArduinoJson (v6+)
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
const char* SERVER_URL    = "http://192.168.1.100:8000/api/ingest"; // your PC IP
const int   USER_ID       = 1;
const int   SEND_INTERVAL_MS = 5000;

// Pins
#define DHT_PIN     D4   // DHT22 data
#define DHT_TYPE    DHT22
#define DUST_LED    D5   // GP2Y1010AU0F LED (inverted, active LOW)
#define DUST_ANALOG A0   // GP2Y1010AU0F analog output
// MAX30102: SDA=D2, SCL=D1

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
  Serial.println("\nWiFi connected. IP: " + WiFi.localIP().toString());
}

float readDustDensity() {
  digitalWrite(DUST_LED, LOW);   // turn LED on
  delayMicroseconds(280);
  int raw = analogRead(DUST_ANALOG);
  delayMicroseconds(40);
  digitalWrite(DUST_LED, HIGH);  // LED off
  delayMicroseconds(9680);
  float voltage = raw * (3.3 / 1024.0);
  float density = 0.17 * voltage - 0.1;   // rough mg/m^3 calibration
  return max(density, 0.0f);
}

void readMax30102(float &spo2, float &pulse) {
  // In production use the full spo2_algorithm.h buffer approach.
  // Simplified placeholder: read IR/RED and compute approximate values.
  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();
  if (irValue < 50000) { spo2 = 0; pulse = 0; return; }
  float ratio = (float)redValue / (float)irValue;
  spo2 = constrain(110.0 - 25.0 * ratio, 80.0, 100.0);
  pulse = 60 + (particleSensor.getIR() % 40);  // replace with real pulse algorithm
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();
  float dust        = readDustDensity();
  float spo2, pulse;
  readMax30102(spo2, pulse);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT22 read failed");
    delay(SEND_INTERVAL_MS);
    return;
  }

  StaticJsonDocument<256> doc;
  doc["user_id"]    = USER_ID;
  doc["spo2"]       = spo2;
  doc["pulse"]      = pulse;
  doc["temperature"]= temperature;
  doc["humidity"]   = humidity;
  doc["dust"]       = dust;
  // doc["pefr"]    = manualValue; // enter PEFR via Serial/Blynk if desired

  String body;
  serializeJson(doc, body);
  Serial.println(body);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(body);
    Serial.printf("HTTP %d\n", code);
    http.end();
  }
  delay(SEND_INTERVAL_MS);
}
