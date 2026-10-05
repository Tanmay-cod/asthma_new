# Leakage Analysis

Longitudinal, repeated-measures dataset → elevated leakage risk. Rules:

## 1. Patient leakage
- Same `user_key` must never appear in both train and test.
- Split by `user_key` (participant-level), stratified by usable covariates if desired.

## 2. Temporal leakage
- Features at prediction day T use only measurements with date ≤ T.
- Targets are defined on (T, T+H] only.
- Personal baselines must be computed from data before T (or from a held-out
  baseline period); a baseline derived from the whole series leaks the target.
- Rolling statistics (means, deviations) must be computed with a strictly
  trailing window.

## 3. Target leakage through proxies
- Reliever-inhaler use and symptom scores are themselves part of the candidate
  outcome ("exacerbation"). Using same-day symptom/inhaler values as predictors
  for an outcome defined by the same construct can be circular.
  → Mitigation: define the outcome window to start the **day after** the last
  predictor day, and/or require symptom deterioration to be *new* relative to
  the input window.
- `weekly_doc`/`weekly_oral` reflect care received — if a doctor visit itself
  is the treatment response to the deterioration, using future visit records as
  outcome components with current predictors is fine temporally, but
  "weekly_oral" as a predictor is near-constant and non-discriminative.

## 4. Encoding / preprocessing leakage
- Fit imputers, scalers, encoders, baselines on the training partition only,
  then apply to validation/test.
- Handle `pefs` (pipe-separated triple) by exploding before computing
  any statistics; do not use count of non-null pefs as an implicit feature.
- `daily_triggers` IDs must be validated against the triggers sheet; unknown IDs
  mapped to a single "unknown" bucket fitted on train only.

## 5. Duplicate / near-duplicate leakage
- `anonym_aamos00_smartwatch1/2/3.csv` — verify no duplicate
  (user_key, date, time) rows across the three files before merging.
- Deduplicate submissions (same user, date, hour measured twice) with a rule
  (e.g., keep best-of-N for PEF, median for hr), fitted on train only.

## 6. Deployment-compatibility check
- A feature is legal only if the production system (IoT + manual forms) can
  produce it at inference time with the same unit, encoding, and definition.
  See the compatibility table in `docs/ml_feature_specification.md`.
