from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Profile
from app.security.auth import get_current_user

router = APIRouter(tags=["profile"])


@router.get("/profile")
def get_profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == user.id).first()
    if not profile:
        return {"user_id": user.id, "email": user.email, "profile": None}
    return {"user_id": user.id, "email": user.email,
            "profile": {c.name: getattr(profile, c.name) for c in profile.__table__.columns}}


@router.put("/profile")
def update_profile(data: dict, user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == user.id).first()
    if not profile:
        profile = Profile(id=user.id)
        db.add(profile)
    allowed = {c.name for c in profile.__table__.columns} - {"id"}
    for k, v in data.items():
        if k in allowed:
            setattr(profile, k, v)
    db.commit()
    return {"status": "updated"}
