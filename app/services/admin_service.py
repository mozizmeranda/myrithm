from typing import Optional
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.stream_repository import StreamRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.track_repository import TrackRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.lead_repository import LeadRepository
from app.services.media_service import MediaService
from app.models.exercise import Exercise
from app.models.track import Track
from app.schemas.exercise import ExerciseResponse, ExerciseCreateRequest, ExerciseUpdateRequest
from app.schemas.track import TrackResponse, TrackCreateRequest, TrackUpdateRequest
from app.schemas.lead import LeadListResponse, LeadResponse
from app.schemas.admin_stats import AdminStatsResponse, StreamLeadCount
from app.schemas.activity import DailyActivityStats
from app.config import settings
from app.errors import AppException

class AdminService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.stream_repo = StreamRepository()
        self.exercise_repo = ExerciseRepository()
        self.track_repo = TrackRepository()
        self.activity_repo = ActivityRepository()
        self.lead_repo = LeadRepository()

    # Exercise methods
    def get_exercises(self, db: Session, stream_id: Optional[str] = None) -> list[ExerciseResponse]:
        exercises = self.exercise_repo.get_all(db, stream_id=stream_id)
        return [ExerciseResponse.model_validate(e) for e in exercises]

    def create_exercise(self, db: Session, req: ExerciseCreateRequest) -> ExerciseResponse:
        stream = self.stream_repo.get_by_id(db, req.stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)

        exercise = Exercise(
            stream_id=req.stream_id,
            title=req.title,
            description=req.description,
            video_url=req.video_url,
            duration=req.duration,
            steps_per_minute=req.steps_per_minute,
            sort_order=req.sort_order,
            is_active=req.is_active
        )
        created = self.exercise_repo.create(db, exercise)
        return ExerciseResponse.model_validate(created)

    def update_exercise(self, db: Session, exercise_id: str, req: ExerciseUpdateRequest) -> ExerciseResponse:
        exercise = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise:
            raise AppException("EXERCISE_NOT_FOUND", "Exercise not found", 404)

        if req.stream_id is not None:
            stream = self.stream_repo.get_by_id(db, req.stream_id)
            if not stream:
                raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)
            exercise.stream_id = req.stream_id

        if req.title is not None:
            exercise.title = req.title
        if req.description is not None:
            exercise.description = req.description

        old_video_url = exercise.video_url
        url_changed = (req.video_url is not None and req.video_url != old_video_url)
        if req.video_url is not None:
            exercise.video_url = req.video_url

        if req.duration is not None:
            exercise.duration = req.duration
        if req.steps_per_minute is not None:
            exercise.steps_per_minute = req.steps_per_minute
        if req.sort_order is not None:
            exercise.sort_order = req.sort_order
        if req.is_active is not None:
            exercise.is_active = req.is_active

        updated = self.exercise_repo.update(db, exercise)

        if url_changed and old_video_url:
            MediaService.delete_local_file_if_unused(
                old_video_url,
                lambda url: self.exercise_repo.count_by_video_url(db, url)
            )

        return ExerciseResponse.model_validate(updated)

    def delete_exercise(self, db: Session, exercise_id: str):
        exercise = self.exercise_repo.get_by_id(db, exercise_id)
        if not exercise:
            raise AppException("EXERCISE_NOT_FOUND", "Exercise not found", 404)

        video_url = exercise.video_url
        self.exercise_repo.delete(db, exercise)
        MediaService.delete_local_file_if_unused(
            video_url,
            lambda url: self.exercise_repo.count_by_video_url(db, url)
        )

    # Track methods
    def get_tracks(self, db: Session, stream_id: Optional[str] = None) -> list[TrackResponse]:
        tracks = self.track_repo.get_all(db, stream_id=stream_id)
        return [TrackResponse.model_validate(t) for t in tracks]

    def create_track(self, db: Session, req: TrackCreateRequest) -> TrackResponse:
        stream = self.stream_repo.get_by_id(db, req.stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)

        track = Track(
            stream_id=req.stream_id,
            title=req.title,
            artist=req.artist,
            audio_url=req.audio_url,
            duration=req.duration,
            sort_order=req.sort_order,
            is_active=req.is_active
        )
        created = self.track_repo.create(db, track)
        return TrackResponse.model_validate(created)

    def update_track(self, db: Session, track_id: str, req: TrackUpdateRequest) -> TrackResponse:
        track = self.track_repo.get_by_id(db, track_id)
        if not track:
            raise AppException("TRACK_NOT_FOUND", "Track not found", 404)

        if req.stream_id is not None:
            stream = self.stream_repo.get_by_id(db, req.stream_id)
            if not stream:
                raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)
            track.stream_id = req.stream_id

        if req.title is not None:
            track.title = req.title
        if req.artist is not None:
            track.artist = req.artist

        old_audio_url = track.audio_url
        url_changed = (req.audio_url is not None and req.audio_url != old_audio_url)
        if req.audio_url is not None:
            track.audio_url = req.audio_url

        if req.duration is not None:
            track.duration = req.duration
        if req.sort_order is not None:
            track.sort_order = req.sort_order
        if req.is_active is not None:
            track.is_active = req.is_active

        updated = self.track_repo.update(db, track)

        if url_changed and old_audio_url:
            MediaService.delete_local_file_if_unused(
                old_audio_url,
                lambda url: self.track_repo.count_by_audio_url(db, url)
            )

        return TrackResponse.model_validate(updated)

    def delete_track(self, db: Session, track_id: str):
        track = self.track_repo.get_by_id(db, track_id)
        if not track:
            raise AppException("TRACK_NOT_FOUND", "Track not found", 404)

        audio_url = track.audio_url
        self.track_repo.delete(db, track)
        MediaService.delete_local_file_if_unused(
            audio_url,
            lambda url: self.track_repo.count_by_audio_url(db, url)
        )

    # Leads view
    def get_leads(self, db: Session, page: int = 1, per_page: int = 20, stream_code: Optional[str] = None) -> LeadListResponse:
        items, total = self.lead_repo.get_paginated(db, page=page, per_page=per_page, stream_code=stream_code)
        return LeadListResponse(
            items=[LeadResponse.model_validate(lead) for lead in items],
            total=total,
            page=page,
            per_page=per_page
        )

    # Global Stats
    def get_admin_stats(self, db: Session) -> AdminStatsResponse:
        total_users = self.user_repo.count(db)
        total_leads = self.lead_repo.count(db)
        leads_by_stream_tuples = self.lead_repo.count_by_stream(db)
        leads_by_stream = [StreamLeadCount(stream_code=code, count=cnt) for code, cnt in leads_by_stream_tuples]

        act_totals = self.activity_repo.get_admin_totals(db)

        # Daily activity for last 7 days
        tz = ZoneInfo(settings.APP_TIMEZONE)
        now_tz = datetime.now(tz)
        today_date = now_tz.date()
        start_7days_date = today_date - timedelta(days=6)
        start_7days_tz = datetime.combine(start_7days_date, datetime.min.time(), tzinfo=tz)
        end_today_tz = datetime.combine(today_date + timedelta(days=1), datetime.min.time(), tzinfo=tz)

        logs = self.activity_repo.get_all_activity_between(
            db,
            start_7days_tz.astimezone(timezone.utc),
            end_today_tz.astimezone(timezone.utc)
        )

        daily_map: dict[date, dict] = {start_7days_date + timedelta(days=i): {"duration": 0, "steps": 0} for i in range(7)}
        for log in logs:
            log_dt_utc = log.created_at.replace(tzinfo=timezone.utc) if log.created_at.tzinfo is None else log.created_at
            log_date = log_dt_utc.astimezone(tz).date()
            if log_date in daily_map:
                daily_map[log_date]["duration"] += log.duration_seconds
                daily_map[log_date]["steps"] += log.estimated_steps

        daily_activity = [
            DailyActivityStats(
                date=d.isoformat(),
                duration_seconds=daily_map[d]["duration"],
                estimated_steps=daily_map[d]["steps"]
            )
            for d in sorted(daily_map.keys())
        ]

        return AdminStatsResponse(
            total_users=total_users,
            total_leads=total_leads,
            leads_by_stream=leads_by_stream,
            total_activity_logs=act_totals["total_activity_logs"],
            total_duration_seconds=act_totals["total_duration_seconds"],
            total_estimated_steps=act_totals["total_estimated_steps"],
            daily_activity=daily_activity
        )
