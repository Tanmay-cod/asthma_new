# Target Analysis (AAMOS-00)

Computed from actual files (`data/aamos00/`). No clinical target validated yet.
Encoding note: in the weekly questionnaire, `weekly_hospital` / `weekly_er` /
`weekly_doc` use `0` = none and negative/other values = event day offsets;
averaging must treat any non-zero/non-empty value as an event occurrence.
Exact clinical semantics of these fields must be confirmed against the study
documentation (`aamos00_anonym_data_documentation.docx`) — **not assumed**.

| Candidate target | Definition | Positive weeks | Event rate | Participants with events | Missingness | Leakage-safe definable? | Verdict |
|---|---|---|---|---|---|---|---|
| weekly_hospital | any hospitalization that week | 6 / 324 | 1.9% | 2 / 22 | 0% | yes | ❌ too few events (n=6) for ML |
| weekly_er | any ER visit that week | 7 / 324 | 2.2% | 3 / 22 | 0% | yes | ❌ too few events |
| weekly_doc | any doctor visit that week | 43 / 324 | 13.3% | 9 / 22 | 0.3% | yes | ⚠️ possible but doctor visit ≠ exacerbation |
| weekly_oral | oral steroid use (encoding unconfirmed) | 323 / 324 | 99.7% | 22 / 22 | 0.3% | yes | ❌ near-constant, non-discriminative; semantics unconfirmed |
| symptom deterioration | e.g. new daily_day_symp/night_symp onset or sustained worsening vs prior week | requires definition | — | — | — | yes if defined on past data | ⚠️ most plausible; **needs clinical definition** |
| reliever-use increase | increase in daily_relief_inhaler vs personal baseline | requires definition | — | — | 0% | yes | ⚠️ usable proxy signal |
| PEF deterioration | pef_max < X% of personal baseline | 709/1516 days <80% of personal max (46.8%) | 46.8% | 16 users | 0% | yes | ✅ most measurable; **80% cutoff needs clinical validation** (common range 80–85%, but NOT assumed) |

Daily symptom prevalence in data: `daily_day_symp` TRUE 77.1%,
`daily_night_symp` TRUE 20.5% — highly prevalent; "any symptom" is not a useful rare-event target.

## Recommendation (pending clinical validation)

**Best candidate target:** PEF deterioration (sustained drop of PEF below a
clinically-validated percentage of the user's personal baseline over a defined
window, e.g., N consecutive days), optionally requiring co-occurrence of
symptom deterioration. Because PEF has 1516 observations across 16 users and
the outcome is directly tied to a deployable measurement (manual PEFR), it is
the only candidate with enough events and deployment compatibility.

Doctor visits (`weekly_doc`) are a secondary, weaker proxy; hospital/ER are
unusable as supervised targets in this dataset.
