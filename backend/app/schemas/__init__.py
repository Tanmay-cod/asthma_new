from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IoTReadingPayload(BaseModel):
    device_id: str
    timestamp: Optional[datetime] = None
    spo2: Optional[float] = None
    heart_rate: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    dust_value: Optional[float] = None
    firmware_version: Optional[str] = None
