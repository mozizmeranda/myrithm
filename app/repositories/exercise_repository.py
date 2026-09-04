from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.exercise import Exercise

class ExerciseRepository:
    def get_by_id(self, db: Session, exercise_id: str) -> Optional[Exercise]:
        return db.scalar(select(Exercise).where(Exercise.id == exercise_id))

    def get_by_stream_id(self, db: Session, stream_id: str, active_only: bool = False) -> list[Exercise]:
        query = select(Exercise).where(Exercise.stream_id == stream_id)
        if active_only:
            query = query.where(Exercise.is_active.is_(True))
        query = query.order_by(Exercise.sort_order, Exercise.created_at)
        return list(db.scalars(query).all())

    def get_all(self, db: Session, stream_id: Optional[str] = None) -> list[Exercise]:
        query = select(Exercise)
        if stream_id:
            query = query.where(Exercise.stream_id == stream_id)
        query = query.order_by(Exercise.stream_id, Exercise.sort_order, Exercise.created_at)
        return list(db.scalars(query).all())

    def count_by_stream_id(self, db: Session, stream_id: str) -> int:
        return db.scalar(select(func.count(Exercise.id)).where(Exercise.stream_id == stream_id)) or 0

    def count_by_video_url(self, db: Session, video_url: str) -> int:
        return db.scalar(select(func.count(Exercise.id)).where(Exercise.video_url == video_url)) or 0

    def create(self, db: Session, exercise: Exercise) -> Exercise:
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        return exercise

    def update(self, db: Session, exercise: Exercise) -> Exercise:
        db.commit()
        db.refresh(exercise)
        return exercise

    def delete(self, db: Session, exercise: Exercise):
        db.delete(exercise)
        db.commit()
