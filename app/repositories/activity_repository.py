from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.activity import ActivityLog

class ActivityRepository:
    def create(self, db: Session, activity_log: ActivityLog) -> ActivityLog:
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

    def count_by_stream_id(self, db: Session, stream_id: str) -> int:
        return db.scalar(select(func.count(ActivityLog.id)).where(ActivityLog.stream_id == stream_id)) or 0

    def get_user_summary(self, db: Session, user_id: str) -> dict:
        result = db.execute(
            select(
                func.coalesce(func.sum(ActivityLog.duration_seconds), 0),
                func.coalesce(func.sum(ActivityLog.estimated_steps), 0),
                func.count(ActivityLog.id)
            ).where(ActivityLog.user_id == user_id)
        ).one()
        return {
            "total_duration_seconds": result[0],
            "total_estimated_steps": result[1],
            "total_sessions": result[2]
        }

    def get_user_activity_between(self, db: Session, user_id: str, start_dt: datetime, end_dt: datetime) -> list[ActivityLog]:
        return list(
            db.scalars(
                select(ActivityLog)
                .where(
                    ActivityLog.user_id == user_id,
                    ActivityLog.created_at >= start_dt,
                    ActivityLog.created_at < end_dt
                )
                .order_by(ActivityLog.created_at)
            ).all()
        )

    def get_admin_totals(self, db: Session) -> dict:
        result = db.execute(
            select(
                func.count(ActivityLog.id),
                func.coalesce(func.sum(ActivityLog.duration_seconds), 0),
                func.coalesce(func.sum(ActivityLog.estimated_steps), 0)
            )
        ).one()
        return {
            "total_activity_logs": result[0],
            "total_duration_seconds": result[1],
            "total_estimated_steps": result[2]
        }

    def get_all_activity_between(self, db: Session, start_dt: datetime, end_dt: datetime) -> list[ActivityLog]:
        return list(
            db.scalars(
                select(ActivityLog)
                .where(
                    ActivityLog.created_at >= start_dt,
                    ActivityLog.created_at < end_dt
                )
            ).all()
        )
