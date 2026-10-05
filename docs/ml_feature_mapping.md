# ML Feature Mapping — AAMOS-00 ↔ Deployed IoT Features

The deployed system can only use features such-that the same signals exist from
your ESP8266 hardware. Training on variables not available at inference time is
leakage/impossibility.

| AAMOS-00 variable | Unit | Available in deployed system? | Deployment source | Notes |
|---|---|---|---|---|
| `pef_max` (peakflow) | L/min | ✅ | Manual PEFR entry | Same quantity. Model uses % of personal baseline. |
| `pefs` individual blows | L/min | ⚠️ derived | Manual entry (best-of-3 possible) | Optional. |
| `hr` (smartwatch) | bpm | ✅ | MAX30102 | Same variable (heart rate). |
| `steps`, `intensity`, `activity_type` | — | ❌ | Not in hardware | Would need smartwatch; exclude or document external source. |
| `daily_night_symp`, `daily_day_symp`, `weekly_*` | score/bool | ✅ (manual) | Symptom questionnaire form | Must match questionnaire wording. |
| `daily_prev_inhaler`, `daily_relief_inhaler`, `weekly_relief_inhaler` | count | ✅ (manual) | Medication tracking form | Include as adherence/usage features. |
| `daily_triggers` (IDs) | categorical | ✅ (manual) | Trigger tracking | Same trigger taxonomy. |
| `date`, `hour`, `time` | day/time | ✅ | Device NTP timestamp | Used for windowing/features. |
| `temperature`, `humidity` | °C, % | ✅ | DHT22 | Present in both. |
| `pm2_5`, `pm10`, `aqi`, no2, o3, so2, co, nh3 | µg/m³ etc. | ⚠️ not equivalent | GP2Y1010AU0F dust indicator | **Do not equate dust indicator with calibrated PM2.5.** Use only as "dust indicator" in both or drop one. |
| Pollen levels (grass/tree/weed) | Low/Mod/High | ❌ | — | Optional external data; else exclude. |
| Wind/pressure | | ❌ | — | Exclude. |
| `severity`, `age_range`, `sex`, `bmi_range`, `smoker`, `pack_years`, `pef_best`, `max_pef_expected` | static | ✅ | User profile form | Available at registration. |
| `name` (smartinhaler, e.g. VENTOLIN) | categorical | ✅ | Medication form | Use as reliever-use flag/count. |
| GPS `position` | | ❌ | — | Exclude (privacy). |
| SUS / empowerment end questionnaire | Likert | ❌ | — | Exclude from model. |

**SpO2**: AAMOS-00 smartwatch files contain NO SpO2 column. Your MAX30102 SpO2
therefore has **no direct training counterpart** — a deployed model using SpO2
cannot be trained on AAMOS-00 without an external SpO2 dataset. This must be
documented as a limitation (see `docs/model_card.md` once created).

## Recommended deployable feature set (initial candidate, pending clinical validation)

- `pefr_pct_of_baseline` (manual PEFR vs personal best)
- `heart_rate` (+ deviation from personal baseline)
- `temperature`, `humidity` (DHT22; optionally also ambient env match)
- `dust_indicator` (GP2Y1010AU0F, same variable name in training and deployment)
- `reliever_use_count` (manual tracking)
- `symptom scores` (daily/weekly questionnaire)
- static profile: age_range, sex, bmi_range, severity, smoker

Features in AAMOS-00 not mirrored by hardware are **excluded** from the
deployed model unless an external source is added.
