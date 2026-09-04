from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserProfileResponse(BaseModel):
    email: str
    created_at: datetime
    total_duration_seconds: int
    total_estimated_steps: int
    total_sessions: int

    model_config = ConfigDict(from_attributes=True)
