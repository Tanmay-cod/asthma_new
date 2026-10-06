# Phase 8 Audit Report

## Executive Summary

Overall status: **PASS WITH WARNINGS**

Critical failures: none
Warnings: calibration instability on small validation set; individual SHAP
examples not persisted; `hr_baseline` smartwatch-derived baseline; small test
population (3 participants, ~13 positive rows); overlapping target windows.

## 1. Target
Status: PASS
Evidence: `labels.candidate_target` uses PEF < 80% of `pef_best`, ≥2 consecutive
below-threshold days, target window strictly after T (`i+1 .. i+H`). T does not
appear in the outcome window.

## 2. Temporal Leakage
Status: PASS
Evidence: features use `date <= T` semantics; baselines use `shift(1)`; targets
use days > T; tests 1–5 pass.

## 3. Participant Leakage
Status: PASS
Evidence: `patient_level_split` + `leakage.assert_user_partition_disjoint`;
split_summary shows 10/2/3 participants, no overlaps.

## 4. Feature Availability
Status: PASS
Evidence: 38 features in `feature_metadata.json` built from AAMOS-00 files.

## 5. Deployment Compatibility
Status: WARNING
Evidence: all features deployable from ESP8266+MAX30102+DHT22+manual input
EXCEPT `hr_baseline`, which was computed from smartwatch HR history; an
MAX30102-based equivalent requires the user's own historical HR. Recorded in
`deployment_feature_audit.csv`.

## 6. Model Selection
Status: PASS
Evidence: XGBoost chosen via documented criteria (SHAP compatibility,
reproducibility, small artifact, similar performance); test metrics used only
for final reporting.

## 7. Calibration
Status: WARNING
Evidence: isotonic fitted on validation probabilities only; raw vs calibrated
Brier reported; instability expected/reported with tiny val participant set.
see `phase8_calibration_audit.json`.

## 8. Individual Explainability
Status: WARNING
Evidence: global SHAP present; per-prediction individual SHAP examples are NOT
persisted — personalized explainability incomplete until inference-time SHAP
examples are stored.

## 9. Personalization
Status: PASS
Evidence: personal baseline (pef_best) + individual history features + static
profile; population-trained model with individualized inputs.

## 10. Safety
Status: PASS
Evidence: no prescription/diagnosis/emergency-replacement; safety layer
independent; SpO₂ and dust excluded from ML features.

## 11. Reproducibility
Status: PARTIAL
Evidence: seed 42, SH-256 dataset inventory, fixed target config, committed
`train.py`. Calibration instability means exact calibrated probabilities are
not guaranteed to be bit-identical; raw ranking metrics are reproducible.

## 12. Documentation
Status: PASS WITH WARNINGS
Evidence: docs consistent with artifacts; `model_calibration.md` honestly
reports instability; `individual_explainability.md` states examples are
inference-time (not persisted).

## Critical Issues
None.

## Warnings
- `hr_baseline` deployment compatibility
- Individual SHAP examples not persisted
- Calibration instability (tiny val set)
- Test metrics from ~3 participants / ~13 positives — high uncertainty
- Overlapping 7-day target windows → row metrics optimistic

## Recommended Next Step

`REQUIRES ENGINEERING FIXES BEFORE CLINICAL REVIEW`

Specifically: persist individual SHAP examples per prediction and replace the
smartwatch-derived `hr_baseline` with a MAX30102-compatible definition (or
document it as unavailable at deployment and exclude it) before clinical review.

MODEL TRAINING BLOCKED — CLINICAL TARGET DEFINITION NOT YET VALIDATED
