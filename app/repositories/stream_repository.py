from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.stream import Stream

class StreamRepository:
    def get_by_id(self, db: Session, stream_id: str) -> Optional[Stream]:
        return db.scalar(select(Stream).where(Stream.id == stream_id))

    def get_all(self, db: Session) -> list[Stream]:
        return list(db.scalars(select(Stream).order_by(Stream.id)).all())

    def create(self, db: Session, stream: Stream) -> Stream:
        db.add(stream)
        db.commit()
        db.refresh(stream)
        return stream

    def update(self, db: Session, stream: Stream) -> Stream:
        db.commit()
        db.refresh(stream)
        return stream

    def delete(self, db: Session, stream: Stream):
        db.delete(stream)
        db.commit()
