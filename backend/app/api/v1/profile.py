from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Profile, User
from app.security.auth import get_current_user

router = APIRouter(tags=["profile"])


@router.get("/profile")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        return {"user_id": user.id, "email": user.email, "role": user.role.value, "profile": None}
    return {"user_id": user.id, "email": user.email, "role": user.role.value,
            "profile": {c.name: getattr(profile, c.name) for c in profile.__table__.columns
                        if c.name not in ("id", "user_id")}}


@router.put("/profile")
def update_profile(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
    allowed = {c.name for c in profile.__table__.columns} - {"id", "user_id"}
    for k, v in data.items():
        if k in allowed:
            setattr(profile, k, v)
    db.commit()
    return {"status": "updated"}
