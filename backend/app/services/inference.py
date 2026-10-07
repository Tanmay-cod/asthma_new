"""Per-user inference service using the FROZEN XGBoost development model."""
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models import (SensorReading, PefrReading, SymptomAssessment,
                        MeasurementSession, Prediction)

ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = ROOT / "models" / "phase8_xgboost.pkl"
MODEL_VERSION = "phase8_xgboost"
TARGET_DEFINITION = "PEF below 80% of personal best for at least 2 consecutive days within 7 days"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def get_model_input_features() -> list[str]:
    import app.ml.train as t
    import inspect
    # derive from the same function used in training
    src_cols = None
    try:
        _, X, _ = t.load_xy()
        src_cols = list(X.columns)
    except Exception:
        pass
    if src_cols:
        return src_cols
    from app.ml.train import load_xy  # noqa
    raise RuntimeError("cannot determine model feature order")


def data_quality_state(db: Session, user_id: str) -> dict:
    latest_pefr = (db.query(PefrReading).filter(PefrReading.user_id == user_id)
                   .order_by(PefrReading.recorded_at.desc()).first())
    from app.models import MeasurementSession
    hr = (db.query(SensorReading)
          .join(MeasurementSession, SensorReading.session_id == MeasurementSession.id)
          .filter(MeasurementSession.user_id == user_id)
          .order_by(SensorReading.recorded_at.desc()).first())
    state = {"pefr": "GOOD_DATA" if latest_pefr else "SENSOR_UNAVAILABLE",
             "hr": "GOOD_DATA" if hr else "SENSOR_UNAVAILABLE"}
    if latest_pefr and (datetime.utcnow() - latest_pefr.recorded_at.replace(tzinfo=None)).total_seconds() > 86400 * 7:
        state["pefr"] = "STALE_DATA"
    if not latest_pefr and not hr:
        state["overall"] = "INSUFFICIENT_DATA"
    else:
        state["overall"] = "GOOD_DATA"
    return state


def build_features_for_user(db: Session, user) -> dict:
    """Approximate deployment-compatible feature vector from stored user data.
    Missing history yields explicit NaN/null — no fabricated values."""
    pefrs = (db.query(PefrReading).filter(PefrReading.user_id == user.id)
             .order_by(PefrReading.recorded_at.desc()).limit(14).all())
    from app.models import MeasurementSession
    hrs = (db.query(SensorReading)
           .join(MeasurementSession, SensorReading.session_id == MeasurementSession.id)
           .filter(MeasurementSession.user_id == user.id)
           .order_by(SensorReading.recorded_at.desc()).limit(100).all())
    temps = hrs
    hums = hrs
    syms = (db.query(SymptomAssessment).filter(SymptomAssessment.user_id == user.id)
            .order_by(SymptomAssessment.timestamp.desc()).limit(7).all())

    def vals(rows, attr):
        return [getattr(r, attr) for r in rows if getattr(r, attr, None) is not None]

    pef_vals = vals(pefrs, "pef_l_min")
    hr_vals = vals(hrs, "heart_rate")
    temp_vals = vals(temps, "temperature_c")
    hum_vals = vals(hums, "humidity_percent")

    personal_best = max(pef_vals) if pef_vals else None
    pb_vals = [p.personal_best_l_min for p in pefrs if p.personal_best_l_min]
    if pb_vals:
        personal_best = max(pb_vals)

    def pct_of_best():
        if pef_vals and personal_best:
            return pef_vals[0] / personal_best * 100
        return np.nan

    reliever_cats = []
    hr_baseline = float(np.median(hr_vals)) if hr_vals else np.nan  # prior personal HR history

    return {
        "personal_best_pef": personal_best,
        "current_pef": pef_vals[0] if pef_vals else None,
        "current_pef_pct_best": pct_of_best(),
        "recent_pef_mean": float(np.mean(pef_vals)) if pef_vals else np.nan,
        "recent_pef_min": float(np.min(pef_vals)) if pef_vals else np.nan,
        "recent_pef_max": float(np.max(pef_vals)) if pef_vals else np.nan,
        "hr_baseline": hr_baseline,
        "hr_median_7d": float(np.median(hr_vals[:7])) if hr_vals else np.nan,
        "temperature_mean_7d": float(np.mean(temp_vals)) if temp_vals else np.nan,
        "humidity_mean_7d": float(np.mean(hum_vals)) if hum_vals else np.nan,
        "symptoms_recent": [{"timestamp": s.timestamp.isoformat(), "cough": s.cough,
                              "wheezing": s.wheezing} for s in syms],
        "recent_pef": [p.pef_l_min for p in pefrs],
    }


def risk_level(p: float) -> str:
    if p < 0.33:
        return "low"
    if p < 0.66:
        return "moderate"
    return "high"


def predict_for_user(db: Session, user) -> dict:
    quality = data_quality_state(db, user.id)
    feats = build_features_for_user(db, user)
    if quality["overall"] == "INSUFFICIENT_DATA" or feats["current_pef"] is None:
        return {"user_id": user.id, "data_quality": quality, "risk": None,
                "message": "Insufficient data for a reliable inference"}

    model = get_model()
    cols = get_model_input_features()
    row = {c: np.nan for c in cols}
    # map available engineered values into the model feature vector best-effort
    mapping = {
        "pef_max": feats["current_pef"],
        "pef_best": feats["personal_best_pef"],
        "max_pef_expected": feats["personal_best_pef"],
        "baseline_pef_best": feats["personal_best_pef"],
        "hr_baseline": feats["hr_baseline"],
        "hr_median_7d": feats["hr_median_7d"],
        "temperature_mean_7d": feats["temperature_mean_7d"],
        "humidity_mean_7d": feats["humidity_mean_7d"],
    }
    for k, v in mapping.items():
        if k in row and v is not None and not (isinstance(v, float) and np.isnan(v)):
            row[k] = v
    X = pd.DataFrame([row])[cols].fillna(0)
    proba = float(model.predict_proba(X)[0][1])

    # SHAP for this single prediction
    try:
        import shap
        expl = shap.TreeExplainer(model)
        sv = expl.shap_values(X)
        shap_pairs = sorted(zip(cols, sv[0]), key=lambda kv: abs(kv[1]), reverse=True)
        top_inc = [{"feature": f, "shap_value": round(float(v), 4)} for f, v in shap_pairs if v > 0][:5]
        top_dec = [{"feature": f, "shap_value": round(float(v), 4)} for f, v in shap_pairs if v < 0][:5]
    except Exception:
        top_inc, top_dec = [], []

    import uuid
    pred = Prediction(id=str(uuid.uuid4()), user_id=user.id,
                      risk_score=round(proba, 4), risk_level=risk_level(proba),
                      model_version=MODEL_VERSION,
                      data_quality=feats.get("data_quality", quality["overall"]),
                      explanation={"top_increasing": top_inc, "top_decreasing": top_dec})
    db.add(pred); db.commit(); db.refresh(pred)

    return {
        "user_id": user.id, "prediction_id": pred.id, "prediction_timestamp": pred.prediction_time.isoformat(),
        "model_version": MODEL_VERSION, "prediction_horizon_days": 7,
        "risk_probability": round(proba, 4), "risk_level": risk_level(proba),
        "target": "pef_deterioration", "target_definition": TARGET_DEFINITION,
        "personal_best_pef": feats["personal_best_pef"], "current_pef": feats["current_pef"],
        "current_pef_pct_best": round(feats["current_pef_pct_best"], 1) if not np.isnan(feats["current_pef_pct_best"]) else None,
        "top_risk_factors": top_inc, "protective_factors": top_dec,
        "data_quality": quality,
    }
