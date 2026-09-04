from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

MEDIA_VIDEO_URL_PATTERN = r"^/media/videos/[a-f0-9]{12}\.[a-z0-9]+$"

class ExerciseCreateRequest(BaseModel):
    stream_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    video_url: str = Field(..., pattern=MEDIA_VIDEO_URL_PATTERN)
    duration: int = Field(60, gt=0, le=3600)
    steps_per_minute: int = Field(90, ge=0, le=300)
    sort_order: int = Field(0, ge=0, le=1000)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class ExerciseUpdateRequest(BaseModel):
    stream_id: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    video_url: Optional[str] = Field(None, pattern=MEDIA_VIDEO_URL_PATTERN)
    duration: Optional[int] = Field(None, gt=0, le=3600)
    steps_per_minute: Optional[int] = Field(None, ge=0, le=300)
    sort_order: Optional[int] = Field(None, ge=0, le=1000)
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
