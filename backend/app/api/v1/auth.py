from fastapi import APIRouter, Depends

from app.models import User
from app.security.auth import get_current_user

router = APIRouter(tags=["auth"])


@router.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    """Registration/login/logout/password-reset are handled by Supabase Auth on the frontend.
    The backend verifies the Supabase-issued JWT server-side (see app/security/auth.py)."""
    return {"user_id": user.id, "email": user.email, "role": user.role.value}
