import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.agents.base_agent import AgentDefinitionSpec, BaseAgentError, DBConfiguredAgent, TaskSpec


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

    request_type = normalized.get("request_type")
    if request_type is None:
        normalized["request_type"] = "feature-request"
    elif not isinstance(request_type, str):
        normalized["request_type"] = str(request_type)

    confidence_score = normalized.get("confidence_score")
    if confidence_score is None:
        normalized["confidence_score"] = 0.5
    elif isinstance(confidence_score, bool):
        normalized["confidence_score"] = 1.0 if confidence_score else 0.0
    elif isinstance(confidence_score, (int, float)):
        normalized["confidence_score"] = float(confidence_score)
    else:
        try:
            normalized["confidence_score"] = float(str(confidence_score).strip())
        except (TypeError, ValueError):
            normalized["confidence_score"] = 0.5

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

    rationale_summary = normalized.get("rationale_summary")
    if rationale_summary is None:
        normalized["rationale_summary"] = ""
    elif not isinstance(rationale_summary, str):
        normalized["rationale_summary"] = str(rationale_summary)

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


def normalize_model_name(model_name: str) -> str:
    if model_name.startswith("ollama/"):
        return model_name.split("/", 1)[1]
    return model_name


class ReceptionistAgent(DBConfiguredAgent):
    @property
    def agent_id(self) -> str:
        return "receptionist"

    @property
    def default_model(self) -> str:
        return settings.receptionist_model

    @property
    def timeout_seconds(self) -> int:
        return settings.receptionist_timeout_seconds

    def default_definition(self) -> AgentDefinitionSpec:
        return {
            "role": DEFAULT_RECEPTIONIST_ROLE,
            "goal": DEFAULT_RECEPTIONIST_GOAL,
            "backstory": DEFAULT_RECEPTIONIST_BACKSTORY,
            "llm_model_override": None,
        }

    def default_tasks(self) -> list[TaskSpec]:
        return [
            {
                "description_template": DEFAULT_RECEPTIONIST_TASK_DESCRIPTION_TEMPLATE,
                "expected_output": DEFAULT_RECEPTIONIST_TASK_EXPECTED_OUTPUT,
                "async_execution": False,
            }
        ]

    def build_context(self, raw_text: str, business_context: str | None, priority_hint: str | None) -> dict[str, str]:
        return {
            "raw_text": raw_text,
            "business_context": business_context or "",
            "priority_hint": priority_hint or "",
        }

    def assess(self, raw_text: str, business_context: str | None, priority_hint: str | None) -> ReceptionistAssessment:
        try:
            raw_output = self.execute_tasks(self.build_context(raw_text, business_context, priority_hint))
        except BaseAgentError as exc:
            raise ReceptionistAgentError(str(exc)) from exc
        except Exception as exc:
            raise ReceptionistAgentError(f"Receptionist agent execution failed: {exc}") from exc

        try:
            payload: dict[str, Any] = _normalize_payload(_extract_json_payload(raw_output))
            assessment = ReceptionistAssessment.model_validate(payload)
            assessment.confidence_score = max(0.0, min(1.0, assessment.confidence_score))
            if assessment.confidence_score >= 0.7:
                assessment.clarification_questions = []
            return assessment
        except (ValueError, ValidationError) as exc:
            raise ReceptionistAgentError(f"Receptionist response parsing failed: {exc}") from exc


def assess_request_with_receptionist(raw_text: str, business_context: str | None, priority_hint: str | None) -> ReceptionistAssessment:
    return ReceptionistAgent().assess(
        raw_text=raw_text,
        business_context=business_context,
        priority_hint=priority_hint,
    )
