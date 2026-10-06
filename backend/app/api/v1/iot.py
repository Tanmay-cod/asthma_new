from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Device, DeviceStatus, SensorReading, SensorType, DataQuality, DataQualityEvent, MeasurementSession, SessionStatus
from app.schemas import IoTReadingPayload
from app.security.auth import get_current_device

router = APIRouter(tags=["iot"])

# Plausibility ranges — configurable; do NOT silently modify values.
RANGES = {
    "spo2": (50.0, 100.0),
    "heart_rate": (20.0, 250.0),
    "temperature": (-20.0, 60.0),
    "humidity": (0.0, 100.0),
    "dust_value": (0.0, 10.0),
}
UNITS = {"spo2": "%", "heart_rate": "bpm", "temperature": "C", "humidity": "%", "dust_value": "mg/m^3_indicator"}

SENSOR_ENUM = {
    "spo2": SensorType.SPO2,
    "heart_rate": SensorType.HEART_RATE,
    "temperature": SensorType.TEMPERATURE,
    "humidity": SensorType.HUMIDITY,
    "dust_value": SensorType.DUST,
}


@router.post("/iot/readings")
def submit_readings(payload: IoTReadingPayload, device: Device = Depends(get_current_device), db: Session = Depends(get_db)):
    if payload.device_id != device.device_code:
        raise HTTPException(403, "Device identity mismatch")

    session = (db.query(MeasurementSession)
               .filter(MeasurementSession.device_id == device.id,
                       MeasurementSession.status == SessionStatus.ACTIVE).first())
    if not session:
        raise HTTPException(409, "No active measurement session for this device; reading not assigned to any user")
    owner_user_id = session.user_id

    ts = payload.timestamp or datetime.utcnow()
    if ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    if ts > datetime.utcnow() + timedelta(minutes=5):
        db.add(DataQualityEvent(user_id=owner_user_id, device_id=device.id,
                                event_type="FUTURE_TIMESTAMP", detail=str(ts)))
        db.commit()
        raise HTTPException(422, "Timestamp is in the future; reading rejected")
    stored, rejected = 0, []
    for field, sensor_enum in SENSOR_ENUM.items():
        value = getattr(payload, field)
        if value is None:
            continue
        lo, hi = RANGES[field]
        quality = DataQuality.VALID if lo <= value <= hi else DataQuality.INVALID
        if quality != DataQuality.VALID:
            db.add(DataQualityEvent(user_id=owner_user_id, device_id=device.id,
                                    event_type="INVALID_RANGE", detail=f"{field}={value}"))
            rejected.append(field)
            # Store but flag invalid — never silently modify
        db.add(SensorReading(user_id=owner_user_id, device_id=device.id, session_id=session.id,
                             sensor_type=sensor_enum, value=value, unit=UNITS[field],
                             source="esp8266", data_quality=quality,
                             firmware_version=payload.firmware_version, timestamp=ts))
        stored += 1

    device.last_seen = datetime.utcnow()
    device.status = DeviceStatus.ONLINE
    db.commit()
    return {"status": "ok", "stored": stored, "flagged": rejected}
