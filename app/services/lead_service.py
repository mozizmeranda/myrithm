from sqlalchemy.orm import Session
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import LeadCreateRequest, LeadResponse
from app.redis_client import increment_lead_counter

class LeadService:
    def __init__(self):
        self.lead_repo = LeadRepository()

    async def create_lead(self, db: Session, req: LeadCreateRequest) -> LeadResponse:
        # Step 1: Save lead in SQLite (source of truth)
        lead = self.lead_repo.create(db, req.email, req.stream_code)

        # Step 2: Non-critical Redis counter increment
        try:
            await increment_lead_counter(req.stream_code)
        except Exception:
            pass

        return LeadResponse.model_validate(lead)
