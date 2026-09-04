from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.activity import ActivitySyncRequest, ActivityStatsResponse
from app.services.activity_service import ActivityService
from app.rate_limiter import sync_limiter
from app.models.user import User

router = APIRouter(prefix="/api/v1/activity", tags=["Activity"])
activity_service = ActivityService()

@router.post("/sync", status_code=status.HTTP_201_CREATED, dependencies=[Depends(sync_limiter)])
def sync_activity(
    req: ActivitySyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return activity_service.sync_activity(db, current_user.id, req)

@router.get("/stats", response_model=ActivityStatsResponse)
def get_activity_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return activity_service.get_user_stats(db, current_user.id)
