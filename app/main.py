import json
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas, ml, alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asthma Risk Prediction System", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/api/users", response_model=schemas.UserOut)
def create_user(u: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.name == u.name).first():
        raise HTTPException(400, "User already exists")
    user = models.User(**u.model_dump())
    db.add(user); db.commit(); db.refresh(user)
    return user


@app.get("/api/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/api/ingest", response_model=schemas.ReadingOut)
def ingest(payload: schemas.SensorPayload, db: Session = Depends(get_db)):
    """Called by ESP8266 firmware, simulator, or manual form. Stores reading + runs prediction."""
    user = db.query(models.User).get(payload.user_id)
    if not user:
        raise HTTPException(404, "User not found")
    reading = models.SensorReading(**payload.model_dump(), timestamp=datetime.utcnow())
    db.add(reading); db.commit(); db.refresh(reading)

    try:
        result = ml.predict_risk(user, reading)
        pred = models.Prediction(
            user_id=user.id,
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            shap_json=json.dumps(result["shap_values"]),
            features_json=json.dumps(result["features"]),
        )
        db.add(pred); db.commit()
        alerts.maybe_alert(user.id, user.name, result["risk_score"], result["risk_level"])
    except Exception as e:
        print("Prediction failed (train model first):", e)
    return reading


@app.get("/api/readings/{user_id}")
def get_readings(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    return (db.query(models.SensorReading)
            .filter(models.SensorReading.user_id == user_id)
            .order_by(models.SensorReading.timestamp.desc())
            .limit(limit).all())


@app.get("/api/prediction/{user_id}", response_model=schemas.PredictionOut)
def get_prediction(user_id: int, db: Session = Depends(get_db)):
    pred = (db.query(models.Prediction)
            .filter(models.Prediction.user_id == user_id)
            .order_by(models.Prediction.created_at.desc()).first())
    if not pred:
        raise HTTPException(404, "No prediction yet")
    shap_values = json.loads(pred.shap_json)
    top = sorted(shap_values.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
    return schemas.PredictionOut(
        risk_score=pred.risk_score,
        risk_level=pred.risk_level,
        shap_values=shap_values,
        top_factors=[{"feature": k, "contribution": v} for k, v in top],
        features=json.loads(pred.features_json),
    )


@app.get("/api/predictions/{user_id}")
def prediction_history(user_id: int, limit: int = 30, db: Session = Depends(get_db)):
    preds = (db.query(models.Prediction)
             .filter(models.Prediction.user_id == user_id)
             .order_by(models.Prediction.created_at.desc())
             .limit(limit).all())
    return [{"risk_score": p.risk_score, "risk_level": p.risk_level, "created_at": p.created_at} for p in reversed(preds)]


# Serve the dashboard
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
