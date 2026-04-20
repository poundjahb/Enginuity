from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AgentDefinition
from app.schemas import AgentDefinitionListResponse, AgentDefinitionResponse, AgentDefinitionUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/definitions", response_model=AgentDefinitionListResponse)
def list_agent_definitions(db: Session = Depends(get_db)):
    records = (
        db.query(AgentDefinition)
        .filter(AgentDefinition.is_active.is_(True))
        .order_by(AgentDefinition.agent_id.asc())
        .all()
    )
    return AgentDefinitionListResponse(items=records, total=len(records))


@router.get("/definitions/{agent_id}", response_model=AgentDefinitionResponse)
def get_agent_definition(agent_id: str, db: Session = Depends(get_db)):
    record = db.query(AgentDefinition).filter(AgentDefinition.agent_id == agent_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Agent definition not found")
    return record


@router.patch("/definitions/{agent_id}", response_model=AgentDefinitionResponse)
def update_agent_definition(agent_id: str, payload: AgentDefinitionUpdate, db: Session = Depends(get_db)):
    record = db.query(AgentDefinition).filter(AgentDefinition.agent_id == agent_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Agent definition not found")

    if record.is_locked:
        raise HTTPException(status_code=403, detail="Agent definition is locked")

    updates = payload.model_dump(exclude_none=True)
    if payload.llm_model_override == "":
        updates["llm_model_override"] = None
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for field_name, value in updates.items():
        setattr(record, field_name, value)

    record.version += 1
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
