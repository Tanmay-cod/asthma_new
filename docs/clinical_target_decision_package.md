# Clinical Target Decision Package

For review by a qualified asthma/clinical advisor.
**This document is for clinical target definition and does not establish a validated clinical endpoint.**

## SECTION 1 — PROJECT PURPOSE

This project develops a personalized asthma monitoring/risk system using
AAMOS-00 as the primary research dataset, deployed with:
- ESP8266 (NodeMCU)
- MAX30102 (SpO₂, HR)
- DHT22 (temperature, humidity)
- GP2Y1010AU0F (dust indicator)
- Manual PEFR, symptoms, and medication tracking

## SECTION 2 — WHAT AAMOS-00 ACTUALLY PROVIDES

### Participants
- 22 total; 16 with PEF data; 15 represented after cold-start pipeline.

### PEF
- `pef_max` = best of 3 blows, L/min; multiple sessions/day possible; daily
  best is used by the current pipeline.

### Weekly outcomes (confirmed encodings)
- `weekly_hospital`, `weekly_er`, `weekly_doc`: `0` = no, `-1…-7` = days ago
- `weekly_oral`: `1` = no, `2` = yes ≤ usual, `3` = yes > usual, `4` = unsure

These fields are **not** treated as validated clinical exacerbation labels.

## SECTION 3 — DEPLOYMENT COMPATIBILITY

| Signal | AAMOS-00 | Deployment | ML Status |
|---|---|---|---|
| PEF | peakflow.pef_max | Manual PEFR | Candidate ML feature/target |
| HR | smartwatch HR | MAX30102 | ML feature |
| SpO₂ | Not available | MAX30102 | Monitoring-only |
| Temperature | environment temperature | DHT22 | ML feature |
| Humidity | environment humidity | DHT22 | ML feature |
| Dust | PM2.5/PM10 environment variables | GP2Y1010AU0F indicator | Monitoring-only |
| Symptoms | questionnaire | App form | Candidate predictor/target component |
| Reliever use | questionnaire/inhaler data | App form | Candidate predictor/target component |
| Triggers | questionnaire | App form | Candidate predictor |
| Static profile | patient_info | Registration | Candidate predictor |

The dust sensor is **not** presented as calibrated PM2.5.

## SECTION 4 — CANDIDATE TARGET

PEF deterioration:

```text
PEF falls below X% of a personal baseline
for N consecutive days
within a future prediction horizon H
```

X = threshold, N = persistence, H = prediction horizon. No final values assigned.

## SECTION 5 — TARGET SENSITIVITY RESULTS (descriptive only)

- 72 configurations; thresholds 60/70/75/80/85/90%; persistence 1/2/3 days; horizons 1/3/7/14 days; primary baseline `expanding_max`.

| Configuration | Event rate |
|---|---:|
| 80% / 2 days / 7 days | 41.3% |
| 85% / 2 days / 7 days | 61.6% |

DESCRIPTIVE ONLY — NOT CLINICALLY VALIDATED. Neither configuration is optimal.

## SECTION 6 — BASELINE DECISION

80% / 2 / 7: `pef_best` 29.2% | `expanding_max` 41.3% | `rolling_median` 1.8%
85% / 2 / 7: `pef_best` 40.1% | `expanding_max` 61.6% | `rolling_median` 4.1%

- `pef_best`: static, self-reported
- `expanding_max`: historical observed max
- `rolling_median`: trailing median (adapts downward in sustained decline)

**Event-rate differences are not evidence that one baseline is clinically superior.**

## SECTION 7 — PERSISTENCE DECISION

- N=1: more sensitive to single-day variation
- N=2: requires persistence
- N=3: sustained deterioration required

Advisor question: should clinically meaningful deterioration require one day or multiple consecutive days below threshold?

## SECTION 8 — PREDICTION HORIZON

- 1 day: shortest warning
- 3 days: short-term warning
- 7 days: weekly-scale
- 14 days: longer-range

Advisor question: which horizon gives clinically meaningful, actionable warning?

## SECTION 9 — SYMPTOMS AND RELIEVER USE

| Option | Target | Predictor role | Concern |
|---|---|---|---|
| A | PEF deterioration only | symptoms/reliever = predictors | simplest, but misses symptom-only deterioration |
| B | PEF + symptom deterioration | PEF co-predictor | needs symptom-deterioration definition |
| C | PEF + increased reliever use | reliever co-predictor | circularity if same-day reliever used as predictor |
| D | combined | all co-predictors | richest but hardest to validate |

Same-day inclusion of any target component as a predictor is circular — temporal separation required.

## SECTION 10 — CLINICAL OUTCOME VS PROXY

- Possible **outcome**: PEF deterioration (measurable signal).
- **Clinical outcome**: asthma exacerbation (requires accepted clinical definition).

> The current AAMOS-00 dataset does not provide a validated clinical
> exacerbation endpoint that this project has established as the final
> supervised learning target.

## SECTION 11 — SAFETY AND PRODUCT LANGUAGE

Use: `PEF deterioration risk`, `monitoring signal`, `risk indicator`,
`decision-support prototype`, `development model`, `not clinically validated`.

Avoid: `diagnoses asthma attack`, `predicts asthma attack with certainty`,
`medical diagnosis`, `clinically proven`, `guaranteed warning`,
`treatment recommendation`.

The ML model must never prescribe, stop, or change medication.

## SECTION 12 — QUESTIONS FOR THE CLINICAL ADVISOR

### Target definition
1. What constitutes clinically meaningful PEF deterioration?
2. What percentage of personal baseline should be used?
3. Which baseline: personal best, historical maximum, or another accepted baseline?
4. Should deterioration persist 1, 2, or 3 days?
5. What prediction horizon is clinically useful?

### Symptoms
6. Should symptoms be required for the target?
7. Which symptoms matter?
8. Severity or persistence?

### Medication
9. Should reliever use be part of the target?
10. What constitutes meaningful increased reliever use?

### Outcome
11. Is PEF deterioration an acceptable proxy target?
12. If not, what validated clinical outcome should be used?

### Deployment
13. Are manual PEFR measurements acceptable for this prototype?
14. Are the proposed monitoring signals appropriate for a non-diagnostic system?
15. Are any additional safety criteria required?

## SECTION 13 — PROPOSED CONFIGURATION TEMPLATE

```yaml
clinical_validation_status: "PENDING"

target:
  type: "pef_deterioration"
  threshold_pct: null
  consecutive_days: null
  baseline_method: null
  prediction_horizon_days: null

symptom_component:
  enabled: null

reliever_component:
  enabled: null

clinical_outcome:
  type: null

approved_by:
  reviewer_role: null
  date: null
```

## SECTION 14 — TRAINING GATE

```text
MODEL TRAINING MAY BEGIN ONLY WHEN:

[ ] Clinical target definition approved
[ ] PEF threshold approved
[ ] Baseline approved
[ ] Persistence approved
[ ] Prediction horizon approved
[ ] Symptom role approved
[ ] Reliever-use role approved
[ ] Proxy vs clinical outcome decision approved
[ ] Deployment feature mapping approved
```

Until then: **MODEL TRAINING BLOCKED**.
