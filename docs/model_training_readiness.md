# Model Training Readiness Checklist

Phase 6 verification. Clinical items intentionally UNCHECKED.

## Data
- [x] Raw data integrity verified (SHA-256 inventory + test 9)
- [x] Schema validation implemented (`data_validation.py`)
- [x] Missingness documented (`data_inventory.json`, `aamos00_data_quality.md`)
- [x] Daily PEF aggregation implemented (`aggregation.py`)
- [x] Baselines implemented (`baselines.py`)
- [x] Temporal features implemented (`features.py`)
- [x] Candidate target generator implemented (`labels.py`)

## Leakage
- [x] Future-feature checks (tests 1–3)
- [x] Baseline leakage checks (tests 4–5, expanding-max participant-boundary bug fixed in Phase 5)
- [x] Patient-level split utility (`dataset.py`, test 6)
- [x] Training-only preprocessing designed (`docs/dataset_split_strategy.md`)
- [x] Trigger vocabulary training-only by design (`features.encode_triggers(vocab=...)`)
- [x] Target/predictor temporal separation (labels use days > T)

## Deployment
- [x] PEF available (manual input)
- [x] HR available (MAX30102)
- [x] temperature available (DHT22)
- [x] humidity available (DHT22)
- [x] symptoms available (app form)
- [x] reliever use available (app form)
- [x] triggers available (app form)
- [x] static profile available (registration)
- [x] SpO₂ documented as monitoring-only (no training feature)
- [x] dust documented as monitoring-only (no PM2.5 conversion)

## Clinical (MUST remain unchecked)
- [ ] Target clinically validated
- [ ] PEF threshold validated
- [ ] Persistence validated
- [ ] Prediction horizon validated
- [ ] Baseline definition validated
- [ ] Symptom/reliever role validated
- [ ] Proxy vs true outcome decided

**Status: NOT READY for model training. READY for future training once the
clinical items are resolved.**
