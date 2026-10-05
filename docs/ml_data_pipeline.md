# ML Data Pipeline (Phase 5)

```
Raw AAMOS-00 (data/aamos00, never modified)
      ↓ ingestion.build_inventory  → artifacts/aamos00/data_inventory.json
      ↓ data_validation.validate_all → artifacts/aamos00/data_validation_report.json
      ↓ aggregation.build_daily_pef  (pef_max best-of-3; daily best = max over sessions)
      ↓ baselines (expanding_max via shift(1); rolling_median; patient_info.pef_best)
      ↓ features: hr / environment / symptoms / medication / triggers (trailing windows, ≤ T)
      ↓ labels.candidate_target (CONFIGURABLE — NOT CLINICALLY VALIDATED)
      ↓ leakage assertions (fail loudly)
      ↓ patient_level_split utility
      ↓ → artifacts/aamos00/feature_matrix.parquet, feature_metadata.json, dataset_summary.json
```

All feature windows use `date <= T` semantics; targets use `(T, T+H]`.
No future data in any feature. SpO₂ and dust indicator are excluded from the
AAMOS-00 training matrix (documented in `docs/ml_feature_specification.md`).

## Candidate target configuration (development only)

```yaml
threshold_pct: 80
consecutive_days: 2
prediction_horizon_days: 7
baseline_method: expanding_max
```

Change the configuration in `backend/app/ml/pipeline.py::CANDIDATE_TARGET`
without touching feature code — see `labels.candidate_configs()` for all 72
analyzed candidates.

## Run

```bash
cd backend
python -m app.ml.pipeline
python -m pytest app/tests/test_ml_pipeline.py
```

## Provenance

- Confirmed by AAMOS-00 docs: per-variable encodings, pef_max semantics, date convention.
- Calculated here: daily PEF aggregation, baselines, trailing features, candidate target events.
- Engineering decisions: expanding-max baseline default, top-5 trigger vocab, range-midpoint reliever categories (kept ordinal).
- Candidate clinical assumptions: 80%/2-day/7-day target config = **NOT VALIDATED**.
