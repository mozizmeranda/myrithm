from typing import Optional
from pydantic import BaseModel, ConfigDict

class StreamCreateRequest(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    is_active: bool = False

    model_config = ConfigDict(from_attributes=True)

class StreamUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class StreamResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
