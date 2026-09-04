from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas.admin_stats import AdminStatsResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/v1/admin/stats", tags=["Admin Stats"], dependencies=[Depends(require_admin)])
admin_service = AdminService()

@router.get("", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db)):
    return admin_service.get_admin_stats(db)
