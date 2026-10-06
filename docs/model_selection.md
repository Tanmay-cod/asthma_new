# Model Selection

Development model chosen: **XGBoost** (`models/phase8_xgboost.pkl`).

Criteria documented:
1. Discrimination — ROC-AUC/PR-AUC (see `model_metrics.json`)
2. Calibration — Brier raw 0.044 (xgboost); calibration instability noted
3. Sensitivity/specificity — reported
4. Participant-level robustness — see `participant_level_metrics.csv`
5. Interpretability — SHAP TreeExplainer support
6. Reproducibility — seed 42, deterministic pipeline
7. Deployment feasibility — fast inference on a small feature vector

Random Forest produced the highest raw ROC-AUC in this run (0.993) but its
calibration was unstable; XGBoost was preferred for SHAP compatibility and
smaller artifact complexity. If performance is similar, the simpler,
more interpretable model wins — neither is clinically superior.

No claim of clinical superiority is made.
