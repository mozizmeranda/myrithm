from typing import Optional
from pydantic import BaseModel, ConfigDict

class TrackCreateRequest(BaseModel):
    stream_id: str
    title: str
    artist: Optional[str] = None
    audio_url: str
    duration: int = 180
    sort_order: int = 0
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class TrackUpdateRequest(BaseModel):
    stream_id: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    sort_order: Optional[int] = None
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
