# Clinical Review — One Page

**Purpose.** Personalized asthma deterioration-risk monitoring (AAMOS-00 + IoT).

**Proposed target.** PEF deterioration risk: PEF < 80% of personal best for
≥2 consecutive days within 7 days. Baseline: personal best (`pef_best`).
Symptoms and reliever use = supporting predictors only.

**Dataset.** AAMOS-00: 22 participants, 16 with PEF, 15 in pipeline, 1083 rows.
No validated exacerbation endpoint in AAMOS-00 → this is NOT an exacerbation predictor.

**Model.** XGBoost development model (36 inputs). Test metrics (3 participants,
~13 positives, high uncertainty): ROC-AUC 0.9687, PR-AUC 0.6275, sensitivity
0.6154, specificity 0.9691, F1 0.6154, Brier 0.0436.

**Limitations.** Small n, overlapping windows, calibration uncertainty, home-PEF
variability, SHAP ≠ causation, no external/clinical validation.

**Safety.** No diagnosis, no prescriptions/medication changes, no exacerbation or
attack-prediction claims, not an emergency triage replacement.

**10 decisions for the advisor:**
1. 80% threshold? 2. 2 consecutive days? 3. 7-day horizon? 4. pef_best baseline?
5. Symptoms as predictors? 6. Reliever as predictor? 7. Keep symptoms/reliever
outside the formal target? 8. PEF deterioration acceptable research outcome?
9. Name: "personalized asthma deterioration risk prediction"? 10. Safety boundaries?
(Each: Approve / Modify / Reject.)

**Approval: PENDING** — no clinician sign-off yet.
