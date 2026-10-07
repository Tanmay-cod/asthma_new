from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Device, DeviceStatus, SensorReading, SensorType, DataQuality, MeasurementSession
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
    # Device is derived entirely from the authenticated token; device_code/device_id are advisory.
    supplied = payload.device_id or payload.device_code
    if supplied is not None and supplied not in (device.device_code, str(device.id)):
        raise HTTPException(403, "Device identity mismatch")

    session = (db.query(MeasurementSession)
               .filter(MeasurementSession.device_id == device.id,
                       MeasurementSession.status == 'ACTIVE').first())
    if not session:
        raise HTTPException(409, "No active measurement session for this device; reading not assigned to any user")
    owner_user_id = session.user_id

    ts = payload.recorded_at or payload.timestamp or datetime.utcnow()
    if ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    if ts > datetime.utcnow() + timedelta(minutes=5):
        raise HTTPException(422, "Timestamp is in the future; reading rejected")

    expected = {
        "heart_rate": payload.heart_rate, "spo2": payload.spo2,
        "temperature_c": payload.temperature_c, "humidity_percent": payload.humidity_percent,
        "dust_indicator": payload.dust_indicator,
    }
    flagged = []
    ranges = {"heart_rate": (20, 250), "spo2": (50, 100), "temperature_c": (-20, 60),
              "humidity_percent": (0, 100), "dust_indicator": (0, 10)}
    for k, v in expected.items():
        if v is not None and not (ranges[k][0] <= v <= ranges[k][1]):
            flagged.append(k)
            # DataQualityEvent table is not present in the live Supabase schema;
            # validation is reported via the response 'flagged' list instead.
    db.add(SensorReading(id=str(__import__('uuid').uuid4()), session_id=session.id, device_id=device.id,
                         heart_rate=payload.heart_rate, spo2=payload.spo2,
                         heart_rate_valid=payload.heart_rate_valid, spo2_valid=payload.spo2_valid,
                         temperature_c=payload.temperature_c, humidity_percent=payload.humidity_percent,
                         temperature_valid=payload.temperature_valid, humidity_valid=payload.humidity_valid,
                         dust_indicator=payload.dust_indicator, dust_valid=payload.dust_valid,
                         wifi_rssi=payload.wifi_rssi, recorded_at=ts))
    device.last_seen_at = datetime.utcnow()
    db.commit()
    return {"status": "ok", "stored": 1, "flagged": flagged}
