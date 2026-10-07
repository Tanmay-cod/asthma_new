import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Device, User
from app.security.auth import get_current_user, hash_device_token

router = APIRouter(tags=["devices"])


class DeviceCreate(BaseModel):
    device_code: str
    device_name: str | None = None


@router.post("/devices")
def register_device(payload: DeviceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Device).filter(Device.device_code == payload.device_code).first():
        raise HTTPException(400, "Device code already registered")
    token = secrets.token_urlsafe(32)
    device = Device(id=str(__import__('uuid').uuid4()), device_code=payload.device_code,
                    device_name=payload.device_name, device_token_hash=hash_device_token(token),
                    is_active=True)
    db.add(device); db.commit(); db.refresh(device)
    return {"device_id": device.id, "device_code": device.device_code, "device_token": token,
            "note": "Store this token on the ESP8266. It will not be shown again."}


@router.get("/devices")
def list_devices(db: Session = Depends(get_db)):
    return [{"id": d.id, "device_code": d.device_code, "device_name": d.device_name,
             "is_active": d.is_active, "last_seen_at": d.last_seen_at} for d in db.query(Device).all()]


@router.delete("/devices/{device_id}")
def delete_device(device_id: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    device.is_active = False
    device.device_token_hash = None
    db.commit()
    return {"status": "deactivated"}


@router.get("/devices/{device_id}/status")
def device_status(device_id: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    stale = device.last_seen_at is None or (datetime.utcnow() - device.last_seen_at.replace(tzinfo=None)).total_seconds() > 60
    return {"device_code": device.device_code,
            "is_active": device.is_active,
            "last_seen_at": device.last_seen_at,
            "stale": stale}
