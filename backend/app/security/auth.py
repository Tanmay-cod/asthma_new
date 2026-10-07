"""Server-side identity verification.

User auth: Supabase-issued JWT, verified against Supabase on every request.
Device auth: separate device credential (Bearer token), hashed in DB.
Never trust a user_id supplied by the frontend.
"""
import hashlib

import requests
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Device, User, Role

bearer = HTTPBearer(auto_error=False)


def _verify_supabase_token(token: str) -> dict:
    if not settings.SUPABASE_URL:
        raise HTTPException(503, "Authentication backend not configured")
    try:
        r = requests.get(
            f"{settings.SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": settings.SUPABASE_ANON_KEY},
            timeout=10,
        )
    except Exception:
        raise HTTPException(503, "Authentication service unavailable")
    if r.status_code != 200:
        raise HTTPException(401, "Invalid or expired token")
    return r.json()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(401, "Missing Authorization header")
    supabase_user = _verify_supabase_token(credentials.credentials)
    from types import SimpleNamespace
    supabase_id = supabase_user.get("id")
    return SimpleNamespace(id=supabase_id, email=supabase_user.get("email", ""), role="PATIENT")


def hash_device_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Device:
    if not credentials:
        raise HTTPException(401, "Missing device credential")
    token_hash = hash_device_token(credentials.credentials)
    device = (db.query(Device)
              .filter(Device.device_token_hash == token_hash, Device.is_active == True)
              .first())
    if not device:
        raise HTTPException(403, "Invalid device credential")
    return device
