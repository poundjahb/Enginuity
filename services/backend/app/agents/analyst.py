import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.config import settings
from app.agents.base_agent import AgentDefinitionSpec, BaseAgentError, DBConfiguredAgent, TaskSpec


class AnalystAgentError(RuntimeError):
    pass


class AnalystBrd(BaseModel):
    business_objective: str = Field(default="")
    problem_statement: str = Field(default="")
    proposed_scope: str = Field(default="")
    acceptance_criteria: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)


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

    raise ValueError("No JSON object found in analyst response")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)

    for str_field in ("business_objective", "problem_statement", "proposed_scope"):
        value = normalized.get(str_field)
        if value is None:
            normalized[str_field] = ""
        elif not isinstance(value, str):
            normalized[str_field] = str(value)

    for list_field in ("acceptance_criteria", "assumptions", "out_of_scope", "success_metrics"):
        value = normalized.get(list_field)
        if isinstance(value, str):
            normalized[list_field] = [value] if value.strip() else []
        elif isinstance(value, list):
            normalized[list_field] = [str(item) for item in value if item is not None]
        else:
            normalized[list_field] = []

    return normalized


DEFAULT_ANALYST_ROLE = "Business Analyst Agent"
DEFAULT_ANALYST_GOAL = (
    "Draft a complete Business Requirements Document (BRD) from an assessed intake request, "
    "capturing objective, problem, scope, acceptance criteria, assumptions, out-of-scope items, "
    "and success metrics."
)
DEFAULT_ANALYST_BACKSTORY = (
    "You are the Business Analyst Agent in the EOH engineering hub. "
    "You receive structured intake assessments and produce formal BRD drafts for human approval. "
    "Your outputs must be structured, complete, and safe for workflow automation."
)
DEFAULT_ANALYST_TASK_DESCRIPTION_TEMPLATE = (
    "Draft a Business Requirements Document based on the intake assessment below. "
    "Return ONLY compact JSON with these keys: "
    "business_objective, problem_statement, proposed_scope, "
    "acceptance_criteria (list), assumptions (list), out_of_scope (list), success_metrics (list). "
    "Keep each field concise and actionable. "
    "acceptance_criteria must be 3-5 measurable items. "
    "success_metrics must be 2-4 quantifiable items.\n\n"
    "request_type: {request_type}\n"
    "raw_text: {raw_text}\n"
    "business_context: {business_context}\n"
    "extracted_scope: {extracted_scope}\n"
    "clarification_answers: {clarification_answers}\n"
)
DEFAULT_ANALYST_TASK_EXPECTED_OUTPUT = "Compact single JSON object only. No markdown, no prose."


class AnalystAgent(DBConfiguredAgent):
    @property
    def agent_id(self) -> str:
        return "analyst"

    @property
    def default_model(self) -> str:
        return settings.analyst_model

    @property
    def timeout_seconds(self) -> int:
        return settings.analyst_timeout_seconds

    def default_definition(self) -> AgentDefinitionSpec:
        return {
            "role": DEFAULT_ANALYST_ROLE,
            "goal": DEFAULT_ANALYST_GOAL,
            "backstory": DEFAULT_ANALYST_BACKSTORY,
            "llm_model_override": None,
        }

    def default_tasks(self) -> list[TaskSpec]:
        return [
            {
                "description_template": DEFAULT_ANALYST_TASK_DESCRIPTION_TEMPLATE,
                "expected_output": DEFAULT_ANALYST_TASK_EXPECTED_OUTPUT,
                "async_execution": False,
            }
        ]

    def build_context(
        self,
        raw_text: str,
        business_context: str | None,
        request_type: str | None,
        extracted_scope: str | None,
        clarification_answers: dict[str, str] | None,
    ) -> dict[str, str]:
        answers_text = (
            "; ".join(f"{k}: {v}" for k, v in clarification_answers.items())
            if clarification_answers
            else ""
        )
        return {
            "raw_text": raw_text,
            "business_context": business_context or "",
            "request_type": request_type or "unclassified",
            "extracted_scope": extracted_scope or "",
            "clarification_answers": answers_text,
        }

    def draft_brd(
        self,
        raw_text: str,
        business_context: str | None,
        request_type: str | None,
        extracted_scope: str | None,
        clarification_answers: dict[str, str] | None,
    ) -> AnalystBrd:
        context = self.build_context(
            raw_text=raw_text,
            business_context=business_context,
            request_type=request_type,
            extracted_scope=extracted_scope,
            clarification_answers=clarification_answers,
        )
        try:
            raw_output = self.execute_tasks(context)
        except BaseAgentError as exc:
            raise AnalystAgentError(str(exc)) from exc
        except Exception as exc:
            raise AnalystAgentError(f"Analyst agent execution failed: {exc}") from exc

        try:
            payload: dict[str, Any] = _normalize_payload(_extract_json_payload(raw_output))
            return AnalystBrd.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            raise AnalystAgentError(f"Analyst response parsing failed: {exc}") from exc


def draft_brd_with_analyst(
    raw_text: str,
    business_context: str | None,
    request_type: str | None,
    extracted_scope: str | None,
    clarification_answers: dict[str, str] | None,
) -> AnalystBrd:
    return AnalystAgent().draft_brd(
        raw_text=raw_text,
        business_context=business_context,
        request_type=request_type,
        extracted_scope=extracted_scope,
        clarification_answers=clarification_answers,
    )


def format_brd_markdown(request_id: str, brd: AnalystBrd) -> str:
    lines = [f"# Business Requirements Document — Request {request_id}", ""]

    lines += ["## 1. Business Objective", brd.business_objective or "_Not provided._", ""]
    lines += ["## 2. Problem Statement", brd.problem_statement or "_Not provided._", ""]
    lines += ["## 3. Proposed Scope", brd.proposed_scope or "_Not provided._", ""]

    lines += ["## 4. Acceptance Criteria"]
    if brd.acceptance_criteria:
        lines += [f"- {item}" for item in brd.acceptance_criteria]
    else:
        lines.append("_None specified._")
    lines.append("")

    lines += ["## 5. Assumptions"]
    if brd.assumptions:
        lines += [f"- {item}" for item in brd.assumptions]
    else:
        lines.append("_None specified._")
    lines.append("")

    lines += ["## 6. Out of Scope"]
    if brd.out_of_scope:
        lines += [f"- {item}" for item in brd.out_of_scope]
    else:
        lines.append("_None specified._")
    lines.append("")

    lines += ["## 7. Success Metrics"]
    if brd.success_metrics:
        lines += [f"- {item}" for item in brd.success_metrics]
    else:
        lines.append("_None specified._")
    lines.append("")

    return "\n".join(lines)
