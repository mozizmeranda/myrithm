from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.lead import LeadCreateRequest, LeadResponse
from app.services.lead_service import LeadService
from app.rate_limiter import lead_limiter

router = APIRouter(prefix="/api/v1/leads", tags=["Leads"])
lead_service = LeadService()

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(lead_limiter)])
async def create_lead(req: LeadCreateRequest, db: Session = Depends(get_db)):
    return await lead_service.create_lead(db, req)
