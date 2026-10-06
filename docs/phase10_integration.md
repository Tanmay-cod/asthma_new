# Phase 10 — Integration

## Architecture

```
ESP8266 (MAX30102/DHT22/GP2Y1010AU0F) + manual PEFR/symptoms/medication
      ↓ device Bearer token
POST /api/v1/iot/readings
      ↓
PostgreSQL (sensor_readings, pefr_readings, symptom_assessments)
      ↓ get_current_user (Supabase JWT)
POST /api/v1/predictions  → inference.predict_for_user (frozen XGBoost)
      ↓ RiskPrediction + PredictionFeature + PredictionExplanation rows
GET  /api/v1/predictions/latest|history|{id}/explanation
POST /api/v1/reports/personalized → per-user report JSON (see personalized_report_spec.md)
      ↓
Next.js dashboard (frontend-next/src/app/dashboard)
```

## User data isolation
Every query filters by `user_id` from the authenticated Supabase identity —
never a frontend-supplied id. `get_current_user` auto-provisions the local
user row on first verified login.

## Personalized feature generation
`services/inference.py::build_features_for_user` builds the user's feature
vector from their own stored PEF / HR / temperature / humidity / symptoms only.
HR baseline = median of the user's own prior HR history (MAX30102-compatible).
Insufficient history → explicit data-quality state, never a fabricated value.

## Frozen model inference
`models/phase8_xgboost.pkl` loaded once; feature order derived from
`app.ml.train.load_xy` (36 ordered inputs). Prediction emits probability,
risk level (low/moderate/high), 7-day horizon, target definition, model version,
data-quality status.

## Individual SHAP
TreeExplainer per prediction; top increasing/decreasing factors returned with
the prediction and persisted to `prediction_explanations`. SHAP = model
contribution, not causation.

## Model versioning
Every prediction stores `model_version_id`/version string + timestamp; history
never overwritten (append-only).

## Safety
ML layer never prescribes/stops/changes medication, never diagnoses, never
replaces emergency assessment. Missing/stale PEF returns a data-quality status,
not a deterioration label.

## Clinical status
Every user-facing report preserves `clinical_validation_status: PENDING`.
