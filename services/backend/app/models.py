from sqlalchemy import Column, DateTime, String, Text, func

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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
