## Phase 4 update — candidate horizons (descriptive, not validated)

From `docs/pef_target_analysis.csv` (expanding-max baseline, daily best PEF,
16 PEF users):

- H = 1 day: ~1083 opportunities; event rates vary widely by threshold/persistence.
- H = 3 days: ~1053 opportunities.
- H = 7 days: ~1001 opportunities; aligns with weekly recall window.
- H = 14 days: ~916 opportunities.

No horizon is clinically validated yet. All remain `candidate — requires
clinical validation`. See `docs/aamos00_target_validation.md` §7.

---

# Prediction Window Design

Goal: given measurements available **today**, estimate near-term risk.
This is a decision to be finalized with the clinical advisor; the design below
prevents temporal leakage by construction.

## Definition of "prediction time T"

T = the day for which we generate a prediction (use only data with date ≤ T,
and for within-day data only timestamps ≤ T).

## Input window (history)

- Features use data from [T−W, T] (e.g., W = 7 or 14 days) plus static profile.
- Personal baseline computed only from data **before** the input window or from
a preceding baseline period — never including future values.

## Target window (outcome)

- Outcome is defined over (T, T+H] — e.g., PEF deterioration occurring in the
  next H days. H must be set before training and never change per split.
- H is a placeholder (CONFIGURABLE, REQUIRES CLINICAL VALIDATION); a typical
  choice in the literature is a few days to 2 weeks, but we do **not** assert
  any specific clinical validity.

## Explicitly forbidden as predictors

- Any feature with timestamp > T (future symptoms, future PEF, future inhaler
  use, future environment, future hospital/ER/doctor visits).
- Same-day post-T questionnaire responses.
- Any statistic computed over a window extending past T.

## Illustrative example

Predict at T=day 100: "PEF will fall below Y% of personal baseline during
days 101–107" (H=7).
Allowed features: days 93–100 PEF/symptoms/inhaler/environment + profile.
Forbidden: day 101+ anything.

## Rolling evaluation

For evaluation/backtesting, slide T across the observation period, recompute
features strictly from ≤T, and never reuse future data in features.
