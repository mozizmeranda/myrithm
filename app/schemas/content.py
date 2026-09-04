from pydantic import BaseModel
from app.schemas.exercise import ExerciseResponse
from app.schemas.track import TrackResponse

class StreamContentResponse(BaseModel):
    stream_id: str
    exercises: list[ExerciseResponse]
    tracks: list[TrackResponse]
