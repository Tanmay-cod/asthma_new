from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IoTReadingPayload(BaseModel):
    device_code: Optional[str] = None
    device_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    recorded_at: Optional[datetime] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    heart_rate_valid: Optional[bool] = None
    spo2_valid: Optional[bool] = None
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    temperature_valid: Optional[bool] = None
    humidity_valid: Optional[bool] = None
    dust_indicator: Optional[float] = None
    dust_valid: Optional[bool] = None
    wifi_rssi: Optional[int] = None
    firmware_version: Optional[str] = None
