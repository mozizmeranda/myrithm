from typing import Optional
from pydantic import BaseModel, ConfigDict

class ActivitySyncRequest(BaseModel):
    stream_id: str
    duration_seconds: int
    estimated_steps: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class DailyActivityStats(BaseModel):
    date: str  # YYYY-MM-DD format
    duration_seconds: int
    estimated_steps: int

    model_config = ConfigDict(from_attributes=True)

class ActivityStatsResponse(BaseModel):
    today_seconds: int
    today_estimated_steps: int
    yesterday_seconds: int
    total_seconds: int
    total_estimated_steps: int
    last_7_days: list[DailyActivityStats]

    model_config = ConfigDict(from_attributes=True)
