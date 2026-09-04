from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

MEDIA_AUDIO_URL_PATTERN = r"^/media/audio/[a-f0-9]{12}\.[a-z0-9]+$"

class TrackCreateRequest(BaseModel):
    stream_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    artist: Optional[str] = Field(None, max_length=200)
    audio_url: str = Field(..., pattern=MEDIA_AUDIO_URL_PATTERN)
    duration: int = Field(180, gt=0, le=3600)
    sort_order: int = Field(0, ge=0, le=1000)
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class TrackUpdateRequest(BaseModel):
    stream_id: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    artist: Optional[str] = Field(None, max_length=200)
    audio_url: Optional[str] = Field(None, pattern=MEDIA_AUDIO_URL_PATTERN)
    duration: Optional[int] = Field(None, gt=0, le=3600)
    sort_order: Optional[int] = Field(None, ge=0, le=1000)
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class TrackResponse(BaseModel):
    id: str
    stream_id: str
    title: str
    artist: Optional[str] = None
    audio_url: str
    duration: int
    sort_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
