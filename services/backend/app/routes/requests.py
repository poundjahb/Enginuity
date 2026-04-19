from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RequestRecord
from app.schemas import RequestCreate, RequestResponse, RequestStatus
from app.services.health import check_ollama_health

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse)
async def create_request(payload: RequestCreate, db: Session = Depends(get_db)):
    healthy, error = await check_ollama_health()
    if not healthy:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "PC1 Ollama dependency is unavailable.",
                "blocked_reason": error or "unknown",
            },
        )

    request_id = str(uuid4())
    record = RequestRecord(
        request_id=request_id,
        channel=payload.channel,
        user_identity=payload.user_identity,
        business_context=payload.business_context,
        raw_text=payload.raw_text,
        priority_hint=payload.priority_hint,
        status="received",
    )
    db.add(record)
    db.commit()

    return RequestResponse(request_id=request_id, status="received")


@router.get("/{request_id}", response_model=RequestStatus)
def get_request_status(request_id: str, db: Session = Depends(get_db)):
    record = db.query(RequestRecord).filter(RequestRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    return record
