from datetime import datetime
from pydantic import BaseModel, Field


class RequestCreate(BaseModel):
    channel: str = Field(default="web")
    user_identity: str = Field(min_length=3)
    business_context: str | None = None
    raw_text: str = Field(min_length=5)
    priority_hint: str | None = None


class RequestResponse(BaseModel):
    request_id: str
    status: str
    blocked_reason: str | None = None


class RequestStatus(BaseModel):
    request_id: str
    channel: str
    user_identity: str
    business_context: str | None
    raw_text: str
    priority_hint: str | None
    status: str
    blocked_reason: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
