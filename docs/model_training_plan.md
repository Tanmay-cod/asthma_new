# Model Training Plan (DESIGN ONLY — not executed)

Pipeline (all steps reproducible, versioned):

1. **Raw AAMOS-00 ingestion** — read the 12 CSVs, store raw checksums + row counts,
   never modify raw files.
2. **Validation** (`backend/app/ml/validation.py` — to be implemented):
   schema check per file (columns, dtypes, allowed ranges), dedupe, referential
   check on `user_key`, report per-file coverage windows.
3. **Temporal feature construction**:
   - For each prediction day T per user: trailing-window features (7/14d) for
     PEF (mean, min, % of baseline, trend), hr (median, deviation), symptoms
     (count of symptomatic days), reliever use (counts), environment (mean temp,
     mean humidity), triggers (top-k one-hots), static profile.
   - Personal baseline per user computed from data prior to T.
4. **Patient-level split** — GroupKFold-style by `user_key`; temporal order
   preserved; test set = whole participants held out entirely.
5. **Preprocessing** — missingness indicators; imputers/scalers fit on train only.
6. **Models** — Logistic Regression (baseline), Random Forest, XGBoost; same
   feature matrix for fair comparison. All artifacts labeled
   `DEVELOPMENT MODEL — NOT CLINICALLY VALIDATED` until validated.
7. **Calibration** — Platt scaling / isotonic on validation set; report Brier
   score + calibration curve.
8. **Evaluation** — sensitivity, specificity, precision, recall, F1, ROC-AUC,
   PR-AUC, Brier; confusion matrix; **never accuracy alone**.
9. **SHAP** — TreeExplainer for tree models; store per-prediction top
   contributors + feature values + explanation version.
10. **Registry** — `model_versions` table rows: name, version, dataset
    version, feature schema version, training date, is_development_model flag,
    artifact path.
11. **Retraining** — pipeline is deterministic w.r.t. dataset version; new
    dataset version triggers a new registry row, never overwrites.

Synthetic fallback (current `app/ml.py`) remains clearly labeled
`DEVELOPMENT ONLY — NOT CLINICALLY VALIDATED` and is excluded from any
clinical claim.

## Stop conditions
- No training until: target clinically validated, feature mapping signed off,
  prediction window confirmed, splitting strategy reviewed.
