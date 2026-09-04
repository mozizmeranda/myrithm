from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.track import Track

class TrackRepository:
    def get_by_id(self, db: Session, track_id: str) -> Optional[Track]:
        return db.scalar(select(Track).where(Track.id == track_id))

    def get_by_stream_id(self, db: Session, stream_id: str, active_only: bool = False) -> list[Track]:
        query = select(Track).where(Track.stream_id == stream_id)
        if active_only:
            query = query.where(Track.is_active.is_(True))
        query = query.order_by(Track.sort_order, Track.created_at)
        return list(db.scalars(query).all())

    def get_all(self, db: Session, stream_id: Optional[str] = None) -> list[Track]:
        query = select(Track)
        if stream_id:
            query = query.where(Track.stream_id == stream_id)
        query = query.order_by(Track.stream_id, Track.sort_order, Track.created_at)
        return list(db.scalars(query).all())

    def count_by_stream_id(self, db: Session, stream_id: str) -> int:
        return db.scalar(select(func.count(Track.id)).where(Track.stream_id == stream_id)) or 0

    def count_by_audio_url(self, db: Session, audio_url: str) -> int:
        return db.scalar(select(func.count(Track.id)).where(Track.audio_url == audio_url)) or 0

    def create(self, db: Session, track: Track) -> Track:
        db.add(track)
        db.commit()
        db.refresh(track)
        return track

    def update(self, db: Session, track: Track) -> Track:
        db.commit()
        db.refresh(track)
        return track

    def delete(self, db: Session, track: Track):
        db.delete(track)
        db.commit()
