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
    request_type: str | None = None
    extracted_scope: str | None = None
    confidence_score: float | None = None
    clarification_questions: list[str] = Field(default_factory=list)


class RequestStatus(BaseModel):
    request_id: str
    channel: str
    user_identity: str
    business_context: str | None
    raw_text: str
    priority_hint: str | None
    status: str
    blocked_reason: str | None
    request_type: str | None
    extracted_scope: str | None
    confidence_score: float | None
    clarification_questions: list[str] = Field(default_factory=list)
    clarification_answers: dict[str, str] = Field(default_factory=dict)
    workflow_events: list[str] = Field(default_factory=list)
    brd_draft: str | None = None
    brd_status: str | None = None
    brd_review_comment: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClarificationSubmit(BaseModel):
    answers: dict[str, str] = Field(min_length=1)


class RequestSummary(BaseModel):
    request_id: str
    user_identity: str
    status: str
    request_type: str | None
    confidence_score: float | None
    updated_at: datetime


class RequestListResponse(BaseModel):
    items: list[RequestSummary]
    total: int


class BrdGenerateResponse(BaseModel):
    request_id: str
    brd_status: str
    brd_draft: str


class BrdReviewSubmit(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    comment: str | None = None


class AgentDefinitionResponse(BaseModel):
    agent_id: str
    name: str
    role: str
    goal: str
    backstory: str
    is_active: bool
    is_locked: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentDefinitionListResponse(BaseModel):
    items: list[AgentDefinitionResponse]
    total: int


class AgentDefinitionUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=3)
    goal: str | None = Field(default=None, min_length=5)
    backstory: str | None = Field(default=None, min_length=10)
