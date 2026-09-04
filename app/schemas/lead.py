from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class LeadCreateRequest(BaseModel):
    email: EmailStr
    stream_code: str = Field(..., min_length=1, max_length=50)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

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
