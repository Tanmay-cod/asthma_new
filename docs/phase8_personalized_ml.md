# Phase 8 — Personalized ML Evaluation

Target (research configuration):

```yaml
clinical_validation_status: "RESEARCH_APPROVED_PENDING_CLINICAL_REVIEW"
target: PEF < 80% personal best for 2 consecutive days within 7 days
baseline_method: pef_best
```

> RESEARCH/DEVELOPMENT ONLY — NOT CLINICALLY VALIDATED.
> PEF deterioration ≠ confirmed asthma exacerbation.

## Split (participant-level, seed 42)

See `artifacts/aamos00/split_summary.json`.

## Model comparison (test set)

See `artifacts/aamos00/model_comparison.csv` and `model_metrics.json`.
Metrics: ROC-AUC, PR-AUC, sensitivity, specificity, F1, Brier — raw and
calibrated (isotonic fitted on VALIDATION probabilities only).

Important observation: isotonic calibration on a very small validation
participant set produces unstable calibrated probabilities — reported honestly
as a limitation. Raw probabilities are used for ranking-oriented analysis.

## Selected development model

XGBoost (see `docs/model_selection.md`), artifact at
`models/phase8_xgboost.pkl`.

## Participant-level evaluation

`artifacts/aamos00/participant_level_metrics.csv` — per-participant
prediction days, positive events, mean/max risk, actual event rate,
sensitivity/specificity where estimable. Not evidence of clinical validity.

## SHAP

`artifacts/aamos00/shap_global_importance.csv` — global mean |SHAP| ranking.
Individual explanations are produced at inference time from the same
TreeExplainer (not persisted for all rows).

## API contract for frontend

```json
{
  "user_id": "...", "prediction_date": "...", "prediction_horizon_days": 7,
  "risk_probability": 0.0, "risk_level": "LOW|MODERATE|HIGH",
  "target": "pef_deterioration",
  "target_definition": "PEF below 80% of personal best for 2 consecutive days within 7 days",
  "personal_best_pef": null, "current_pef": null,
  "current_pef_percent_personal_best": null,
  "top_risk_factors": [], "protective_factors": [],
  "model_version": "phase8_xgboost"
}
```

Populate factor arrays from actual SHAP values only.

## Safety boundaries

- No medication advice, no diagnosis, no emergency-care replacement.
- SpO₂ and dust excluded from training (monitoring-only signals).
- Model and safety layer remain separate.
