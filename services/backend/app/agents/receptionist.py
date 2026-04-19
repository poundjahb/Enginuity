import json
import os
from typing import Any

from crewai import Agent, Crew, LLM, Task
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import AgentDefinition


class ReceptionistAgentError(RuntimeError):
    pass


class ReceptionistAssessment(BaseModel):
    request_type: str = Field(default="feature-request")
    extracted_scope: str = Field(default="No business context provided")
    confidence_score: float = Field(default=0.5)
    clarification_questions: list[str] = Field(default_factory=list)
    rationale_summary: str = Field(default="")


def _extract_json_payload(raw_output: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()

    try:
        parsed = json.loads(raw_output)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    for index, char in enumerate(raw_output):
        if char not in "{[":
            continue
        try:
            parsed, _ = decoder.raw_decode(raw_output[index:])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError("No JSON object found in receptionist response")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)

    extracted_scope = normalized.get("extracted_scope")
    if isinstance(extracted_scope, list):
        normalized["extracted_scope"] = ", ".join(str(item) for item in extracted_scope)
    elif isinstance(extracted_scope, dict):
        normalized["extracted_scope"] = json.dumps(extracted_scope)
    elif extracted_scope is None:
        normalized["extracted_scope"] = ""
    elif not isinstance(extracted_scope, str):
        normalized["extracted_scope"] = str(extracted_scope)

    clarification_questions = normalized.get("clarification_questions")
    if isinstance(clarification_questions, str):
        normalized["clarification_questions"] = [clarification_questions]
    elif not isinstance(clarification_questions, list):
        normalized["clarification_questions"] = []
    else:
        normalized["clarification_questions"] = [str(item) for item in clarification_questions if item is not None]

    return normalized


DEFAULT_RECEPTIONIST_ROLE = "Receptionist Agent"
DEFAULT_RECEPTIONIST_GOAL = (
    "Read and understand software intake requests, classify request type, "
    "estimate confidence, and ask clarification questions when needed."
)
DEFAULT_RECEPTIONIST_BACKSTORY = (
    "You are the first EOH agent. Your outputs must be structured and safe for "
    "workflow automation."
)


def normalize_model_name(model_name: str) -> str:
    if model_name.startswith("ollama/"):
        return model_name.split("/", 1)[1]
    return model_name


def _build_llm() -> LLM:
    # CrewAI uses LiteLLM providers. Prefixing with ollama/ forces Ollama routing.
    model_name = normalize_model_name(settings.receptionist_model)
    routed_model_name = f"ollama/{model_name}"

    if settings.disable_openai:
        os.environ["OPENAI_API_KEY"] = "disabled"

    return LLM(
        model=routed_model_name,
        base_url=settings.ollama_base_url.rstrip("/"),
        timeout=settings.receptionist_timeout_seconds,
        temperature=0,
        max_tokens=220,
    )


def _default_receptionist_definition() -> dict[str, str]:
    return {
        "role": DEFAULT_RECEPTIONIST_ROLE,
        "goal": DEFAULT_RECEPTIONIST_GOAL,
        "backstory": DEFAULT_RECEPTIONIST_BACKSTORY,
    }


def _load_receptionist_definition(db: Session) -> dict[str, str]:
    record = (
        db.query(AgentDefinition)
        .filter(AgentDefinition.agent_id == "receptionist")
        .filter(AgentDefinition.is_active.is_(True))
        .first()
    )
    if record:
        return {
            "role": record.role,
            "goal": record.goal,
            "backstory": record.backstory,
        }

    if settings.agent_definition_fallback_enabled:
        return _default_receptionist_definition()

    raise ReceptionistAgentError("Receptionist definition not found in database")


def assess_request_with_receptionist(raw_text: str, business_context: str | None, priority_hint: str | None) -> ReceptionistAssessment:
    llm = _build_llm()

    definition = _default_receptionist_definition()
    if settings.agent_definition_db_enabled:
        db = SessionLocal()
        try:
            definition = _load_receptionist_definition(db)
        finally:
            db.close()

    receptionist = Agent(
        role=definition["role"],
        goal=definition["goal"],
        backstory=definition["backstory"],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    task = Task(
        description=(
            "Assess the request and return ONLY compact JSON with these keys: "
            "request_type, extracted_scope, confidence_score, clarification_questions, rationale_summary. "
            "Set confidence_score from 0.0 to 1.0. If confidence_score < 0.7, return 2-3 short "
            "targeted clarification_questions. Keep rationale_summary under 30 words.\n\n"
            f"raw_text: {raw_text}\n"
            f"business_context: {business_context or ''}\n"
            f"priority_hint: {priority_hint or ''}\n"
        ),
        expected_output="Compact single JSON object only. No markdown, no prose.",
        agent=receptionist,
    )

    crew = Crew(agents=[receptionist], tasks=[task], verbose=False)

    try:
        result = crew.kickoff()
    except Exception as exc:
        raise ReceptionistAgentError(f"Receptionist agent execution failed: {exc}") from exc

    try:
        raw_output = getattr(result, "raw", None) or str(result)
        payload: dict[str, Any] = _normalize_payload(_extract_json_payload(raw_output))
        assessment = ReceptionistAssessment.model_validate(payload)
        assessment.confidence_score = max(0.0, min(1.0, assessment.confidence_score))
        if assessment.confidence_score >= 0.7:
            assessment.clarification_questions = []
        return assessment
    except (ValueError, ValidationError) as exc:
        raise ReceptionistAgentError(f"Receptionist response parsing failed: {exc}") from exc
