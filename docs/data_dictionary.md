# AAMOS-00 Data Dictionary

Source: `data/aamos00/` (provided dataset, license in `license.txt`).
Dataset: AAMOS-00 — adult asthma monitoring study, 22 participants, ~184 days of phase-2 data.
All dates are **days after study phase-2 start** (integer `date`, day 0 … ~184), **not** calendar timestamps.
`user_key` is a pseudo-anonymized participant identifier.

---

## File: `anonym_aamos00_patient_info.csv` — 22 rows × 28 cols
| Column | Type | Missing | Notes |
|---|---|---|---|
| user_key | int | 0% | participant id |
| sex | categorical | 0% | male/female |
| age_range | categorical (ranges) | 0% | e.g. `30-39yo`, `50+yo` |
| bmi_range | categorical | 0% | e.g. `Obesity`, `Pre-obesity` |
| age_diagnosed_range | categorical | 4.5% | |
| max_pef_expected | int | 0% | expected max PEF, L/min |
| smoker | categorical | 0% | |
| pack_years | float | 0% | |
| race | categorical | 0% | |
| severity | categorical | 0% | asthma severity |
| pef_best | float | 4.5% | personal best PEF, L/min |
| n_inhalers | float | 4.5% | |
| region, nation | categorical | 0% | |
| phase2_start / phase2_end | int | 0% | study window (days) |
| daily_/weekly_/miband_/position_/pef_/inhaler_ start/end_date | int/float | 0–27% | per-device coverage windows |

## File: `anonym_aamos00_dailyquestionnaire.csv` — 1583 rows × 8
| Column | Type | Missing | Notes |
|---|---|---|---|
| user_key, date | int | 0% | |
| daily_night_symp | bool | 0% | night symptoms past 24h |
| daily_day_symp | bool | 0% | day symptoms past 24h |
| daily_limit_activity | bool-ish | 0.1% | |
| daily_prev_inhaler | int 1–5 | 0% | preventer inhaler use |
| daily_relief_inhaler | int | 0% | reliever inhaler puffs |
| daily_triggers | string "5,9" | 0.7% | trigger IDs (see triggers sheet) |

## File: `anonym_aamos00_weeklyquestionnaire.csv` — 324 rows × 12
| Column | Type | Missing | Notes |
|---|---|---|---|
| weekly_night_symp / weekly_day_symp / weekly_limit_activity | float 0–? | 54%/10%/35% | weekly symptom scores |
| weekly_short_breath, weekly_wheeze | int | 0% | |
| weekly_relief_inhaler | int | 0% | |
| weekly_doc / weekly_hospital / weekly_er / weekly_oral | int/float | ~0% | **healthcare utilization — candidate outcome events** |

## File: `anonym_aamos00_endquestionnaire.csv` — 14 rows × 58
SUS System Usability Scale + healthcare empowerment items, Likert `(1) Strongly disagree` … `(5) Strongly agree`. Not used for prediction.

## File: `anonym_aamos00_environment.csv` — 1657 rows × 21
| Column | Type | Notes |
|---|---|---|
| temperature / temperature_min / temperature_max | float | °C (per dataset docs) |
| pressure | int | hPa |
| humidity | int | % |
| wind_speed, wind_deg | float/int | |
| aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3 | float | air quality (missing ~0.3%) |
| grass_pollen, tree_pollen, weed_pollen | categorical Low/Moderate/High | missing ~3% |

## File: `anonym_aamos00_peakflow.csv` — 1516 rows × 6
| Column | Type | Missing | Notes |
|---|---|---|---|
| user_key, date, hour | int | 0% | |
| pef_max | int | 0% | L/min |
| pefs | string "469\|99\|144" | 11.4% | individual blow readings |
| morning | bool | 0% | |

## File: `anonym_aamos00_smartinhaler.csv` — 2904 rows × 4
`user_key, date, hour, name` — inhaler actuation events (e.g. `VENTOLIN`).

## File: `anonym_aamos00_smartwatch{1,2,3}.csv` — ~700k rows × 7
`user_key, date, time (HH:MM:SS), activity_type (code, see miband_activity_lookup), intensity, steps, hr`
`hr` missing 18–33% across files. 6 distinct smartwatch users total.

## Relationships
- All files join on `user_key`; events keyed by `date` (+`hour`/`time` where present).
- `triggers` sheet in the xlsx maps `daily_triggers` IDs to names (1 = none, 2 = a cold, 3 = exercise, 6 = house dust/mites, …).
- `miband_activity_lookup` sheet maps `activity_type` codes to labels (walk, sedentary, …).

## Candidate outcome variables (target candidates — NOT yet validated)
1. `weekly_hospital` > 0 / `weekly_er` > 0 — but very rare; likely insufficient events.
2. Composite exacerbation: sustained increase in symptoms (daily_day_symp / weekly scores) + reliever-inhaler use increase — **must be clinically defined/validated before use**.
3. PEF drop below X% of personal baseline — threshold **requires clinical validation**.

⚠️ No target has been clinically pre-defined in this report. Do not invent one; confirm with a clinician or the study documentation.
