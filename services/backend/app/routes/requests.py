import json
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RequestRecord
from app.schemas import (
    BrdGenerateResponse,
    BrdReviewSubmit,
    ClarificationSubmit,
    RequestCreate,
    RequestListResponse,
    RequestResponse,
    RequestStatus,
    RequestSummary,
)
from app.services.health import check_ollama_health, check_receptionist_model_available, check_analyst_model_available
from app.agents.receptionist import ReceptionistAgentError
from app.agents.analyst import AnalystAgentError, format_brd_markdown
from app.workflow.receptionist_flow import run_receptionist_flow
from app.workflow.analyst_flow import run_analyst_flow

router = APIRouter(prefix="/requests", tags=["requests"])


def _load_json(raw_value: str | None, fallback: Any):
    if not raw_value:
        return fallback
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return fallback


def _store_json(value: Any) -> str:
    return json.dumps(value)


def _event_message(status: str, confidence_score: float | None = None) -> str:
    if status == "assessing":
        return "Receptionist agent is assessing request context"
    if status == "clarifying":
        return "Clarification requested from user"
    if status == "assessment_complete":
        pct = int((confidence_score or 0) * 100)
        return f"Assessment completed at {pct}% confidence"
    return "Request received"


def _status_payload(record: RequestRecord) -> RequestStatus:
    return RequestStatus(
        request_id=record.request_id,
        channel=record.channel,
        user_identity=record.user_identity,
        business_context=record.business_context,
        raw_text=record.raw_text,
        priority_hint=record.priority_hint,
        status=record.status,
        blocked_reason=record.blocked_reason,
        request_type=record.request_type,
        extracted_scope=record.extracted_scope,
        confidence_score=record.confidence_score,
        clarification_questions=_load_json(record.clarification_questions, []),
        clarification_answers=_load_json(record.clarification_answers, {}),
        workflow_events=_load_json(record.workflow_events, []),
        brd_draft=record.brd_draft,
        brd_status=record.brd_status,
        brd_review_comment=record.brd_review_comment,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


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

    model_ready, model_error = await check_receptionist_model_available()
    if not model_ready:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Configured receptionist model is unavailable in Ollama.",
                "blocked_reason": model_error or "unknown",
            },
        )

    try:
        assessment = await run_in_threadpool(
            run_receptionist_flow,
            payload.raw_text,
            payload.business_context,
            payload.priority_hint,
        )
    except ReceptionistAgentError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Receptionist agent execution failed.",
                "blocked_reason": str(exc),
            },
        ) from exc
    request_type = assessment.request_type
    extracted_scope = assessment.extracted_scope
    confidence_score = assessment.confidence_score
    questions = assessment.clarification_questions
    status = "clarifying" if questions else "assessment_complete"
    events = [
        "Request submitted",
        _event_message("assessing"),
        _event_message(status, confidence_score),
    ]
    if assessment.rationale_summary:
        events.append(f"Receptionist rationale: {assessment.rationale_summary}")

    request_id = str(uuid4())
    record = RequestRecord(
        request_id=request_id,
        channel=payload.channel,
        user_identity=payload.user_identity,
        business_context=payload.business_context,
        raw_text=payload.raw_text,
        priority_hint=payload.priority_hint,
        status=status,
        request_type=request_type,
        extracted_scope=extracted_scope,
        confidence_score=confidence_score,
        clarification_questions=_store_json(questions),
        clarification_answers=_store_json({}),
        workflow_events=_store_json(events),
    )
    db.add(record)
    db.commit()

    return RequestResponse(
        request_id=request_id,
        status=status,
        request_type=request_type,
        extracted_scope=extracted_scope,
        confidence_score=confidence_score,
        clarification_questions=questions,
    )


@router.post("/{request_id}/clarifications", response_model=RequestStatus)
def submit_clarifications(request_id: str, payload: ClarificationSubmit, db: Session = Depends(get_db)):
    record = db.query(RequestRecord).filter(RequestRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")

    if record.status != "clarifying":
        raise HTTPException(status_code=400, detail="Request is not awaiting clarification")

    existing_answers = _load_json(record.clarification_answers, {})
    for key, value in payload.answers.items():
        existing_answers[key] = value

    record.clarification_answers = _store_json(existing_answers)
    record.confidence_score = min(0.95, (record.confidence_score or 0.5) + 0.3)
    record.status = "assessment_complete"
    record.clarification_questions = _store_json([])

    events = _load_json(record.workflow_events, [])
    events.append("User submitted clarification answers")
    events.append(_event_message("assessment_complete", record.confidence_score))
    record.workflow_events = _store_json(events)

    db.add(record)
    db.commit()
    db.refresh(record)
    return _status_payload(record)


@router.post("/{request_id}/brd/generate", response_model=BrdGenerateResponse)
async def generate_brd(request_id: str, db: Session = Depends(get_db)):
    record = db.query(RequestRecord).filter(RequestRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")

    if record.status not in {"assessment_complete", "brd_rejected"}:
        raise HTTPException(status_code=400, detail="BRD generation requires completed assessment")

    healthy, error = await check_ollama_health()
    if not healthy:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "PC1 Ollama dependency is unavailable.",
                "blocked_reason": error or "unknown",
            },
        )

    model_ready, model_error = await check_analyst_model_available()
    if not model_ready:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Configured analyst model is unavailable in Ollama.",
                "blocked_reason": model_error or "unknown",
            },
        )

    clarification_answers: dict[str, str] = _load_json(record.clarification_answers, {})

    try:
        brd = await run_in_threadpool(
            run_analyst_flow,
            record.raw_text,
            record.business_context,
            record.request_type,
            record.extracted_scope,
            clarification_answers or None,
        )
    except AnalystAgentError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Analyst agent execution failed.",
                "blocked_reason": str(exc),
            },
        ) from exc

    brd_text = format_brd_markdown(record.request_id, brd)
    record.brd_draft = brd_text
    record.brd_status = "pending_approval"
    record.status = "brd_pending_approval"
    record.brd_review_comment = None

    events = _load_json(record.workflow_events, [])
    events.append("Analyst agent generated BRD draft")
    events.append("BRD submitted for reviewer approval")
    record.workflow_events = _store_json(events)

    db.add(record)
    db.commit()
    db.refresh(record)
    return BrdGenerateResponse(request_id=record.request_id, brd_status=record.brd_status, brd_draft=record.brd_draft)


@router.post("/{request_id}/brd/review", response_model=RequestStatus)
def review_brd(request_id: str, payload: BrdReviewSubmit, db: Session = Depends(get_db)):
    record = db.query(RequestRecord).filter(RequestRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")

    if record.brd_status != "pending_approval":
        raise HTTPException(status_code=400, detail="BRD is not awaiting review")

    events = _load_json(record.workflow_events, [])
    record.brd_review_comment = payload.comment
    if payload.decision == "approve":
        record.brd_status = "approved"
        record.status = "brd_approved"
        events.append("Reviewer approved BRD draft")
    else:
        record.brd_status = "rejected"
        record.status = "brd_rejected"
        events.append("Reviewer rejected BRD draft")

    record.workflow_events = _store_json(events)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _status_payload(record)


@router.get("", response_model=RequestListResponse)
def list_requests(db: Session = Depends(get_db)):
    records = (
        db.query(RequestRecord)
        .order_by(RequestRecord.updated_at.desc())
        .limit(25)
        .all()
    )

    items = [
        RequestSummary(
            request_id=record.request_id,
            user_identity=record.user_identity,
            status=record.status,
            request_type=record.request_type,
            confidence_score=record.confidence_score,
            updated_at=record.updated_at,
        )
        for record in records
    ]

    return RequestListResponse(items=items, total=len(items))


@router.get("/{request_id}", response_model=RequestStatus)
def get_request_status(request_id: str, db: Session = Depends(get_db)):
    record = db.query(RequestRecord).filter(RequestRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Request not found")
    return _status_payload(record)
