from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.config import settings
from app.db import Base, engine
from app.models import AgentDefinition
from app.routes.agents import router as agents_router
from app.routes.requests import router as requests_router
from app.services.health import check_ollama_health
from app.agents.receptionist import (
    DEFAULT_RECEPTIONIST_BACKSTORY,
    DEFAULT_RECEPTIONIST_GOAL,
    DEFAULT_RECEPTIONIST_ROLE,
)

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
        existing = connection.execute(
            text("SELECT agent_id FROM agent_definitions WHERE agent_id = :agent_id"),
            {"agent_id": "receptionist"},
        ).fetchone()
        if existing:
            return

        connection.execute(
            text(
                """
                INSERT INTO agent_definitions (
                    agent_id, name, role, goal, backstory, is_active, is_locked, version
                ) VALUES (
                    :agent_id, :name, :role, :goal, :backstory, :is_active, :is_locked, :version
                )
                """
            ),
            {
                "agent_id": "receptionist",
                "name": "Receptionist Agent",
                "role": DEFAULT_RECEPTIONIST_ROLE,
                "goal": DEFAULT_RECEPTIONIST_GOAL,
                "backstory": DEFAULT_RECEPTIONIST_BACKSTORY,
                "is_active": True,
                "is_locked": False,
                "version": 1,
            },
        )


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    _ensure_requests_schema_columns()
    _seed_default_agent_definitions()
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
