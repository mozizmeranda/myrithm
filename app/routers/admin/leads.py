from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_admin
from app.schemas.lead import LeadListResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/v1/admin/leads", tags=["Admin Leads"], dependencies=[Depends(require_admin)])
admin_service = AdminService()

@router.get("", response_model=LeadListResponse)
def get_leads(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    stream_code: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    return admin_service.get_leads(db, page=page, per_page=per_page, stream_code=stream_code)
