# Phase 11 — IoT End-to-End Validation

Status: PASS WITH WARNINGS (software path validated; hardware not physically connected here).

## Architecture
ESP8266 + MAX30102 + DHT22 + GP2Y1010AU0F → POST /api/v1/iot/readings (device Bearer token)
→ range/timestamp validation → SensorReading rows → get_current_user (Supabase JWT)
→ POST /api/v1/predictions (frozen XGBoost) → SHAP → dashboard / personalized report.

## Sensor mappings
- heart_rate → HEART_RATE (ML feature path)
- spo2 → SPO2 (stored + displayed; NOT in frozen ML features)
- temperature → TEMPERATURE (ML feature)
- humidity → HUMIDITY (ML feature)
- dust_value → DUST (stored/displayed as dust indicator; NOT converted to PM2.5/PM10)

## API mappings
- POST /api/v1/devices — registers device, issues one-time device token
- POST /api/v1/iot/readings — device-authenticated ingestion
- POST /api/v1/predictions, GET /api/v1/predictions/latest|history|{id}/explanation
- POST /api/v1/reports/personalized, GET /api/v1/predictions/history

## Authentication & isolation
ESP8266 uses a per-device token (SHA-256 hashed in `device_credentials`); user
identity derives from the device→user association, never from a frontend-sent
user_id. User JWT endpoints enforce per-user filtering on predictions/reports.

## Timestamps
Future timestamps (>5 min ahead) are rejected with 422 and logged as
`FUTURE_TIMESTAMP` data-quality event. Storage is naive-UTC (documented
convention); no future timestamp silently accepted.

## Data quality
Invalid ranges are stored flagged as INVALID + logged, never silently modified.
Missing PEF/HR/etc. yields explicit data-quality states; no fabricated values.

## Circularity protection
Features at T use only data <= T; target uses (T, T+7d]. Tests enforce this.

## Frozen model
`models/phase8_xgboost.pkl` unchanged; 36 ordered inputs verified at load in test.

## Prediction snapshots / history
Predictions and explanations are persisted at inference time; historical rows are
never overwritten — a later PEF reading does not alter earlier predictions.

## Failure handling
Malformed payload → 401/403/422/200-with-flagged, never a fabricated prediction.
Backend/DB down → ESP8266 should buffer/retry (firmware design); production
deployment still requires a reliable network.

## Hardware test status
`HARDWARE VALIDATION: NOT EXECUTED — physical ESP8266 device not connected.`
Software ingestion path validated via TEST DATA only.

## Security
Device tokens hashed at rest; no secrets in frontend; no health data logged
unnecessarily; user isolation enforced in DB queries.

Clinical validation status: PENDING. Research/development prototype only.
