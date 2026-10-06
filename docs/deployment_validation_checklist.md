# Deployment Validation Checklist

- [x] ESP8266 ingestion path (software)
- [x] Device authentication + user association
- [x] User/device isolation
- [x] Timestamp validation (future rejected)
- [x] Sensor range validation with flagged-not-modified behavior
- [x] PEF percentage = current / personal best × 100 (documented distinction from 80% reduction)
- [x] Personal best = stored profile value or personal max; never AAMOS-00 value
- [x] Symptom/reliever inputs stored; range-coded values not treated as exact counts
- [x] Temporal leakage protection (tests)
- [x] Frozen model loads; 36-feature order verified
- [x] Individual SHAP persisted per prediction
- [x] Dashboard / personalized report / history
- [x] Prediction snapshot immutability (append-only)
- [x] Error handling for invalid payloads
- [ ] Physical hardware end-to-end (NOT EXECUTED — device not connected)
- [ ] Rate limiting on IoT endpoint (future hardening)
- [ ] TLS on ESP8266 path (production requirement)
