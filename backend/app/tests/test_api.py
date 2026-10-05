from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_iot_requires_device_token():
    r = client.post("/api/v1/iot/readings", json={"device_id": "X"})
    assert r.status_code == 401


def test_profile_requires_auth():
    r = client.get("/api/v1/profile")
    assert r.status_code == 401
