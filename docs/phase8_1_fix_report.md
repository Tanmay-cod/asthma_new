# Phase 8.1 Fix Report

No target change, no model optimization, no clinical validation.

## Fix 1 — hr_baseline

Documented as: median of the user's own prior HR medians (history only, before T).
Defined in `features.hr_features_at`; reproducible from MAX30102 HR history →
DEPLOYMENT READY WITH SENSOR-SOURCE NOTE.

See `docs/deployment_feature_mapping.md`.

## Fix 2 — Individual SHAP persisted

Now generated at training time from the same XGBoost model and feature matrix:

- `artifacts/aamos00/shap_individual_examples.csv` — participant×date×feature rows
- `artifacts/aamos00/shap_individual_examples.json` — structured examples per case

Cases: low / moderate / high / time-varying participant (where present). Missing
categories recorded as `NOT AVAILABLE IN DATA`, not fabricated.

## Calibration

Unchanged: isotonic on validation only, raw vs calibrated Brier reported. Small
validation population limitation retained.

## Test metrics

Unchanged: 3 participants / ~13 positive rows; high uncertainty documented.

## Overlapping windows

Documented; no target change.

## Model file

`models/phase8_xgboost.pkl` regenerated only to reproduce artifacts; target and
hyperparameters unchanged; metrics consistent with Phase 8.
