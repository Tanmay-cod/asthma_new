# AAMOS-00 Target Validation

Phase 4 output. Sources: `data/aamos00/aamos00_anonym_data_documentation.docx`,
`data/aamos00/aamos00_data_dictionary.xlsx`, and the raw CSVs.
No model trained; no threshold presented as clinically validated.

---

## 1. Confirmed by the original documentation

- Study: "AAMOS-00 Study: Predicting Asthma Attacks Using Connected Mobile
  Devices and Machine Learning" (Kevin C.H. Tsang et al., IRAS 285505,
  REC 20/EE/0286, BMJ Open protocol DOI: 10.1136/bmjopen-2022-064166).
- 22 participants, UK, phase-2 monitoring June 2021–June 2022, 2054 unique
  patient-days (per documentation), dates stored relative to phase-2 start.
- Anonymisation removed medication list, dates of entry, locations; dates
  transformed to days-after-phase-2-start; user keys re-randomised 100–999.
- License: CC BY 4.0; attribution required to participants and investigators.

### Weekly outcome fields (exact semantics from the xlsx)

| Field | Question | Encoding |
|---|---|---|
| `weekly_hospital` | Hospitalised due to asthma in past week? | 0 = No; −1 = yesterday, −2 = 2 days ago … −7 = 7 days ago |
| `weekly_er` | ER visit for asthma in past week? | same 0 / −n encoding |
| `weekly_doc` | GP/asthma doctor visit (not regular visits) in past week? | same 0 / −n encoding |
| `weekly_oral` | Systemic corticosteroids in past week? | 1 = No, 2 = Yes (≤ usual), 3 = Yes (> usual), 4 = unsure |

So non-zero values are **event timing ("how many days ago"), not counts**.
`weekly_oral` is coded 1–4 (NOT 0/1); our earlier "99.7% nonzero" note refers
to that numeric coding, i.e. nearly everyone reports "No". Usable as an
exacerbation proxy only in its "more than usual" (value 3) direction and only
as a weak signal.

**Limitation:** These fields are self-reported weekly aggregates; AAMOS-00 is a
monitoring feasibility study, not a validated exacerbation trial. None of these
fields is a validated clinical outcome definition on its own.

## 2. PEF data analysis (from `anonym_aamos00_peakflow.csv`)

- Participants with PEF measurements: **16** (of 22).
- Rows: 1516 session records; per-user per-day best PEF values span day 0–~186.
- `pef_max` = "The maximum PEF out of three PEF measurements taken" (L/min) —
  already a best-of-3 session value.
- `pefs` = the three individual blows as "v1|v2|v3"; 11.4% missing.
- `morning` boolean; `hour` 0–23 → both session and day structure exist;
  multiple sessions per day occur (per-user per-day best used for daily series).
- `patient_info.pef_best` = self-reported personal best (4.5% missing);
  `max_pef_expected` = theoretical max from age/sex/height.

## 3. Baseline alternatives

| Option | Definition | Data required | Deployment-ready | Leakage | Stability | First-version suitability |
|---|---|---|---|---|---|---|
| A. `pef_best` (user-reported) | static per user | registration input | ✅ | none temporal | static; may be stale | ✅ use as reference, but self-reported |
| B. personal historical max | max of all PEF so far | all prior PEF | ✅ | must exclude day T (shift(1)) | drifts upward | ✅ dynamic variant |
| C. rolling baseline (e.g. 7–14d median) | median over trailing window | last W days | ✅ | uses only past | responsive; can drift with deterioration | ⚠️ good for trend features |
| D. initial baseline period | mean/median of first N days | first N days only | after onboarding | none if fixed from past | stable but anchored to possibly unrepresentative period | ⚠️ fixed per user |

Recommended: report all three derived features (% of static pef_best, % of
expanding max so far, % of rolling median) and let the model compare; the
semantics must be documented per feature. No single clinically valid choice is
asserted.

## 4. Candidate target formulations (no selection made)

- **Target A**: PEF < X% of personal baseline at any time in (T, T+H].
- **Target B**: PEF < X% for ≥ N consecutive days within (T, T+H].
- **Target C**: PEF drops ≥ X% relative to user's recent rolling baseline.
- **Target D**: PEF deterioration (A or B) AND symptom deterioration and/or
  increased reliever use.

All thresholds/window lengths are **candidates — require clinical validation**.

## 5. Event statistics (computed, descriptive only)

See `docs/pef_target_analysis.csv` — 72 configurations
(threshold 60/70/75/80/85/90% × N=1/2/3 × H=1/3/7/14).
Method: daily best PEF per user; baseline = expanding max of that user's prior
days (`shift(1)` — no same-day leakage); outcome = ≥N consecutive days below
X% of baseline within the next H days.

Illustrative rows (NOT validated):
- 80%, N=1, H=3: 49.5% event rate, 10/16 participants
- 80%, N=2, H=7: 41.3%, 8 participants
- 80%, N=3, H=7: 29.7%, 8 participants
- 85%, N=3, H=7: 50.3%, 9 participants
- 60%, N=3, H=14: 6.7%, 1 participant (too rare)

These are descriptive; no threshold chosen. Rare-event configurations
(60%, N≥2, H=1) have ~0 events.

## 6. Symptom/reliever signal design

- Predictors: `daily_day_symp`, `daily_night_symp`, `daily_limit_activity`,
  `daily_prev_inhaler`, `daily_relief_inhaler`, `daily_triggers` — all usable
  as predictors if restricted to days ≤ T.
- Target components: allowed only if temporally separated — the target window
  must start AFTER the last predictor day.
- Circularity example: "increased reliever use" as outcome ⇒ same-day
  `daily_relief_inhaler` must not be a predictor of that outcome at the same T.
- `daily_relief_inhaler` encoding is ranged (0,1-2,3-4,5-8,9-12,12+) —
  ordinal, not a count.

## 7. Prediction horizons

| Horizon | Opportunities (typical) | Notes |
|---|---|---|
| 1 day | ~1083 | shortest, most events per day but very noisy PEF; candidate |
| 3 days | ~1053 | balances noise and utility; candidate |
| 7 days | ~1001 | aligns with weekly symptom recall; candidate |
| 14 days | ~916 | more clinically actionable but fewer labels; candidate |

All are **candidates — require clinical validation**.

## 8. Deployment compatibility

| Feature | AAMOS-00 | ESP8266 / manual app | Same definition? | Training allowed? | Notes |
|---|---|---|---|---|---|
| PEF | peakflow.pef_max (L/min) | manual entry | ✅ | ✅ | best-of-3 available in app |
| HR | smartwatch.hr | MAX30102 | ✅ | ✅ | same quantity |
| SpO₂ | none | MAX30102 | n/a | ❌ monitoring-only | document limitation |
| Temperature | environment.temperature | DHT22 | ✅ (ambient) | ✅ | |
| Humidity | environment.humidity | DHT22 | ✅ | ✅ | |
| Dust | pm2_5/pm10 (calibrated) | GP2Y1010AU0F indicator | ❌ not equivalent | ❌ (excluded from AAMOS-00 model) | monitoring-only unless calibration established |
| Symptoms | daily/weekly questionnaires | symptom form | ✅ | ✅ | same wording |
| Reliever use | daily_relief_inhaler ranges / inhaler events | medication form | ✅ | ✅ | |
| Triggers | daily_triggers IDs | trigger form | ✅ | ✅ | same taxonomy |
| Static profile | patient_info | profile | ✅ | ✅ | |

## 9. Leakage & data-quality notes

- `pefs` pipe-separated triple — explode before statistics.
- Smartwatch hr missing 18–33% — imputation fit on training fold only.
- `weekly_*` encoding of healthcare events uses negative day offsets — parse
  carefully; do not treat as counts.
- 6 of 22 participants have no PEF records; exclude or treat separately.

## 10. Unresolved questions (→ `docs/clinical_validation_questions.md`)

- Clinical meaning of PEF %-of-baseline thresholds
- Whether deterioration must persist (N) and over what horizon (H)
- Whether symptoms/reliever use must be co-required
- Proxy vs true clinical outcome
- Dust indicator calibration validity

## Conclusion

`MODEL TRAINING BLOCKED — CLINICAL TARGET DEFINITION NOT YET VALIDATED`
