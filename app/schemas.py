from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    age: int
    gender: str
    smoking: str = "never"
    personal_best_pefr: float
    baseline_spo2: float = 97.0
    baseline_pulse: float = 75.0


class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True


class SensorPayload(BaseModel):
    """Payload sent by ESP8266 (or manual form / simulator)."""
    user_id: int
    spo2: float
    pulse: float
    temperature: float
    humidity: float
    dust: float
    pefr: Optional[float] = None  # L/min, manual entry


class ReadingOut(BaseModel):
    id: int
    user_id: int
    spo2: float
    pulse: float
    temperature: float
    humidity: float
    dust: float
    pefr: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    risk_score: float
    risk_level: str
    shap_values: Dict[str, float]
    top_factors: list
    features: Dict[str, float]
