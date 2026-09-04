from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class LeadCreateRequest(BaseModel):
    email: EmailStr
    stream_code: str

    model_config = ConfigDict(from_attributes=True)

class LeadResponse(BaseModel):
    id: str
    email: str
    stream_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    per_page: int

    model_config = ConfigDict(from_attributes=True)
