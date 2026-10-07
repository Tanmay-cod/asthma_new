from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Device, MeasurementSession, SessionStatus, SensorReading, User
from app.security.auth import get_current_user

router = APIRouter(tags=["measurement-sessions"])


@router.get("/measurement-sessions/current/latest-readings")
def latest_session_readings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = (db.query(MeasurementSession)
         .filter(MeasurementSession.user_id == user.id, MeasurementSession.status == SessionStatus.ACTIVE)
         .first())
    if not s:
        return {"status": "NO_ACTIVE_SESSION"}
    rows = (db.query(SensorReading)
            .filter(SensorReading.session_id == s.id)
            .order_by(SensorReading.recorded_at.desc()).limit(20).all())
    out = {}
    for r in rows:
        if r.heart_rate is not None and "heart_rate" not in out:
            out["heart_rate"] = {"value": r.heart_rate, "unit": "bpm", "timestamp": r.recorded_at}
        if r.spo2 is not None and "spo2" not in out:
            out["spo2"] = {"value": r.spo2, "unit": "%", "timestamp": r.recorded_at}
        if r.temperature_c is not None and "temperature_c" not in out:
            out["temperature_c"] = {"value": r.temperature_c, "unit": "C", "timestamp": r.recorded_at}
        if r.humidity_percent is not None and "humidity_percent" not in out:
            out["humidity_percent"] = {"value": r.humidity_percent, "unit": "%", "timestamp": r.recorded_at}
        if r.dust_indicator is not None and "dust_indicator" not in out:
            out["dust_indicator"] = {"value": r.dust_indicator, "unit": "indicator", "timestamp": r.recorded_at}
    return {"session_id": s.id, "status": "ACTIVE", "latest": out}


class StartRequest(BaseModel):
    device_id: str | None = None  # uuid string in Supabase


@router.post("/measurement-sessions/start")
def start_session(payload: StartRequest | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # prevent duplicate active session for this user
    existing = db.query(MeasurementSession).filter(
        MeasurementSession.user_id == user.id, MeasurementSession.status == SessionStatus.ACTIVE).first()
    if existing:
        raise HTTPException(400, "You already have an active measurement session")

    if payload and payload.device_id:
        device = db.query(Device).filter(Device.id == payload.device_id).first()
    else:
        device = db.query(Device).first()
    if not device:
        raise HTTPException(404, "No device registered")
    active = db.query(MeasurementSession).filter(
        MeasurementSession.device_id == device.id, MeasurementSession.status == SessionStatus.ACTIVE).first()
    if active:
        raise HTTPException(409, "Device currently in use; please wait until the current session ends")

    s = MeasurementSession(user_id=user.id, device_id=device.id, status=SessionStatus.ACTIVE)
    db.add(s); db.commit(); db.refresh(s)
    return {"session_id": s.id, "user_id": user.id, "device_id": device.id, "status": "ACTIVE", "started_at": s.started_at}


@router.post("/measurement-sessions/{session_id}/end")
def end_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(MeasurementSession).filter(MeasurementSession.id == session_id,
                                            MeasurementSession.user_id == user.id).first()
    if not s:
        raise HTTPException(404, "Session not found or not yours")
    if s.status != SessionStatus.ACTIVE:
        raise HTTPException(400, "Session already ended")
    s.status = SessionStatus.COMPLETED
    s.ended_at = datetime.utcnow()
    db.commit()
    return {"session_id": s.id, "status": "COMPLETED", "ended_at": s.ended_at}


@router.get("/measurement-sessions/current")
def current_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    s = db.query(MeasurementSession).filter(MeasurementSession.user_id == user.id,
                                            MeasurementSession.status == SessionStatus.ACTIVE).first()
    if not s:
        return {"status": "NO_ACTIVE_SESSION"}
    return {"session_id": s.id, "device_id": s.device_id, "status": "ACTIVE", "started_at": s.started_at}


@router.get("/measurement-sessions/history")
def session_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(MeasurementSession).filter(MeasurementSession.user_id == user.id).order_by(MeasurementSession.started_at.desc()).limit(50).all()
    return [{"session_id": s.id, "device_id": s.device_id, "status": s.status.value,
             "started_at": s.started_at, "ended_at": s.ended_at} for s in rows]
