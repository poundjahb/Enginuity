from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import TaskDefinition
from app.schemas import (
    TaskDefinitionCreate,
    TaskDefinitionListResponse,
    TaskDefinitionReorder,
    TaskDefinitionResponse,
    TaskDefinitionUpdate,
)

router = APIRouter(prefix="/agents", tags=["tasks"])


@router.get("/{agent_id}/tasks", response_model=TaskDefinitionListResponse)
def list_agent_tasks(
    agent_id: str,
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(TaskDefinition).filter(TaskDefinition.agent_id == agent_id)
    if not include_inactive:
        query = query.filter(TaskDefinition.is_active.is_(True))

    records = query.order_by(TaskDefinition.execution_order.asc(), TaskDefinition.task_id.asc()).all()
    return TaskDefinitionListResponse(items=records, total=len(records))


@router.post("/{agent_id}/tasks", response_model=TaskDefinitionResponse)
def create_agent_task(agent_id: str, payload: TaskDefinitionCreate, db: Session = Depends(get_db)):
    task_id = payload.task_id or str(uuid4())

    existing = db.query(TaskDefinition).filter(TaskDefinition.task_id == task_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Task definition already exists")

    max_order = (
        db.query(func.max(TaskDefinition.execution_order))
        .filter(TaskDefinition.agent_id == agent_id)
        .scalar()
    )
    next_order = (max_order or 0) + 1

    record = TaskDefinition(
        task_id=task_id,
        agent_id=agent_id,
        name=payload.name,
        description_template=payload.description_template,
        expected_output=payload.expected_output,
        async_execution=payload.async_execution,
        execution_order=payload.execution_order or next_order,
        is_active=True,
        is_locked=False,
        version=1,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{agent_id}/tasks/{task_id}", response_model=TaskDefinitionResponse)
def get_agent_task(agent_id: str, task_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.task_id == task_id)
        .filter(TaskDefinition.agent_id == agent_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Task definition not found")
    return record


@router.patch("/{agent_id}/tasks/{task_id}", response_model=TaskDefinitionResponse)
def update_agent_task(agent_id: str, task_id: str, payload: TaskDefinitionUpdate, db: Session = Depends(get_db)):
    record = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.task_id == task_id)
        .filter(TaskDefinition.agent_id == agent_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Task definition not found")

    if record.is_locked:
        raise HTTPException(status_code=403, detail="Task definition is locked")

    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for field_name, value in updates.items():
        setattr(record, field_name, value)

    record.version += 1
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{agent_id}/tasks/{task_id}", response_model=TaskDefinitionResponse)
def deactivate_agent_task(agent_id: str, task_id: str, db: Session = Depends(get_db)):
    record = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.task_id == task_id)
        .filter(TaskDefinition.agent_id == agent_id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Task definition not found")

    if record.is_locked:
        raise HTTPException(status_code=403, detail="Task definition is locked")

    if not record.is_active:
        raise HTTPException(status_code=400, detail="Task definition already inactive")

    record.is_active = False
    record.version += 1
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/{agent_id}/tasks/reorder", response_model=TaskDefinitionListResponse)
def reorder_agent_tasks(agent_id: str, payload: TaskDefinitionReorder, db: Session = Depends(get_db)):
    records = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.agent_id == agent_id)
        .filter(TaskDefinition.is_active.is_(True))
        .order_by(TaskDefinition.execution_order.asc(), TaskDefinition.task_id.asc())
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail="No active tasks found for agent")

    existing_ids = {record.task_id for record in records}
    proposed_ids = payload.ordered_task_ids

    if set(proposed_ids) != existing_ids:
        raise HTTPException(status_code=400, detail="ordered_task_ids must match active task ids exactly")

    for order, task_id in enumerate(proposed_ids, start=1):
        record = next(item for item in records if item.task_id == task_id)
        if record.is_locked:
            raise HTTPException(status_code=403, detail=f"Task {task_id} is locked")
        record.execution_order = order
        record.version += 1
        db.add(record)

    db.commit()

    ordered_case = case({task_id: index for index, task_id in enumerate(proposed_ids)}, value=TaskDefinition.task_id)
    updated_records = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.agent_id == agent_id)
        .filter(TaskDefinition.task_id.in_(proposed_ids))
        .order_by(ordered_case.asc())
        .all()
    )
    return TaskDefinitionListResponse(items=updated_records, total=len(updated_records))
