from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SensorReading, MeasurementSession, PefrReading, SymptomAssessment, PersonalBaseline
from app.security.auth import get_current_user

router = APIRouter(tags=["measurements"])


@router.get("/readings/latest")
def latest_readings(user=Depends(get_current_user), db: Session = Depends(get_db)):
    r = (db.query(SensorReading)
         .join(MeasurementSession, SensorReading.session_id == MeasurementSession.id)
         .filter(MeasurementSession.user_id == user.id)
         .order_by(SensorReading.recorded_at.desc()).first())
    if not r:
        return {}
    return {
        "heart_rate": {"value": r.heart_rate, "unit": "bpm", "timestamp": r.recorded_at},
        "spo2": {"value": r.spo2, "unit": "%", "timestamp": r.recorded_at},
        "temperature_c": {"value": r.temperature_c, "unit": "C", "timestamp": r.recorded_at},
        "humidity_percent": {"value": r.humidity_percent, "unit": "%", "timestamp": r.recorded_at},
        "dust_indicator": {"value": r.dust_indicator, "unit": "indicator", "timestamp": r.recorded_at},
    }


class PefrCreate(BaseModel):
    pefr: float
    unit: str = "L/min"
    notes: str | None = None
    timestamp: datetime | None = None


@router.post("/pefr")
def add_pefr(payload: PefrCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not (50 <= payload.pefr <= 800):
        raise HTTPException(422, "PEFR value outside plausible range (50-800 L/min)")
    row = PefrReading(id=str(__import__('uuid').uuid4()), user_id=user.id,
                      pef_l_min=payload.pefr,
                      recorded_at=payload.timestamp or datetime.utcnow(), source="manual")
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "pef_l_min": row.pef_l_min, "recorded_at": row.recorded_at}


@router.get("/pefr")
def list_pefr(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(PefrReading).filter(PefrReading.user_id == user.id)
            .order_by(PefrReading.recorded_at.desc()).limit(50).all())
    return [{"id": r.id, "pef_l_min": r.pef_l_min, "personal_best_l_min": r.personal_best_l_min,
             "recorded_at": r.recorded_at} for r in rows]


class SymptomCreate(BaseModel):
    cough: int = 0
    wheezing: int = 0
    shortness_of_breath: int = 0
    chest_tightness: int = 0
    night_symptoms: bool = False
    exercise_limitation: bool = False
    notes: str | None = None


@router.post("/symptoms")
def add_symptoms(payload: SymptomCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = SymptomAssessment(user_id=user.id, **payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "timestamp": row.timestamp}


@router.get("/symptoms")
def list_symptoms(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(SymptomAssessment).filter(SymptomAssessment.user_id == user.id)
            .order_by(SymptomAssessment.timestamp.desc()).limit(50).all())
    return [{"id": r.id, "cough": r.cough, "wheezing": r.wheezing,
             "shortness_of_breath": r.shortness_of_breath, "chest_tightness": r.chest_tightness,
             "night_symptoms": r.night_symptoms, "timestamp": r.timestamp} for r in rows]


@router.get("/baseline")
def get_baselines(user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models import PersonalBaseline
    rows = db.query(PersonalBaseline).filter(PersonalBaseline.user_id == user.id).all()
    if not rows:
        return {"status": "insufficient_data",
                "message": "Personal baseline is still being established."}
    return [{"metric": r.metric, "baseline_value": r.baseline_value,
             "observation_count": r.observation_count, "quality": r.quality,
             "calculation_version": r.calculation_version} for r in rows]


@router.get("/risk/current")
def risk_current():
    return {"status": "planned", "message": "Risk endpoint is implemented in Phase 12 (model serving)."}


@router.get("/risk/history")
def risk_history():
    return {"status": "planned", "message": "Risk history is implemented in Phase 12."}


@router.get("/recommendations")
def recommendations():
    return {"status": "planned", "message": "Recommendations are implemented in Phase 15."}
