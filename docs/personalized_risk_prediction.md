# Personalized Risk Prediction

The model estimates an individual user's probability of the defined PEF
deterioration event within 7 days, from that user's own history:

- Personal profile: age_range, sex, bmi_range, severity, smoking, pack_years, pef_best, max_pef_expected
- PEF history: current PEF, % of personal best, trailing-window mean/min/max
- Symptoms: day/night/activity limitation counts over trailing window
- Reliever use: ordinal range categories (no fake exact counts)
- Environment: DHT22 temperature/humidity trailing stats
- Temporal: trailing-week features only; nothing after prediction day T

Same hardware features only — no invented signals.
