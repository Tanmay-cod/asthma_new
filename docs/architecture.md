# Phase 2 — Architecture

## Layout

```
asthama/
├── app/                  # LEGACY prototype (FastAPI + SQLite) — preserved
├── frontend/             # LEGACY dashboard (index.html, Chart.js, PWA) — preserved
├── firmware/             # LEGACY ESP8266 sketch
├── simulate.py           # LEGACY simulator
├── data/asthma.db        # LEGACY SQLite database — preserved
├── models/               # LEGACY dev-model artifacts (XGBoost + SHAP)
│
├── backend/              # NEW modular FastAPI
│   ├── app/
│   │   ├── api/v1/       # versioned REST endpoints
│   │   ├── core/         # config, database
│   │   ├── models/       # SQLAlchemy models (23 tables)
│   │   ├── schemas/      # Pydantic payloads
│   │   ├── security/     # Supabase JWT verification + device tokens
│   │   ├── iot/          # (placeholder — firmware/docs later)
│   │   ├── ml/           # (placeholder — Phase 9-14)
│   │   ├── safety/       # (placeholder — Phase 16)
│   │   ├── personalization/ # (placeholder — Phase 13)
│   │   ├── audit/        # (placeholder — Phase 17)
│   │   └── ml, services, repositories, tests/
│   ├── alembic/          # schema migrations
│   └── Dockerfile
├── frontend-next/        # NEW Next.js + TS + Tailwind
├── docker-compose.yml    # PostgreSQL (+ backend)
└── docs/

## Flow

ESP8266 → HTTPS → FastAPI /api/v1/iot/readings (device Bearer token)
       → validation → PostgreSQL → Next.js dashboard (Supabase JWT)

## Auth model

- Users: Supabase Auth JWT, verified server-side against Supabase /auth/v1/user.
  The backend auto-provisions a local `users` row on first verified login.
- Devices: per-device random token, stored hashed (SHA-256) in `device_credentials`.
  Device_id alone is never accepted as authentication.
- Frontend never receives the service-role key; ESP8266 never receives
  DB credentials or Supabase keys.

## Database

PostgreSQL (docker-compose). Alembic manages schema. Initial migration
`a7207068a450` creates all tables (verified via SQLite offline check because
Docker is not installed on this dev machine — see README note).

## Versioning

All new endpoints live under /api/v1. Legacy endpoints remain under the old app.

## Known gaps / next phases

- Real-time WebSocket updates: Phase 7
- Profile/device CRUD full Zod forms in Next.js: Phase 3-4
- Personalization engine: Phase 13
- Safety rules file: Phase 16
