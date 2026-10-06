# Clinical Target — One-Page Summary

**Objective.** Personalized asthma risk monitoring with explainable ML, deployed
with ESP8266 + MAX30102 + DHT22 + GP2Y1010AU0F + manual PEFR.

**Dataset.** AAMOS-00: 22 participants, 16 with PEF (`pef_max` = best of 3,
L/min), weekly outcomes coded as event timing (hospital/ER/doc: 0/−1…−7;
oral: 1–4). No validated exacerbation endpoint established.

**Candidate target.** `PEF deterioration` — below X% of personal baseline for N
consecutive days within horizon H. Nothing yet validated.

**Choices to approve:**
- Threshold X ∈ {60,70,75,80,85,90}%
- Persistence N ∈ {1,2,3} days
- Horizon H ∈ {1,3,7,14} days
- Baseline ∈ {pef_best, expanding_max, rolling_median}
- Symptoms Yes/No · Reliever component Yes/No
- Proxy target vs validated clinical outcome

**Sensitivity highlights (descriptive only):** 80%/2d/7d → 41% events;
85%/2d/7d → 62%; rolling-median baseline → 2–4%. Events concentrated in few
participants; rolling-window labels overlap in time.

**Questions for the advisor (top):**
1. What PEF drop is clinically meaningful, and relative to what baseline?
2. Must it persist, and for how long?
3. What warning horizon is actionable?
4. Must symptoms/reliever use be required?
5. Is PEF deterioration an acceptable proxy, or is a true clinical outcome required?
6–15. See `docs/clinical_target_decision_package.md` §12.

**Approval checklist.** Training gate in decision package §14; schema at
`docs/clinical_target_schema.yaml` (status: pending). Until approved:

`MODEL TRAINING BLOCKED — AWAITING CLINICAL TARGET VALIDATION`
