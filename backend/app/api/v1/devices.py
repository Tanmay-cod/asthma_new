import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Device, DeviceCredential, DeviceStatus, User
from app.security.auth import get_current_user, hash_device_token

router = APIRouter(tags=["devices"])


class DeviceCreate(BaseModel):
    device_code: str
    name: str | None = None


@router.post("/devices")
def register_device(payload: DeviceCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Device).filter(Device.device_code == payload.device_code).first():
        raise HTTPException(400, "Device code already registered")
    device = Device(user_id=user.id, device_code=payload.device_code, name=payload.name)
    db.add(device); db.flush()
    token = secrets.token_urlsafe(32)
    db.add(DeviceCredential(device_id=device.id, token_hash=hash_device_token(token)))
    db.commit()
    db.refresh(device)
    # Show plaintext token ONCE — store only the hash
    return {"device_id": device.id, "device_code": device.device_code, "device_token": token,
            "note": "Store this token on the ESP8266. It will not be shown again."}


@router.get("/devices")
def list_devices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": d.id, "device_code": d.device_code, "status": d.status.value,
             "last_seen": d.last_seen} for d in db.query(Device).filter(Device.user_id == user.id).all()]


@router.delete("/devices/{device_id}")
def delete_device(device_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.user_id == user.id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    if device.credentials:
        device.credentials.revoked = True
    db.delete(device)
    db.commit()
    return {"status": "deleted"}


@router.get("/devices/{device_id}/status")
def device_status(device_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id, Device.user_id == user.id).first()
    if not device:
        raise HTTPException(404, "Device not found")
    stale = device.last_seen is None or (datetime.utcnow() - device.last_seen).total_seconds() > 60
    return {"device_code": device.device_code,
            "status": "OFFLINE" if stale else "ONLINE",
            "last_seen": device.last_seen}
