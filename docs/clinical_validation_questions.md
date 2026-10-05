# Clinical Validation Questions

Must be answered by a qualified asthma/clinical advisor before any model
training. Until then: MODEL TRAINING BLOCKED.

1. What PEF value constitutes clinically meaningful deterioration relative to
   the patient's personal baseline? Is a single threshold (e.g., 80%)
   appropriate, and at what %?
2. Must deterioration persist for more than one day (N) to be considered
   clinically meaningful?
3. Over what window (H) should deterioration be assessed? Is that window
   useful for a patient-facing warning?
4. Should symptoms (day/night/limitation) be required as co-criteria for an
   exacerbation-risk label?
5. Should increased reliever-inhaler use be part of the outcome, and if so how
   (e.g., doubling of usual puffs)?
6. Are `weekly_hospital` / `weekly_er` / `weekly_doc` / `weekly_oral`
   encodings (negative day-offsets, ordinal 1–4) correct as parsed, and which
   of them represent an asthma exacerbation?
7. Is "PEF deterioration" an acceptable proxy target, or must a validated
   exacerbation definition from the literature/protocol be used?
8. Is `daily_relief_inhaler` range-coding (0, 1–2, 3–4, 5–8, 9–12, 12+)
   suitable, and what increment is clinically meaningful?
9. Can the GP2Y1010AU0F dust indicator ever be calibrated to a validated
   PM2.5/PM10 relationship for use in the model?
10. Does the 14-day prediction horizon have clinical actionability, or is a
    shorter horizon (1–3 days) more appropriate?
