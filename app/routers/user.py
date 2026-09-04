from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.user import UserProfileResponse
from app.repositories.activity_repository import ActivityRepository
from app.models.user import User

router = APIRouter(prefix="/api/v1/user", tags=["User Profile"])
activity_repo = ActivityRepository()

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = activity_repo.get_user_summary(db, current_user.id)
    return UserProfileResponse(
        email=current_user.email,
        created_at=current_user.created_at,
        total_duration_seconds=summary["total_duration_seconds"],
        total_estimated_steps=summary["total_estimated_steps"],
        total_sessions=summary["total_sessions"]
    )
