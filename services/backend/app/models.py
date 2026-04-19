from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.db import Base


class RequestRecord(Base):
    __tablename__ = "requests"

    request_id = Column(String(64), primary_key=True, index=True)
    channel = Column(String(32), nullable=False, default="web")
    user_identity = Column(String(255), nullable=False)
    business_context = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    priority_hint = Column(String(32), nullable=True)
    status = Column(String(32), nullable=False, default="received")
    blocked_reason = Column(String(255), nullable=True)
    request_type = Column(String(64), nullable=True)
    extracted_scope = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    clarification_questions = Column(Text, nullable=True)
    clarification_answers = Column(Text, nullable=True)
    workflow_events = Column(Text, nullable=True)
    brd_draft = Column(Text, nullable=True)
    brd_status = Column(String(32), nullable=True)
    brd_review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AgentDefinition(Base):
    __tablename__ = "agent_definitions"

    agent_id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    role = Column(Text, nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
