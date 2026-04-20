from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.config import settings
from app.db import Base, engine
from app.models import AgentDefinition
from app.routes.agents import router as agents_router
from app.routes.tasks import router as tasks_router
from app.routes.requests import router as requests_router
from app.services.health import check_ollama_health
from app.agents.receptionist import (
    DEFAULT_RECEPTIONIST_BACKSTORY,
    DEFAULT_RECEPTIONIST_GOAL,
    DEFAULT_RECEPTIONIST_ROLE,
)
from app.agents.analyst import (
    DEFAULT_ANALYST_BACKSTORY,
    DEFAULT_ANALYST_GOAL,
    DEFAULT_ANALYST_ROLE,
    DEFAULT_ANALYST_TASK_DESCRIPTION_TEMPLATE as _ANALYST_TASK_TMPL,
    DEFAULT_ANALYST_TASK_EXPECTED_OUTPUT as _ANALYST_TASK_OUTPUT,
)

DEFAULT_RECEPTIONIST_TASK_ID = "receptionist-assessment"
DEFAULT_RECEPTIONIST_TASK_NAME = "Assess Intake Request"
DEFAULT_RECEPTIONIST_TASK_DESCRIPTION_TEMPLATE = (
    "Assess the request and return ONLY compact JSON with these keys: "
    "request_type, extracted_scope, confidence_score, clarification_questions, rationale_summary. "
    "Set confidence_score from 0.0 to 1.0. If confidence_score < 0.7, return 2-3 short "
    "targeted clarification_questions. Keep rationale_summary under 30 words.\n\n"
    "raw_text: {raw_text}\n"
    "business_context: {business_context}\n"
    "priority_hint: {priority_hint}\n"
)
DEFAULT_RECEPTIONIST_TASK_EXPECTED_OUTPUT = "Compact single JSON object only. No markdown, no prose."

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_requests_schema_columns() -> None:
    inspector = inspect(engine)
    if "requests" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("requests")}
    expected_columns = {
        "request_type": "TEXT",
        "extracted_scope": "TEXT",
        "confidence_score": "REAL",
        "clarification_questions": "TEXT",
        "clarification_answers": "TEXT",
        "workflow_events": "TEXT",
        "brd_draft": "TEXT",
        "brd_status": "TEXT",
        "brd_review_comment": "TEXT",
    }

    with engine.begin() as connection:
        for column_name, column_type in expected_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE requests ADD COLUMN {column_name} {column_type}"))
                existing_columns.add(column_name)


def _seed_default_agent_definitions() -> None:
    with engine.begin() as connection:
        for agent_id, name, role, goal, backstory in [
            (
                "receptionist",
                "Receptionist Agent",
                DEFAULT_RECEPTIONIST_ROLE,
                DEFAULT_RECEPTIONIST_GOAL,
                DEFAULT_RECEPTIONIST_BACKSTORY,
            ),
            (
                "analyst",
                "Business Analyst Agent",
                DEFAULT_ANALYST_ROLE,
                DEFAULT_ANALYST_GOAL,
                DEFAULT_ANALYST_BACKSTORY,
            ),
        ]:
            existing = connection.execute(
                text("SELECT agent_id FROM agent_definitions WHERE agent_id = :agent_id"),
                {"agent_id": agent_id},
            ).fetchone()
            if existing:
                continue

            connection.execute(
                text(
                    """
                    INSERT INTO agent_definitions (
                        agent_id, name, role, goal, backstory, llm_model_override, is_active, is_locked, version
                    ) VALUES (
                        :agent_id, :name, :role, :goal, :backstory, :llm_model_override, :is_active, :is_locked, :version
                    )
                    """
                ),
                {
                    "agent_id": agent_id,
                    "name": name,
                    "role": role,
                    "goal": goal,
                    "backstory": backstory,
                    "llm_model_override": None,
                    "is_active": True,
                    "is_locked": False,
                    "version": 1,
                },
            )


def _ensure_agent_definitions_schema_columns() -> None:
    inspector = inspect(engine)
    if "agent_definitions" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("agent_definitions")}
    expected_columns = {
        "llm_model_override": "TEXT",
    }

    with engine.begin() as connection:
        for column_name, column_type in expected_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE agent_definitions ADD COLUMN {column_name} {column_type}"))
                existing_columns.add(column_name)


def _ensure_task_definitions_schema_columns() -> None:
    inspector = inspect(engine)
    if "task_definitions" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("task_definitions")}
    expected_columns = {
        "agent_id": "VARCHAR(64)",
        "name": "VARCHAR(128)",
        "description_template": "TEXT",
        "expected_output": "TEXT",
        "async_execution": "BOOLEAN NOT NULL DEFAULT 0",
        "execution_order": "INTEGER",
        "is_active": "BOOLEAN",
        "is_locked": "BOOLEAN",
        "version": "INTEGER",
    }

    with engine.begin() as connection:
        for column_name, column_type in expected_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE task_definitions ADD COLUMN {column_name} {column_type}"))
                existing_columns.add(column_name)


DEFAULT_ANALYST_TASK_ID = "analyst-brd-draft"
DEFAULT_ANALYST_TASK_NAME = "Draft Business Requirements Document"


def _seed_default_task_definitions() -> None:
    _TASK_SEEDS = [
        {
            "task_id": DEFAULT_RECEPTIONIST_TASK_ID,
            "agent_id": "receptionist",
            "name": DEFAULT_RECEPTIONIST_TASK_NAME,
            "description_template": DEFAULT_RECEPTIONIST_TASK_DESCRIPTION_TEMPLATE,
            "expected_output": DEFAULT_RECEPTIONIST_TASK_EXPECTED_OUTPUT,
        },
        {
            "task_id": DEFAULT_ANALYST_TASK_ID,
            "agent_id": "analyst",
            "name": DEFAULT_ANALYST_TASK_NAME,
            "description_template": _ANALYST_TASK_TMPL,
            "expected_output": _ANALYST_TASK_OUTPUT,
        },
    ]

    with engine.begin() as connection:
        for seed in _TASK_SEEDS:
            existing = connection.execute(
                text(
                    """
                    SELECT task_id
                    FROM task_definitions
                    WHERE task_id = :task_id
                      AND agent_id = :agent_id
                    """
                ),
                {"task_id": seed["task_id"], "agent_id": seed["agent_id"]},
            ).fetchone()
            if existing:
                continue

            connection.execute(
                text(
                    """
                    INSERT INTO task_definitions (
                        task_id,
                        agent_id,
                        name,
                        description_template,
                        expected_output,
                        async_execution,
                        execution_order,
                        is_active,
                        is_locked,
                        version
                    ) VALUES (
                        :task_id,
                        :agent_id,
                        :name,
                        :description_template,
                        :expected_output,
                        :async_execution,
                        :execution_order,
                        :is_active,
                        :is_locked,
                        :version
                    )
                    """
                ),
                {
                    "task_id": seed["task_id"],
                    "agent_id": seed["agent_id"],
                    "name": seed["name"],
                    "description_template": seed["description_template"],
                    "expected_output": seed["expected_output"],
                    "async_execution": False,
                    "execution_order": 1,
                    "is_active": True,
                    "is_locked": False,
                    "version": 1,
                },
            )


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    _ensure_requests_schema_columns()
    _ensure_agent_definitions_schema_columns()
    _ensure_task_definitions_schema_columns()
    _seed_default_agent_definitions()
    _seed_default_task_definitions()
    if settings.startup_fail_fast:
        healthy, error = await check_ollama_health()
        if not healthy:
            raise RuntimeError(f"Ollama dependency unavailable at startup: {error}")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "profile": {
            "name": settings.profile_name,
            "max_workers": settings.max_workers,
            "heavy_workers": settings.heavy_workers,
        },
    }


@app.get("/health/dependencies")
async def dependency_health():
    healthy, error = await check_ollama_health()
    return {
        "ollama": {
            "healthy": healthy,
            "base_url": settings.ollama_base_url,
            "error": error,
        }
    }


app.include_router(requests_router)
app.include_router(agents_router)
app.include_router(tasks_router)
