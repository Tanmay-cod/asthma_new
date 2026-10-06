from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.api.v1 import iot, devices, measurements, profile, auth

app = FastAPI(title="Asthma Risk System API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                    allow_methods=["*"], allow_headers=["*"])

app.include_router(v1_router.router)
for r in (auth.router, profile.router, devices.router, iot.router, measurements.router):
    app.include_router(r, prefix="/api/v1")
from app.api.v1 import predictions, sessions
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
