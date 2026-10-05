# ML Feature Specification

Source of truth: `docs/data_dictionary.md`, `docs/ml_feature_mapping.md`.
Status: **DESIGN ONLY — no model trained.**

Legend for "Leakage risk": does this feature use information occurring AFTER the prediction time?

## Physiological
| Feature | AAMOS-00 source | Deployment source | Unit | Type | Missingness | Preprocessing | Inference-usable | Leakage risk | Clinical validation |
|---|---|---|---|---|---|---|---|---|---|
| pefr_max | peakflow.pef_max | Manual PEFR entry | L/min | numeric | 0% (study weeks) / user-dependent in deployment | best-of-N per session | ✅ | low (use current or past) | baseline definition needs validation |
| pef_pct_of_baseline | derived: pef_max / personal baseline | derived | % | numeric | depends on baseline | personal baseline engine | ✅ | low | threshold semantics need validation |
| heart_rate | smartwatch.hr | MAX30102 | bpm | numeric | 18–33% in AAMOS-00 | median per window, IQR outlier handling | ✅ | low | none for use as feature |
| heart_rate_deviation | derived | derived | bpm | numeric | depends on baseline | personal HR baseline | ✅ | low | none |
| **spo2** | **not present in AAMOS-00** | MAX30102 | % | numeric | — | — | monitoring-only | n/a | excluded from training (see model card) |

## Environmental
| Feature | AAMOS-00 source | Deployment source | Unit | Type | Missingness | Preprocessing | Inference-usable | Leakage risk | Clinical validation |
|---|---|---|---|---|---|---|---|---|---|
| temperature | environment.temperature | DHT22 | °C | numeric | 0% | daily mean/min/max | ✅ | low | none |
| humidity | environment.humidity | DHT22 | % | numeric | 0% | daily mean | ✅ | low | none |
| dust indicator | **no equivalent** | GP2Y1010AU0F | mg/m³ (indicator, uncalibrated) | numeric | — | **decision: EXCLUDED from first AAMOS-00 model** (Option A — no equivalent training feature; no invented conversion to pm2_5) | ❌ for AAMOS-00 model; ✅ for monitoring | — | dust_indicator ≠ PM2.5; calibration required before inclusion |
| pm2_5 / pm10 / pollen / aqi | environment.* | none | — | — | ~0.3–3% | — | ❌ no hardware source | — | excluded unless external source added |

## Symptoms
| Feature | AAMOS-00 source | Deployment source | Type | Missingness | Preprocessing | Inference-usable | Leakage risk | Clinical validation |
|---|---|---|---|---|---|---|---|---|
| daily_night_symp | dailyquestionnaire | symptom form | boolean | 0% | as-is | ✅ | must use day ≤ prediction day | wording kept identical |
| daily_day_symp | dailyquestionnaire | symptom form | boolean | 0% | as-is | ✅ | same | same |
| daily_limit_activity | dailyquestionnaire | symptom form | boolean | 0.1% | as-is | ✅ | same | same |
| weekly_* symptom scores | weeklyquestionnaire | weekly form | ordinal | 10–54% | impute/flag insufficient | ✅ | only past weeks | same |

## Medication
| Feature | AAMOS-00 source | Deployment source | Type | Missingness | Preprocessing | Inference-usable | Leakage risk | Clinical validation |
|---|---|---|---|---|---|---|---|---|
| daily_prev_inhaler | dailyquestionnaire / smartinhaler | medication form | ordinal 1–5 | 0% | as-is | ✅ | past only | none |
| daily_relief_inhaler | dailyquestionnaire / smartinhaler | medication form | count | 0% | as-is | ✅ | past only | none |
| weekly_relief_inhaler | weeklyquestionnaire | weekly form | count | 0% | as-is | ✅ | past only | none |

## Triggers
| Feature | AAMOS-00 source | Deployment source | Type | Missingness | Inference-usable | Leakage risk | Notes |
|---|---|---|---|---|---|---|---|
| daily_triggers | dailyquestionnaire (IDs → trigger names via xlsx sheet) | trigger form | multi-label categorical | 0.7% | ✅ | past only | encode top-k one-hots |

## Static profile
| Feature | AAMOS-00 source | Deployment source | Type | Notes |
|---|---|---|---|---|
| age_range | patient_info | profile | categorical | same variable at registration |
| sex | patient_info | profile | categorical | |
| bmi_range | patient_info | profile | categorical | |
| severity | patient_info | profile | categorical | only if clinically documented by user/clinician |
| smoker, pack_years | patient_info | profile | categorical/numeric | |
| pef_best, max_pef_expected | patient_info | profile | numeric | used for baseline |

## Excluded from ML (monitoring/other)
smartwatch steps/intensity/activity_type, GPS position, SUS end-questionnaire, wind/pressure, uncalibrated pm equivalences, SpO2 (training).
