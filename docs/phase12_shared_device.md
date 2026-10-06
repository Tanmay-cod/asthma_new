# Phase 12 — Shared ESP8266 Multi-User Device

## Architecture

```text
User login → POST /api/v1/measurement-sessions/start
  → MeasurementSession(user_id, device_id, status=ACTIVE)
Shared ESP8266 (device token) → POST /api/v1/iot/readings
  → find ACTIVE session for that device → assign user_id + session_id
→ dashboard polls GET /api/v1/measurement-sessions/current/latest-readings
User ends via POST /api/v1/measurement-sessions/{id}/end
```

## Identity rules
- ESP8266 authenticates as a DEVICE only (device_id = e.g. ESP001, per-device token).
- No hard-coded user_id in firmware.
- Device is bound to at most one ACTIVE session; a second user's start is rejected (409) until the first session is COMPLETED.
- Readings with no active session are rejected (409) — never attributed to a previous user.
- A user cannot end another user's session (404).

## Sensor semantics
- MAX30102: heart_rate + spo2 (spo2 stored/displayed, NOT in frozen ML features).
- DHT22: temperature + humidity.
- GP2Y1010AU0F: dust_value stored/displayed as a dust indicator only — not PM2.5/PM10, not in frozen model.
- Invalid values stored flagged INVALID; future timestamps rejected.

## PEF
Remains user-specific: PEF history, personal best, PEF features, and predictions
are all keyed by user_id only — never by device.

## Frozen ML
Unchanged: `models/phase8_xgboost.pkl`, 36 ordered inputs, PEF <80% of personal
best, 2 consecutive days, 7-day horizon, clinical validation PENDING.

## Security
Device tokens hashed at rest; JWT for user endpoints; no secrets in frontend;
device→active-session→user mapping enforced server-side.
