from typing import Optional
from pydantic import BaseModel, ConfigDict

class ExerciseCreateRequest(BaseModel):
    stream_id: str
    title: str
    description: Optional[str] = None
    video_url: str
    duration: int = 60
    steps_per_minute: int = 90
    sort_order: int = 0
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class ExerciseUpdateRequest(BaseModel):
    stream_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    steps_per_minute: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class ExerciseResponse(BaseModel):
    id: str
    stream_id: str
    title: str
    description: Optional[str] = None
    video_url: str
    duration: int
    steps_per_minute: int
    sort_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
