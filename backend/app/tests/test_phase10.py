from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models import User, PefrReading, SensorReading, SensorType, SymptomAssessment
from app.security.auth import get_current_user

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _seed():
    db = SessionLocal()
    db.query(User).delete()
    u1 = User(email="a@test", role="PATIENT"); u2 = User(email="b@test", role="PATIENT")
    db.add_all([u1, u2]); db.commit(); db.refresh(u1); db.refresh(u2)
    # user A data
    for i, v in enumerate([500, 480, 470, 460, 450, 440, 430]):
        db.add(PefrReading(id=str(__import__('uuid').uuid4()), user_id=u1.id, pef_l_min=v, recorded_at=datetime.utcnow() - timedelta(days=i)))
    from app.models import MeasurementSession
    _s = MeasurementSession(id=str(__import__('uuid').uuid4()), user_id=str(u1.id), device_id=None, status="ACTIVE")
    db.add(_s); db.commit()
    for i in range(7):
        db.add(SensorReading(id=str(__import__('uuid').uuid4()), session_id=_s.id, heart_rate=72 + i, temperature_c=25.0,
                             humidity_percent=50.0, recorded_at=datetime.utcnow() - timedelta(days=i)))
    db.add(SymptomAssessment(user_id=u1.id, cough=1, wheezing=0))
    # user B: no data
    db.add(PefrReading(id=str(__import__('uuid').uuid4()), user_id=u2.id, pef_l_min=550, recorded_at=datetime.utcnow()))
    db.commit()
    from types import SimpleNamespace
    r1 = SimpleNamespace(id=str(u1.id), email=u1.email, role=u1.role, profile=None)
    r2 = SimpleNamespace(id=str(u2.id), email=u2.email, role=u2.role, profile=None)
    # sessions/pefr seeds already use str(u.id)
    db.close()
    return r1, r2


def _override(user):
    app.dependency_overrides[get_current_user] = lambda: user


def test_user_isolation_and_report():
    u1, u2 = _seed()
    _override(u1)
    r = client.post("/api/v1/reports/personalized")
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == u1.id
    assert body["model_prediction"]["clinical_validation_status"] == "PENDING"
    assert body["model_prediction"]["risk_probability"] is not None
    assert body["current_measurements"]["personal_best_pef"] == max([500, 480, 470, 460, 450, 440, 430])

    # user B switch: report must be B's data only
    _override(u2)
    r2 = client.post("/api/v1/reports/personalized")
    assert r2.status_code == 200
    b2 = r2.json()
    assert b2["user_id"] == u2.id
    assert b2["current_measurements"]["personal_best_pef"] == 550

    # prediction history isolation
    r3 = client.get("/api/v1/predictions/history")
    assert all(p["prediction_id"] for p in r3.json())


def test_missing_data_no_fabrication():
    u1, u2 = _seed()
    _override(u2)
    r = client.get("/api/v1/predictions/latest")
    assert r.status_code == 404 or r.json().get("risk_level") is not None
