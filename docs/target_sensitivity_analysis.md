# Target Sensitivity Analysis (descriptive only)

> This is descriptive sensitivity analysis only. No clinical target was
> selected or validated.

## Candidate grid

72 configurations: threshold ∈ {60,70,75,80,85,90}% × persistence ∈ {1,2,3}
days × horizon ∈ {1,3,7,14} days, baseline = `expanding_max` (primary).
Baseline method itself varied descriptively for two representative configs
(`80%/2d/7d`, `85%/2d/7d`) against `pef_best`, `expanding_max`,
`rolling_median` in `artifacts/aamos00/baseline_sensitivity.csv`.

## Event distribution (72 configs)

- Opportunities per config: 916–1083
- Positive events per config: 0–925; event rate 0.0–0.975
- Median event rate across configs ≈ 0.23
- `docs/pef_target_analysis.csv` / `artifacts/aamos00/target_sensitivity.csv`

## Participant concentration

- Participants with ≥1 event per config: 0–13 of 16 PEF users
- Many configs concentrate events: max events/participant often 74–165,
  median ~28–55 → a few participants dominate positives
- `median_days_between_events` ≈ 1 day in most configs → events are
  temporally clustered, i.e. rolling prediction rows around the same
  deterioration episode are **not independent**

## Overlapping windows

With H=7 and daily predictions, window(T) = days T+1..T+7 overlaps window(T+1)
by 6 of 7 days. Positive rows therefore cluster and cannot be treated as
independent events in accuracy estimates. Consequence: evaluation must report
both row-level and person-level metrics, and confidence intervals should be
clustered by participant.

## Cold-start

- `expanding_max` baseline unavailable until a participant's first PEF day
  (pipeline removed 16 cold-start rows; 15 participants remain)
- `pef_best` available from registration (no temporal cold start, but
  self-reported)
- `rolling_median` needs ≥3 prior days within the window
- 6 of 22 participants have no PEF data at all → unusable for PEF targets

## Baseline sensitivity (representative)

| Config | Baseline | Event rate | Participants w/ events | Max events/participant |
|---|---|---|---|---|
| 80/2/7 | pef_best | 0.292 | 7 | 127 |
| 80/2/7 | expanding_max | 0.413 | 8 | 118 |
| 80/2/7 | rolling_median | 0.018 | 3 | 6 |
| 85/2/7 | pef_best | 0.401 | 7 | 136 |
| 85/2/7 | expanding_max | 0.616 | 9 | 137 |
| 85/2/7 | rolling_median | 0.041 | 6 | 10 |

`rolling_median` flags far fewer deteriorations because the trailing median
adapts downward during sustained declines — it measures deviation from a
*moving* reference rather than a fixed personal best. No baseline chosen.

## Symptom / reliever co-occurrence (descriptive)

On days with PEF < 80% of prior expanding max (n=334):
- daily day symptoms also reported: 0.98 (overall rate 0.85)
- night symptoms: 0.19 (overall 0.21)
- activity limitation: 0.56
- reliever use > 0: 0.38 (overall 0.48)
→ PEF dips frequently coincide with reported symptoms, but this is
**co-occurrence observed in AAMOS-00**, not confirmation of exacerbation.

## Weekly clinical event comparison (descriptive)

Weeks with non-zero coded events: hospitalization 6/324, ER 7/324,
doctor visit 43/324, oral steroids (> usual) 82/324. These are too rare
(hospital/ER) to serve as ML labels and are not validated exacerbation
definitions. Temporal overlap between PEF-deterioration episodes and these
weekly codes should be examined with clinician input before any use.

## Limitations

- 22 participants total; 16 with PEF; 15 after cold-start
- Self-reported questionnaires; consumer sensors
- No validated exacerbation endpoint; dates are relative study days
- Deployment sensors (DHT22, GP2Y1010AU0F, MAX30102) do not perfectly
  reproduce AAMOS-00 environment/smartwatch measurements
- Target not clinically validated

`MODEL TRAINING BLOCKED — CLINICAL TARGET DEFINITION NOT YET VALIDATED`
