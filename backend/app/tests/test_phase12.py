from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models import User
from app.security.auth import get_current_user

Base.metadata.create_all(bind=engine)
_db = SessionLocal()
from app.models import MeasurementSession as _MS
_db.query(_MS).delete()
_db.commit()
_db.close()
client = TestClient(app)


def _mk_user(email):
    db = SessionLocal()
    u = User(email=email, role="PATIENT")
    db.add(u); db.commit(); db.refresh(u)
    out = SimpleNamespace(id=u.id, email=u.email, role=u.role, profile=None)
    db.close()
    return out


def _register(user, code):
    app.dependency_overrides[get_current_user] = lambda: user
    r = client.post("/api/v1/devices", json={"device_code": code})
    app.dependency_overrides.pop(get_current_user)
    return r.json()["device_id"], r.json()["device_token"]


def test_session_rules():
    uA = _mk_user(f"sA_{datetime.now().timestamp()}@t")
    uB = _mk_user(f"sB_{datetime.now().timestamp()}@t")
    did, tok = _register(uA, f"ESP001-{datetime.now().timestamp()}")
    code = None
    # re-register is not needed; get code from device list
    from app.core.database import SessionLocal as SL
    from app.models import Device as D
    db = SL(); code = db.query(D).filter(D.id == did).first().device_code; db.close()

    # User A starts
    app.dependency_overrides[get_current_user] = lambda: uA
    r = client.post("/api/v1/measurement-sessions/start", json={"device_id": did})
    assert r.status_code == 200, r.text
    sidA = r.json()["session_id"]

    # User B cannot start while A active
    app.dependency_overrides[get_current_user] = lambda: uB
    r = client.post("/api/v1/measurement-sessions/start", json={"device_id": did})
    assert r.status_code == 409

    # User B cannot end A's session
    r = client.post(f"/api/v1/measurement-sessions/{sidA}/end")
    assert r.status_code == 404

    # A ends
    app.dependency_overrides[get_current_user] = lambda: uA
    r = client.post(f"/api/v1/measurement-sessions/{sidA}/end")
    assert r.status_code == 200

    # After end, readings rejected
    r = client.post("/api/v1/iot/readings", headers={"Authorization": f"Bearer {tok}"},
                    json={"device_id": code, "heart_rate": 70})
    assert r.status_code in (401, 409, 422)

    # B can now start
    app.dependency_overrides[get_current_user] = lambda: uB
    r = client.post("/api/v1/measurement-sessions/start", json={"device_id": did})
    assert r.status_code == 200, r.text

    # Session ownership isolation of history
    app.dependency_overrides[get_current_user] = lambda: uA
    h = client.get("/api/v1/measurement-sessions/history").json()
    assert all(s["session_id"] == sidA for s in h)
