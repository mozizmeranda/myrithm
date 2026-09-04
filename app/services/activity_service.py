from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.repositories.stream_repository import StreamRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.activity_repository import ActivityRepository
from app.models.activity import ActivityLog
from app.schemas.activity import ActivitySyncRequest, ActivityStatsResponse, DailyActivityStats
from app.config import settings
from app.errors import AppException

class ActivityService:
    def __init__(self):
        self.stream_repo = StreamRepository()
        self.exercise_repo = ExerciseRepository()
        self.activity_repo = ActivityRepository()

    def sync_activity(self, db: Session, user_id: str, req: ActivitySyncRequest) -> dict:
        stream = self.stream_repo.get_by_id(db, req.stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)
        if not stream.is_active:
            raise AppException("STREAM_INACTIVE", "Cannot sync activity for an inactive stream", 403)

        if req.duration_seconds <= 0 or req.duration_seconds > 60:
            raise AppException("INVALID_DURATION", "Duration must be between 1 and 60 seconds", 400)

        estimated_steps = req.estimated_steps
        if estimated_steps is None:
            exercises = self.exercise_repo.get_by_stream_id(db, req.stream_id, active_only=True)
            if exercises:
                avg_spm = sum(e.steps_per_minute for e in exercises) / len(exercises)
            else:
                avg_spm = 90
            estimated_steps = round((req.duration_seconds / 60.0) * avg_spm)

        if estimated_steps < 0:
            raise AppException("INVALID_STEPS", "Estimated steps must be greater than or equal to 0", 400)

        log = ActivityLog(
            user_id=user_id,
            stream_id=req.stream_id,
            duration_seconds=req.duration_seconds,
            estimated_steps=estimated_steps
        )
        saved = self.activity_repo.create(db, log)
        return {
            "id": saved.id,
            "stream_id": saved.stream_id,
            "duration_seconds": saved.duration_seconds,
            "estimated_steps": saved.estimated_steps,
            "created_at": saved.created_at
        }

    def get_user_stats(self, db: Session, user_id: str) -> ActivityStatsResponse:
        tz = ZoneInfo(settings.APP_TIMEZONE)
        now_tz = datetime.now(tz)
        today_date = now_tz.date()

        # Overall summary
        summary = self.activity_repo.get_user_summary(db, user_id)

        # Date range for last 7 days (today_date - 6 days to today_date)
        start_7days_date = today_date - timedelta(days=6)
        start_7days_tz = datetime.combine(start_7days_date, datetime.min.time(), tzinfo=tz)
        end_today_tz = datetime.combine(today_date + timedelta(days=1), datetime.min.time(), tzinfo=tz)

        logs = self.activity_repo.get_user_activity_between(
            db,
            user_id,
            start_7days_tz.astimezone(timezone.utc),
            end_today_tz.astimezone(timezone.utc)
        )

        # Group logs by local date in APP_TIMEZONE
        daily_map: dict[date, dict] = {}
        for i in range(7):
            d = start_7days_date + timedelta(days=i)
            daily_map[d] = {"duration": 0, "steps": 0}

        for log in logs:
            # Convert UTC created_at to APP_TIMEZONE date
            log_dt_utc = log.created_at.replace(tzinfo=timezone.utc) if log.created_at.tzinfo is None else log.created_at
            log_date = log_dt_utc.astimezone(tz).date()
            if log_date in daily_map:
                daily_map[log_date]["duration"] += log.duration_seconds
                daily_map[log_date]["steps"] += log.estimated_steps

        yesterday_date = today_date - timedelta(days=1)
        today_data = daily_map.get(today_date, {"duration": 0, "steps": 0})
        yesterday_data = daily_map.get(yesterday_date, {"duration": 0, "steps": 0})

        last_7_days = [
            DailyActivityStats(
                date=d.isoformat(),
                duration_seconds=daily_map[d]["duration"],
                estimated_steps=daily_map[d]["steps"]
            )
            for d in sorted(daily_map.keys())
        ]

        return ActivityStatsResponse(
            today_seconds=today_data["duration"],
            today_estimated_steps=today_data["steps"],
            yesterday_seconds=yesterday_data["duration"],
            total_seconds=summary["total_duration_seconds"],
            total_estimated_steps=summary["total_estimated_steps"],
            last_7_days=last_7_days
        )
