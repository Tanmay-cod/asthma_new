# Clinical Review Package

## 1. Purpose
Define the exact prediction target for clinical review. AAMOS-00 is the primary
research dataset. This document does not establish a validated clinical endpoint.

## 2. Intended Use
Personalized PEF deterioration-risk monitoring for an individual user; research/
development decision-support only.

## 3. Proposed Clinical Target
A future PEF deterioration event within the next 7 days.

## 4. Target Definition
PEF remaining below 80% of the user's personal best for at least 2 consecutive
days within the next 7 days. "Below 80% of personal best" — NOT an 80% drop.
Research-informed candidate pending clinical review.

## 5. Baseline Definition
Personal best PEF (`pef_best`).

## 6. Prediction Horizon
7 days after prediction day T.

## 7. Symptoms
Supporting predictors only (`daily_day_symp`, `daily_night_symp`,
`daily_limit_activity`); outside the formal PEF target definition.

## 8. Reliever Medication Use
Supporting predictor (`daily_relief_inhaler`, ordinal ranges); outside the
formal PEF target definition.

## 9. Why PEF Deterioration Is Being Used
Only AAMOS-00 outcome with enough events (16 PEF users), deployable via manual
PEFR, and directly tied to the user's own baseline. Hospital/ER events too rare.

## 10. What This Model Does NOT Predict
- Asthma attacks (not validated)
- Asthma exacerbations (not validated endpoint)
- Diagnosis, treatment, prognosis
- SpO₂ or dust outcomes

## 11. Candidate User-Facing Risk Output
"Your estimated PEF deterioration risk over the next 7 days is 78%."
Plus contributing factors from SHAP, plus: "This is a research/development risk
indicator and is not a diagnosis or treatment recommendation."

## 12. Explainability
Per-user SHAP values: positive contribution → pushes risk up; negative → pushes
risk down. SHAP describes model contribution, NOT clinical causation.

## 13. Dataset and Evidence
AAMOS-00: 22 participants, 16 with PEF, 15 in current pipeline; 1083 prediction
rows; no SpO₂; smartwatch variables not deployment inputs; dust ≠ calibrated
PM2.5. AAMOS-00 does NOT provide a validated exacerbation endpoint.

## 14. Model Development Summary
XGBoost, participant-level split 10/2/3, 36 model input features,
ROC-AUC 0.9687, PR-AUC 0.6275, sensitivity 0.6154, specificity 0.9691,
F1 0.6154, raw Brier 0.0436. Small-sample caveats apply.

## 15. Known Limitations
Small n; 3 test participants; ~13 positive rows; overlapping 7-day windows;
calibration uncertain (validation = 2 participants); PEF deterioration ≠
exacerbation; home PEF variability; PB quality dependence; temporal/circularity
risks for symptoms/reliever if mis-timestamped; MAX30102 SpO2 monitoring-only;
dust ≠ PM2.5; SHAP not causal; no external validation; no clinical validation.

## 16. Safety Boundaries
Does not diagnose, prescribe, change/stop medication, replace a clinician,
predict confirmed exacerbations/attacks, or replace emergency triage.
Safety layer independent from the ML model.

## 17. Questions Requiring Clinical Decision
Q1 80% threshold? Q2 2 consecutive days? Q3 7-day horizon? Q4 pef_best baseline?
Q5 symptoms as predictors? Q6 reliever as predictor? Q7 symptoms/reliever
outside formal target? Q8 PEF deterioration acceptable research outcome?
Q9 describe as "personalized asthma deterioration risk prediction"?
Q10 safety boundaries appropriate? Each: Approve / Modify / Reject.

## 18. Clinical Approval Record

Clinical validation status: PENDING
Reviewer role: ____
Reviewer name: ____
Date: ____
Decision: [ ] APPROVE [ ] APPROVE WITH MODIFICATIONS [ ] REVISE [ ] REJECT
Approved target: ____
Approved baseline: ____
Approved consecutive-day requirement: ____
Approved prediction horizon: ____
Additional clinical comments: ____

Do not fill. No approval claimed.
