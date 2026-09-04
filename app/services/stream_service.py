from sqlalchemy.orm import Session
from app.repositories.stream_repository import StreamRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.track_repository import TrackRepository
from app.repositories.activity_repository import ActivityRepository
from app.models.stream import Stream
from app.schemas.stream import StreamResponse, StreamCreateRequest, StreamUpdateRequest
from app.schemas.exercise import ExerciseResponse
from app.schemas.track import TrackResponse
from app.schemas.content import StreamContentResponse
from app.errors import AppException

class StreamService:
    def __init__(self):
        self.stream_repo = StreamRepository()
        self.exercise_repo = ExerciseRepository()
        self.track_repo = TrackRepository()
        self.activity_repo = ActivityRepository()

    def get_all_streams(self, db: Session) -> list[StreamResponse]:
        streams = self.stream_repo.get_all(db)
        return [StreamResponse.model_validate(s) for s in streams]

    def get_stream_content(self, db: Session, stream_id: str) -> StreamContentResponse:
        stream = self.stream_repo.get_by_id(db, stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)
        if not stream.is_active:
            raise AppException("STREAM_INACTIVE", "This workout stream is currently inactive", 403)

        exercises = self.exercise_repo.get_by_stream_id(db, stream_id, active_only=True)
        tracks = self.track_repo.get_by_stream_id(db, stream_id, active_only=True)

        return StreamContentResponse(
            stream_id=stream_id,
            exercises=[ExerciseResponse.model_validate(e) for e in exercises],
            tracks=[TrackResponse.model_validate(t) for t in tracks]
        )

    # Admin methods
    def create_stream(self, db: Session, req: StreamCreateRequest) -> StreamResponse:
        existing = self.stream_repo.get_by_id(db, req.id)
        if existing:
            raise AppException("DUPLICATE_STREAM", f"Stream with ID '{req.id}' already exists", 409)
        stream = Stream(
            id=req.id,
            title=req.title,
            description=req.description,
            is_active=req.is_active
        )
        created = self.stream_repo.create(db, stream)
        return StreamResponse.model_validate(created)

    def update_stream(self, db: Session, stream_id: str, req: StreamUpdateRequest) -> StreamResponse:
        stream = self.stream_repo.get_by_id(db, stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)
        
        if req.title is not None:
            stream.title = req.title
        if req.description is not None:
            stream.description = req.description
        if req.is_active is not None:
            stream.is_active = req.is_active

        updated = self.stream_repo.update(db, stream)
        return StreamResponse.model_validate(updated)

    def delete_stream(self, db: Session, stream_id: str) -> dict:
        stream = self.stream_repo.get_by_id(db, stream_id)
        if not stream:
            raise AppException("STREAM_NOT_FOUND", "Stream not found", 404)

        activity_count = self.activity_repo.count_by_stream_id(db, stream_id)
        if activity_count > 0:
            # Rule: Streams with activity logs cannot be physically deleted. Soft-archive instead.
            stream.is_active = False
            self.stream_repo.update(db, stream)
            return {"message": "Stream has associated activity logs. Stream has been archived (is_active = false) to preserve user statistics."}

        exercise_count = self.exercise_repo.count_by_stream_id(db, stream_id)
        track_count = self.track_repo.count_by_stream_id(db, stream_id)
        if exercise_count > 0 or track_count > 0:
            raise AppException("CANNOT_DELETE_STREAM", "Cannot delete stream with associated exercises or tracks. Please delete associated content first.", 409)

        self.stream_repo.delete(db, stream)
        return {"message": f"Stream '{stream_id}' successfully deleted."}
