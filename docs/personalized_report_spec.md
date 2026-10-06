# Personalized Report Spec

## Authorization
Only the authenticated user's own data may appear. User A must never see User B's report. AAMOS-00 participant data must not appear in production reports.

## Fields
1. User information — user id, report timestamp (no unnecessary PII)
2. Current measurements — current PEF, personal-best PEF, PEF % of personal best, current HR, temperature, humidity
3. Recent trend — recent PEF values (facts only, no clinical conclusions)
4. Symptoms — recent symptom entries
5. Reliever use — recent reliever pattern (range-coded in AAMOS-00; exact counts not assumed)
6. Personalized model prediction — probability, 7-day horizon, target definition, risk level
7. Individual explanation — top increasing/decreasing SHAP contributors; model contribution ≠ causation
8. Data quality — missing/stale/insufficient/sensor-unavailable states for each source
9. Safety/interpretation — research/development indicator; not a diagnosis; no treatment instructions
10. Model information — model name/version, prediction timestamp, target definition, clinical validation status = PENDING

## Calculation rules
- PEF % personal best = current PEF / personal best × 100
- Personal best = user's stored `baseline_pefr` if set, else max of their recorded PEF values
- HR baseline = median of the user's prior HR history (MAX30102-compatible definition)
- No synthetic values; missing inputs yield explicit data-quality states

## Audit
Store prediction_id, user_id, timestamp, model_version, probability, target
definition, feature snapshot, SHAP explanation, data-quality status. Historical
predictions are append-only.
