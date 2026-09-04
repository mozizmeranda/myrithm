from sqlalchemy.orm import Session
from app.repositories.lead_repository import LeadRepository
from app.repositories.stream_repository import StreamRepository
from app.schemas.lead import LeadCreateRequest, LeadResponse
from app.redis_client import increment_lead_counter
from app.errors import AppException

class LeadService:
    def __init__(self):
        self.lead_repo = LeadRepository()
        self.stream_repo = StreamRepository()

    async def create_lead(self, db: Session, req: LeadCreateRequest) -> LeadResponse:
        # Step 1: Validate stream code existence
        stream = self.stream_repo.get_by_id(db, req.stream_code)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", f"Stream '{req.stream_code}' not found", 404)

        email = req.email.strip().lower()

        # Step 2: Check for duplicate lead
        existing = self.lead_repo.get_by_email_and_stream(db, email, req.stream_code)
        if existing:
            return LeadResponse.model_validate(existing)

        # Step 3: Save lead in SQLite (source of truth)
        lead = self.lead_repo.create(db, email, req.stream_code)

        # Step 4: Non-critical Redis counter increment
        try:
            await increment_lead_counter(req.stream_code)
        except Exception:
            pass

        return LeadResponse.model_validate(lead)

