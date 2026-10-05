from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SensorReading, SensorType, PefrReading, SymptomAssessment, User
from app.security.auth import get_current_user

router = APIRouter(tags=["measurements"])


@router.get("/readings/latest")
def latest_readings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    out = {}
    for st in SensorType:
        r = (db.query(SensorReading)
             .filter(SensorReading.user_id == user.id, SensorReading.sensor_type == st)
             .order_by(SensorReading.timestamp.desc()).first())
        if r:
            out[st.value] = {"value": r.value, "unit": r.unit, "timestamp": r.timestamp,
                             "data_quality": r.data_quality.value}
    return out


class PefrCreate(BaseModel):
    pefr: float
    unit: str = "L/min"
    notes: str | None = None
    timestamp: datetime | None = None


@router.post("/pefr")
def add_pefr(payload: PefrCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not (50 <= payload.pefr <= 800):
        raise HTTPException(422, "PEFR value outside plausible range (50-800 L/min)")
    row = PefrReading(user_id=user.id, pefr=payload.pefr, unit=payload.unit,
                      notes=payload.notes, timestamp=payload.timestamp or datetime.utcnow())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "pefr": row.pefr, "timestamp": row.timestamp}


@router.get("/pefr")
def list_pefr(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(PefrReading).filter(PefrReading.user_id == user.id)
            .order_by(PefrReading.timestamp.desc()).limit(50).all())
    return [{"id": r.id, "pefr": r.pefr, "unit": r.unit, "timestamp": r.timestamp} for r in rows]


class SymptomCreate(BaseModel):
    cough: int = 0
    wheezing: int = 0
    shortness_of_breath: int = 0
    chest_tightness: int = 0
    night_symptoms: bool = False
    exercise_limitation: bool = False
    notes: str | None = None


@router.post("/symptoms")
def add_symptoms(payload: SymptomCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = SymptomAssessment(user_id=user.id, **payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "timestamp": row.timestamp}


@router.get("/symptoms")
def list_symptoms(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(SymptomAssessment).filter(SymptomAssessment.user_id == user.id)
            .order_by(SymptomAssessment.timestamp.desc()).limit(50).all())
    return [{"id": r.id, "cough": r.cough, "wheezing": r.wheezing,
             "shortness_of_breath": r.shortness_of_breath, "chest_tightness": r.chest_tightness,
             "night_symptoms": r.night_symptoms, "timestamp": r.timestamp} for r in rows]


@router.get("/baseline")
def get_baselines(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
