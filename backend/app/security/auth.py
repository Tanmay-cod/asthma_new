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
from app.models import Device, DeviceCredential, User, Role

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
    supabase_id = supabase_user.get("id")
    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not user:
        # Auto-provision local user record on first verified login
        user = User(supabase_id=supabase_id, email=supabase_user.get("email", ""), role=Role.PATIENT)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def hash_device_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Device:
    if not credentials:
        raise HTTPException(401, "Missing device credential")
    token_hash = hash_device_token(credentials.credentials)
    cred = (db.query(DeviceCredential)
            .filter(DeviceCredential.token_hash == token_hash, DeviceCredential.revoked == False)
            .first())
    if not cred:
        raise HTTPException(403, "Invalid device credential")
    return cred.device
