from pydantic import BaseModel
from app.schemas.activity import DailyActivityStats

class StreamLeadCount(BaseModel):
    stream_code: str
    count: int

class AdminStatsResponse(BaseModel):
    total_users: int
    total_leads: int
    leads_by_stream: list[StreamLeadCount]
    total_activity_logs: int
    total_duration_seconds: int
    total_estimated_steps: int
    daily_activity: list[DailyActivityStats]
