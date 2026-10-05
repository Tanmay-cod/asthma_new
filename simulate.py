"""Simulates an ESP8266 sending sensor data to the backend for testing."""
import random
import time
import requests

API = "http://127.0.0.1:8000"
USER_ID = 1

if __name__ == "__main__":
    while True:
        payload = {
            "user_id": USER_ID,
            "spo2": round(random.uniform(92, 99), 1),
            "pulse": round(random.uniform(65, 105), 1),
            "temperature": round(random.uniform(22, 35), 1),
            "humidity": round(random.uniform(30, 80), 1),
            "dust": round(random.uniform(0.01, 0.4), 3),
            "pefr": round(random.uniform(300, 550), 1),
        }
        try:
            r = requests.post(f"{API}/api/ingest", json=payload, timeout=5)
            print("Sent:", payload, "->", r.status_code)
        except Exception as e:
            print("Error:", e)
        time.sleep(5)
