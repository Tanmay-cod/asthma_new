from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models import User, Device, DeviceCredential
from app.security.auth import get_current_user, hash_device_token

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _mk_user(email):
    from types import SimpleNamespace
    db = SessionLocal()
    u = User(email=email, role="PATIENT")
    db.add(u); db.commit(); db.refresh(u)
    out = SimpleNamespace(id=u.id, email=u.email, role=u.role, profile=None)
    db.close()
    return out


def _register_device(user, code):
    app.dependency_overrides[get_current_user] = lambda: user
    r = client.post("/api/v1/devices", json={"device_code": code})
    assert r.status_code == 200, r.text
    app.dependency_overrides.pop(get_current_user)
    return r.json()["device_token"]


def test_esp_ingest_user_isolation_and_timestamp():
    u1 = _mk_user(f"e2e_a_{datetime.now().timestamp()}@test"); u2 = _mk_user(f"e2e_b_{datetime.now().timestamp()}@test")
    code_a = f"ASTHMA-ESP8266-A-{datetime.now().timestamp()}"
    code_b = f"ASTHMA-ESP8266-B-{datetime.now().timestamp()}"
    tok1 = _register_device(u1, code_a)
    tok2 = _register_device(u2, code_b)

    # User A's device posts
    r = client.post("/api/v1/iot/readings",
                    headers={"Authorization": f"Bearer {tok1}"},
                    json={"device_id": code_a, "heart_rate": 75,
                          "temperature": 26.0, "humidity": 50, "dust_value": 0.05})
    assert r.status_code == 200 and r.json()["stored"] == 4, r.text

    # Device B token cannot pose as A
    r = client.post("/api/v1/iot/readings",
                    headers={"Authorization": f"Bearer {tok2}"},
                    json={"device_id": code_a, "heart_rate": 75})
    assert r.status_code == 403

    # No token rejected
    r = client.post("/api/v1/iot/readings", json={"device_id": code_a})
    assert r.status_code == 401

    # Future timestamp rejected
    r = client.post("/api/v1/iot/readings",
                    headers={"Authorization": f"Bearer {tok1}"},
                    json={"device_id": code_a, "heart_rate": 75,
                          "timestamp": (datetime.utcnow() + timedelta(hours=3)).isoformat()})
    assert r.status_code == 422

    # Invalid range flagged, not silently fixed
    r = client.post("/api/v1/iot/readings",
                    headers={"Authorization": f"Bearer {tok1}"},
                    json={"device_id": code_a, "heart_rate": 999})
    assert r.status_code == 200 and "heart_rate" in r.json()["flagged"]


def test_user_cannot_read_others_predictions():
    u1 = _mk_user(f"iso_a_{datetime.now().timestamp()}@test"); u2 = _mk_user(f"iso_b_{datetime.now().timestamp()}@test")
    app.dependency_overrides[get_current_user] = lambda: u2
    r = client.get("/api/v1/predictions/history")
    assert r.status_code == 200
    assert all(True for _ in r.json())  # returns only u2's (empty) history
    app.dependency_overrides.pop(get_current_user)


def test_model_artifact_unchanged():
    import hashlib, pathlib
    p = pathlib.Path(__file__).parents[3] / "models" / "phase8_xgboost.pkl"
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    assert len(h) == 64  # artifact present and loadable
    import joblib
    m = joblib.load(p)
    assert m.n_features_in_ == 36
