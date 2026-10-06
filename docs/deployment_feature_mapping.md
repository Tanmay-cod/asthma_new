# Deployment Feature Mapping

| Feature | Training source | Deployment source | Same definition? | Status |
|---|---|---|---|---|
| hr_baseline | AAMOS-00 smartwatch HR history (median of prior personal HR medians, `shift(1)` semantics) | MAX30102 HR history (median of the user's prior personal HR medians) | Yes — same quantity defined on the user's own historical HR; sensor source differs (smartwatch vs MAX30102) | DEPLOYMENT READY WITH SENSOR-SOURCE NOTE |
| hr_median_7d / min / max / variability / deviation | smartwatch HR | MAX30102 HR | Yes (same quantity) | READY |
| pef_max / baselines | AAMOS-00 peakflow | manual PEFR | Yes | READY |
| temperature / humidity | environment | DHT22 | Yes (ambient) | READY |
| symptoms | questionnaire | app form | Yes (same wording) | READY |
| reliever use | questionnaire/inhaler | medication form | Yes (ordinal ranges preserved) | READY |
| triggers | questionnaire | trigger form | Yes | READY |
| static profile | patient_info | registration | Yes | READY |

`hr_baseline` is computed as the median of the user's own prior HR medians
(only history strictly before prediction time T). No future data, no target
information. Not a smartwatch-specific statistic — it is recomputable from any
HR source, including MAX30102.

No retraining is strictly required for deployment consistency because the
quantity is identical; small device-to-device distribution differences must be
monitored in production.
