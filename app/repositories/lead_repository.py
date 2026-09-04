from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.lead import StreamLead

class LeadRepository:
    def create(self, db: Session, email: str, stream_code: str) -> StreamLead:
        lead = StreamLead(email=email, stream_code=stream_code)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    def get_paginated(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        stream_code: Optional[str] = None
    ) -> tuple[list[StreamLead], int]:
        query = select(StreamLead)
        if stream_code:
            query = query.where(StreamLead.stream_code == stream_code)
        
        total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
        
        offset = (page - 1) * per_page
        items = list(
            db.scalars(
                query.order_by(StreamLead.created_at.desc()).offset(offset).limit(per_page)
            ).all()
        )
        return items, total

    def count(self, db: Session) -> int:
        return db.scalar(select(func.count(StreamLead.id))) or 0

    def count_by_stream(self, db: Session) -> list[tuple[str, int]]:
        results = db.execute(
            select(StreamLead.stream_code, func.count(StreamLead.id))
            .group_by(StreamLead.stream_code)
        ).all()
        return [(r[0], r[1]) for r in results]
